from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str

    # Default: everything runs locally via Ollama (zero API cost).
    # Switch providers via LLM_PROVIDER / EMBEDDING_PROVIDER.
    llm_provider: str = "ollama"  # "ollama" | "anthropic"
    embedding_provider: str = "ollama"  # "ollama" | "openai"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "qwen2.5:7b"
    ollama_embedding_model: str = "nomic-embed-text"

    # Anthropic (used when llm_provider == "anthropic")
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"

    # OpenAI (used when embedding_provider == "openai")
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"

    # Must match the active embedding model's output dimension.
    # nomic-embed-text        -> 768
    # text-embedding-3-small  -> 1536
    embedding_dim: int = 768

    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5


settings = Settings()
