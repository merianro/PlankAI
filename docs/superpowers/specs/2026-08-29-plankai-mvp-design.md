# PlankAI MVP — Design Document

## Overview

AI-powered system for generating furniture cutting lists from blueprints. Processes images and PDFs to extract piece dimensions, calculates materials, and outputs a structured parts list.

**Target**: Professional woodworkers and carpentry workshops (personal use first, commercializable later).

## Architecture

### Pipeline

```
PDF/Imagen → PyMuPDF → OCR/Regex → AI (fallback) → Calculadora → Output
```

### Hexagonal Architecture (Ports & Adapters)

```
src/
├── domain/                    # Core business logic (NO external dependencies)
│   ├── models.py              # Piece, Blueprint, CuttingList (dataclasses)
│   ├── calculator.py          # Parts calculation logic
│   └── validator.py           # Business rules validation
├── ports/                     # Interfaces (protocols)
│   ├── input.py               # InputPort (BlueprinAnalyzer)
│   ├── output.py              # OutputPort (CuttingListPresenter)
│   ├── storage.py             # StoragePort (CorrectionsRepository)
│   └── vision.py              # VisionPort (ImageAnalyzer)
├── adapters/                  # External implementations
│   ├── telegram/              # Telegram bot adapter
│   │   ├── bot.py
│   │   └── handlers.py
│   ├── vision/                # Vision adapters
│   │   ├── ocr_adapter.py     # Tesseract/EasyOCR
│   │   └── api_adapter.py     # OpenAI GPT-4o-mini
│   ├── pdf/                   # PDF processing
│   │   └── pymupdf_adapter.py
│   └── storage/               # Data persistence
│       └── sqlite_adapter.py
├── prompts/                   # AI prompts (text files)
│   └── blueprint_analyzer.txt
├── config.py                  # Configuration management
├── logging_config.py          # Structured logging setup
└── main.py                    # Composition root
```

### Components

| Component | Type | Cost |
|-----------|------|------|
| PDF → Image | PyMuPDF (local) | Free |
| Text extraction | OCR + Regex (local) | Free |
| AI interpretation | GPT-5.6 Luna API (fallback only) | ~$0.0001/imagen |
| Calculation | Algorithm (local) | Free |
| Output formatting | Template (local) | Free |

### Key Design Decisions

1. **AI usage minimization**: Only activate AI when OCR/regex fails to extract clear dimensions. 90%+ of blueprints should work without AI.

2. **Hexagonal architecture**: Domain logic is isolated from external dependencies. Adapters can be swapped without changing business rules.

3. **Dependency inversion**: Domain defines interfaces (ports), adapters implement them. Makes testing trivial.

4. **Validation-first approach**:
   - Mathematical validation (dimension logic, panel fitting)
   - Human confirmation flow in bot
   - Corrections storage for future prompt improvement

## Code Quality Standards

### SOLID Principles

| Principle | Application |
|-----------|-------------|
| **S**ingle Responsibility | Each module does ONE thing: `calculator.py` calculates, `parser.py` parses, `validator.py` validates |
| **O**pen/Closed | Domain logic open for extension (new adapters), closed for modification |
| **L**iskov Substitution | Any `VisionPort` implementation works interchangeably (OCR, API, mock) |
| **I**nterface Segregation | Small, focused interfaces: `InputPort`, `OutputPort`, `StoragePort` |
| **D**ependency Inversion | Domain depends on abstractions (ports), not concrete implementations |

### Testing Strategy (TDD)

```
tests/
├── unit/                      # Pure business logic (NO I/O)
│   ├── test_calculator.py
│   ├── test_parser.py
│   └── test_validator.py
├── integration/               # Adapter interactions
│   ├── test_ocr_adapter.py
│   └── test_sqlite_adapter.py
├── fixtures/                  # Test data
│   ├── images/
│   └── pdfs/
└── conftest.py               # Shared fixtures
```

- **Unit tests**: 100% coverage on domain logic. No mocks needed.
- **Integration tests**: Test adapter implementations with real dependencies.
- **Test command**: `pytest tests/ -v --cov=src --cov-report=term-missing`
- **Coverage target**: 90%+ on domain, 70%+ overall

### Code Style & Tooling

| Tool | Purpose | Config |
|------|---------|--------|
| **Ruff** | Linting + formatting | `pyproject.toml` |
| **Black** | Code formatting (if Ruff insufficient) | Default |
| **MyPy** | Static type checking | Strict mode |
| **Pre-commit** | Git hooks for quality gates | `.pre-commit-config.yaml` |

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

### Error Handling

```python
# Custom exceptions hierarchy
class PlankAIError(Exception):
    """Base exception for all PlankAI errors."""

class BlueprintAnalysisError(PlankAIError):
    """Failed to analyze blueprint."""

class DimensionParsingError(PlankAIError):
    """Could not parse dimensions from text."""

class ValidationError(PlankAIError):
    """Business rule validation failed."""
```

- Never catch generic `Exception`
- Log errors with context (image filename, timestamp, partial results)
- Return meaningful errors to user (not stack traces)

### Logging

```python
# Structured logging with context
logger = logging.getLogger(__name__)

logger.info(
    "Blueprint analyzed",
    extra={
        "file": filename,
        "pieces_found": len(pieces),
        "ai_used": ai_fallback_triggered,
        "duration_ms": elapsed,
    }
)
```

- Use `structlog` or standard `logging` with JSON formatter
- Log levels: DEBUG (dev), INFO (operations), WARNING (fallbacks), ERROR (failures)
- Never log: API keys, user data, full image content

### Configuration Management

```python
# config.py — Pydantic Settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # AI
    openai_api_key: str
    vision_model: str = "gpt-5.6-luna"
    
    # OCR
    ocr_engine: str = "tesseract"  # or "easyocr"
    
    # Storage
    database_url: str = "sqlite:///data/corrections.db"
    
    # Bot
    telegram_token: str
    
    class Config:
        env_file = ".env"
        env_prefix = "PLANKAI_"
```

- All config via environment variables (`.env` for local, real env for prod)
- Never hardcode secrets or magic numbers
- Pydantic validates config at startup

### Documentation

- **Docstrings**: Google style, all public functions
- **Type hints**: Mandatory everywhere (enforced by MyPy)
- **README.md**: Setup, usage, development workflow
- **Architecture Decision Records**: Document non-obvious choices in `docs/adr/`

```python
def calculate_panels(pieces: list[Piece], panel: Panel) -> int:
    """Calculate how many panels are needed for the given pieces.
    
    Args:
        pieces: List of pieces to cut.
        panel: Standard panel dimensions.
    
    Returns:
        Number of panels required.
    
    Raises:
        ValidationError: If a piece exceeds panel dimensions.
    """
```

## Scope

### MVP (Fase 1) — This spec

- [ ] PDF/Image upload and processing
- [ ] Text/dimension extraction via OCR
- [ ] AI fallback for ambiguous inputs
- [ ] Parts list calculation (pieces + quantities + dimensions)
- [ ] Material requirement estimation (panels needed)
- [ ] Telegram bot interface (upload → result)
- [ ] Human confirmation flow
- [ ] Corrections storage

### Future (Fase 2+)

- [ ] Cutting optimization (nesting algorithm)
- [ ] PDF export with cutting diagram
- [ ] Multiple panel sizes/materials
- [ ] Inventory tracking
- [ ] Auto-improvement from correction history
- [ ] Commercial deployment

## Tech Stack

- **Language**: Python 3.11+
- **PDF Processing**: PyMuPDF (fitz)
- **OCR**: Tesseract or EasyOCR (TBD)
- **AI API**: OpenAI GPT-5.6 Luna (text extraction mode)
- **Bot Framework**: python-telegram-bot
- **Data Storage**: SQLite (corrections, history)
- **Config**: Pydantic Settings
- **Testing**: pytest + coverage
- **Linting**: Ruff + MyPy

## Cost Estimate

- **1000 images/month**: ~$0.10 USD (90% algorithmic, 10% AI fallback)
- **Infrastructure**: $0 (runs locally)
- **Total monthly cost**: <$1 USD for typical workshop usage

## Validation Strategy

1. **Mathematical**: Check dimension logic, panel fitting, quantity coherence
2. **Human**: Bot asks "Correcto? ✅ Confirmar | ✏️ Editar" after each analysis
3. **Learning**: Store corrections in SQLite, analyze patterns after 50+ corrections

## Open Questions (resolved)

| Question | Decision |
|----------|----------|
| Input types | Images + PDFs (no CAD for now) |
| Processing location | Local first, Telegram bot in Fase 2 |
| Hardware | No GPU → API-based vision |
| Output format | Simple parts list (no nesting) |
| Interaction | Upload → direct result, no conversation |
| Vision model | GPT-5.6 Luna (cheap, good text extraction) |
| Validation | Math + human confirmation + corrections storage |
| Architecture | Hexagonal (Ports & Adapters) |
| Code quality | SOLID, TDD, strict typing, Ruff + MyPy |
