"""Vision port — image analysis interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.domain.models import Piece


class ImageAnalyzer(Protocol):
    """Analyzes images to extract text or blueprint data."""

    def extract_text(self, image: bytes) -> str:
        """Extract raw text from an image.

        Args:
            image: Raw image bytes.

        Returns:
            Extracted text content.

        Raises:
            BlueprintAnalysisError: If extraction fails.
        """
        ...

    def analyze_blueprint(self, image: bytes) -> list[Piece]:
        """Analyze an image and extract piece dimensions.

        Args:
            image: Raw image bytes.

        Returns:
            List of extracted pieces.

        Raises:
            BlueprintAnalysisError: If analysis fails.
        """
        ...
