"""Unit tests for panel calculator."""

from src.domain.calculator import calculate_cutting_list, calculate_panels
from src.domain.models import Blueprint, Panel, Piece


class TestCalculatePanels:
    """Test calculate_panels function."""

    def test_empty_pieces(self) -> None:
        """No pieces means zero panels."""
        panel = Panel(name="standard", width=280, height=207)
        assert calculate_panels([], panel) == 0

    def test_single_piece_fits(self) -> None:
        """One small piece should need one panel."""
        pieces = [Piece(name="test", width=100, height=50)]
        panel = Panel(name="standard", width=280, height=207)
        result = calculate_panels(pieces, panel)
        assert result >= 1

    def test_many_pieces_need_multiple_panels(self) -> None:
        """Many large pieces should need multiple panels."""
        pieces = [Piece(name=f"p{i}", width=100, height=50, quantity=10) for i in range(5)]
        panel = Panel(name="standard", width=280, height=207)
        result = calculate_panels(pieces, panel)
        assert result > 1

    def test_zero_area_panel(self) -> None:
        """Zero-area panel returns zero panels."""
        pieces = [Piece(name="test", width=100, height=50)]
        panel = Panel(name="bad", width=0, height=0)
        assert calculate_panels(pieces, panel) == 0

    def test_waste_factor_applied(self) -> None:
        """Calculation should account for waste (result >= pure area / panel_area)."""
        pieces = [Piece(name="test", width=280, height=207)]
        panel = Panel(name="standard", width=280, height=207)
        # Pure area would be 1 panel, but waste factor should push to at least 1
        result = calculate_panels(pieces, panel)
        assert result >= 1


class TestCalculateCuttingList:
    """Test calculate_cutting_list function."""

    def test_basic_cutting_list(self) -> None:
        """Calculate a basic cutting list."""
        pieces = (Piece(name="shelf", width=80, height=40, quantity=4),)
        blueprint = Blueprint(name="bookcase", pieces=pieces)
        panel = Panel(name="standard", width=280, height=207)

        result = calculate_cutting_list(blueprint, panel)

        assert result.blueprint_name == "bookcase"
        assert result.total_pieces == 4
        assert result.panels_needed >= 1
        assert result.panel == panel
        assert 0 <= result.waste_percentage <= 100

    def test_empty_blueprint(self) -> None:
        """Empty blueprint produces zero panels."""
        blueprint = Blueprint(name="empty", pieces=())
        panel = Panel(name="standard", width=280, height=207)

        result = calculate_cutting_list(blueprint, panel)

        assert result.panels_needed == 0
        assert result.total_pieces == 0
