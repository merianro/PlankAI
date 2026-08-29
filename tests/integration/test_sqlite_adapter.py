"""Integration tests for SQLite corrections repository."""

from pathlib import Path

import pytest

from src.adapters.storage.sqlite_adapter import SQLiteCorrectionsRepository
from src.domain.models import Piece


@pytest.fixture
def repo(tmp_path: Path) -> SQLiteCorrectionsRepository:
    """Create a temporary SQLite repository."""
    db_path = str(tmp_path / "test_corrections.db")
    return SQLiteCorrectionsRepository(db_path=db_path)


class TestSQLiteCorrectionsRepository:
    """Test SQLite corrections repository."""

    def test_save_and_retrieve(self, repo: SQLiteCorrectionsRepository) -> None:
        """Save a correction and retrieve it."""
        original = [Piece(name="shelf", width=80, height=40)]
        corrected = [Piece(name="shelf", width=80, height=42)]

        repo.save_correction("bookcase", original, corrected)
        corrections = repo.get_corrections("bookcase")

        assert len(corrections) == 1
        assert corrections[0]["blueprint_name"] == "bookcase"
        assert corrections[0]["original_pieces"][0]["w"] == 80
        assert corrections[0]["corrected_pieces"][0]["h"] == 42

    def test_multiple_corrections(self, repo: SQLiteCorrectionsRepository) -> None:
        """Multiple corrections for same blueprint."""
        original = [Piece(name="a", width=10, height=20)]

        repo.save_correction("test", original, [Piece(name="a", width=10, height=21)])
        repo.save_correction("test", original, [Piece(name="a", width=10, height=22)])

        corrections = repo.get_corrections("test")
        assert len(corrections) == 2

    def test_different_blueprints(self, repo: SQLiteCorrectionsRepository) -> None:
        """Corrections for different blueprints are isolated."""
        repo.save_correction(
            "bp1",
            [Piece(name="a", width=10, height=20)],
            [Piece(name="a", width=10, height=21)],
        )
        repo.save_correction(
            "bp2",
            [Piece(name="b", width=30, height=40)],
            [Piece(name="b", width=30, height=41)],
        )

        assert len(repo.get_corrections("bp1")) == 1
        assert len(repo.get_corrections("bp2")) == 1
        assert len(repo.get_corrections("bp3")) == 0

    def test_empty_corrections(self, repo: SQLiteCorrectionsRepository) -> None:
        """No corrections returns empty list."""
        assert repo.get_corrections("nonexistent") == []

    def test_database_created(self, tmp_path: Path) -> None:
        """Database file is created on init."""
        db_path = str(tmp_path / "new.db")
        SQLiteCorrectionsRepository(db_path=db_path)
        assert Path(db_path).exists()
