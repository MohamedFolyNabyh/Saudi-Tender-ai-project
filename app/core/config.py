import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # ========================================================
    # Database Configuration
    # ========================================================

    DATABASE_URL: str
    REDIS_URL: str
    QDRANT_URL: str

    # ========================================================
    # Security Configuration
    # ========================================================

    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # ========================================================
    # Existing Application LLM - OpenRouter
    # ========================================================

    OPENROUTER_API_KEY: str

    FAST_MODEL: str
    FAST_FALLBACK_MODEL: str

    HEAVY_MODEL: str
    HEAVY_FALLBACK_MODEL: str

    # ========================================================
    # RAGAS ONLY - Google Gemini
    # ========================================================

    GEMINI_API_KEY: str

    GEMINI_MODEL: str = "gemini-2.5-flash-lite"

    # ========================================================
    # Google API compatibility
    # ========================================================
    # Some LangChain / RAGAS integrations expect this name.

    GOOGLE_API_KEY: Optional[str] = None

    # ========================================================
    # Hugging Face
    # ========================================================

    HF_TOKEN: Optional[str] = None

    # ========================================================
    # LangSmith
    # ========================================================

    LANGSMITH_API_KEY: str

    LANGSMITH_PROJECT: str = "Saudi Tender Agent"

    LANGSMITH_TRACING: bool = True

    # ========================================================
    # Pydantic Settings
    # ========================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# ============================================================
# Singleton
# ============================================================

settings = Settings()


# ============================================================
# Environment Variables
# ============================================================

os.environ["LANGSMITH_TRACING"] = (
    str(settings.LANGSMITH_TRACING).lower()
)

os.environ["LANGSMITH_API_KEY"] = (
    settings.LANGSMITH_API_KEY
)

os.environ["LANGSMITH_PROJECT"] = (
    settings.LANGSMITH_PROJECT
)


# ============================================================
# Gemini
# ============================================================

os.environ["GEMINI_API_KEY"] = (
    settings.GEMINI_API_KEY
)

# Compatibility for Google/LangChain packages
os.environ["GOOGLE_API_KEY"] = (
    settings.GEMINI_API_KEY
)


# ============================================================
# Hugging Face
# ============================================================

# if settings.HF_TOKEN:

#     os.environ["HF_TOKEN"] = settings.HF_TOKEN