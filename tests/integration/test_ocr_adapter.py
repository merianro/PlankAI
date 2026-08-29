"""Integration tests for OCR adapter."""

import pytest

from src.adapters.vision.ocr_adapter import OCRAdapter

pytesseract = pytest.importorskip("pytesseract")


class TestOCRAdapter:
    """Test OCR adapter (requires tesseract installed)."""

    @pytest.fixture
    def adapter(self) -> OCRAdapter:
        """Create OCR adapter instance."""
        return OCRAdapter(lang="eng")

    def test_extract_text_returns_string(self, adapter: OCRAdapter) -> None:
        """Extract text returns a string (even if empty for invalid image)."""
        # Minimal 1x1 white PNG
        import struct
        import zlib

        def make_minimal_png() -> bytes:
            width, height = 10, 10
            raw_data = b""
            for _ in range(height):
                raw_data += b"\x00" + b"\xff\xff\xff" * width  # white pixels

            def chunk(chunk_type: bytes, data: bytes) -> bytes:
                c = chunk_type + data
                crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
                return struct.pack(">I", len(data)) + c + crc

            ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
            compressed = zlib.compress(raw_data)

            return (
                b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", compressed)
                + chunk(b"IEND", b"")
            )

        png_bytes = make_minimal_png()
        result = adapter.extract_text(png_bytes)
        assert isinstance(result, str)

    def test_analyze_blueprint_returns_list(self, adapter: OCRAdapter) -> None:
        """analyze_blueprint returns a list (OCR only extracts text)."""
        result = adapter.analyze_blueprint(b"fake-image")
        assert isinstance(result, list)
        assert result == []
