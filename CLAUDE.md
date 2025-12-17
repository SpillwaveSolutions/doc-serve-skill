# Doc-Serve Development Guidelines

Instructions for Claude Code when working on this repository.

## Project Overview

Doc-Serve is a RAG-based document indexing and semantic search system. It's a monorepo containing:

| Package | Path | Description |
|---------|------|-------------|
| doc-serve-server | `doc-serve-server/` | FastAPI REST API server |
| doc-svr-ctl | `doc-svr-ctl/` | CLI management tool |
| doc-serve-skill | `doc-serve-skill/` | Claude Code skill |

## Technology Stack

- **Python**: 3.10+
- **Build System**: Poetry
- **Server**: FastAPI + Uvicorn
- **CLI**: Click + Rich
- **Vector Store**: ChromaDB
- **Embeddings**: OpenAI text-embedding-3-large
- **Indexing**: LlamaIndex

## Build and Test Commands

### doc-serve-server

```bash
cd doc-serve-server
poetry install                    # Install dependencies
poetry run doc-serve              # Run server
poetry run pytest                 # Run tests
poetry run pytest --cov=src       # Tests with coverage
poetry run mypy src               # Type checking
poetry run ruff check src         # Linting
poetry run black src              # Format code
```

### doc-svr-ctl

```bash
cd doc-svr-ctl
poetry install                    # Install dependencies
poetry run doc-svr-ctl --help     # Show CLI help
poetry run pytest                 # Run tests
poetry run mypy src               # Type checking
poetry run ruff check src         # Linting
poetry run black src              # Format code
```

### Full Quality Check

```bash
# Run from package directory
poetry run black src tests && poetry run ruff check src tests && poetry run mypy src && poetry run pytest
```

## Project Structure

```
doc-serve/
├── doc-serve-server/           # FastAPI server
│   ├── src/
│   │   ├── api/                # REST endpoints
│   │   │   ├── main.py         # App entry point
│   │   │   └── routers/        # Route handlers
│   │   ├── config/             # Settings (Pydantic)
│   │   ├── indexing/           # Document processing
│   │   ├── models/             # Request/response models
│   │   ├── services/           # Business logic
│   │   └── storage/            # ChromaDB integration
│   └── tests/
├── doc-svr-ctl/                # CLI tool
│   ├── src/
│   │   ├── cli.py              # Main entry point
│   │   ├── client/             # API client
│   │   └── commands/           # CLI commands
│   └── tests/
├── doc-serve-skill/            # Claude skill
│   └── doc-serve/
│       └── SKILL.md
└── docs/                       # Documentation
```

## Code Style

### Python Standards
- **Formatter**: Black (line length 88)
- **Linter**: Ruff
- **Type Checker**: mypy (strict mode)
- **Type Hints**: Required for all function signatures

### Style Guidelines
1. Use Google-style docstrings
2. Sort imports with Ruff/isort
3. Type hint all function parameters and returns
4. Keep functions focused and testable

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/health/status` | GET | Indexing status |
| `/query` | POST | Semantic search |
| `/query/count` | GET | Document count |
| `/index` | POST | Start indexing |
| `/index/add` | POST | Add documents |
| `/index` | DELETE | Clear index |

## CLI Commands

| Command | Description |
|---------|-------------|
| `doc-svr-ctl status` | Check server status |
| `doc-svr-ctl query "text"` | Search documents |
| `doc-svr-ctl index /path` | Index documents |
| `doc-svr-ctl reset --yes` | Clear index |

## Environment Variables

### Server (doc-serve-server/.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `API_HOST` | No | Server host (default: 127.0.0.1) |
| `API_PORT` | No | Server port (default: 8000) |
| `DEBUG` | No | Debug mode (default: false) |

### CLI

| Variable | Description |
|----------|-------------|
| `DOC_SERVE_URL` | Server URL (default: http://127.0.0.1:8000) |

## Security Notes

- **Never commit** `.env` files or API keys
- `.env.example` files are safe to commit (no real keys)
- Check `.gitignore` excludes all sensitive files

## Documentation

- [User Guide](docs/USER_GUIDE.md) - End-user documentation
- [Developer Guide](docs/DEVELOPERS_GUIDE.md) - Development setup
- [API Reference](doc-serve-skill/doc-serve/references/api_reference.md) - Full API docs
- [Original Spec](docs/ORIGINAL_SPEC.md) - Project specification

## Quality Assurance

After making code changes:
1. Run tests: `poetry run pytest`
2. Check types: `poetry run mypy src`
3. Lint: `poetry run ruff check src`
4. Format: `poetry run black src`

## Git Workflow

- Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- Create feature branches from main
- Run all quality checks before committing
