"""Integration tests for Telegram bot handlers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

pytest.importorskip("telegram")

from src.adapters.telegram.handlers import Handlers


@pytest.fixture
def handlers() -> Handlers:
    """Create handlers with mock adapters."""
    return Handlers(
        ocr=MagicMock(),
        api_vision=MagicMock(),
        pdf_extractor=MagicMock(),
        repository=MagicMock(),
    )


def _make_update(text: str | None = None) -> MagicMock:
    """Create a mock Update object."""
    update = MagicMock()
    update.message = MagicMock()
    update.message.text = text
    update.message.reply_text = AsyncMock()
    return update


@pytest.mark.asyncio
async def test_start_command(handlers: Handlers) -> None:
    """Test /start command sends welcome message."""
    update = _make_update()
    context = MagicMock()

    await handlers.start(update, context)

    update.message.reply_text.assert_called_once()
    sent = update.message.reply_text.call_args[0][0]
    assert "PlankAI" in sent


@pytest.mark.asyncio
async def test_handle_text_parses_dimensions(handlers: Handlers) -> None:
    """Test text message triggers dimension parsing."""
    update = _make_update("100×50")
    context = MagicMock()

    await handlers.handle_text(update, context)

    update.message.reply_text.assert_called()
    sent = update.message.reply_text.call_args[0][0]
    assert "Piezas" in sent or "100" in sent


@pytest.mark.asyncio
async def test_handle_text_invalid(handlers: Handlers) -> None:
    """Test invalid text sends error message."""
    update = _make_update("hello world")
    context = MagicMock()

    await handlers.handle_text(update, context)

    update.message.reply_text.assert_called()
    sent = update.message.reply_text.call_args[0][0]
    assert "❌" in sent


@pytest.mark.asyncio
async def test_handle_document_non_pdf(handlers: Handlers) -> None:
    """Test non-PDF document sends rejection."""
    update = MagicMock()
    update.message = MagicMock()
    update.message.document = MagicMock()
    update.message.document.mime_type = "image/png"
    update.message.reply_text = AsyncMock()
    context = MagicMock()

    await handlers.handle_document(update, context)

    update.message.reply_text.assert_called()
    sent = update.message.reply_text.call_args[0][0]
    assert "PDF" in sent
