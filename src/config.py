"""Configuration management via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AI
    openai_api_key: str = ""
    vision_model: str = "gpt-5.6-luna"

    # OCR
    ocr_engine: str = "tesseract"

    # Storage
    database_url: str = "sqlite:///data/corrections.db"

    # Telegram
    telegram_token: str = ""

    model_config = {"env_prefix": "PLANKAI_", "env_file": ".env"}
