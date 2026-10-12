import logging

from google.cloud import texttospeech

from ..core.config import settings

logger = logging.getLogger(__name__)

_client: texttospeech.TextToSpeechClient | None = None


def _get_client() -> texttospeech.TextToSpeechClient:
    global _client
    if _client is None:
        _client = texttospeech.TextToSpeechClient()
    return _client


def synthesize(text: str) -> bytes:
    client = _get_client()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=settings.TTS_LANGUAGE_CODE,
        name=settings.TTS_VOICE_NAME,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=settings.TTS_SPEAKING_RATE,
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config,
    )

    logger.info("TTS synthesized %d bytes for %d chars", len(response.audio_content), len(text))
    return response.audio_content
