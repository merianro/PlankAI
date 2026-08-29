"""PDF adapter — extract images from PDFs using PyMuPDF."""

from __future__ import annotations

import logging

import fitz  # PyMuPDF

from src.domain.exceptions import BlueprintAnalysisError

logger = logging.getLogger(__name__)


class PDFImageExtractor:
    """Extract images from PDF files using PyMuPDF."""

    def extract_images(self, pdf_path: str) -> list[bytes]:
        """Extract all images from a PDF file.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            List of image bytes (PNG format).

        Raises:
            BlueprintAnalysisError: If extraction fails.
        """
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            raise BlueprintAnalysisError(f"Failed to open PDF: {pdf_path}") from e

        images: list[bytes] = []

        try:
            for page_index in range(len(doc)):
                page = doc[page_index]
                image_list = page.get_images(full=True)

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    images.append(image_bytes)

                    logger.info(
                        "Extracted image from PDF",
                        extra={
                            "file": pdf_path,
                            "page": page_index + 1,
                            "image_index": img_index + 1,
                            "size_bytes": len(image_bytes),
                        },
                    )
        finally:
            doc.close()

        if not images:
            raise BlueprintAnalysisError(f"No images found in PDF: {pdf_path}")

        return images

    def extract_images_from_bytes(self, pdf_bytes: bytes) -> list[bytes]:
        """Extract images from PDF bytes.

        Args:
            pdf_bytes: Raw PDF file bytes.

        Returns:
            List of image bytes (PNG format).

        Raises:
            BlueprintAnalysisError: If extraction fails.
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            raise BlueprintAnalysisError("Failed to open PDF from bytes") from e

        images: list[bytes] = []

        try:
            for page_index in range(len(doc)):
                page = doc[page_index]
                image_list = page.get_images(full=True)

                for img in image_list:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    images.append(image_bytes)
        finally:
            doc.close()

        return images
