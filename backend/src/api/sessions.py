import base64
import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session as DBSession

from ..db.session import get_db
from ..engine.state_machine import QuestionnaireEngine
from ..agent.llm_client import process_message, generate_greeting
from ..core.config import settings
from ..models.models import Session, Answer, RiskResult
from ..schemas.schemas import (
    CreateSessionRequest, ChatRequest, SessionResponse,
    SessionDetail, RiskResultResponse, VoiceResponse,
    AnswerRequest, AnswerResponse, QuestionResponse,
    TTSRequest, TTSResponse,
)
from ..voice.stt import transcribe
from ..voice.tts import synthesize

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.post("")
def create_session(
    req: CreateSessionRequest,
    db: DBSession = Depends(get_db),
):
    engine = QuestionnaireEngine.create_session(db, channel=req.channel, language=req.language)

    if req.mode == "structured":
        next_q = engine.get_next_question()
        state = engine.get_session_state()
        return {
            "session_id": engine.session.id,
            "status": "session_created",
            "next_question": next_q,
            "progress": {"answered": state["answered"], "total": state["total"], "progress_pct": state["progress_pct"]},
        }

    result = generate_greeting(db, engine.session.id)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    audio_b64 = None
    if req.voice:
        try:
            audio_bytes = synthesize(result["response"])
            audio_b64 = base64.b64encode(audio_bytes).decode("ascii")
        except Exception:
            logger.exception("TTS failed for greeting")

    return SessionResponse(
        session_id=result["session_id"],
        response=result["response"],
        session_status=result["session_status"],
        first_question=result.get("first_question"),
        audio_base64=audio_b64,
        voice_mode=settings.VOICE_MODE if req.voice else None,
    )


@router.post("/{session_id}/answer", response_model=AnswerResponse)
def submit_answer(
    session_id: str,
    req: AnswerRequest,
    db: DBSession = Depends(get_db),
):
    session = db.query(Session).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status not in ("active", "referred"):
        raise HTTPException(status_code=400, detail=f"Session is {session.status}, cannot continue")

    engine = QuestionnaireEngine(db, session_id)
    result = engine.record_answer(req.factor_id, req.value)

    if result["status"] == "rejected":
        return AnswerResponse(status="rejected", factor_id=req.factor_id, error=result["error"])

    next_q = engine.get_next_question()
    state = engine.get_session_state()

    if next_q["status"] == "assessment_complete":
        risk = engine.compute_risk_score()
        return AnswerResponse(
            status="assessment_complete",
            factor_id=req.factor_id,
            value=result["value"],
            next_question=None,
            progress={"answered": state["answered"], "total": state["total"], "progress_pct": 100},
            urgent_referral=result.get("urgent_referral"),
        )

    return AnswerResponse(
        status="accepted",
        factor_id=req.factor_id,
        value=result["value"],
        next_question=QuestionResponse(**next_q),
        progress={"answered": state["answered"], "total": state["total"], "progress_pct": state["progress_pct"]},
        urgent_referral=result.get("urgent_referral"),
    )


@router.get("/{session_id}/question", response_model=QuestionResponse)
def get_current_question(
    session_id: str,
    db: DBSession = Depends(get_db),
):
    session = db.query(Session).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    engine = QuestionnaireEngine(db, session_id)
    next_q = engine.get_next_question()
    return QuestionResponse(**next_q)


@router.post("/tts", response_model=TTSResponse)
def text_to_speech(req: TTSRequest):
    try:
        audio_bytes = synthesize(req.text)
        audio_b64 = base64.b64encode(audio_bytes).decode("ascii")
    except Exception:
        logger.exception("TTS synthesis failed")
        raise HTTPException(status_code=500, detail="TTS synthesis failed")
    return TTSResponse(audio_base64=audio_b64)


@router.post("/{session_id}/voice", response_model=VoiceResponse)
async def voice_chat(
    session_id: str,
    audio: UploadFile = File(...),
    db: DBSession = Depends(get_db),
):
    session = db.query(Session).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status not in ("active", "referred"):
        raise HTTPException(status_code=400, detail=f"Session is {session.status}, cannot continue")

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    transcription = transcribe(audio_bytes)
    if not transcription:
        raise HTTPException(status_code=400, detail="Could not transcribe audio")

    result = process_message(db, session_id, transcription)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    try:
        tts_audio = synthesize(result["response"])
        audio_b64 = base64.b64encode(tts_audio).decode("ascii")
    except Exception:
        logger.exception("TTS synthesis failed")
        audio_b64 = ""

    return VoiceResponse(
        session_id=result["session_id"],
        transcription=transcription,
        response=result["response"],
        audio_base64=audio_b64,
        session_status=result["session_status"],
        tool_calls_made=result.get("tool_calls_made"),
    )


@router.post("/{session_id}/chat", response_model=SessionResponse)
def chat(
    session_id: str,
    req: ChatRequest,
    db: DBSession = Depends(get_db),
):
    session = db.query(Session).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status not in ("active", "referred"):
        raise HTTPException(status_code=400, detail=f"Session is {session.status}, cannot continue")

    result = process_message(db, session_id, req.message)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return SessionResponse(
        session_id=result["session_id"],
        response=result["response"],
        session_status=result["session_status"],
        tool_calls_made=result.get("tool_calls_made"),
    )


@router.get("/{session_id}", response_model=SessionDetail)
def get_session(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    answers = db.query(Answer).filter_by(session_id=session_id).all()

    return SessionDetail(
        session_id=session.id,
        channel=session.channel,
        language=session.language,
        status=session.status,
        current_tier=session.current_tier,
        risk_level=session.risk_level,
        risk_score=session.risk_score,
        urgent_referral=session.urgent_referral,
        answers=[
            {"factor_id": a.factor_id, "value": a.value, "raw_utterance": a.raw_utterance}
            for a in answers
        ],
        created_at=session.created_at.isoformat() if session.created_at else "",
        completed_at=session.completed_at.isoformat() if session.completed_at else None,
    )


@router.get("/{session_id}/result", response_model=RiskResultResponse)
def get_result(session_id: str, db: DBSession = Depends(get_db)):
    result = db.query(RiskResult).filter_by(session_id=session_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="No risk result for this session")

    return RiskResultResponse(
        session_id=result.session_id,
        risk_level=result.risk_level,
        risk_probability=result.risk_probability,
        key_risk_factors=result.key_risk_factors,
        protective_factors=result.protective_factors,
        recommendations=result.recommendations,
        model_version=result.model_version,
    )


@router.delete("/{session_id}")
def end_session(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    engine = QuestionnaireEngine(db, session_id)
    result = engine.end_session()
    return result
