from pydantic_settings import BaseSettings, SettingsConfigDict

UNSET_OPENAI_API_KEY_PLACEHOLDER = "openai-api-key-not-set"


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-6-luna"
    openai_embedding_model: str = "text-embedding-3-small"
    chroma_path: str = "./data/chroma"
    pages_dir: str = "./pages"
    chunk_size: int = 900
    chunk_overlap: int = 150
    retrieve_k: int = 5
    max_distance: float = 0.85
    hybrid_search_enabled: bool = True
    hybrid_rrf_k: int = 60
    history_window: int = 12
    cors_origins: str = "http://localhost:5174,http://127.0.0.1:5174"
    redis_url: str = "redis://127.0.0.1:6379/0"
    redis_required: bool = False
    rate_limit_enabled: bool = True
    rate_limit_fail_closed: bool = True
    rate_limit_window_seconds: int = 60
    rate_limit_ask_per_minute: int = 10
    rate_limit_ask_per_day: int = 40
    rate_limit_ask_global_per_day: int = 200
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


def load_settings() -> Settings:
    return Settings()
