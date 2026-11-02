from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_API_DIR = Path(__file__).resolve().parent.parent  # apps/api
_PROJECT_ROOT = _API_DIR.parent.parent              # docuchat/

# Preference order: docuchat/.env.local (Neon pulled), docuchat/.env,
# apps/api/.env (legacy local). First existing wins.
_ENV_CANDIDATES = [
    _PROJECT_ROOT / ".env.local",
    _PROJECT_ROOT / ".env",
    _API_DIR / ".env",
]
_ENV_FILE = next((p for p in _ENV_CANDIDATES if p.exists()), _API_DIR / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), extra="ignore")

    database_url: str

    # Provider selection — defaults keep everything local (zero API cost).
    llm_provider: str = "ollama"  # "ollama" | "anthropic"
    embedding_provider: str = "ollama"  # "ollama" | "openai"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "qwen3:8b"
    ollama_embedding_model: str = "bge-m3"

    # Anthropic (used when llm_provider == "anthropic")
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"

    # OpenAI (used when embedding_provider == "openai")
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"

    # Must match the active embedding model's output dimension.
    embedding_dim: int = 1024

    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5

    # --- Neon Object Storage ---
    # Falls through standard AWS env chain; we read these explicitly so boto3
    # can be initialized with the Neon endpoint.
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = ""
    aws_endpoint_url_s3: str = ""
    uploads_bucket: str = "uploads"

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_db_url(cls, v: str) -> str:
        """Neon ships `postgresql://…`; SQLAlchemy + psycopg3 needs the
        `postgresql+psycopg://` scheme."""
        if not isinstance(v, str):
            return v
        if v.startswith("postgres://"):
            v = "postgresql://" + v[len("postgres://"):]
        if v.startswith("postgresql://") and "+" not in v.split("://", 1)[0]:
            v = "postgresql+psycopg://" + v[len("postgresql://"):]
        return v


settings = Settings()
