---
name: using-agent-brain
description: |
  Agent Brain document search with BM25 keyword, semantic vector, and hybrid retrieval modes.
  Use when asked to "search documentation", "query domain", "find in docs",
  "bm25 search", "hybrid search", "semantic search", "agent-brain query",
  "brain search", "brain query", or "knowledge base search".
  Supports multi-instance architecture with automatic server discovery.
license: MIT
metadata:
  version: 1.3.0
  category: ai-tools
  author: Spillwave
---

# Agent Brain Search Skill

Document search with three modes: BM25 (keyword), Vector (semantic), and Hybrid (fusion). Supports multi-instance architecture with per-project isolation and automatic server discovery.

## Contents

- [Quick Start](#quick-start)
- [Search Modes](#search-modes)
- [Server Discovery](#server-discovery)
- [Best Practices](#best-practices)
- [Reference Documentation](#reference-documentation)

---

## Quick Start

```bash
# 1. Check server is running
agent-brain status

# 2. Search with default hybrid mode
agent-brain query "search term" --mode hybrid

# 3. Search with specific mode
agent-brain query "AuthenticationError" --mode bm25      # Technical terms
agent-brain query "how does auth work" --mode vector     # Concepts
```

### Pre-Search Checklist

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

### Mode Selection Guide

```bash
# Technical terms -> BM25
agent-brain query "recursiveCharacterTextSplitter" --mode bm25

# Concepts -> Vector
agent-brain query "best practices for error handling" --mode vector

# Comprehensive -> Hybrid (default)
agent-brain query "complete OAuth implementation" --mode hybrid --alpha 0.6
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--mode` | hybrid | Search mode: bm25, vector, hybrid |
| `--threshold` | 0.7 | Minimum similarity (0.0-1.0) |
| `--top-k` | 5 | Number of results |
| `--alpha` | 0.5 | Hybrid balance (0=BM25, 1=Vector) |
| `--scores` | false | Show individual BM25/vector scores |

### Alpha Tuning (Hybrid Mode)

The `--alpha` parameter controls the balance between vector and BM25 search:

- `alpha = 1.0`: 100% vector (pure semantic)
- `alpha = 0.8`: 80% vector, 20% BM25 (mostly semantic)
- `alpha = 0.5`: 50% each (balanced - recommended default)
- `alpha = 0.3`: 30% vector, 70% BM25 (mostly keyword)
- `alpha = 0.0`: 100% BM25 (pure keyword)

**Recommendations by content type:**
- Technical docs: `alpha = 0.3-0.4` (favor exact terms)
- Conceptual guides: `alpha = 0.7-0.8` (favor meaning)
- Mixed content: `alpha = 0.5` (balanced)

---

## Server Discovery

Agent Brain uses per-project server instances. The server URL is discovered from:

1. `.claude/agent-brain/runtime.json` (project-specific)
2. `DOC_SERVE_URL` environment variable
3. Default: `http://127.0.0.1:8000`

### Runtime File Format

```json
{
  "mode": "project",
  "port": 49321,
  "base_url": "http://127.0.0.1:49321",
  "pid": 12345,
  "project_id": "my-project",
  "started_at": "2026-01-27T10:30:00Z"
}
```

### Server Commands

```bash
agent-brain init           # Initialize project config
agent-brain start --daemon # Start with auto-port
agent-brain status         # Show port, mode, document count
agent-brain list           # List all running instances
agent-brain stop           # Graceful shutdown
```

---

## Best Practices

1. **Mode Selection**: BM25 for exact terms, Vector for concepts, Hybrid for comprehensive
2. **Threshold Tuning**: Start at 0.7, lower to 0.3-0.5 for more results
3. **Server Discovery**: Use `runtime.json` rather than assuming port 8000
4. **Resource Cleanup**: Run `agent-brain stop` when done
5. **Source Citation**: Always reference source filenames in responses
6. **Index First**: Ensure documents are indexed before searching

---

## Reference Documentation

| Guide | Description |
|-------|-------------|
| [Hybrid Search Guide](references/hybrid-search-guide.md) | Combined keyword and semantic search |
| [BM25 Search Guide](references/bm25-search-guide.md) | Keyword matching for technical queries |
| [Vector Search Guide](references/vector-search-guide.md) | Semantic similarity for concepts |
| [API Reference](references/api_reference.md) | REST endpoint documentation |

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
