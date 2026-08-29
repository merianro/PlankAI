"""Composition root — wire all adapters and start the bot."""

from __future__ import annotations

import logging
import sys

from src.adapters.pdf.pymupdf_adapter import PDFImageExtractor
from src.adapters.storage.sqlite_adapter import SQLiteCorrectionsRepository
from src.adapters.telegram.bot import PlankAIBot
from src.adapters.telegram.handlers import Handlers
from src.adapters.vision.api_adapter import APIVisionAdapter
from src.adapters.vision.ocr_adapter import OCRAdapter
from src.config import Settings


def setup_logging() -> None:
    """Configure structured logging."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def create_bot() -> PlankAIBot:
    """Create and configure the PlankAI bot.

    Returns:
        Configured bot instance.
    """
    settings = Settings()

    # Adapters
    ocr = OCRAdapter()
    api_vision = APIVisionAdapter(
        api_key=settings.openai_api_key,
        model=settings.vision_model,
    )
    pdf_extractor = PDFImageExtractor()
    repository = SQLiteCorrectionsRepository()

    # Handlers
    handlers = Handlers(
        ocr=ocr,
        api_vision=api_vision,
        pdf_extractor=pdf_extractor,
        repository=repository,
    )

    # Bot
    return PlankAIBot(token=settings.telegram_token, handlers=handlers)


def main() -> None:
    """Entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)

    settings = Settings()
    if not settings.telegram_token:
        logger.error("TELEGRAM_TOKEN not set")
        sys.exit(1)

    bot = create_bot()
    logger.info("Starting PlankAI bot")
    bot.run()


if __name__ == "__main__":
    main()
