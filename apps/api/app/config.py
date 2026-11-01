from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    anthropic_api_key: str
    openai_api_key: str
    anthropic_model: str = "claude-haiku-4-5-20251001"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5


settings = Settings()
