from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5435/mindbridge"

    # ── JWT Auth ──────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str  # No default — must be set in .env / environment
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── MindBridge Fine-Tuned Llama 3 Model ──────────────────────────────────
    MINDBRIDGE_BASE_MODEL: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    MINDBRIDGE_ADAPTER_ID: str = "aayush0K/Llama-3-MindBridge"
    INFERENCE_URL: str = "http://localhost:8001/generate"
    REMOTE_INFERENCE_API_KEY: str = ""  # Optional auth key for remote GPU server

    # ── Redis (conversation memory) ───────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6380"
    MEMORY_TTL_SECONDS: int = 86_400          # 24 h — auto-expire idle sessions

    # ── Semantic Response Cache ───────────────────────────────────────────────
    SEMANTIC_CACHE_ENABLED: bool = True
    SEMANTIC_CACHE_THRESHOLD: float = 0.90
    SEMANTIC_CACHE_TTL_DAYS: int = 30

    # ── App ───────────────────────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000"
    CORPUS_PATH: str = "./corpus/mental_health_corpus.json"
    APP_ENV: str = "development"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
