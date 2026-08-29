"""Unit tests for dimension validator."""

from src.domain.models import Panel, Piece, ValidationErrorType
from src.domain.validator import validate_dimensions, validate_panel_fit


class TestValidateDimensions:
    """Test validate_dimensions function."""

    def test_valid_pieces(self) -> None:
        """Valid pieces produce no errors."""
        pieces = [Piece(name="ok", width=100, height=50)]
        errors = validate_dimensions(pieces)
        assert errors == []

    def test_zero_dimension(self) -> None:
        """Zero dimension is caught."""
        pieces = [Piece(name="bad", width=0, height=50)]
        errors = validate_dimensions(pieces)
        assert len(errors) == 1
        assert errors[0].type == ValidationErrorType.DIMENSION_ZERO

    def test_negative_dimension(self) -> None:
        """Negative dimension is caught (triggers zero check since <= 0)."""
        pieces = [Piece(name="bad", width=-10, height=50)]
        errors = validate_dimensions(pieces)
        assert len(errors) >= 1
        # width=-10 triggers DIMENSION_ZERO (width <= 0 check)
        assert errors[0].type == ValidationErrorType.DIMENSION_ZERO

    def test_too_large_dimension(self) -> None:
        """Dimension exceeding 10000cm is caught."""
        pieces = [Piece(name="huge", width=15000, height=50)]
        errors = validate_dimensions(pieces)
        types = [e.type for e in errors]
        assert ValidationErrorType.DIMENSION_TOO_LARGE in types

    def test_illogical_aspect_ratio(self) -> None:
        """Aspect ratio > 100:1 is caught."""
        pieces = [Piece(name="needle", width=10000, height=1)]
        errors = validate_dimensions(pieces)
        types = [e.type for e in errors]
        assert ValidationErrorType.illogical_aspect_ratio in types

    def test_multiple_errors(self) -> None:
        """Multiple pieces with errors produce multiple errors."""
        pieces = [
            Piece(name="a", width=0, height=50),
            Piece(name="b", width=20000, height=50),
        ]
        errors = validate_dimensions(pieces)
        assert len(errors) >= 2

    def test_validates_all_fields(self) -> None:
        """Validates piece_name is set on errors."""
        pieces = [Piece(name="test_piece", width=0, height=50)]
        errors = validate_dimensions(pieces)
        assert errors[0].piece_name == "test_piece"


class TestValidatePanelFit:
    """Test validate_panel_fit function."""

    def test_pieces_fit(self) -> None:
        """Pieces that fit produce no errors."""
        pieces = [Piece(name="small", width=100, height=50)]
        panel = Panel(name="standard", width=280, height=207)
        errors = validate_panel_fit(pieces, panel)
        assert errors == []

    def test_piece_exceeds_panel(self) -> None:
        """Piece larger than panel in both orientations is caught."""
        pieces = [Piece(name="big", width=400, height=300)]
        panel = Panel(name="standard", width=280, height=207)
        errors = validate_panel_fit(pieces, panel)
        assert len(errors) == 1
        assert errors[0].type == ValidationErrorType.PIECE_EXCEEDS_PANEL

    def test_piece_fits_rotated(self) -> None:
        """Piece that fits when rotated produces no error."""
        pieces = [Piece(name="rotatable", width=200, height=100)]
        panel = Panel(name="standard", width=280, height=207)
        errors = validate_panel_fit(pieces, panel)
        assert errors == []

    def test_piece_too_large_even_rotated(self) -> None:
        """Piece too large in both orientations."""
        pieces = [Piece(name="huge", width=500, height=400)]
        panel = Panel(name="standard", width=280, height=207)
        errors = validate_panel_fit(pieces, panel)
        assert len(errors) == 1
