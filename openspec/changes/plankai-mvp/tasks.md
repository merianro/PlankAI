# Tasks: PlankAI MVP

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 800-1200 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 → PR 4 |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Project setup + domain models + ports | PR 1 → develop | `pytest tests/unit/test_models.py` | N/A — pure dataclasses | src/domain/, src/ports/, pyproject.toml |
| 2 | Core logic: calculator + validator + parser | PR 2 → PR 1 | `pytest tests/unit/` | N/A — pure functions | src/domain/calculator.py, src/domain/validator.py, src/domain/parser.py |
| 3 | Adapters: OCR, PDF, API, SQLite | PR 3 → PR 2 | `pytest tests/integration/` | N/A — adapter tests with mocks | src/adapters/ |
| 4 | Telegram bot + wiring + main | PR 4 → PR 3 | `pytest tests/` | Manual: send image to bot | src/adapters/telegram/, src/main.py |

## Phase 1: Foundation

- [ ] 1.1 Create `pyproject.toml` with Python 3.11, dependencies (python-telegram-bot, PyMuPDF, openai, pydantic-settings, ruff, mypy, pytest, pytest-cov)
- [ ] 1.2 Create `src/__init__.py` and domain package structure
- [ ] 1.3 Create `src/domain/models.py` — dataclasses: Piece, Blueprint, CuttingList, Panel with type hints
- [ ] 1.4 Create `src/ports/input.py` — InputPort protocol (BlueprinAnalyzer)
- [ ] 1.5 Create `src/ports/output.py` — OutputPort protocol (CuttingListPresenter)
- [ ] 1.6 Create `src/ports/vision.py` — VisionPort protocol (ImageAnalyzer)
- [ ] 1.7 Create `src/ports/storage.py` — StoragePort protocol (CorrectionsRepository)
- [ ] 1.8 Create `src/config.py` — Pydantic Settings with env vars (OPENAI_API_KEY, TELEGRAM_TOKEN, VISION_MODEL, DATABASE_URL)
- [ ] 1.9 Create `.env.example` with all required env vars

## Phase 2: Core Logic

- [ ] 2.1 Create `src/domain/parser.py` — parse_dimensions(text: str) -> list[Piece] using regex
- [ ] 2.2 Create `src/domain/calculator.py` — calculate_panels(pieces, panel) -> int and calculate_cutting_list(blueprint) -> CuttingList
- [ ] 2.3 Create `src/domain/validator.py` — validate_dimensions(pieces) -> list[ValidationError], check panel fitting, check logical dimensions
- [ ] 2.4 Create `tests/unit/test_parser.py` — test regex parsing of "180cm × 90cm", "70×7×3", edge cases
- [ ] 2.5 Create `tests/unit/test_calculator.py` — test panel calculation, quantity logic
- [ ] 2.6 Create `tests/unit/test_validator.py` — test validation rules, error cases

## Phase 3: Adapters

- [ ] 3.1 Create `src/adapters/pdf/pymupdf_adapter.py` — implement InputPort: extract_image_from_pdf(pdf_path) -> Image
- [ ] 3.2 Create `src/adapters/vision/ocr_adapter.py` — implement VisionPort: extract_text(image) -> str using Tesseract/EasyOCR
- [ ] 3.3 Create `src/adapters/vision/api_adapter.py` — implement VisionPort: analyze_blueprint(image) -> list[Piece] using GPT-5.6 Luna
- [ ] 3.4 Create `src/adapters/storage/sqlite_adapter.py` — implement StoragePort: save_correction(), get_corrections()
- [ ] 3.5 Create `tests/integration/test_ocr_adapter.py` — test OCR with sample images
- [ ] 3.6 Create `tests/integration/test_sqlite_adapter.py` — test CRUD operations

## Phase 4: Integration

- [ ] 4.1 Create `src/adapters/telegram/bot.py` — TelegramBot class with handlers
- [ ] 4.2 Create `src/adapters/telegram/handlers.py` — handle_document(), handle_confirmation(), handle_edit()
- [ ] 4.3 Create `src/main.py` — composition root: wire all adapters, start bot
- [ ] 4.4 Create `tests/integration/test_bot.py` — test bot flow with mocks

## Phase 5: Quality

- [ ] 5.1 Run `ruff check src/` and fix all linting issues
- [ ] 5.2 Run `mypy src/` and fix all type errors
- [ ] 5.3 Run `pytest tests/ -v --cov=src --cov-report=term-missing` — verify 90%+ coverage on domain
- [ ] 5.4 Create `README.md` with setup instructions, usage, development workflow
- [ ] 5.5 Add `.gitignore` for .env, __pycache__, .pytest_cache, .mypy_cache
