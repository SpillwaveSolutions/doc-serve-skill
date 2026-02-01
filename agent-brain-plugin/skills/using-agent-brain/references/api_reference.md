# Agent Brain API Reference

## Base URL Discovery

Agent Brain uses per-project server instances. Discover the URL from:

**Runtime file (recommended):**
```bash
cat .claude/agent-brain/runtime.json | jq -r '.base_url'
# Example: http://127.0.0.1:54321
```

**Environment variable:**
```bash
export DOC_SERVE_URL="http://127.0.0.1:54321"
```

**Default (single instance):** `http://127.0.0.1:8000`

---

## Health Endpoints

### GET /health

Check server health status.

**Response:**

```json
{
  "status": "healthy | indexing | degraded | unhealthy",
  "message": "Server is running and ready for queries",
  "version": "1.0.0",
  "timestamp": "2024-12-15T10:00:00Z"
}
```

**Status Values:**
| Status | Description |
|--------|-------------|
| `healthy` | Server ready for queries |
| `indexing` | Indexing in progress, queries may fail |
| `degraded` | Server up but some services unavailable |
| `unhealthy` | Server not operational |

---

### GET /health/status

Get detailed indexing status.

**Response:**

```json
{
  "total_documents": 100,
  "total_chunks": 500,
  "indexing_in_progress": false,
  "current_job_id": null,
  "progress_percent": 0.0,
  "last_indexed_at": "2024-12-15T10:00:00Z",
  "indexed_folders": ["/docs/kubernetes", "/docs/python"]
}
```

---

## Query Endpoints

### POST /query

Execute a semantic search on indexed documents.

**Request Body:**

```json
{
  "query": "how to configure pod networking",
  "top_k": 5,
  "similarity_threshold": 0.7,
  "mode": "hybrid",
  "alpha": 0.5
}
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query text |
| `top_k` | integer | No | 5 | Number of results (1-100) |
| `similarity_threshold` | float | No | 0.7 | Minimum similarity (0.0-1.0) |
| `mode` | string | No | hybrid | Retrieval mode: `vector`, `bm25`, `hybrid` |
| `alpha` | float | No | 0.5 | Hybrid weight (1.0=vector, 0.0=bm25) |

**Response:**

```json
{
  "results": [
    {
      "text": "Pod networking in Kubernetes allows...",
      "source": "docs/kubernetes/networking.md",
      "score": 0.92,
      "vector_score": 0.92,
      "bm25_score": 0.85,
      "chunk_id": "chunk_abc123",
      "metadata": {
        "page": 1,
        "section": "Pod Networking"
      }
    }
  ],
  "query_time_ms": 45.2,
  "total_results": 1
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| 400 | Query is empty or invalid |
| 503 | Index not ready (indexing in progress) |
| 500 | Internal server error |

---

### GET /query/count

Get the total number of indexed document chunks.

**Response:**

```json
{
  "total_chunks": 500,
  "ready": true
}
```

---

## Index Endpoints

### POST /index

Start indexing documents from a folder. Uses stable IDs based on file paths, so re-indexing updates existing records (upsert).

**Request Body:**

```json
{
  "folder_path": "/path/to/documents",
  "recursive": true,
  "chunk_size": 512,
  "chunk_overlap": 50
}
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `folder_path` | string | Yes | - | Absolute or relative path to documents |
| `recursive` | boolean | No | true | Include subdirectories |
| `chunk_size` | integer | No | 512 | Target tokens per chunk |
| `chunk_overlap` | integer | No | 50 | Overlap between chunks |

**Response:**

```json
{
  "job_id": "idx_123456",
  "status": "started",
  "message": "Indexing started for /path/to/documents"
}
```

---

### POST /index/add

Add documents incrementally without clearing existing index.

**Request Body:**

```json
{
  "folder_path": "/path/to/more/documents",
  "recursive": true
}
```

---

### DELETE /index

Clear all indexed documents.

**Response:**

```json
{
  "job_id": "reset",
  "status": "completed",
  "message": "Index cleared successfully"
}
```

---

## CLI Commands Reference

The `agent-brain` CLI provides these commands:

### Status Commands
```bash
agent-brain status           # Check server health
agent-brain status --json    # JSON output
agent-brain list             # List all running instances
```

### Query Commands
```bash
agent-brain query "search text"
agent-brain query "search text" --mode bm25
agent-brain query "search text" --mode vector
agent-brain query "search text" --mode hybrid --alpha 0.6
agent-brain query "search text" --top-k 10 --threshold 0.5
agent-brain query "search text" --json
agent-brain query "search text" --scores
```

### Index Commands
```bash
agent-brain index /path/to/docs
agent-brain index /path/to/docs --recursive
agent-brain index /path/to/docs --include-code
agent-brain reset --yes
```

### Server Commands
```bash
agent-brain init             # Initialize project
agent-brain start --daemon   # Start server
agent-brain stop             # Stop server
```

**Global Options:**
- `--url URL` - Server URL (default: from runtime.json or http://127.0.0.1:8000)
- `--json` - Output as JSON
- `--help` - Show help message

---

## OpenAPI Documentation

Interactive API documentation available when server is running:

| Endpoint | Description |
|----------|-------------|
| `/docs` | Swagger UI |
| `/redoc` | ReDoc documentation |
| `/openapi.json` | OpenAPI specification |

---

## Code Search Parameters

When code is indexed with `--include-code`:

### Source Type Filtering
```bash
agent-brain query "database" --source-types doc      # Docs only
agent-brain query "database" --source-types code     # Code only
agent-brain query "database"                         # Both (default)
```

### Language Filtering
```bash
agent-brain query "error handling" --languages python
agent-brain query "API endpoints" --languages python,typescript
```

**Supported Languages:** Python, TypeScript, JavaScript, Java, Go, Rust, C, C++, C#
