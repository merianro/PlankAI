"""Output port — cutting list presentation interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.domain.models import CuttingList


class CuttingListPresenter(Protocol):
    """Presents a cutting list to the user."""

    def present(self, cutting_list: CuttingList) -> str:
        """Format a cutting list for display.

        Args:
            cutting_list: The computed cutting list.

        Returns:
            Formatted string representation.
        """
        ...
