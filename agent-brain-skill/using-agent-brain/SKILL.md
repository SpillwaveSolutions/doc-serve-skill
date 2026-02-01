---
name: using-agent-brain
description: |
  Agent Brain document search with BM25 keyword, semantic vector, hybrid, graph, and multi retrieval modes.
  Use when asked to "search documentation", "query domain", "find in docs",
  "bm25 search", "hybrid search", "semantic search", "graph search", "multi search",
  "find dependencies", "code relationships", "agent-brain init",
  "agent-brain start", "agent-brain stop", "agent-brain status",
  "agent brain", "brain search", "brain query", or "knowledge base search".
  Supports multi-instance architecture with automatic server discovery.
  GraphRAG mode enables relationship-aware queries for code dependencies and entity connections.
license: MIT
metadata:
  version: 1.4.0
  category: ai-tools
  author: Spillwave
---

# Agent Brain Skill

Document search with five modes: BM25 (keyword), Vector (semantic), Hybrid (fusion), Graph (knowledge graph), and Multi (comprehensive fusion). Supports multi-instance architecture with per-project isolation and automatic server discovery.

## Contents

- [Quick Start](#quick-start)
- [Search Modes](#search-modes)
- [Server Management](#server-management)
- [Best Practices](#best-practices)
- [Reference Documentation](#reference-documentation)

---

## Quick Start

```bash
# 1. Initialize project (first time only)
agent-brain init

# 2. Start server with auto-port
agent-brain start --daemon

# 3. Index documents
agent-brain index /path/to/docs

# 4. Search
agent-brain query "search term" --mode hybrid

# 5. Stop when done
agent-brain stop
```

### Validation Checklist

Before querying, verify:
- [ ] Server running: `agent-brain status` shows healthy
- [ ] Documents indexed: status shows document count > 0
- [ ] API key set: `OPENAI_API_KEY` for vector/hybrid modes

---

## Search Modes

| Mode | Speed | Use For | Example |
|------|-------|---------|---------|
| `bm25` | Fast (10-50ms) | Technical terms, function names, error codes | `"AuthenticationError"` |
| `vector` | Slower (800-1500ms) | Concepts, explanations | `"how authentication works"` |
| `hybrid` | Slower (1000-1800ms) | Comprehensive results | `"OAuth implementation guide"` |
| `graph` | Medium (500-1200ms) | Relationships, dependencies, entity connections | `"what calls AuthService"` |
| `multi` | Slowest (1500-2500ms) | Most comprehensive with entity relationships | `"complete auth flow with dependencies"` |

### Mode Selection

```bash
# Technical terms → BM25
agent-brain query "recursiveCharacterTextSplitter" --mode bm25

# Concepts → Vector
agent-brain query "best practices for error handling" --mode vector

# Comprehensive → Hybrid (default)
agent-brain query "complete OAuth implementation" --mode hybrid --alpha 0.6

# Relationships → Graph (requires ENABLE_GRAPH_INDEX=true)
agent-brain query "what functions call AuthService" --mode graph

# Everything → Multi (combines all modes with RRF)
agent-brain query "complete auth implementation with all dependencies" --mode multi
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--mode` | hybrid | Search mode: bm25, vector, hybrid, graph, multi |
| `--threshold` | 0.7 | Minimum similarity (0.0-1.0) |
| `--top-k` | 5 | Number of results |
| `--alpha` | 0.5 | Hybrid balance (0=BM25, 1=Vector) |
| `--traversal-depth` | 2 | Graph traversal depth for graph/multi modes |
| `--include-relationships` | false | Include entity relationships in results |

---

## GraphRAG (Knowledge Graph Search)

GraphRAG enables relationship-aware retrieval by building a knowledge graph from your documents. It extracts entities (functions, classes, modules) and their relationships (calls, imports, inherits).

### Enabling GraphRAG

GraphRAG requires explicit enablement during server startup:

```bash
# Enable graph indexing
export ENABLE_GRAPH_INDEX=true
agent-brain start --daemon

# Or in .env file
ENABLE_GRAPH_INDEX=true
GRAPH_STORE_TYPE=simple  # or 'kuzu' for production
```

### When to Use Graph Mode

**Choose `graph` mode when:**
- Exploring code dependencies ("what calls this function?")
- Understanding inheritance hierarchies
- Finding import relationships
- Tracing data flow through modules

**Choose `multi` mode when:**
- Need the most comprehensive results
- Want both content matches AND relationship context
- Investigating complex code paths

### Graph Query Examples

```bash
# Find what calls a specific function
agent-brain query "what functions call process_payment" --mode graph

# Explore class inheritance
agent-brain query "classes that inherit from BaseService" --mode graph --traversal-depth 3

# Find module dependencies
agent-brain query "modules that import authentication" --mode graph

# Comprehensive search with relationships
agent-brain query "complete payment flow implementation" --mode multi --include-relationships
```

See [Graph Search Guide](references/graph-search-guide.md) for detailed usage.

---

## Server Management

### Lifecycle Commands

```bash
agent-brain init           # Initialize project config
agent-brain start --daemon # Start with auto-port
agent-brain status         # Show port, mode, document count
agent-brain list           # List all running instances
agent-brain stop           # Graceful shutdown
```

### Multi-Instance

Each project runs its own isolated instance. Server details stored in `.claude/agent-brain/runtime.json`. Multiple Claude agents in the same project share one instance automatically.

See [Server Discovery Guide](references/server-discovery.md) for implementation details.

---

## Best Practices

1. **Mode Selection**: BM25 for exact terms, Vector for concepts, Hybrid for comprehensive, Graph for relationships, Multi for everything
2. **Threshold Tuning**: Start at 0.7, lower to 0.3-0.5 for more results
3. **Server Discovery**: Use `runtime.json` rather than assuming port 8000
4. **Resource Cleanup**: Run `agent-brain stop` when done
5. **Source Citation**: Always reference source filenames in responses
6. **Graph Queries**: Use graph mode for "what calls X", "what imports Y", dependency exploration
7. **Traversal Depth**: Start with depth 2, increase to 3-4 for deeper relationship chains

---

## Reference Documentation

| Guide | Description |
|-------|-------------|
| [BM25 Search](references/bm25-search-guide.md) | Keyword matching for technical queries |
| [Vector Search](references/vector-search-guide.md) | Semantic similarity for concepts |
| [Hybrid Search](references/hybrid-search-guide.md) | Combined keyword and semantic search |
| [Graph Search](references/graph-search-guide.md) | Knowledge graph and relationship queries |
| [Server Discovery](references/server-discovery.md) | Auto-discovery, multi-agent sharing |
| [Integration Guide](references/integration-guide.md) | Scripts, Python API, CI/CD patterns |
| [API Reference](references/api_reference.md) | REST endpoint documentation |
| [Troubleshooting](references/troubleshooting-guide.md) | Common issues and solutions |

---

## Configuration

### Required Environment Variables

```bash
export OPENAI_API_KEY="sk-proj-..."    # Required for vector/hybrid/graph/multi
export ANTHROPIC_API_KEY="sk-ant-..."  # Optional for summarization
```

### GraphRAG Environment Variables

```bash
export ENABLE_GRAPH_INDEX=true         # Enable knowledge graph indexing
export GRAPH_STORE_TYPE=simple         # Graph store: 'simple' or 'kuzu'
export GRAPH_TRAVERSAL_DEPTH=2         # Default traversal depth
export GRAPH_EXTRACTION_MODEL=gpt-4o-mini  # Model for entity extraction
```

### Installation

```bash
pip install agent-brain-rag agent-brain-cli
```

---

## Limitations

- Vector/hybrid/graph/multi modes require OpenAI API credits
- Graph mode requires additional memory for knowledge graph storage
- Supports: Markdown, PDF, plain text, code files
- Does not support: Word docs, images
- Server requires ~500MB RAM for typical collections (~1GB with graph enabled)
