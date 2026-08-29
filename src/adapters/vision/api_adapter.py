"""API adapter — analyze blueprints using OpenAI GPT vision."""

from __future__ import annotations

import base64
import json
import logging
import re
import time

from src.adapters.vision.cost_tracker import CostTracker
from src.domain.exceptions import BlueprintAnalysisError
from src.domain.models import Piece

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# PROMPTS — el harness completo de extracción
# ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert CAD blueprint reader for woodworking and furniture manufacturing.

Your ONLY job is to extract piece dimensions with absolute precision. Every number matters.

## How to read CAD drawings

CAD blueprints use specific conventions:
- Dimension lines: thin lines with arrows pointing to edges, with a number in the middle
- Extension lines: thin lines extending from the object to the dimension line
- Numbers without units are typically in centimeters (cm) for furniture
- Numbers with decimal points (e.g. 2.45) may be in meters — treat them as meters
- The same dimension may appear multiple times from different angles

## What to extract

For EACH physical piece that would be cut from material:
1. Find its name from labels (cajon, lateral, estante, fondo, tapa, etc.)
2. Find its WIDTH (horizontal dimension, often labeled "ancho" or just the horizontal number)
3. Find its HEIGHT (vertical dimension, often labeled "alto" or just the vertical number)

## Critical rules

- READ EVERY NUMBER CAREFULLY. Do not guess or round.
- If a number says 272, write 272 — not 172, not 270.
- If you see "2 cajoneros de 60", there are 2 pieces of width 60.
- Depth (profundidad) is NOT width or height — ignore it for cutting list.
- If multiple pieces share the same dimensions, list them separately with quantity.
- Pay attention to the layout: pieces are usually drawn to scale relative to each other.

## Output format

Return ONLY a JSON array. No explanation, no markdown, no extra text.

Each object must have:
- "name": string — piece name in lowercase Spanish
- "width": number — width in centimeters (NO quotes around numbers)
- "height": number — height in centimeters (NO quotes around numbers)
- "quantity": number (optional, default 1) — how many of this piece

Example:
[
  {"name": "lateral", "width": 80, "height": 45, "quantity": 2},
  {"name": "estante", "width": 60, "height": 40}
]

CRITICAL: Return ONLY the JSON array. Nothing else."""

USER_PROMPT = """Extract ALL piece dimensions from this furniture blueprint.

Look carefully at:
1. Every dimension line and its number
2. Every text label that names a piece
3. Quantity indicators (e.g. "2 cajoneros", "3 estantes")
4. The overall layout to understand which numbers belong to which piece

Return the JSON array of pieces with their exact dimensions in centimeters."""


def _clean_json_response(text: str) -> str:
    """Clean model response to extract valid JSON."""
    # Remove markdown code blocks if present
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    # Remove any leading/trailing non-JSON text
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        return match.group(0)
    return text


def _validate_piece(name: str, width: float, height: float) -> bool:
    """Validate piece dimensions are reasonable for furniture."""
    if width <= 0 or height <= 0:
        return False
    if width > 600 or height > 600:  # No furniture piece > 6m
        return False
    if width < 1 or height < 1:  # Too small to be a real piece
        return False
    return True


class APIVisionAdapter:
    """Analyze blueprints using OpenAI GPT vision API."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        """Initialize API vision adapter.

        Args:
            api_key: OpenAI API key.
            model: Model to use for vision analysis.
        """
        self.api_key = api_key
        self.model = model
        self.tracker = CostTracker(model=model)

    def _call_api(self, image: bytes, operation: str) -> str:
        """Make a single API call and return raw text response."""
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        b64_image = base64.b64encode(image).decode("utf-8")

        t0 = time.monotonic()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": USER_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64_image}",
                                "detail": "high",  # Use high detail for CAD precision
                            },
                        },
                    ],
                },
            ],
            max_completion_tokens=4000,
        )
        duration_ms = int((time.monotonic() - t0) * 1000)

        usage = response.usage
        self.tracker.record_request(
            operation=operation,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            duration_ms=duration_ms,
            image_size_bytes=len(image),
        )

        return response.choices[0].message.content or ""

    def extract_text(self, image: bytes) -> str:
        """Extract text description from image via API.

        Args:
            image: Raw image bytes.

        Returns:
            Text description of the blueprint.

        Raises:
            BlueprintAnalysisError: If API call fails.
        """
        try:
            text = self._call_api(image, "extract_text")
            logger.info(
                "API vision text extracted",
                extra={"model": self.model, "text_length": len(text)},
            )
            return text
        except Exception as e:
            raise BlueprintAnalysisError(f"API vision failed: {e}") from e

    def analyze_blueprint(self, image: bytes) -> list[Piece]:
        """Analyze blueprint image and extract piece dimensions.

        Uses a two-pass approach:
        1. Extract raw dimensions from the image
        2. Parse and validate the results

        Args:
            image: Raw image bytes.

        Returns:
            List of extracted pieces.

        Raises:
            BlueprintAnalysisError: If analysis fails.
        """
        try:
            # Pass 1: Extract raw data from image
            raw_response = self._call_api(image, "analyze_blueprint")

            # Pass 2: Parse and validate
            cleaned = _clean_json_response(raw_response)

            try:
                pieces_data = json.loads(cleaned)
            except json.JSONDecodeError as e:
                logger.warning(
                    "Failed to parse API response as JSON",
                    extra={"raw_response": raw_response[:500], "error": str(e)},
                )
                raise BlueprintAnalysisError(
                    f"Invalid JSON from API: {e}\nRaw: {raw_response[:200]}"
                ) from e

            # Build pieces with validation
            pieces: list[Piece] = []
            for p in pieces_data:
                name = p.get("name", "pieza")
                try:
                    width = float(p.get("width", 0))
                    height = float(p.get("height", 0))
                    quantity = int(p.get("quantity", 1))
                except (ValueError, TypeError):
                    continue

                if not _validate_piece(name, width, height):
                    logger.warning(
                        "Skipping invalid piece",
                        extra={"name": name, "width": width, "height": height},
                    )
                    continue

                # Add piece with quantity
                for _ in range(quantity):
                    pieces.append(Piece(name=name, width=width, height=height))

            logger.info(
                "API blueprint analyzed",
                extra={
                    "model": self.model,
                    "raw_pieces": len(pieces_data),
                    "valid_pieces": len(pieces),
                },
            )

            return pieces

        except BlueprintAnalysisError:
            raise
        except Exception as e:
            raise BlueprintAnalysisError(f"API analysis failed: {e}") from e
