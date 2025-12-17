# Doc-Serve Developer Guide

This guide covers setting up a development environment, running tests, and contributing to Doc-Serve.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Building and Testing](#building-and-testing)
- [Code Style](#code-style)
- [Adding Features](#adding-features)
- [Testing Guidelines](#testing-guidelines)
- [Contributing](#contributing)

---

## Development Setup

### Prerequisites

- **Python 3.10+**: Required for type hints and modern features
- **Poetry**: Dependency management (`pip install poetry`)
- **Git**: Version control
- **OpenAI API key**: For running integration tests

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/spillwave/doc-serve.git
cd doc-serve

# Install server dependencies
cd doc-serve-server
poetry install

# Install CLI dependencies
cd ../doc-svr-ctl
poetry install

# Return to root
cd ..
```

### Environment Configuration

Create environment files for each package:

#### doc-serve-server/.env

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Development settings
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=true

# Indexing
CHUNK_SIZE=512
CHUNK_OVERLAP=50
EMBEDDING_MODEL=text-embedding-3-large
```

**Security Note**: Never commit `.env` files. They are excluded in `.gitignore`.

### IDE Setup

#### VS Code

Recommended extensions:
- Python
- Pylance
- Ruff
- Black Formatter

`.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

#### PyCharm

1. Set Python interpreter to Poetry environment
2. Enable Black formatter
3. Configure Ruff as external tool

---

## Project Structure

```
doc-serve/
├── doc-serve-server/           # FastAPI REST server
│   ├── src/
│   │   ├── api/                # REST endpoints
│   │   │   ├── main.py         # FastAPI app entry
│   │   │   └── routers/        # Route handlers
│   │   │       ├── health.py   # Health endpoints
│   │   │       ├── index.py    # Indexing endpoints
│   │   │       └── query.py    # Query endpoints
│   │   ├── config/             # Configuration
│   │   │   └── settings.py     # Pydantic settings
│   │   ├── indexing/           # Document processing
│   │   │   ├── chunking.py     # Text chunking
│   │   │   ├── document_loader.py  # File loading
│   │   │   └── embedding.py    # Embedding generation
│   │   ├── models/             # Pydantic models
│   │   │   ├── health.py       # Health response models
│   │   │   ├── index.py        # Index request/response
│   │   │   └── query.py        # Query request/response
│   │   ├── services/           # Business logic
│   │   │   ├── indexing_service.py
│   │   │   └── query_service.py
│   │   └── storage/            # Vector store
│   │       └── vector_store.py # ChromaDB integration
│   ├── tests/                  # Server tests
│   └── pyproject.toml
│
├── doc-svr-ctl/                # CLI tool
│   ├── src/
│   │   ├── cli.py              # Main CLI entry
│   │   ├── client/             # API client
│   │   │   └── api_client.py
│   │   └── commands/           # CLI commands
│   │       ├── index.py
│   │       ├── query.py
│   │       ├── reset.py
│   │       └── status.py
│   ├── tests/                  # CLI tests
│   └── pyproject.toml
│
├── doc-serve-skill/            # Claude Code skill
│   └── doc-serve/
│       ├── SKILL.md            # Skill definition
│       └── references/
│           └── api_reference.md
│
├── docs/                       # Documentation
│   ├── USER_GUIDE.md
│   ├── DEVELOPERS_GUIDE.md
│   ├── ORIGINAL_SPEC.md
│   └── design/
│
├── .gitignore
├── CLAUDE.md                   # Claude Code instructions
├── AGENTS.md                   # Agent definitions
└── README.md
```

---

## Building and Testing

### Server (doc-serve-server)

```bash
cd doc-serve-server

# Install dependencies
poetry install

# Run the server (development)
poetry run doc-serve

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src --cov-report=html

# Type checking
poetry run mypy src

# Linting
poetry run ruff check src

# Formatting
poetry run black src
```

### CLI (doc-svr-ctl)

```bash
cd doc-svr-ctl

# Install dependencies
poetry install

# Run CLI commands
poetry run doc-svr-ctl --help

# Run tests
poetry run pytest

# Type checking
poetry run mypy src

# Linting
poetry run ruff check src

# Formatting
poetry run black src
```

### Quick Test Commands

```bash
# Run all tests across packages
cd doc-serve-server && poetry run pytest && cd ../doc-svr-ctl && poetry run pytest

# Full quality check
cd doc-serve-server && poetry run ruff check . && poetry run mypy src && poetry run pytest
```

---

## Code Style

### Python Standards

- **Python Version**: 3.10+
- **Formatter**: Black (line length 88)
- **Linter**: Ruff
- **Type Checker**: mypy (strict mode)

### Style Rules

1. **Type Hints**: Required for all function signatures
   ```python
   def process_document(path: str, recursive: bool = True) -> list[Document]:
       ...
   ```

2. **Docstrings**: Google style
   ```python
   def query_documents(query: str, top_k: int = 5) -> QueryResponse:
       """Execute semantic search on indexed documents.

       Args:
           query: The search query text.
           top_k: Maximum number of results to return.

       Returns:
           QueryResponse containing matching document chunks.

       Raises:
           ValueError: If query is empty.
           ServiceUnavailableError: If indexing is in progress.
       """
   ```

3. **Imports**: Sorted by Ruff/isort
   ```python
   # Standard library
   import logging
   from pathlib import Path

   # Third-party
   from fastapi import FastAPI
   from pydantic import BaseModel

   # Local
   from .models import QueryRequest
   ```

### Pre-commit Checks

Before committing, run:

```bash
# Format
poetry run black src tests

# Lint
poetry run ruff check src tests --fix

# Type check
poetry run mypy src

# Test
poetry run pytest
```

---

## Adding Features

### Adding a New API Endpoint

1. **Create the router** in `src/api/routers/`:
   ```python
   # src/api/routers/new_feature.py
   from fastapi import APIRouter

   router = APIRouter()

   @router.get("/")
   async def get_feature():
       return {"feature": "data"}
   ```

2. **Register in main.py**:
   ```python
   from .routers.new_feature import router as new_feature_router

   app.include_router(new_feature_router, prefix="/new-feature", tags=["New Feature"])
   ```

3. **Add models** in `src/models/`

4. **Add tests** in `tests/`

### Adding a CLI Command

1. **Create command** in `src/commands/`:
   ```python
   # src/commands/new_command.py
   import click

   @click.command()
   @click.option("--option", help="Description")
   def new_command(option: str):
       """Command description."""
       click.echo(f"Running with {option}")
   ```

2. **Register in cli.py**:
   ```python
   from .commands.new_command import new_command

   cli.add_command(new_command, name="new-command")
   ```

3. **Add tests** in `tests/`

---

## Testing Guidelines

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_api/             # API tests
│   ├── test_health.py
│   ├── test_index.py
│   └── test_query.py
├── test_services/        # Service tests
│   ├── test_indexing.py
│   └── test_query.py
└── test_integration/     # Integration tests
    └── test_full_flow.py
```

### Writing Tests

```python
# tests/test_api/test_health.py
import pytest
from httpx import AsyncClient

from src.api.main import app


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "indexing", "degraded", "unhealthy"]
```

### Test Categories

| Category | Description | Marker |
|----------|-------------|--------|
| Unit | Test individual functions | `@pytest.mark.unit` |
| Integration | Test component interactions | `@pytest.mark.integration` |
| E2E | Full workflow tests | `@pytest.mark.e2e` |

### Running Specific Tests

```bash
# Run only unit tests
poetry run pytest -m unit

# Run specific test file
poetry run pytest tests/test_api/test_health.py

# Run with verbose output
poetry run pytest -v

# Run with print statements visible
poetry run pytest -s
```

---

## Contributing

### Workflow

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/my-feature`
3. **Make changes** with tests
4. **Run quality checks**:
   ```bash
   poetry run black src tests
   poetry run ruff check src tests
   poetry run mypy src
   poetry run pytest
   ```
5. **Commit**: Use conventional commits
   - `feat: Add new query filter`
   - `fix: Handle empty document folders`
   - `docs: Update API reference`
6. **Push** and create a Pull Request

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

### Pull Request Checklist

- [ ] Tests pass locally
- [ ] New tests added for changes
- [ ] Code formatted with Black
- [ ] No Ruff warnings
- [ ] mypy passes
- [ ] Documentation updated
- [ ] Commit messages follow convention

### Code Review

PRs require review before merging. Reviewers check:
- Code quality and style
- Test coverage
- Documentation
- Security considerations
