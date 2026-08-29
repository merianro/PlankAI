"""Calculator — panel and cutting list computation."""

from __future__ import annotations

import math

from src.domain.models import Blueprint, CuttingList, Panel, Piece


def calculate_panels(pieces: list[Piece], panel: Panel) -> int:
    """Calculate how many panels are needed for the given pieces.

    Uses a simple greedy area-based estimation. This is NOT a nesting
    optimization — that's Phase 2+ territory.

    Args:
        pieces: List of pieces to cut.
        panel: Standard panel dimensions.

    Returns:
        Number of panels required.
    """
    if not pieces:
        return 0

    total_area = sum(p.width * p.height * p.quantity for p in pieces)
    panel_area = panel.width * panel.height

    if panel_area <= 0:
        return 0

    # Add 15% waste factor for kerf and offcuts
    effective_area = panel_area * 0.85
    return math.ceil(total_area / effective_area)


def calculate_cutting_list(blueprint: Blueprint, panel: Panel) -> CuttingList:
    """Compute a cutting list from a blueprint.

    Args:
        blueprint: Parsed blueprint with pieces.
        panel: Standard panel to cut from.

    Returns:
        Structured cutting list with panel requirements.
    """
    panels_needed = calculate_panels(list(blueprint.pieces), panel)
    total_piece_area = blueprint.total_area
    total_panel_area = panels_needed * panel.area

    waste_percentage = 0.0
    if total_panel_area > 0:
        waste_percentage = round((1 - total_piece_area / total_panel_area) * 100, 1)

    return CuttingList(
        blueprint_name=blueprint.name,
        pieces=blueprint.pieces,
        panels_needed=panels_needed,
        panel=panel,
        waste_percentage=waste_percentage,
    )
