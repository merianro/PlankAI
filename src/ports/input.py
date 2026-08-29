"""Input port — blueprint analysis interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.domain.models import Blueprint


class BlueprintAnalyzer(Protocol):
    """Analyzes images/PDFs to extract blueprint data."""

    def analyze(self, file_path: str) -> Blueprint:
        """Analyze a file and return a parsed blueprint.

        Args:
            file_path: Path to the image or PDF file.

        Returns:
            Parsed blueprint with pieces.

        Raises:
            BlueprintAnalysisError: If analysis fails.
        """
        ...
