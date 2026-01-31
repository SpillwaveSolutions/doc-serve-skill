---
name: using-agent-brain
description: |
  Agent Brain document search with BM25 keyword, semantic vector, and hybrid retrieval modes.
  Use when asked to "search documentation", "query domain", "find in docs",
  "bm25 search", "hybrid search", "semantic search", "agent-brain init",
  "agent-brain start", "agent-brain stop", "agent-brain status",
  "agent brain", "brain search", "brain query", or "knowledge base search".
  Supports multi-instance architecture with automatic server discovery.
license: MIT
metadata:
  version: 1.3.0
  category: ai-tools
  author: Spillwave
---

# Agent Brain Skill

Document search with three modes: BM25 (keyword), Vector (semantic), and Hybrid (fusion). Supports multi-instance architecture with per-project isolation and automatic server discovery.

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

### Mode Selection

```bash
# Technical terms → BM25
agent-brain query "recursiveCharacterTextSplitter" --mode bm25

# Concepts → Vector
agent-brain query "best practices for error handling" --mode vector

# Comprehensive → Hybrid (default)
agent-brain query "complete OAuth implementation" --mode hybrid --alpha 0.6
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--mode` | hybrid | Search mode: bm25, vector, hybrid |
| `--threshold` | 0.7 | Minimum similarity (0.0-1.0) |
| `--top-k` | 5 | Number of results |
| `--alpha` | 0.5 | Hybrid balance (0=BM25, 1=Vector) |

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

1. **Mode Selection**: BM25 for exact terms, Vector for concepts, Hybrid for comprehensive
2. **Threshold Tuning**: Start at 0.7, lower to 0.3-0.5 for more results
3. **Server Discovery**: Use `runtime.json` rather than assuming port 8000
4. **Resource Cleanup**: Run `agent-brain stop` when done
5. **Source Citation**: Always reference source filenames in responses

---

## Reference Documentation

| Guide | Description |
|-------|-------------|
| [BM25 Search](references/bm25-search-guide.md) | Keyword matching for technical queries |
| [Vector Search](references/vector-search-guide.md) | Semantic similarity for concepts |
| [Hybrid Search](references/hybrid-search-guide.md) | Combined keyword and semantic search |
| [Server Discovery](references/server-discovery.md) | Auto-discovery, multi-agent sharing |
| [Integration Guide](references/integration-guide.md) | Scripts, Python API, CI/CD patterns |
| [API Reference](references/api_reference.md) | REST endpoint documentation |
| [Troubleshooting](references/troubleshooting-guide.md) | Common issues and solutions |

---

## Configuration

### Required Environment Variables

```bash
export OPENAI_API_KEY="sk-proj-..."    # Required for vector/hybrid
export ANTHROPIC_API_KEY="sk-ant-..."  # Optional for summarization
```

### Installation

```bash
pip install agent-brain-rag agent-brain-cli
```

---

## Limitations

- Vector/hybrid modes require OpenAI API credits
- Supports: Markdown, PDF, plain text, code files
- Does not support: Word docs, images
- Server requires ~500MB RAM for typical collections
