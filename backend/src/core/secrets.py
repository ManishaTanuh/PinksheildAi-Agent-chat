import logging
import os

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        from google.cloud import secretmanager

        _client = secretmanager.SecretManagerServiceClient()
    return _client


def get_secret(secret_id: str, fallback_env: str = "") -> str:
    """Fetch a secret from Google Cloud Secret Manager.

    Falls back to the env var named by fallback_env if set, or if
    Secret Manager is unreachable (e.g. local dev without SM access).
    """
    if fallback_env:
        env_val = os.getenv(fallback_env)
        if env_val:
            return env_val

    project = os.getenv("GCP_PROJECT", "bcd-prototypes")
    try:
        client = _get_client()
        name = f"projects/{project}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("utf-8")
    except Exception as exc:
        logger.debug("Secret Manager lookup failed for %s: %s", secret_id, exc)
        return ""
