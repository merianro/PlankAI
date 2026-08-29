"""OCR adapter — extract text from images using Tesseract."""

from __future__ import annotations

import logging
from typing import Any

from src.domain.exceptions import BlueprintAnalysisError

logger = logging.getLogger(__name__)


class OCRAdapter:
    """Extract text from images using Tesseract OCR."""

    def __init__(self, lang: str = "spa+eng") -> None:
        """Initialize OCR adapter.

        Args:
            lang: Tesseract language codes (default: Spanish + English).
        """
        self.lang = lang

    def extract_text(self, image: bytes) -> str:
        """Extract raw text from an image.

        Args:
            image: Raw image bytes.

        Returns:
            Extracted text content.

        Raises:
            BlueprintAnalysisError: If extraction fails.
        """
        try:
            import io

            import pytesseract
            from PIL import Image

            img = Image.open(io.BytesIO(image))
            text: str = pytesseract.image_to_string(img, lang=self.lang)

            logger.info(
                "OCR text extracted",
                extra={
                    "text_length": len(text),
                    "lang": self.lang,
                },
            )

            return text.strip()
        except Exception as e:
            raise BlueprintAnalysisError(f"OCR extraction failed: {e}") from e

    def analyze_blueprint(self, image: bytes) -> list[Any]:
        """Analyze image and extract pieces (delegates to parser).

        This adapter only extracts raw text. The domain parser
        handles dimension extraction from text.

        Args:
            image: Raw image bytes.

        Returns:
            List of pieces (empty — parser handles extraction).
        """
        # OCR adapter extracts text only; parser does the rest
        return []
