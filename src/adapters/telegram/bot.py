"""Telegram bot adapter — main bot class."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

if TYPE_CHECKING:
    from src.adapters.telegram.handlers import Handlers

logger = logging.getLogger(__name__)


class PlankAIBot:
    """Telegram bot for PlankAI."""

    def __init__(self, token: str, handlers: Handlers) -> None:
        """Initialize the bot.

        Args:
            token: Telegram bot token.
            handlers: Handler functions for bot interactions.
        """
        self.token = token
        self.handlers = handlers
        self.app: Application[Any, Any, Any, Any, Any, Any] | None = None

    def build(self) -> Application[Any, Any, Any, Any, Any, Any]:
        """Build and configure the Telegram application.

        Returns:
            Configured Application instance.
        """
        self.app = Application.builder().token(self.token).build()

        # Register handlers
        self.app.add_handler(CommandHandler("start", self.handlers.start))
        self.app.add_handler(
            MessageHandler(filters.PHOTO, self.handlers.handle_photo)
        )
        self.app.add_handler(
            MessageHandler(filters.Document.ALL, self.handlers.handle_document)
        )
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.handle_text)
        )

        logger.info("Telegram bot built")
        return self.app

    def run(self) -> None:
        """Start the bot (blocking)."""
        if self.app is None:
            self.build()

        assert self.app is not None
        logger.info("Starting PlankAI Telegram bot")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
