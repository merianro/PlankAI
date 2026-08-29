"""Domain models — core data structures for PlankAI."""

from dataclasses import dataclass
from enum import Enum


class ValidationErrorType(Enum):
    """Types of validation errors."""

    DIMENSION_TOO_LARGE = "dimension_too_large"
    DIMENSION_ZERO = "dimension_zero"
    NEGATIVE_DIMENSION = "negative_dimension"
    illogical_aspect_ratio = "illogical_aspect_ratio"
    PIECE_EXCEEDS_PANEL = "piece_exceeds_panel"


@dataclass(frozen=True)
class Piece:
    """A single piece to be cut from a panel."""

    name: str
    width: float
    height: float
    quantity: int = 1
    thickness: float | None = None

    @property
    def area(self) -> float:
        """Total area of this piece (width * height * quantity)."""
        return self.width * self.height * self.quantity


@dataclass(frozen=True)
class Panel:
    """Standard panel dimensions (raw material)."""

    name: str
    width: float
    height: float
    thickness: float | None = None

    @property
    def area(self) -> float:
        """Total area of the panel."""
        return self.width * self.height


@dataclass(frozen=True)
class Blueprint:
    """A parsed blueprint containing pieces to cut."""

    name: str
    pieces: tuple[Piece, ...]
    source_file: str | None = None

    @property
    def total_pieces(self) -> int:
        """Total number of individual pieces (sum of quantities)."""
        return sum(p.quantity for p in self.pieces)

    @property
    def total_area(self) -> float:
        """Total area required by all pieces."""
        return sum(p.area for p in self.pieces)


@dataclass(frozen=True)
class CuttingList:
    """Output — structured cutting list with panel requirements."""

    blueprint_name: str
    pieces: tuple[Piece, ...]
    panels_needed: int
    panel: Panel
    waste_percentage: float

    @property
    def total_pieces(self) -> int:
        """Total number of individual pieces."""
        return sum(p.quantity for p in self.pieces)


@dataclass(frozen=True)
class ValidationError:
    """A validation error found during blueprint analysis."""

    type: ValidationErrorType
    message: str
    piece_name: str | None = None
