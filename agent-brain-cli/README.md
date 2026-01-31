# Agent Brain CLI

Command-line interface for managing AI agent memory and knowledge retrieval with the Agent Brain RAG server.

## Installation

```bash
pip install agent-brain-cli
```

## Quick Start

```bash
agent-brain init          # Initialize project
agent-brain start         # Start server
agent-brain index ./docs  # Index documents
agent-brain query "search term"
```

> **Note**: The legacy command `doc-svr-ctl` is still available but deprecated. Please use `agent-brain` for new installations.

## Development Installation

```bash
cd agent-brain-cli
poetry install
```

## Usage

```bash
# Check server status
agent-brain status

# Search documents
agent-brain query "how to use python"

# Index documents from a folder
agent-brain index ./docs

# Reset/clear the index
agent-brain reset --yes
```

## Configuration

Set the server URL via environment variable:

```bash
export AGENT_BRAIN_URL=http://localhost:8000
```

Or use the `--url` flag:

```bash
agent-brain --url http://localhost:8000 status
```

> **Note**: The legacy environment variable `DOC_SERVE_URL` is still supported for backwards compatibility.

## Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize project for Agent Brain |
| `start` | Start the Agent Brain server |
| `stop` | Stop the running server |
| `list` | List all running Agent Brain instances |
| `status` | Check server health and indexing status |
| `query` | Search indexed documents |
| `index` | Start indexing documents from a folder |
| `reset` | Clear all indexed documents |

## Options

All commands support:
- `--url` - Server URL (or `AGENT_BRAIN_URL` / `DOC_SERVE_URL` env var)
- `--json` - Output as JSON for scripting
