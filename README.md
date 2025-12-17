# Doc-Serve

A RAG-based (Retrieval-Augmented Generation) document indexing and semantic search system. Doc-Serve enables AI assistants and applications to query domain-specific documentation using natural language.

## Overview

Doc-Serve is a monorepo containing three packages:

| Package | Description |
|---------|-------------|
| **doc-serve-server** | FastAPI REST API for document indexing and semantic search |
| **doc-svr-ctl** | Command-line interface for managing the server |
| **doc-serve-skill** | Claude Code skill for AI-powered documentation queries |

## Features

- **Semantic Search**: Query documents using natural language with OpenAI embeddings
- **Vector Store**: ChromaDB for efficient similarity search
- **Context-Aware Chunking**: Intelligent document splitting with overlap
- **REST API**: Full OpenAPI-documented REST interface
- **CLI Tool**: Comprehensive command-line management
- **Claude Integration**: Native Claude Code skill for AI workflows

## Quick Start

### Prerequisites

- Python 3.10+
- Poetry (dependency management)
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/spillwave/doc-serve.git
cd doc-serve

# Install the server
cd doc-serve-server
poetry install

# Install the CLI (optional, in another terminal)
cd ../doc-svr-ctl
poetry install
```

### Configuration

Create a `.env` file in `doc-serve-server/`:

```bash
OPENAI_API_KEY=your-openai-api-key
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=false
```

### Running the Server

```bash
cd doc-serve-server
poetry run doc-serve
```

The server starts at `http://127.0.0.1:8000` with interactive docs at `/docs`.

### Using the CLI

```bash
# Check server status
doc-svr-ctl status

# Index documents
doc-svr-ctl index /path/to/documents

# Query the index
doc-svr-ctl query "how to configure authentication"

# Reset the index
doc-svr-ctl reset --yes
```

## Architecture

```
doc-serve/
├── doc-serve-server/     # FastAPI server
│   └── src/
│       ├── api/          # REST endpoints
│       ├── config/       # Settings management
│       ├── indexing/     # Document processing
│       ├── models/       # Pydantic models
│       ├── services/     # Business logic
│       └── storage/      # Vector store
├── doc-svr-ctl/          # CLI tool
│   └── src/
│       ├── client/       # API client
│       └── commands/     # CLI commands
├── doc-serve-skill/      # Claude skill
│   └── doc-serve/
│       └── SKILL.md      # Skill definition
└── docs/                 # Documentation
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/health/status` | GET | Detailed indexing status |
| `/query` | POST | Semantic search |
| `/query/count` | GET | Document count |
| `/index` | POST | Start indexing |
| `/index/add` | POST | Add documents incrementally |
| `/index` | DELETE | Clear index |

## Documentation

- [User Guide](docs/USER_GUIDE.md) - How to use Doc-Serve
- [Developer Guide](docs/DEVELOPERS_GUIDE.md) - Setup and contribution guide
- [API Reference](doc-serve-skill/doc-serve/references/api_reference.md) - Full API documentation
- [Original Spec](docs/ORIGINAL_SPEC.md) - Original project specification

## Technology Stack

- **Server**: FastAPI + Uvicorn
- **Vector Store**: ChromaDB
- **Embeddings**: OpenAI text-embedding-3-large
- **Indexing**: LlamaIndex
- **CLI**: Click + Rich
- **Build System**: Poetry

## License

MIT License - see LICENSE file for details.

## Contributing

See the [Developer Guide](docs/DEVELOPERS_GUIDE.md) for setup instructions and contribution guidelines.
