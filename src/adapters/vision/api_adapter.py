"""API adapter — analyze blueprints using OpenAI GPT vision."""

from __future__ import annotations

import base64
import json
import logging

from src.domain.exceptions import BlueprintAnalysisError
from src.domain.models import Piece

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a blueprint analyzer for woodworking.
Extract piece dimensions from the image.
Return a JSON array of objects with: name (string), width (number in cm), height (number in cm).
Example: [{"name": "shelf", "width": 80, "height": 40}]
Only return the JSON array, no other text."""


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
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            b64_image = base64.b64encode(image).decode("utf-8")

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                            "Describe this blueprint in detail. "
                            "List all visible pieces with their dimensions."
                        ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64_image}",
                                    "detail": "low",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=1000,
            )

            text = response.choices[0].message.content or ""
            logger.info(
                "API vision text extracted",
                extra={"model": self.model, "text_length": len(text)},
            )
            return text

        except Exception as e:
            raise BlueprintAnalysisError(f"API vision failed: {e}") from e

    def analyze_blueprint(self, image: bytes) -> list[Piece]:
        """Analyze blueprint image and extract piece dimensions.

        Args:
            image: Raw image bytes.

        Returns:
            List of extracted pieces.

        Raises:
            BlueprintAnalysisError: If analysis fails.
        """
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            b64_image = base64.b64encode(image).decode("utf-8")

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this blueprint and extract all piece dimensions.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64_image}",
                                    "detail": "low",
                                },
                            },
                        ],
                    },
                ],
                max_tokens=1000,
            )

            content = response.choices[0].message.content or "[]"
            pieces_data = json.loads(content)

            pieces = [
                Piece(
                    name=p.get("name", "piece"),
                    width=float(p.get("width", 0)),
                    height=float(p.get("height", 0)),
                )
                for p in pieces_data
                if p.get("width") and p.get("height")
            ]

            logger.info(
                "API blueprint analyzed",
                extra={"model": self.model, "pieces_found": len(pieces)},
            )

            return pieces

        except json.JSONDecodeError as e:
            raise BlueprintAnalysisError(f"Invalid API response format: {e}") from e
        except Exception as e:
            raise BlueprintAnalysisError(f"API analysis failed: {e}") from e
