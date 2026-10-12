from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    channel: str = "rest"
    language: str = "en"
    voice: bool = False
    mode: str = "chat"  # "chat" (LLM) or "structured" (direct engine)


class ChatRequest(BaseModel):
    message: str


class AnswerRequest(BaseModel):
    factor_id: str
    value: str


class QuestionResponse(BaseModel):
    status: str
    factor_id: str | None = None
    question: str | None = None
    data_type: str | None = None
    ui_type: str | None = None
    options: list[str] | None = None
    display_labels: dict[str, str] | None = None
    min_val: int | None = None
    max_val: int | None = None
    clarification: str | None = None
    message: str | None = None


class AnswerResponse(BaseModel):
    status: str
    factor_id: str | None = None
    value: str | None = None
    error: str | None = None
    next_question: QuestionResponse | None = None
    progress: dict | None = None
    urgent_referral: dict | None = None


class TTSRequest(BaseModel):
    text: str


class TTSResponse(BaseModel):
    audio_base64: str


class VoiceResponse(BaseModel):
    session_id: str
    transcription: str
    response: str
    audio_base64: str
    session_status: str
    tool_calls_made: int | None = None


class SessionResponse(BaseModel):
    session_id: str
    response: str
    session_status: str
    first_question: dict | None = None
    tool_calls_made: int | None = None
    audio_base64: str | None = None
    voice_mode: str | None = None


class SessionDetail(BaseModel):
    session_id: str
    channel: str
    language: str
    status: str
    current_tier: int
    risk_level: str | None
    risk_score: float | None
    urgent_referral: bool
    answers: list[dict]
    created_at: str
    completed_at: str | None


class RiskResultResponse(BaseModel):
    session_id: str
    risk_level: str
    risk_probability: float
    key_risk_factors: list[dict]
    protective_factors: list[dict]
    recommendations: list[str]
    model_version: str
