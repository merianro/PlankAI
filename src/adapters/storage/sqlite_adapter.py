"""SQLite adapter — persist corrections for future prompt improvement."""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path

from src.domain.models import Piece

logger = logging.getLogger(__name__)


class SQLiteCorrectionsRepository:
    """Store and retrieve blueprint corrections in SQLite."""

    def __init__(self, db_path: str = "data/corrections.db") -> None:
        """Initialize SQLite repository.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    blueprint_name TEXT NOT NULL,
                    original_pieces TEXT NOT NULL,
                    corrected_pieces TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def save_correction(
        self,
        blueprint_name: str,
        original_pieces: list[Piece],
        corrected_pieces: list[Piece],
    ) -> None:
        """Save a user correction.

        Args:
            blueprint_name: Name of the blueprint.
            original_pieces: Pieces originally extracted.
            corrected_pieces: Pieces after user correction.
        """
        original_json = json.dumps(
            [{"name": p.name, "w": p.width, "h": p.height} for p in original_pieces]
        )
        corrected_json = json.dumps(
            [{"name": p.name, "w": p.width, "h": p.height} for p in corrected_pieces]
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO corrections (blueprint_name, original_pieces, corrected_pieces) "
                "VALUES (?, ?, ?)",
                (blueprint_name, original_json, corrected_json),
            )

        logger.info(
            "Correction saved",
            extra={
                "blueprint_name": blueprint_name,
                "original_count": len(original_pieces),
                "corrected_count": len(corrected_pieces),
            },
        )

    def get_corrections(self, blueprint_name: str) -> list[dict[str, object]]:
        """Retrieve past corrections for a blueprint.

        Args:
            blueprint_name: Name of the blueprint.

        Returns:
            List of correction records.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM corrections WHERE blueprint_name = ? ORDER BY created_at DESC",
                (blueprint_name,),
            )
            rows = cursor.fetchall()

        return [
            {
                "id": row["id"],
                "blueprint_name": row["blueprint_name"],
                "original_pieces": json.loads(row["original_pieces"]),
                "corrected_pieces": json.loads(row["corrected_pieces"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]
