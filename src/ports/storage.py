"""Storage port — corrections and history persistence interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.domain.models import Piece


class CorrectionsRepository(Protocol):
    """Stores and retrieves blueprint corrections."""

    def save_correction(
        self,
        blueprint_name: str,
        original_pieces: list[Piece],
        corrected_pieces: list[Piece],
    ) -> None:
        """Save a user correction for future prompt improvement.

        Args:
            blueprint_name: Name of the blueprint.
            original_pieces: Pieces originally extracted.
            corrected_pieces: Pieces after user correction.
        """
        ...

    def get_corrections(self, blueprint_name: str) -> list[dict[str, object]]:
        """Retrieve past corrections for a blueprint.

        Args:
            blueprint_name: Name of the blueprint.

        Returns:
            List of correction records.
        """
        ...
