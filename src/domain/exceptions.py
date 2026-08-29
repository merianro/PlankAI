"""Custom exception hierarchy for PlankAI."""


class PlankAIError(Exception):
    """Base exception for all PlankAI errors."""


class BlueprintAnalysisError(PlankAIError):
    """Failed to analyze blueprint."""


class DimensionParsingError(PlankAIError):
    """Could not parse dimensions from text."""


class ValidationError(PlankAIError):
    """Business rule validation failed."""
