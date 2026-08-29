"""Telegram bot handlers — document processing and user interaction."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from telegram import Update
from telegram.ext import ContextTypes

if TYPE_CHECKING:
    from src.adapters.pdf.pymupdf_adapter import PDFImageExtractor
    from src.adapters.storage.sqlite_adapter import SQLiteCorrectionsRepository
    from src.adapters.vision.api_adapter import APIVisionAdapter
    from src.adapters.vision.ocr_adapter import OCRAdapter
    from src.domain.parser import parse_dimensions
    from src.domain.validator import validate_dimensions, validate_panel_fit

logger = logging.getLogger(__name__)


class Handlers:
    """Handler functions for Telegram bot interactions."""

    def __init__(
        self,
        ocr: OCRAdapter,
        api_vision: APIVisionAdapter,
        pdf_extractor: PDFImageExtractor,
        repository: SQLiteCorrectionsRepository,
        panel_width: float = 280,
        panel_height: float = 207,
    ) -> None:
        """Initialize handlers.

        Args:
            ocr: OCR adapter for text extraction.
            api_vision: API vision adapter for blueprint analysis.
            pdf_extractor: PDF image extraction adapter.
            repository: Corrections storage.
            panel_width: Default panel width in cm.
            panel_height: Default panel height in cm.
        """
        self.ocr = ocr
        self.api_vision = api_vision
        self.pdf_extractor = pdf_extractor
        self.repository = repository
        self.panel_width = panel_width
        self.panel_height = panel_height

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        if update.message:
            await update.message.reply_text(
                "🪚 PlankAI — Generador de despieces\n\n"
                "Envíame una imagen o PDF de un plano y generaré "
                "la lista de cortes con las dimensiones de cada pieza."
            )

    async def handle_photo(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle photo messages."""
        if not update.message or not update.message.photo:
            return

        await update.message.reply_text("📸 Procesando imagen...")

        try:
            photo = update.message.photo[-1]
            file = await photo.get_file()
            image_bytes = await file.download_as_bytearray()

            pieces = self.ocr.analyze_blueprint(bytes(image_bytes))
            if not pieces:
                text = self.ocr.extract_text(bytes(image_bytes))
                pieces = parse_dimensions(text)

            if not pieces:
                await update.message.reply_text(
                    "❌ No pude extraer dimensiones de la imagen. "
                    "Intentá con una imagen más clara."
                )
                return

            await self._present_results(update, list(pieces))

        except Exception as e:
            logger.error("Error processing photo", exc_info=True)
            await update.message.reply_text(f"❌ Error: {e}")

    async def handle_document(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle document messages (PDFs)."""
        if not update.message or not update.message.document:
            return

        doc = update.message.document
        if doc.mime_type != "application/pdf":
            await update.message.reply_text("Solo acepto archivos PDF.")
            return

        await update.message.reply_text("📄 Procesando PDF...")

        try:
            file = await doc.get_file()
            pdf_bytes = await file.download_as_bytearray()

            images = self.pdf_extractor.extract_images_from_bytes(bytes(pdf_bytes))
            all_pieces: list[Any] = []

            for img_bytes in images:
                pieces = self.ocr.analyze_blueprint(img_bytes)
                if not pieces:
                    text = self.ocr.extract_text(img_bytes)
                    pieces = parse_dimensions(text)
                all_pieces.extend(pieces)

            if not all_pieces:
                await update.message.reply_text(
                    "❌ No pude extraer dimensiones del PDF."
                )
                return

            await self._present_results(update, all_pieces)

        except Exception as e:
            logger.error("Error processing PDF", exc_info=True)
            await update.message.reply_text(f"❌ Error: {e}")

    async def handle_text(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle text messages (direct dimension input)."""
        if not update.message or not update.message.text:
            return

        text = update.message.text
        try:
            pieces = parse_dimensions(text)
            await self._present_results(update, pieces)
        except Exception:
            await update.message.reply_text(
                "❌ No pude parsear dimensiones. "
                "Usá el formato: 180cm × 90cm"
            )

    async def _present_results(
        self, update: Update, pieces: list[Any]
    ) -> None:
        """Present cutting list results to user."""
        from src.domain.calculator import calculate_cutting_list
        from src.domain.models import Blueprint, Panel

        panel = Panel(name="standard", width=self.panel_width, height=self.panel_height)
        blueprint = Blueprint(name="plano", pieces=tuple(pieces))
        cutting_list = calculate_cutting_list(blueprint, panel)

        errors = validate_dimensions(pieces)
        panel_errors = validate_panel_fit(pieces, panel)

        msg_lines = [
            f"🪚 **Despiece generado** — {cutting_list.total_pieces} piezas",
            f"📏 Panel estándar: {panel.width}×{panel.height}cm",
            f"📦 Paneles necesarios: {cutting_list.panels_needed}",
            f"📉 Desperdicio: {cutting_list.waste_percentage}%",
            "",
            "**Piezas:**",
        ]

        for p in pieces:
            msg_lines.append(f"  • {p.name}: {p.width}×{p.height}cm")

        if errors:
            msg_lines.append("")
            msg_lines.append("⚠️ **Advertencias:**")
            for err in errors:
                msg_lines.append(f"  • {err.message}")

        if panel_errors:
            msg_lines.append("")
            msg_lines.append("🚫 **Errores de ajuste:**")
            for err in panel_errors:
                msg_lines.append(f"  • {err.message}")

        if update.message:
            await update.message.reply_text("\n".join(msg_lines))
