# Agent Brain Plugin and Skill Guide

Agent Brain integrates seamlessly with Claude Code through both a plugin and a skill. This guide explains the available commands, proactive agents, and customization options.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Commands Reference](#commands-reference)
- [Search Modes](#search-modes)
- [Server Management](#server-management)
- [Proactive Agents](#proactive-agents)
- [Reference Documentation](#reference-documentation)
- [Customization](#customization)
- [Integration Patterns](#integration-patterns)

---

## Overview

Agent Brain provides two integration points for Claude Code:

| Integration | Location | Purpose |
|-------------|----------|---------|
| **Skill** | `agent-brain-skill/using-agent-brain/SKILL.md` | Natural language instructions for Claude |
| **Plugin** | Installed separately | CLI-based automation |

### When to Use Each

- **Skill**: When you want Claude to search documentation or code on your behalf
- **Plugin**: When you need programmatic access or CI/CD integration

### Key Capabilities

- Document and code search with 5 retrieval modes
- Per-project server management
- Automatic server discovery
- Multi-instance support (multiple projects simultaneously)
- GraphRAG for relationship-aware queries

---

## Installation

### Prerequisites

```bash
# Install Agent Brain packages
pip install agent-brain-rag agent-brain-cli

# Set required API keys
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-..."  # Optional for summarization
```

### Initialize a Project

```bash
cd /path/to/your/project
agent-brain init
```

This creates `.claude/agent-brain/` with configuration files.

### Start the Server

```bash
agent-brain start --daemon
```

The server starts on an automatically-assigned port and writes connection details to `.claude/agent-brain/runtime.json`.

---

## Commands Reference

### Project Management Commands

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Initialize Agent Brain for current project | `agent-brain init` |
| `start` | Start the server for this project | `agent-brain start --daemon` |
| `stop` | Stop the running server | `agent-brain stop` |
| `list` | List all running Agent Brain instances | `agent-brain list` |

### Data Commands

| Command | Description | Example |
|---------|-------------|---------|
| `status` | Check server status and document count | `agent-brain status` |
| `query` | Search indexed documents | `agent-brain query "search term"` |
| `index` | Index documents from a folder | `agent-brain index /path/to/docs` |
| `reset` | Clear all indexed documents | `agent-brain reset --yes` |

### Command Details

#### `agent-brain init`

Initializes Agent Brain for the current project.

```bash
agent-brain init
# Creates: .claude/agent-brain/config.json
```

#### `agent-brain start`

Starts the Agent Brain server.

```bash
# Start in foreground
agent-brain start

# Start in background (daemon mode)
agent-brain start --daemon

# Start on specific port
agent-brain start --port 8080
```

**Flags**:
- `--daemon, -d`: Run in background
- `--port, -p`: Specify port (default: auto-assign)
- `--host, -h`: Bind address (default: 127.0.0.1)

#### `agent-brain stop`

Stops the running server gracefully.

```bash
agent-brain stop
```

#### `agent-brain list`

Lists all running Agent Brain instances across all projects.

```bash
agent-brain list
```

**Example Output**:
```
project-a: http://127.0.0.1:49321 (project mode)
project-b: http://127.0.0.1:49322 (project mode)
```

#### `agent-brain status`

Shows server health and indexing status.

```bash
agent-brain status
```

**Example Output**:
```json
{
  "status": "healthy",
  "total_documents": 150,
  "total_chunks": 1200,
  "total_doc_chunks": 800,
  "total_code_chunks": 400,
  "indexed_folders": ["/path/to/docs"],
  "supported_languages": ["python", "typescript"]
}
```

#### `agent-brain query`

Searches indexed documents.

```bash
# Basic query
agent-brain query "authentication"

# With options
agent-brain query "OAuth implementation" \
  --mode hybrid \
  --top-k 10 \
  --threshold 0.5 \
  --alpha 0.6

# Filter by content type
agent-brain query "database" --source-types code

# Filter by language
agent-brain query "error handling" --languages python,typescript

# JSON output
agent-brain query "api endpoints" --json
```

**Flags**:
| Flag | Default | Description |
|------|---------|-------------|
| `--mode` | hybrid | Search mode: bm25, vector, hybrid, graph, multi |
| `--top-k` | 5 | Number of results to return |
| `--threshold` | 0.7 | Minimum similarity score (0.0-1.0) |
| `--alpha` | 0.5 | Hybrid balance (0=BM25, 1=Vector) |
| `--source-types` | all | Filter: doc, code, or both |
| `--languages` | all | Filter by programming languages |
| `--scores` | false | Display individual component scores |
| `--json` | false | Output as JSON |

#### `agent-brain index`

Indexes documents from a folder.

```bash
# Index documentation only
agent-brain index /path/to/docs

# Index code and documentation
agent-brain index /path/to/project --include-code

# With options
agent-brain index /path/to/project \
  --include-code \
  --languages python,typescript \
  --chunk-size 512 \
  --recursive
```

**Flags**:
| Flag | Default | Description |
|------|---------|-------------|
| `--include-code` | false | Include source code files |
| `--languages` | all | Languages to index (comma-separated) |
| `--chunk-size` | 512 | Chunk size in tokens |
| `--overlap` | 50 | Chunk overlap in tokens |
| `--recursive/--no-recursive` | true | Scan subdirectories |
| `--generate-summaries` | false | Generate LLM summaries for code |

#### `agent-brain reset`

Clears all indexed documents.

```bash
agent-brain reset --yes
```

**Flags**:
- `--yes, -y`: Skip confirmation prompt

---

## Search Modes

Agent Brain supports five search modes, each optimized for different query types:

### BM25 Mode (Keyword)

Best for exact term matching: function names, error codes, technical identifiers.

```bash
agent-brain query "AuthenticationError" --mode bm25
agent-brain query "recursiveCharacterTextSplitter" --mode bm25
```

**Speed**: Fast (10-50ms)

### Vector Mode (Semantic)

Best for conceptual queries and natural language questions.

```bash
agent-brain query "how does caching improve performance" --mode vector
agent-brain query "best practices for error handling" --mode vector
```

**Speed**: Slower (800-1500ms)

### Hybrid Mode (Fusion)

Default mode. Combines BM25 precision with vector semantics.

```bash
agent-brain query "OAuth implementation guide" --mode hybrid
agent-brain query "configure database connection" --mode hybrid --alpha 0.6
```

**Speed**: Slower (1000-1800ms)

**Alpha Parameter**:
- `alpha=1.0`: Pure vector search
- `alpha=0.5`: Balanced (default)
- `alpha=0.0`: Pure BM25 search

### Graph Mode (Relationships)

Best for dependency and relationship queries. Requires GraphRAG enabled.

```bash
agent-brain query "what calls AuthService" --mode graph
agent-brain query "classes that extend BaseController" --mode graph
agent-brain query "modules that import jwt" --mode graph
```

**Speed**: Medium (500-1200ms)

**Enabling GraphRAG**:
```bash
export ENABLE_GRAPH_INDEX=true
agent-brain start --daemon
```

### Multi Mode (Comprehensive)

Combines all three methods with Reciprocal Rank Fusion.

```bash
agent-brain query "complete authentication flow with dependencies" --mode multi
agent-brain query "full overview of data processing pipeline" --mode multi
```

**Speed**: Slowest (1500-2500ms)

---

## Server Management

### Multi-Instance Architecture

Each project runs its own isolated Agent Brain server:

```bash
# Terminal 1: Project A
cd /path/to/project-a
agent-brain start --daemon
# → Started on port 49321

# Terminal 2: Project B
cd /path/to/project-b
agent-brain start --daemon
# → Started on port 49322

# List all instances
agent-brain list
# project-a: http://127.0.0.1:49321 (project mode)
# project-b: http://127.0.0.1:49322 (project mode)
```

### Runtime Discovery

Server details are stored in `.claude/agent-brain/runtime.json`:

```json
{
  "mode": "project",
  "port": 49321,
  "base_url": "http://127.0.0.1:49321",
  "pid": 12345,
  "instance_id": "abc123",
  "project_id": "project-a",
  "started_at": "2026-01-27T10:30:00Z"
}
```

Claude Code reads this file to discover the running server automatically.

### Working from Subdirectories

Agent Brain resolves the project root from any subdirectory:

```bash
cd /path/to/project-a/src/deep/nested
agent-brain status
# → Connects to server for /path/to/project-a
```

### Graceful Shutdown

```bash
agent-brain stop
# → Stops server, cleans up runtime.json
```

---

## Proactive Agents

When the Agent Brain skill is active, Claude Code can proactively use it for relevant tasks:

### Automatic Activation

The skill activates when Claude detects:
- Questions about documentation or code structure
- Requests to "search", "find", or "query" knowledge
- Commands like "agent-brain", "brain search", or "knowledge base search"

### Example Interactions

**User**: "How does authentication work in this project?"

**Claude** (with skill):
1. Detects documentation query
2. Runs `agent-brain query "authentication" --mode hybrid`
3. Synthesizes answer from results

**User**: "What functions call the UserService?"

**Claude** (with skill):
1. Detects relationship query
2. Runs `agent-brain query "calls UserService" --mode graph`
3. Returns list of callers

---

## Reference Documentation

The skill includes detailed reference guides:

| Guide | Description | Path |
|-------|-------------|------|
| BM25 Search | Keyword matching for technical queries | `references/bm25-search-guide.md` |
| Vector Search | Semantic similarity for concepts | `references/vector-search-guide.md` |
| Hybrid Search | Combined keyword and semantic | `references/hybrid-search-guide.md` |
| Graph Search | Knowledge graph queries | `references/graph-search-guide.md` |
| Server Discovery | Auto-discovery and multi-agent | `references/server-discovery.md` |
| Integration Guide | Scripts, Python API, CI/CD | `references/integration-guide.md` |
| API Reference | REST endpoint documentation | `references/api_reference.md` |
| Troubleshooting | Common issues and solutions | `references/troubleshooting-guide.md` |

---

## Customization

### Environment Variables

Configure Agent Brain behavior via environment variables:

```bash
# API Keys (required)
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Server Configuration
export API_HOST="127.0.0.1"
export API_PORT="8000"
export DEBUG="false"

# Embedding Configuration
export EMBEDDING_MODEL="text-embedding-3-large"
export EMBEDDING_DIMENSIONS="3072"

# GraphRAG Configuration
export ENABLE_GRAPH_INDEX="true"
export GRAPH_STORE_TYPE="simple"
export GRAPH_TRAVERSAL_DEPTH="2"
```

### Project Configuration

Customize per-project settings in `.claude/agent-brain/config.json`:

```json
{
  "default_mode": "hybrid",
  "default_top_k": 10,
  "default_threshold": 0.5,
  "include_code": true,
  "languages": ["python", "typescript"],
  "exclude_patterns": ["node_modules/**", "__pycache__/**"]
}
```

### Skill Customization

Modify the skill's behavior in `SKILL.md`:

```yaml
---
name: using-agent-brain
description: |
  Agent Brain document search with...
license: MIT
metadata:
  version: 1.4.0
---
```

---

## Integration Patterns

### CI/CD Integration

Use Agent Brain in CI/CD pipelines for documentation validation:

```yaml
# .github/workflows/docs-check.yml
jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Agent Brain
        run: pip install agent-brain-rag agent-brain-cli

      - name: Start Server
        run: agent-brain start --daemon

      - name: Index Documentation
        run: agent-brain index ./docs

      - name: Validate Links
        run: |
          agent-brain query "broken link" --mode bm25 --json | \
          jq '.results | length == 0'
```

### Python API

Access Agent Brain programmatically:

```python
import httpx

# Discover server from runtime.json
import json
from pathlib import Path

runtime_path = Path(".claude/agent-brain/runtime.json")
runtime = json.loads(runtime_path.read_text())
base_url = runtime["base_url"]

# Query documents
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{base_url}/query",
        json={
            "query": "authentication",
            "mode": "hybrid",
            "top_k": 5,
        }
    )
    results = response.json()
    for result in results["results"]:
        print(f"{result['source']}: {result['score']:.2f}")
```

### Shell Scripts

Automate common workflows:

```bash
#!/bin/bash
# index-and-search.sh

# Ensure server is running
agent-brain status || agent-brain start --daemon

# Index project
agent-brain index . --include-code

# Search for common issues
agent-brain query "TODO" --mode bm25 --json | jq '.results[] | .source'
```

---

## Troubleshooting

### "Server not running"

```bash
# Check status
agent-brain status

# If not running, start it
agent-brain start --daemon
```

### "No results found"

1. Check indexing: `agent-brain status` should show documents
2. Lower threshold: `--threshold 0.3`
3. Try different mode: `--mode bm25` for exact terms

### "GraphRAG not enabled"

```bash
# Enable GraphRAG
export ENABLE_GRAPH_INDEX=true

# Restart server
agent-brain stop
agent-brain start --daemon

# Re-index
agent-brain index /path/to/project
```

### "Port already in use"

```bash
# List running instances
agent-brain list

# Stop existing instance
agent-brain stop

# Start with auto-port
agent-brain start --daemon --port 0
```

---

## Next Steps

- [Architecture Overview](ARCHITECTURE.md) - System design and components
- [GraphRAG Integration](GRAPHRAG_GUIDE.md) - Knowledge graph features
- [Code Indexing](CODE_INDEXING.md) - AST-aware chunking
- [API Reference](API_REFERENCE.md) - REST API documentation
