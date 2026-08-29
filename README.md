# PlankAI

Generador de listas de cortes (despieces) a partir de planos de mobiliario, potenciado por IA.

## Descripcion

PlankAI procesa imagenes y PDFs de planos para extraer dimensiones de piezas, calcular materiales y generar una lista de cortes estructurada.

**Target**: Carpinteros profesionales y talleres de muebles.

## Arquitectura

Hexagonal (Ports & Adapters):

```
src/
├── domain/          # Logica de negocio (sin dependencias externas)
├── ports/           # Interfaces (protocols)
├── adapters/        # Implementaciones externas
│   ├── telegram/    # Bot de Telegram
│   ├── vision/      # OCR y API de vision
│   ├── pdf/         # Procesamiento de PDFs
│   └── storage/     # Persistencia en SQLite
├── config.py        # Configuracion via env vars
└── main.py          # Composition root
```

## Stack

- **Python** 3.11+
- **PyMuPDF** — extraccion de imagenes de PDFs
- **Tesseract/EasyOCR** — OCR local (gratuito)
- **OpenAI GPT** — fallback para planos ambiguos
- **python-telegram-bot** — interfaz de usuario
- **SQLite** — persistencia de correcciones
- **Pydantic Settings** — configuracion

## Instalacion

```bash
# Clonar
git clone https://github.com/merianro/PlankAI.git
cd PlankAI

# Crear venv
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -e ".[dev]"

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys
```

## Uso

```bash
# Ejecutar bot de Telegram
python -m src.main
```

Envia una imagen o PDF de un plano al bot y te devolvera la lista de cortes.

## Desarrollo

```bash
# Linting
ruff check src/ tests/

# Type checking
mypy src/

# Tests
pytest tests/ -v

# Tests con coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

## Estructura de tests

```
tests/
├── unit/                    # Logica pura (sin I/O)
│   ├── test_parser.py
│   ├── test_calculator.py
│   └── test_validator.py
├── integration/             # Interacciones con adaptadores
│   ├── test_sqlite_adapter.py
│   ├── test_ocr_adapter.py
│   └── test_bot.py
└── fixtures/                # Datos de prueba
```

## Formato de entrada

El parser soporta:
- `180cm × 90cm`
- `70×7×3` (con espesor)
- `Tablero 120 x 80` (con nombre)
- `50.5cm*30cm` (decimales)

## Licencia

MIT
