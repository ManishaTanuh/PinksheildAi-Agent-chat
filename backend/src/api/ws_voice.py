"""WebSocket endpoint for speech-native voice mode via Gemini Live API."""

import asyncio
import base64
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..db.session import get_db_context
from ..engine.state_machine import QuestionnaireEngine
from ..models.models import Session
from ..voice.gemini_live import GeminiLiveSession

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/voice/{session_id}")
async def voice_live(ws: WebSocket, session_id: str):
    await ws.accept()

    with get_db_context() as db:
        session = db.query(Session).filter_by(id=session_id).first()
        if not session:
            await ws.send_json({"type": "error", "text": "Session not found"})
            await ws.close()
            return

        if session.status not in ("active", "referred"):
            await ws.send_json({"type": "error", "text": f"Session is {session.status}"})
            await ws.close()
            return

        engine = QuestionnaireEngine(db, session_id)
        live = GeminiLiveSession(engine, db, session_id)

        try:
            await live.connect()
            logger.info("Gemini Live session started for %s", session_id)

            recv_task = asyncio.create_task(
                _gemini_to_client(live, ws), name="gemini-recv"
            )
            send_task = asyncio.create_task(
                _client_to_gemini(ws, live), name="client-send"
            )

            done, pending = await asyncio.wait(
                [recv_task, send_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for t in pending:
                t.cancel()
            for t in done:
                if t.exception():
                    logger.error("Voice WS task error: %s", t.exception())

        except WebSocketDisconnect:
            logger.info("Client disconnected from voice WS: %s", session_id)
        except Exception:
            logger.exception("Voice WS error for session %s", session_id)
            try:
                await ws.send_json({"type": "error", "text": "Voice session error"})
            except Exception:
                pass
        finally:
            await live.close()
            logger.info("Gemini Live session closed for %s", session_id)


async def _gemini_to_client(live: GeminiLiveSession, ws: WebSocket):
    """Run the Gemini receive loop and forward messages to the WebSocket client."""
    accumulated_text = ""

    async for response in live.receive_responses():
        try:
            if response.type == "audio":
                await ws.send_json({"type": "audio", "data": response.data})
            elif response.type == "text":
                await ws.send_json({"type": "text", "text": response.text})
            elif response.type == "status":
                await ws.send_json({"type": "status", "session_status": response.session_status})
            elif response.type == "turn_complete":
                await ws.send_json({"type": "turn_complete"})
        except Exception:
            break


async def _client_to_gemini(ws: WebSocket, live: GeminiLiveSession):
    """Forward client audio/text to Gemini Live session."""
    try:
        while True:
            raw = await ws.receive()

            if raw.get("bytes"):
                await live.send_audio(raw["bytes"])
            elif raw.get("text"):
                data = json.loads(raw["text"])
                if data["type"] == "audio":
                    pcm = base64.b64decode(data["data"])
                    await live.send_audio(pcm)
                elif data["type"] == "text":
                    await live.send_text(data["text"])
    except WebSocketDisconnect:
        pass
