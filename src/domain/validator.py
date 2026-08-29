"""Validator — business rules for dimension and panel validation."""

from __future__ import annotations

from src.domain.models import Panel, Piece, ValidationError, ValidationErrorType


def validate_dimensions(pieces: list[Piece]) -> list[ValidationError]:
    """Validate piece dimensions against business rules.

    Checks:
    - No zero or negative dimensions
    - No absurdly large dimensions (> 10000cm = 100m)
    - No illogical aspect ratios (> 100:1)

    Args:
        pieces: List of pieces to validate.

    Returns:
        List of validation errors (empty if all valid).
    """
    errors: list[ValidationError] = []

    for piece in pieces:
        errors.extend(_validate_single_piece(piece))

    return errors


def validate_panel_fit(pieces: list[Piece], panel: Panel) -> list[ValidationError]:
    """Validate that pieces can fit on the panel.

    Args:
        pieces: List of pieces to check.
        panel: Standard panel dimensions.

    Returns:
        List of validation errors (empty if all fit).
    """
    errors: list[ValidationError] = []

    for piece in pieces:
        if piece.width > panel.width or piece.height > panel.height:
            # Try rotated fit
            if piece.width > panel.height or piece.height > panel.width:
                errors.append(
                    ValidationError(
                        type=ValidationErrorType.PIECE_EXCEEDS_PANEL,
                        message=(
                            f"Piece '{piece.name}' ({piece.width}x{piece.height}) "
                            f"exceeds panel ({panel.width}x{panel.height})"
                        ),
                        piece_name=piece.name,
                    )
                )

    return errors


def _validate_single_piece(piece: Piece) -> list[ValidationError]:
    """Validate a single piece."""
    errors: list[ValidationError] = []

    # Zero or negative dimensions
    if piece.width <= 0 or piece.height <= 0:
        errors.append(
            ValidationError(
                type=ValidationErrorType.DIMENSION_ZERO,
                message=f"Piece '{piece.name}' has zero or negative dimension",
                piece_name=piece.name,
            )
        )
        return errors  # Don't check further

    if piece.width < 0 or piece.height < 0:
        errors.append(
            ValidationError(
                type=ValidationErrorType.NEGATIVE_DIMENSION,
                message=f"Piece '{piece.name}' has negative dimension",
                piece_name=piece.name,
            )
        )

    # Too large (> 10000cm = 100m)
    max_dim = 10000.0
    if piece.width > max_dim or piece.height > max_dim:
        errors.append(
            ValidationError(
                type=ValidationErrorType.DIMENSION_TOO_LARGE,
                message=(
                    f"Piece '{piece.name}' dimension exceeds {max_dim}cm: "
                    f"{piece.width}x{piece.height}"
                ),
                piece_name=piece.name,
            )
        )

    # Illogical aspect ratio (> 100:1)
    ratio = max(piece.width, piece.height) / min(piece.width, piece.height)
    if ratio > 100:
        errors.append(
            ValidationError(
                type=ValidationErrorType.illogical_aspect_ratio,
                message=(
                    f"Piece '{piece.name}' has illogical aspect ratio "
                    f"{ratio:.1f}:1 ({piece.width}x{piece.height})"
                ),
                piece_name=piece.name,
            )
        )

    return errors
