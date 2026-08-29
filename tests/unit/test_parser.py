"""Unit tests for dimension parser."""

import pytest

from src.domain.exceptions import DimensionParsingError
from src.domain.parser import parse_dimensions


class TestParseDimensions:
    """Test parse_dimensions function."""

    def test_simple_format(self) -> None:
        """Parse '180cm × 90cm' format."""
        result = parse_dimensions("180cm × 90cm")
        assert len(result) == 1
        assert result[0].width == 180.0
        assert result[0].height == 90.0
        assert result[0].quantity == 1

    def test_without_unit(self) -> None:
        """Parse dimensions without unit suffix."""
        result = parse_dimensions("70×7")
        assert len(result) == 1
        assert result[0].width == 70.0
        assert result[0].height == 7.0

    def test_with_name_prefix(self) -> None:
        """Parse dimensions with name prefix."""
        result = parse_dimensions("Tablero 120 x 80")
        assert len(result) == 1
        assert result[0].name == "Tablero"
        assert result[0].width == 120.0
        assert result[0].height == 80.0

    def test_three_dimensions(self) -> None:
        """Parse three-dimensional specs (w×h×t)."""
        result = parse_dimensions("70×7×3")
        assert len(result) == 1
        assert result[0].width == 70.0
        assert result[0].height == 7.0
        assert result[0].thickness == 3.0

    def test_float_dimensions(self) -> None:
        """Parse decimal dimensions."""
        result = parse_dimensions("50.5cm*30cm")
        assert len(result) == 1
        assert result[0].width == 50.5
        assert result[0].height == 30.0

    def test_multiple_lines(self) -> None:
        """Parse multiple pieces from multi-line text."""
        text = """180 × 90
120 × 60
80 × 40"""
        result = parse_dimensions(text)
        assert len(result) == 3
        assert result[0].width == 180.0
        assert result[1].width == 120.0
        assert result[2].width == 80.0

    def test_mixed_content(self) -> None:
        """Parse dimensions from text with surrounding content."""
        text = "Piezas: 100×50, 200×100"
        result = parse_dimensions(text)
        assert len(result) == 2

    def test_empty_text_raises(self) -> None:
        """Empty text raises DimensionParsingError."""
        with pytest.raises(DimensionParsingError):
            parse_dimensions("")

    def test_no_dimensions_raises(self) -> None:
        """Text without dimensions raises DimensionParsingError."""
        with pytest.raises(DimensionParsingError):
            parse_dimensions("Hello world, no dimensions here")

    def test_x_separator(self) -> None:
        """Parse with lowercase x separator."""
        result = parse_dimensions("100x50")
        assert len(result) == 1
        assert result[0].width == 100.0
        assert result[0].height == 50.0

    def test_uppercase_x_separator(self) -> None:
        """Parse with uppercase X separator."""
        result = parse_dimensions("100X50")
        assert len(result) == 1
        assert result[0].width == 100.0
        assert result[0].height == 50.0

    def test_asterisk_separator(self) -> None:
        """Parse with asterisk separator."""
        result = parse_dimensions("100*50")
        assert len(result) == 1
        assert result[0].width == 100.0
        assert result[0].height == 50.0
