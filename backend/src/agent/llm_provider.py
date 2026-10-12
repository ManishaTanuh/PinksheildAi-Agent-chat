"""LLM provider abstraction for PinkShieldAI.

All providers run on GCP — Vertex AI partner models (Claude), native Gemini,
and Model Garden (Llama, Gemma, MedGemma) via the OpenAI-compatible endpoint.
No external API keys needed; everything uses Google Cloud auth.
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ..core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class ChatResult:
    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)


class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    def chat(
        self,
        model: str,
        system: str,
        messages: list[dict],
        tools: list[dict],
    ) -> ChatResult:
        ...

    @abstractmethod
    def format_messages(self, messages: list[dict]) -> list:
        """Convert internal message format to provider-native format."""
        ...


# ---------------------------------------------------------------------------
# Anthropic (Claude via Vertex AI)
# ---------------------------------------------------------------------------

class AnthropicProvider(LLMProvider):

    def __init__(self):
        from anthropic import AnthropicVertex

        self._client = AnthropicVertex(
            project_id=settings.GCP_PROJECT,
            region=settings.GCP_REGION,
        )

    def chat(self, model, system, messages, tools):
        native_msgs = self.format_messages(messages)

        response = self._client.messages.create(
            model=model,
            max_tokens=1024,
            system=system,
            messages=native_msgs,
            tools=tools,
        )

        result = ChatResult()
        for block in response.content:
            if block.type == "text":
                result.text = (result.text or "") + block.text
            elif block.type == "tool_use":
                result.tool_calls.append(
                    ToolCall(id=block.id, name=block.name, input=block.input)
                )
        return result

    def format_messages(self, messages):
        native = []
        for msg in messages:
            if msg["role"] == "tool_results":
                native.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": r["tool_call_id"],
                            "content": r["result"],
                        }
                        for r in msg["results"]
                    ],
                })
            elif msg["role"] == "assistant" and msg.get("tool_calls"):
                content = []
                if msg.get("content"):
                    content.append({"type": "text", "text": msg["content"]})
                for tc in msg["tool_calls"]:
                    content.append({
                        "type": "tool_use",
                        "id": tc["id"],
                        "name": tc["name"],
                        "input": tc["input"],
                    })
                native.append({"role": "assistant", "content": content})
            else:
                native.append({"role": msg["role"], "content": msg["content"]})
        return native


# ---------------------------------------------------------------------------
# Google Gemini (native Vertex AI)
# ---------------------------------------------------------------------------

class GeminiProvider(LLMProvider):

    def __init__(self):
        from google import genai

        self._genai = genai
        self._client = genai.Client(
            project=settings.GCP_PROJECT,
            location=settings.GCP_REGION,
        )

    @staticmethod
    def _strip_unsupported_keys(schema: dict) -> dict:
        unsupported = {"additionalProperties"}
        cleaned = {k: v for k, v in schema.items() if k not in unsupported}
        if "properties" in cleaned:
            cleaned["properties"] = {
                k: GeminiProvider._strip_unsupported_keys(v)
                for k, v in cleaned["properties"].items()
            }
        return cleaned

    def _convert_tools(self, tools: list[dict]):
        types = self._genai.types
        declarations = []
        for t in tools:
            schema = self._strip_unsupported_keys(t["input_schema"])
            declarations.append(types.FunctionDeclaration(
                name=t["name"],
                description=t.get("description", ""),
                parameters=schema if schema.get("properties") else None,
            ))
        return types.Tool(function_declarations=declarations)

    def chat(self, model, system, messages, tools):
        types = self._genai.types
        native_msgs = self.format_messages(messages)
        gemini_tools = self._convert_tools(tools)

        response = self._client.models.generate_content(
            model=model,
            contents=native_msgs,
            config=types.GenerateContentConfig(
                system_instruction=system,
                tools=[gemini_tools],
                max_output_tokens=1024,
            ),
        )

        result = ChatResult()
        for part in response.candidates[0].content.parts:
            if part.text:
                result.text = (result.text or "") + part.text
            elif part.function_call:
                fc = part.function_call
                result.tool_calls.append(
                    ToolCall(
                        id=fc.name,
                        name=fc.name,
                        input=dict(fc.args) if fc.args else {},
                    )
                )
        return result

    def format_messages(self, messages):
        types = self._genai.types
        native = []
        for msg in messages:
            if msg["role"] == "tool_results":
                parts = []
                for r in msg["results"]:
                    parts.append(types.Part.from_function_response(
                        name=r["name"],
                        response=json.loads(r["result"]),
                    ))
                native.append(types.Content(role="user", parts=parts))
            elif msg["role"] == "assistant" and msg.get("tool_calls"):
                parts = []
                if msg.get("content"):
                    parts.append(types.Part.from_text(text=msg["content"]))
                for tc in msg["tool_calls"]:
                    parts.append(types.Part.from_function_call(
                        name=tc["name"],
                        args=tc["input"],
                    ))
                native.append(types.Content(role="model", parts=parts))
            elif msg["role"] == "assistant":
                native.append(types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=msg["content"])],
                ))
            else:
                native.append(types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=msg["content"])],
                ))
        return native


# ---------------------------------------------------------------------------
# Vertex AI Model Garden (Llama, Gemma, MedGemma)
# Uses the OpenAI-compatible endpoint with Google Cloud auth.
# ---------------------------------------------------------------------------

class ModelGardenProvider(LLMProvider):

    def __init__(self):
        import google.auth
        import google.auth.transport.requests
        from openai import OpenAI

        self._google_auth = google.auth
        self._google_requests = google.auth.transport.requests

        credentials, project = google.auth.default()
        credentials.refresh(google.auth.transport.requests.Request())

        self._credentials = credentials
        self._openai_cls = OpenAI

        location = settings.LLM_LOCATION or settings.GCP_REGION
        project_id = settings.GCP_PROJECT

        self._base_url = (
            f"https://{location}-aiplatform.googleapis.com/v1beta1/"
            f"projects/{project_id}/locations/{location}/endpoints/openapi"
        )
        self._client = self._build_client()

    def _build_client(self):
        self._credentials.refresh(self._google_requests.Request())
        return self._openai_cls(
            base_url=self._base_url,
            api_key=self._credentials.token,
        )

    def _ensure_fresh_token(self):
        if not self._credentials.valid:
            self._client = self._build_client()

    @staticmethod
    def _convert_tools(tools: list[dict]) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t["input_schema"],
                },
            }
            for t in tools
        ]

    def chat(self, model, system, messages, tools):
        self._ensure_fresh_token()

        native_msgs = [{"role": "system", "content": system}]
        native_msgs.extend(self.format_messages(messages))
        oai_tools = self._convert_tools(tools)

        response = self._client.chat.completions.create(
            model=model,
            messages=native_msgs,
            tools=oai_tools,
            max_tokens=1024,
        )

        choice = response.choices[0]
        result = ChatResult()
        if choice.message.content:
            result.text = choice.message.content
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                result.tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        input=json.loads(tc.function.arguments),
                    )
                )
        return result

    def format_messages(self, messages):
        native = []
        for msg in messages:
            if msg["role"] == "tool_results":
                for r in msg["results"]:
                    native.append({
                        "role": "tool",
                        "tool_call_id": r["tool_call_id"],
                        "content": r["result"],
                    })
            elif msg["role"] == "assistant" and msg.get("tool_calls"):
                oai_msg = {"role": "assistant", "content": msg.get("content") or None}
                oai_msg["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["input"]),
                        },
                    }
                    for tc in msg["tool_calls"]
                ]
                native.append(oai_msg)
            else:
                native.append({"role": msg["role"], "content": msg["content"]})
        return native


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_provider: LLMProvider | None = None


def get_provider() -> LLMProvider:
    global _provider
    if _provider is not None:
        return _provider

    provider_name = settings.LLM_PROVIDER
    if provider_name == "gemini":
        _provider = GeminiProvider()
    elif provider_name == "model_garden":
        _provider = ModelGardenProvider()
    else:
        _provider = AnthropicProvider()

    logger.info("LLM provider: %s, model: %s", provider_name, settings.LLM_MODEL)
    return _provider
