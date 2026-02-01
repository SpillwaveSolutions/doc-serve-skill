# Quickstart: CLI Entry Points Installation

**Feature**: 003-cli-entrypoints
**Prerequisites**: Python 3.10+, pip or Poetry

## Overview

This guide shows how to install the Agent Brain CLI tools so they're available directly from your terminal.

## Installation Options

### Option 1: Using pip (Recommended for most users)

```bash
# From the project root directory

# Install agent-brain (CLI tool)
pip install -e ./agent-brain

# Install agent-brain-server (API server)
pip install -e ./agent-brain-server
```

### Option 2: Using Poetry (For development)

```bash
# Install agent-brain
cd agent-brain
poetry install
cd ..

# Install agent-brain-server
cd agent-brain-server
poetry install
cd ..
```

## Verification

After installation, verify the commands are available:

```bash
# Check agent-brain
agent-brain --help
agent-brain --version

# Check agent-brain-serve (starts the server)
agent-brain-serve
# Press Ctrl+C to stop
```

## Available Commands

### agent-brain

```bash
agent-brain status              # Check server health
agent-brain query "your query"  # Search indexed documents
agent-brain index ./docs        # Index documents from a directory
agent-brain reset --yes         # Clear all indexed documents
```

### agent-brain-serve

```bash
agent-brain-serve                       # Start the API server
# Server runs at http://127.0.0.1:8000 by default
# API docs at http://127.0.0.1:8000/docs
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOC_SERVE_URL` | `http://127.0.0.1:8000` | Server URL for CLI |
| `API_HOST` | `127.0.0.1` | Server bind host |
| `API_PORT` | `8000` | Server bind port |
| `DEBUG` | `false` | Enable debug mode |

## Troubleshooting

### Command not found after installation

Ensure your Python environment's `bin` directory is in your PATH:

```bash
# Check where pip installs scripts
pip show agent-brain | grep Location

# Or use pip's script location directly
python -m site --user-base
# Add {output}/bin to your PATH
```

### Poetry environment not activated

If using Poetry, either activate the environment or use `poetry run`:

```bash
# Option 1: Activate environment
poetry shell
agent-brain --help

# Option 2: Use poetry run
poetry run agent-brain --help
```

### Server won't start - port in use

```bash
# Check what's using port 8000
lsof -i :8000

# Use a different port
API_PORT=8001 agent-brain-serve
```
