"""Gemini Live API session manager for speech-native voice mode.

Wraps the Gemini Live API (via google-genai SDK on Vertex AI) to provide
bidirectional audio streaming with function calling for the PinkShieldAI
questionnaire.
"""

import base64
import logging
from dataclasses import dataclass

from google import genai
from google.genai import types

from ..agent.llm_client import _execute_tool, _save_turn
from ..agent.system_prompt import SAKHI_SYSTEM_PROMPT, build_state_context
from ..agent.tools import TOOL_DEFINITIONS
from ..core.config import settings
from ..engine.state_machine import QuestionnaireEngine

logger = logging.getLogger(__name__)


def _strip_unsupported_keys(schema: dict) -> dict:
    unsupported = {"additionalProperties"}
    cleaned = {k: v for k, v in schema.items() if k not in unsupported}
    if "properties" in cleaned:
        cleaned["properties"] = {
            k: _strip_unsupported_keys(v)
            for k, v in cleaned["properties"].items()
        }
    return cleaned


def _build_gemini_tools() -> list[types.Tool]:
    declarations = []
    for t in TOOL_DEFINITIONS:
        schema = _strip_unsupported_keys(t["input_schema"])
        declarations.append(types.FunctionDeclaration(
            name=t["name"],
            description=t.get("description", ""),
            parameters=schema if schema.get("properties") else None,
        ))
    return [types.Tool(function_declarations=declarations)]


def _build_live_config(state_context: str) -> types.LiveConnectConfig:
    system = SAKHI_SYSTEM_PROMPT
    if state_context:
        system += f"\n\n## Current session state\n{state_context}"

    return types.LiveConnectConfig(
        response_modalities=["AUDIO", "TEXT"],
        tools=_build_gemini_tools(),
        system_instruction=system,
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=settings.GEMINI_VOICE_NAME,
                )
            )
        ),
    )


@dataclass
class LiveMessage:
    type: str  # "audio" | "text" | "status" | "turn_complete"
    data: str = ""
    text: str = ""
    session_status: str = ""


class GeminiLiveSession:
    """Manages a single Gemini Live API session for one user conversation."""

    def __init__(self, engine: QuestionnaireEngine, db, session_id: str):
        self.engine = engine
        self.db = db
        self.session_id = session_id
        self._client = genai.Client(
            vertexai=True,
            project=settings.GCP_PROJECT,
            location=settings.LLM_LOCATION or settings.GCP_REGION,
        )
        self._session = None
        self._turn_number = 0

    async def connect(self):
        state = self.engine.get_session_state()
        state_context = build_state_context(state)
        config = _build_live_config(state_context)
        model = settings.GEMINI_LIVE_MODEL

        self._session = await self._client.aio.live.connect(
            model=model,
            config=config,
        ).__aenter__()

        first_q = self.engine.get_next_question()
        greeting_prompt = (
            f"This is a brand new session. The user just started the assessment. "
            f"The first question to ask is: {first_q['question']} "
            f"Factor ID: {first_q['factor_id']}, Data type: {first_q['data_type']}, "
            f"Options: {first_q.get('options')}. "
            f"Greet the user warmly, briefly explain what this assessment is about "
            f"(a quick health check-in about breast health, takes about 4 minutes, "
            f"all answers are confidential), and then naturally lead into the first question."
        )
        await self._session.send_client_content(
            turns=types.Content(
                role="user",
                parts=[types.Part.from_text(text=greeting_prompt)],
            )
        )

    async def close(self):
        if self._session:
            await self._session.__aexit__(None, None, None)
            self._session = None

    async def send_audio(self, pcm_data: bytes):
        if self._session:
            await self._session.send_realtime_input(
                audio=types.Blob(data=pcm_data, mime_type="audio/pcm;rate=16000")
            )

    async def send_text(self, text: str):
        if self._session:
            self._turn_number += 1
            _save_turn(self.db, self.session_id, self._turn_number, "user", text)
            await self._session.send_client_content(
                turns=types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=text)],
                )
            )

    async def receive_responses(self):
        """Async generator yielding LiveMessage objects from the Gemini session."""
        accumulated_text = ""

        async for response in self._session.receive():
            if response.data is not None:
                audio_b64 = base64.b64encode(response.data).decode("ascii")
                yield LiveMessage(type="audio", data=audio_b64)

            if response.text is not None:
                accumulated_text += response.text
                yield LiveMessage(type="text", text=response.text)

            if response.tool_call:
                for fc in response.tool_call.function_calls:
                    tool_input = dict(fc.args) if fc.args else {}
                    result = _execute_tool(self.engine, fc.name, tool_input)
                    logger.info("Tool call: %s(%s) -> %s", fc.name, tool_input, result)

                    fn_response = types.FunctionResponse(
                        id=fc.id,
                        name=fc.name,
                        response=result,
                    )
                    await self._session.send_tool_response(
                        function_responses=[fn_response]
                    )

                    yield LiveMessage(
                        type="status",
                        session_status=self.engine.session.status,
                    )

            if response.server_content and response.server_content.turn_complete:
                if accumulated_text:
                    self._turn_number += 1
                    _save_turn(self.db, self.session_id, self._turn_number,
                               "assistant", accumulated_text)
                    accumulated_text = ""

                yield LiveMessage(type="turn_complete")
