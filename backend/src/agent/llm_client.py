"""Provider-agnostic LLM client with tool-use loop for PinkShieldAI."""

import json
import logging

from sqlalchemy.orm import Session as DBSession

from ..core.config import settings
from ..engine.factors import FACTORS_BY_ID
from ..engine.state_machine import QuestionnaireEngine
from ..models.models import ConversationTurn
from .llm_provider import get_provider
from .system_prompt import SAKHI_SYSTEM_PROMPT, build_state_context
from .tools import TOOL_DEFINITIONS

logger = logging.getLogger(__name__)

MAX_TOOL_CALLS_PER_TURN = 10


def process_message(
    db: DBSession,
    session_id: str,
    user_message: str,
) -> dict:
    """Process a user message through the configured LLM with tool-use loop."""
    engine = QuestionnaireEngine(db, session_id)
    if not engine.session:
        return {"error": "Session not found"}

    history = _load_conversation_history(db, session_id)
    state = engine.get_session_state()
    state_context = build_state_context(state)

    system = SAKHI_SYSTEM_PROMPT
    if state_context:
        system += f"\n\n## Current session state\n{state_context}"

    user_turn_number = len(history) + 1
    history.append({"role": "user", "content": user_message})

    _save_turn(db, session_id, user_turn_number, "user", user_message)

    provider = get_provider()
    model = settings.LLM_MODEL
    tool_call_count = 0
    assistant_text = ""

    while tool_call_count < MAX_TOOL_CALLS_PER_TURN:
        result = provider.chat(model, system, history, TOOL_DEFINITIONS)

        assistant_msg = {"role": "assistant", "content": result.text or ""}
        if result.tool_calls:
            assistant_msg["tool_calls"] = [
                {"id": tc.id, "name": tc.name, "input": tc.input}
                for tc in result.tool_calls
            ]
        history.append(assistant_msg)

        if not result.tool_calls:
            assistant_text = result.text or ""
            break

        tool_results = []
        for tc in result.tool_calls:
            tool_call_count += 1
            output = _execute_tool(engine, tc.name, tc.input)
            tool_results.append({
                "tool_call_id": tc.id,
                "name": tc.name,
                "result": json.dumps(output),
            })

        history.append({"role": "tool_results", "results": tool_results})

        state = engine.get_session_state()
        state_context = build_state_context(state)
        if state_context:
            system = SAKHI_SYSTEM_PROMPT + f"\n\n## Current session state\n{state_context}"

    assistant_turn_number = user_turn_number + 1
    _save_turn(db, session_id, assistant_turn_number, "assistant", assistant_text)

    return {
        "session_id": session_id,
        "response": assistant_text,
        "session_status": engine.session.status,
        "tool_calls_made": tool_call_count,
    }


def generate_greeting(db: DBSession, session_id: str) -> dict:
    """Generate Sakhi's opening greeting for a new session."""
    engine = QuestionnaireEngine(db, session_id)
    if not engine.session:
        return {"error": "Session not found"}

    first_q = engine.get_next_question()
    context = f"""This is a brand new session. The user just started the assessment.
The first question to ask is: {first_q['question']}
Factor ID: {first_q['factor_id']}, Data type: {first_q['data_type']}, Options: {first_q.get('options')}

Greet the user warmly, briefly explain what this assessment is about (a quick health check-in about breast health, takes about 4 minutes, all answers are confidential), and then naturally lead into the first question."""

    provider = get_provider()
    model = settings.LLM_MODEL

    result = provider.chat(
        model=model,
        system=SAKHI_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": context}],
        tools=TOOL_DEFINITIONS,
    )

    greeting = result.text or ""
    _save_turn(db, session_id, 1, "assistant", greeting)

    return {
        "session_id": session_id,
        "response": greeting,
        "session_status": "active",
        "first_question": first_q,
    }


def _execute_tool(engine: QuestionnaireEngine, tool_name: str, tool_input: dict) -> dict:
    if tool_name == "record_answer":
        return engine.record_answer(
            factor_id=tool_input["factor_id"],
            value=tool_input["value"],
            raw_utterance=tool_input.get("raw_utterance"),
        )
    elif tool_name == "get_next_question":
        return engine.get_next_question()
    elif tool_name == "flag_urgent_referral":
        return engine.flag_urgent_referral(
            reason=tool_input["reason"],
            details=tool_input.get("details"),
        )
    elif tool_name == "compute_risk_score":
        return engine.compute_risk_score()
    elif tool_name == "get_session_state":
        return engine.get_session_state()
    elif tool_name == "clarify_question":
        factor = FACTORS_BY_ID.get(tool_input["factor_id"])
        if factor:
            return {"factor_id": factor.id, "clarification": factor.clarification}
        return {"error": f"Unknown factor: {tool_input['factor_id']}"}
    elif tool_name == "switch_language":
        return {"status": "noted", "language": tool_input["language"],
                "message": "Language preference recorded. MVP currently supports English only."}
    elif tool_name == "end_session":
        return engine.end_session(reason=tool_input.get("reason", "user_ended"))
    else:
        return {"error": f"Unknown tool: {tool_name}"}


def _load_conversation_history(db: DBSession, session_id: str) -> list[dict]:
    turns = (
        db.query(ConversationTurn)
        .filter_by(session_id=session_id)
        .order_by(ConversationTurn.turn_number)
        .all()
    )
    return [{"role": turn.role, "content": turn.content} for turn in turns]


def _save_turn(
    db: DBSession,
    session_id: str,
    turn_number: int,
    role: str,
    content: str,
    tool_calls: list | None = None,
    tool_results: list | None = None,
):
    turn = ConversationTurn(
        session_id=session_id,
        turn_number=turn_number,
        role=role,
        content=content,
        tool_calls=tool_calls,
        tool_results=tool_results,
    )
    db.add(turn)
    db.commit()
