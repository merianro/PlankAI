"""Parser — extract piece dimensions from text using regex."""

from __future__ import annotations

import re

from src.domain.exceptions import DimensionParsingError
from src.domain.models import Piece

# Separator: x, X, ×, or *
_SEP = r"[xX×*]"
_UNIT = r"(?:cm|mm)?"

# Pattern: optional name prefix, then WxH, optional thickness
# e.g. "Tablero 120 x 80", "180cm × 90cm", "70×7×3", "50.5cm*30cm"
_DIMENSION_RE = re.compile(
    r"(?:(?P<name>[A-Za-záéíóúñÁÉÍÓÚÑ_][A-Za-záéíóúñÁÉÍÓÚÑ_0-9]*)\s+)?"  # optional name
    r"(?P<w>\d+(?:\.\d+)?)" + _UNIT +  # width + optional unit
    r"\s*" + _SEP + r"\s*"  # separator
    + r"(?P<h>\d+(?:\.\d+)?)" + _UNIT +  # height + optional unit
    r"(?:\s*" + _SEP + r"\s*(?P<t>\d+(?:\.\d+)?)" + _UNIT + r")?"  # optional thickness
)


def parse_dimensions(text: str) -> list[Piece]:
    """Parse piece dimensions from text.

    Supports formats like:
    - "180cm × 90cm"
    - "70×7×3"
    - "Tablero 120 x 80"
    - "50.5cm*30cm"

    Args:
        text: Text containing dimension specifications.

    Returns:
        List of parsed pieces.

    Raises:
        DimensionParsingError: If no valid dimensions found.
    """
    pieces: list[Piece] = []
    lines = text.strip().splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        for match in _DIMENSION_RE.finditer(line):
            piece = _match_to_piece(match)
            if piece:
                pieces.append(piece)

    if not pieces:
        raise DimensionParsingError(
            f"No valid dimensions found in text: {text[:100]}..."
        )

    return pieces


def _match_to_piece(match: re.Match[str]) -> Piece | None:
    """Convert a regex match to a Piece."""
    try:
        w = float(match.group("w"))
        h = float(match.group("h"))
    except (ValueError, IndexError):
        return None

    if w <= 0 or h <= 0:
        return None

    name = match.group("name") or "pieza"
    thickness_str = match.group("t")
    thickness = float(thickness_str) if thickness_str else None

    return Piece(name=name.strip(), width=w, height=h, thickness=thickness)
