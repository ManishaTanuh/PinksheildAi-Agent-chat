import logging

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

from ..core.config import settings

logger = logging.getLogger(__name__)

_client: SpeechClient | None = None

STT_REGION = "us-central1"


def _get_client() -> SpeechClient:
    global _client
    if _client is None:
        _client = SpeechClient(
            client_options={"api_endpoint": f"{STT_REGION}-speech.googleapis.com"}
        )
    return _client


def transcribe(audio_bytes: bytes) -> str:
    client = _get_client()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=[settings.STT_LANGUAGE_CODE],
        model=settings.STT_MODEL,
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{settings.GCP_PROJECT}/locations/{STT_REGION}/recognizers/_",
        config=config,
        content=audio_bytes,
    )

    response = client.recognize(request=request)

    transcript_parts = []
    for result in response.results:
        if result.alternatives:
            transcript_parts.append(result.alternatives[0].transcript)

    transcript = " ".join(transcript_parts).strip()
    logger.info("STT transcription: %s", transcript[:100])
    return transcript
