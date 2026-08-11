import os
from typing import Optional
from huggingface_hub import login
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    DATABASE_URL: str
    REDIS_URL: str
    QDRANT_URL: str

    SECRET_KEY: str
    ALGORITHM: str

    OPENROUTER_API_KEY: str

    # Hugging Face Token (اختياري لتجنب أخطاء التحميل)
    HF_TOKEN: Optional[str] = None

    FAST_MODEL: str
    FAST_FALLBACK_MODEL: str

    HEAVY_MODEL: str
    HEAVY_FALLBACK_MODEL: str

    # LangSmith
    LANGSMITH_API_KEY: str
    LANGSMITH_PROJECT: str = "Saudi Tender Agent"
    LANGSMITH_TRACING: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# ============================================================
# Environment Variables & Initializations
# ============================================================

# LangSmith Setup
os.environ["LANGSMITH_TRACING"] = str(settings.LANGSMITH_TRACING).lower()
os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT

# Hugging Face Login Setup
# if settings.HF_TOKEN:
#     os.environ["HF_TOKEN"] = settings.HF_TOKEN