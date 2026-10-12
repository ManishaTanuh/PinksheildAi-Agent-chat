import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session as DBSession

from ..models.models import Session, Answer, RiskResult
from .factors import FACTORS_BY_ID, TIER_1_ORDER, Factor
from .validation import validate_answer
from .risk_model import compute_risk


class QuestionnaireEngine:
    """Deterministic questionnaire state machine. Reconstructed from DB per request."""

    def __init__(self, db: DBSession, session_id: str):
        self.db = db
        self.session_id = session_id
        self._session: Session | None = None
        self._answers: dict[str, str] = {}
        self._load()

    def _load(self):
        self._session = self.db.query(Session).filter_by(id=self.session_id).first()
        if self._session:
            rows = self.db.query(Answer).filter_by(session_id=self.session_id).all()
            self._answers = {a.factor_id: a.value for a in rows}

    @classmethod
    def create_session(cls, db: DBSession, channel: str = "rest", language: str = "en") -> "QuestionnaireEngine":
        session_id = str(uuid.uuid4())
        session = Session(id=session_id, channel=channel, language=language)
        db.add(session)
        db.commit()
        db.refresh(session)
        engine = cls(db, session_id)
        return engine

    @property
    def session(self) -> Session:
        return self._session

    @property
    def answers(self) -> dict[str, str]:
        return dict(self._answers)

    def record_answer(self, factor_id: str, value: str, raw_utterance: str | None = None) -> dict:
        """Validate and store an answer. Returns status dict."""
        value_clean = value.strip().lower()
        is_valid, error = validate_answer(factor_id, value_clean)

        if not is_valid:
            return {"status": "rejected", "factor_id": factor_id, "error": error}

        existing = self.db.query(Answer).filter_by(
            session_id=self.session_id, factor_id=factor_id
        ).first()

        if existing:
            existing.value = value_clean
            existing.raw_utterance = raw_utterance
        else:
            answer = Answer(
                session_id=self.session_id,
                factor_id=factor_id,
                value=value_clean,
                raw_utterance=raw_utterance,
            )
            self.db.add(answer)

        self.db.commit()
        self._answers[factor_id] = value_clean

        referral = self._check_safety(factor_id, value_clean)

        return {
            "status": "accepted",
            "factor_id": factor_id,
            "value": value_clean,
            "urgent_referral": referral,
        }

    def get_next_question(self) -> dict:
        """Determine the next unanswered factor, respecting skip logic and sub-question triggers."""
        for factor_id in TIER_1_ORDER:
            factor = FACTORS_BY_ID[factor_id]

            if factor_id in self._answers:
                continue

            if self._should_skip(factor):
                continue

            if self._is_sub_question(factor) and not self._sub_question_triggered(factor):
                continue

            return {
                "status": "next_question",
                "factor_id": factor.id,
                "question": factor.question,
                "data_type": factor.data_type,
                "ui_type": factor.ui_type,
                "options": factor.options,
                "display_labels": factor.display_labels,
                "min_val": factor.min_val,
                "max_val": factor.max_val,
                "clarification": factor.clarification,
            }

        return {"status": "assessment_complete", "message": "All Tier 1 questions answered."}

    def get_session_state(self) -> dict:
        """Return a summary of progress for Claude's context."""
        total = sum(
            1 for fid in TIER_1_ORDER
            if not self._should_skip(FACTORS_BY_ID[fid])
            and (not self._is_sub_question(FACTORS_BY_ID[fid]) or self._sub_question_triggered(FACTORS_BY_ID[fid]))
        )
        answered = len(self._answers)
        factors_summary = []
        for fid, val in self._answers.items():
            f = FACTORS_BY_ID.get(fid)
            if f:
                factors_summary.append({"factor_id": fid, "label": f.label, "value": val})

        return {
            "session_id": self.session_id,
            "status": self._session.status if self._session else "unknown",
            "answered": answered,
            "total": total,
            "progress_pct": round(answered / total * 100) if total > 0 else 0,
            "answers": factors_summary,
        }

    def flag_urgent_referral(self, reason: str, details: str | None = None) -> dict:
        """Mark session for urgent clinical referral."""
        if self._session:
            self._session.urgent_referral = True
            existing_reasons = self._session.referral_reasons or []
            existing_reasons.append({"reason": reason, "details": details})
            self._session.referral_reasons = existing_reasons
            self._session.status = "referred"
            self.db.commit()

        return {
            "status": "referral_flagged",
            "reason": reason,
            "message": "This session has been flagged for urgent clinical referral.",
        }

    def compute_risk_score(self) -> dict:
        """Compute risk score from collected answers."""
        result = compute_risk(self._answers)

        if self._session:
            self._session.risk_score = result["risk_probability"]
            self._session.risk_level = result["risk_level"]
            self._session.status = "completed"
            self._session.completed_at = datetime.now(timezone.utc)

            risk_result = RiskResult(
                session_id=self.session_id,
                risk_level=result["risk_level"],
                risk_probability=result["risk_probability"],
                key_risk_factors=result["key_risk_factors"],
                protective_factors=result["protective_factors"],
                recommendations=result["recommendations"],
                model_version=result["model_version"],
            )
            self.db.add(risk_result)
            self.db.commit()

        return result

    def end_session(self, reason: str = "user_ended") -> dict:
        """End the session early."""
        if self._session:
            self._session.status = "abandoned" if reason == "user_ended" else reason
            self._session.completed_at = datetime.now(timezone.utc)
            self.db.commit()

        return {"status": "session_ended", "reason": reason}

    def _should_skip(self, factor: Factor) -> bool:
        """Evaluate skip conditions. Handles both single-value and multi_select (comma-separated) answers."""
        if not factor.skip_if:
            return False

        conditions = factor.skip_if.split(",")
        for cond in conditions:
            parts = cond.strip().split("=")
            if len(parts) != 2:
                continue
            ref_id, ref_val = parts
            if ref_id not in self._answers:
                continue
            answer = self._answers[ref_id]
            answer_values = [v.strip() for v in answer.split(",")]
            if ref_val in answer_values:
                return True

        return False

    def _is_sub_question(self, factor: Factor) -> bool:
        """Check if this factor is a sub-question (has a letter suffix like 1.4b)."""
        return factor.id[-1].isalpha()

    def _sub_question_triggered(self, factor: Factor) -> bool:
        """Check if the parent question's answer triggers this sub-question."""
        parent_id = factor.id[:-1]  # "1.4b" -> "1.4"
        parent = FACTORS_BY_ID.get(parent_id)
        if not parent or parent_id not in self._answers:
            return False

        if not parent.trigger_condition:
            return False

        trigger_values = set(v.strip() for v in parent.trigger_condition.split(","))
        answer_values = set(v.strip() for v in self._answers[parent_id].split(","))
        return bool(trigger_values & answer_values)

    def _check_safety(self, factor_id: str, value: str) -> dict | None:
        """Check if an answer triggers an urgent referral."""
        factor = FACTORS_BY_ID.get(factor_id)
        if not factor or not factor.is_safety_critical:
            return None

        if value == "yes":
            reason = (
                "Current breast symptoms reported"
                if factor_id == "1.12"
                else "Nipple discharge or skin changes reported"
            )
            return self.flag_urgent_referral(reason)

        return None
