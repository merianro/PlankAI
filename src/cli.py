"""CLI — test the PlankAI pipeline without Telegram.

Usage:
    # From text input
    python -m src.cli --text "180cm × 90cm"
    python -m src.cli --text "Tablero 120 x 80" --text "100 × 50"

    # From image (OCR)
    python -m src.cli --image path/to/blueprint.png

    # From PDF (tries text extraction first, then OCR)
    python -m src.cli --pdf path/to/blueprint.pdf

    # Show raw extracted text (debug)
    python -m src.cli --pdf path/to/blueprint.pdf --show-text

    # Dimensions in meters (auto-convert to cm)
    python -m src.cli --text "1.35 0.8" --unit m

    # Custom panel size (default: 280×207 cm)
    python -m src.cli --text "180 × 90" --panel-width 360 --panel-height 180
"""

from __future__ import annotations

import argparse
import logging
import sys

from src.domain.calculator import calculate_cutting_list
from src.domain.models import Blueprint, Panel, Piece
from src.domain.parser import parse_dimensions
from src.domain.validator import validate_dimensions, validate_panel_fit


def parse_numbers_as_dimensions(text: str) -> list[Piece]:
    """Extract all numbers from text and pair them as W×H dimensions.

    Assumes numbers appear in order: w1, h1, w2, h2, ...
    Skips numbers that look like labels (very small or very large).
    """
    import re
    numbers = []
    for match in re.finditer(r"\d+(?:\.\d+)?", text):
        val = float(match.group())
        numbers.append(val)

    if len(numbers) < 2:
        return []

    pieces: list[Piece] = []
    # Pair consecutive numbers as (width, height)
    i = 0
    while i + 1 < len(numbers):
        w = numbers[i]
        h = numbers[i + 1]

        # Skip if both are very small (< 1, probably not dimensions in cm)
        if w < 1 and h < 1:
            i += 1
            continue

        # Skip if either is unreasonably large (> 1000cm = 10m)
        if w > 1000 or h > 1000:
            i += 1
            continue

        name = f"pieza_{len(pieces) + 1}"
        pieces.append(Piece(name=name, width=w, height=h))
        i += 2

    return pieces


def print_cutting_list(pieces: list[Piece], panel: Panel) -> None:
    """Calculate and print cutting list."""
    blueprint = Blueprint(name="input", pieces=tuple(pieces))
    cutting_list = calculate_cutting_list(blueprint, panel)

    errors = validate_dimensions(pieces)
    panel_errors = validate_panel_fit(pieces, panel)

    print("\n" + "=" * 50)
    print(f"  PLANKAI — DESPIECE GENERADO")
    print("=" * 50)
    print(f"  Piezas encontradas: {cutting_list.total_pieces}")
    print(f"  Panel estandar:     {panel.width} x {panel.height} cm")
    print(f"  Paneles necesarios: {cutting_list.panels_needed}")
    print(f"  Desperdicio:        {cutting_list.waste_percentage}%")
    print("-" * 50)
    print("  PIEZAS:")
    for p in pieces:
        qty = f" x{p.quantity}" if p.quantity > 1 else ""
        thick = f" (espesor: {p.thickness}cm)" if p.thickness else ""
        print(f"    - {p.name}: {p.width} x {p.height}cm{thick}{qty}")

    if errors:
        print("-" * 50)
        print("  ADVERTENCIAS:")
        for err in errors:
            print(f"    ! {err.message}")

    if panel_errors:
        print("-" * 50)
        print("  ERRORES DE AJUSTE:")
        for err in panel_errors:
            print(f"    X {err.message}")

    print("=" * 50 + "\n")


def process_text(texts: list[str], panel: Panel) -> None:
    """Process text input."""
    combined = "\n".join(texts)
    try:
        pieces = parse_dimensions(combined)
        print_cutting_list(pieces, panel)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def process_image(image_path: str, panel: Panel) -> None:
    """Process image input via OCR."""
    try:
        from src.adapters.vision.ocr_adapter import OCRAdapter
    except ImportError as e:
        print(f"Missing dependency: {e}", file=sys.stderr)
        print("Install with: pip install pytesseract Pillow", file=sys.stderr)
        sys.exit(1)

    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
    except FileNotFoundError:
        print(f"File not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    ocr = OCRAdapter()

    # Try direct blueprint analysis first (returns empty for OCR adapter)
    pieces = ocr.analyze_blueprint(image_bytes)

    if not pieces:
        # Fallback: extract text then parse dimensions
        print(f"Extracting text from {image_path}...")
        text = ocr.extract_text(image_bytes)
        if text:
            print(f"OCR text:\n{text}\n")
            pieces = parse_dimensions(text)
        else:
            print("No text found in image.", file=sys.stderr)
            sys.exit(1)

    print_cutting_list(list(pieces), panel)


def process_image_api(image_path: str, panel: Panel, api_key: str, model: str) -> None:
    """Process image input via OpenAI Vision API with cost tracking."""
    from src.adapters.vision.api_adapter import APIVisionAdapter

    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
    except FileNotFoundError:
        print(f"File not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    adapter = APIVisionAdapter(api_key=api_key, model=model)
    print(f"Analyzing {image_path} with {model}...")

    pieces = adapter.analyze_blueprint(image_bytes)

    if not pieces:
        # Fallback: extract text then parse
        print("No pieces from direct analysis, trying text extraction...")
        text = adapter.extract_text(image_bytes)
        if text:
            print(f"API text:\n{text}\n")
            pieces = parse_dimensions(text)

    print_cutting_list(list(pieces), panel)
    print(adapter.tracker.summary())


def process_pdf(pdf_path: str, panel: Panel, show_text: bool = False, unit: str = "cm", mode: str = "standard", api_key: str = "", model: str = "") -> None:
    """Process PDF input — try text extraction first, then OCR on images."""
    try:
        import pymupdf
    except ImportError as e:
        print(f"Missing dependency: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        print(f"Failed to open PDF: {e}", file=sys.stderr)
        sys.exit(1)

    all_text: list[str] = []
    all_pieces: list[Piece] = []

    # Strategy 1: Extract text from PDF pages
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text()
        if text.strip():
            all_text.append(text)

    # Strategy 2: Extract images and OCR them
    images: list[bytes] = []
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            images.append(base_image["image"])
    doc.close()

    if show_text:
        print("\n--- EXTRACTED TEXT ---")
        for i, text in enumerate(all_text):
            print(f"\n[Page text block {i + 1}]")
            print(text)
        if images:
            print(f"\n[Found {len(images)} embedded image(s) — OCR with --image to process]")
        print("--- END ---\n")
        return

    # Parse text for dimensions
    combined_text = "\n".join(all_text)
    if combined_text.strip():
        print(f"Extracted {len(combined_text)} chars of text from PDF")
        try:
            if mode == "numbers":
                pieces = parse_numbers_as_dimensions(combined_text)
                if pieces:
                    all_pieces.extend(pieces)
                else:
                    print("  No parseable number pairs found")
            else:
                pieces = parse_dimensions(combined_text)
                all_pieces.extend(pieces)
        except Exception:
            print("  No standard dimensions found in text (try --show-text to inspect)")

    # If no pieces from text, try OCR on images
    if not all_pieces and images:
        if api_key:
            # Use API vision for better results
            print(f"\nUsing API vision on {len(images)} embedded image(s)...")
            from src.adapters.vision.api_adapter import APIVisionAdapter
            adapter = APIVisionAdapter(api_key=api_key, model=model or "gpt-5.6-luna")
            for i, img_bytes in enumerate(images):
                print(f"  Analyzing image {i + 1}/{len(images)}...")
                try:
                    pieces = adapter.analyze_blueprint(img_bytes)
                    all_pieces.extend(pieces)
                except Exception as e:
                    print(f"    API error: {e}")
            print(adapter.tracker.summary())
        else:
            print(f"\nFalling back to OCR on {len(images)} embedded image(s)...")
            try:
                from src.adapters.vision.ocr_adapter import OCRAdapter
            except ImportError as e:
                print(f"Missing OCR dependency: {e}", file=sys.stderr)
                sys.exit(1)

            ocr = OCRAdapter()
            for i, img_bytes in enumerate(images):
                print(f"  OCR image {i + 1}/{len(images)}...")
                text = ocr.extract_text(img_bytes)
                if text:
                    print(f"    Text: {text[:100]}...")
                    try:
                        pieces = parse_dimensions(text)
                        all_pieces.extend(pieces)
                    except Exception:
                        pass

    if not all_pieces:
        print("No dimensions found in PDF.", file=sys.stderr)
        print("Try --show-text to see raw extracted content.", file=sys.stderr)
        sys.exit(1)

    # Apply unit conversion if needed
    if unit == "m":
        all_pieces = [
            Piece(name=p.name, width=p.width * 100, height=p.height * 100,
                  quantity=p.quantity, thickness=p.thickness * 100 if p.thickness else None)
            for p in all_pieces
        ]

    print_cutting_list(all_pieces, panel)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PlankAI — Generate cutting lists from text, images, or PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--text", "-t",
        action="append",
        help="Dimension text (can be repeated for multiple pieces)",
    )
    input_group.add_argument(
        "--image", "-i",
        help="Path to blueprint image (PNG, JPG)",
    )
    input_group.add_argument(
        "--pdf", "-p",
        help="Path to blueprint PDF",
    )

    parser.add_argument(
        "--panel-width",
        type=float,
        default=280.0,
        help="Panel width in cm (default: 280)",
    )
    parser.add_argument(
        "--panel-height",
        type=float,
        default=207.0,
        help="Panel height in cm (default: 207)",
    )
    parser.add_argument(
        "--unit", "-u",
        choices=["cm", "m"],
        default="cm",
        help="Unit of input dimensions (default: cm). Use 'm' to auto-convert meters to cm.",
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["standard", "numbers"],
        default="standard",
        help="Parsing mode: 'standard' expects '180×90' format, 'numbers' pairs standalone numbers as dimensions.",
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (enables AI vision for images/PDFs)",
    )
    parser.add_argument(
        "--api-model",
        default="gpt-5.6-luna",
        help="OpenAI model for vision (default: gpt-5.6-luna)",
    )
    parser.add_argument(
        "--show-text",
        action="store_true",
        help="Show raw extracted text from PDF and exit (debug mode)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    panel = Panel(name="standard", width=args.panel_width, height=args.panel_height)

    if args.text:
        process_text(args.text, panel)
    elif args.image:
        if args.api_key:
            process_image_api(args.image, panel, args.api_key, args.api_model)
        else:
            process_image(args.image, panel)
    elif args.pdf:
        process_pdf(args.pdf, panel, show_text=args.show_text, unit=args.unit, mode=args.mode, api_key=args.api_key or "", model=args.api_model)


if __name__ == "__main__":
    main()
