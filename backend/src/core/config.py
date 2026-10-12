import os
import urllib.parse
from dotenv import load_dotenv

from .secrets import get_secret

load_dotenv()


class Settings:
    PROJECT_NAME: str = "PinkShieldAI API"
    PROJECT_VERSION: str = "0.1.0"

    MYSQL_USER: str = os.getenv("MYSQL_USER", "")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "pinkshieldAI_insurance")
    MYSQL_QUERY: str = os.getenv("MYSQL_QUERY", "charset=utf8mb4")

    CLOUD_SQL_CONNECTION_NAME: str = os.getenv("CLOUD_SQL_CONNECTION_NAME", "")
    USE_CLOUD_SQL_CONNECTOR: bool = os.getenv("USE_CLOUD_SQL_CONNECTOR", "false").lower() == "true"

    GCP_PROJECT: str = os.getenv("GCP_PROJECT", "bcd-prototypes")
    GCP_REGION: str = os.getenv("GCP_REGION", "us-east5")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6-20250929")
    USE_VERTEX_AI: bool = os.getenv("USE_VERTEX_AI", "true").lower() == "true"

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "")
    LLM_LOCATION: str = os.getenv("LLM_LOCATION", "")

    VOICE_MODE: str = os.getenv("VOICE_MODE", "classic")
    GEMINI_LIVE_MODEL: str = os.getenv("GEMINI_LIVE_MODEL", "gemini-2.5-flash")
    GEMINI_VOICE_NAME: str = os.getenv("GEMINI_VOICE_NAME", "Aoede")

    @property
    def LLM_MODEL(self) -> str:
        explicit = os.getenv("LLM_MODEL", "")
        if explicit:
            return explicit
        return self.CLAUDE_MODEL

    TTS_LANGUAGE_CODE: str = os.getenv("TTS_LANGUAGE_CODE", "en-IN")
    TTS_VOICE_NAME: str = os.getenv("TTS_VOICE_NAME", "en-IN-Neural2-A")
    TTS_SPEAKING_RATE: float = float(os.getenv("TTS_SPEAKING_RATE", "1.0"))
    STT_LANGUAGE_CODE: str = os.getenv("STT_LANGUAGE_CODE", "en-IN")
    STT_MODEL: str = os.getenv("STT_MODEL", "chirp_2")

    def __init__(self):
        self.SECRET_KEY = get_secret("pinkshieldai-secret-key", "SECRET_KEY")
        self.ANTHROPIC_API_KEY = get_secret("pinkshieldai-anthropic-api-key", "ANTHROPIC_API_KEY")
        self.MYSQL_PASSWORD = get_secret("pinkshieldai-mysql-password", "MYSQL_PASSWORD")
        self.MYSQL_SSL_CA = get_secret("pinkshieldai-mysql-ssl-ca", "MYSQL_SSL_CA")
        self.MYSQL_SSL_CERT = get_secret("pinkshieldai-mysql-ssl-cert", "MYSQL_SSL_CERT")
        self.MYSQL_SSL_KEY = get_secret("pinkshieldai-mysql-ssl-key", "MYSQL_SSL_KEY")

    @property
    def DATABASE_URL(self) -> str:
        password = urllib.parse.quote_plus(self.MYSQL_PASSWORD) if self.MYSQL_PASSWORD else ""
        url = f"mysql+pymysql://{self.MYSQL_USER}:{password}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        if self.MYSQL_QUERY:
            url += f"?{self.MYSQL_QUERY}"
        return url


settings = Settings()
