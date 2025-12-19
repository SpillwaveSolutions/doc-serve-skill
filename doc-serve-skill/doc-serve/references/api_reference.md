# Doc-Serve API Reference

## Base URL

```
http://127.0.0.1:8000
```

Configure via environment variable: `DOC_SERVE_URL`

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
- `healthy` - Server ready for queries
- `indexing` - Indexing in progress, queries may fail
- `degraded` - Server up but some services unavailable
- `unhealthy` - Server not operational

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
| `mode` | string | No | hybrid | Retrieval mode (`vector`, `bm25`, `hybrid`) |
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

Start indexing documents from a folder. The system uses stable IDs based on file paths and chunk indices, meaning re-indexing the same folder will update existing records (upsert) rather than creating duplicates.

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

## OpenAPI Documentation

Interactive API documentation available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

---

## CLI Commands Reference

The `doc-svr-ctl` CLI provides these commands:

```bash
# Check server health and status
doc-svr-ctl status
doc-svr-ctl status --json

# Query documents
doc-svr-ctl query "search text"
doc-svr-ctl query "search text" --top-k 10
doc-svr-ctl query "search text" --json

# Index documents
doc-svr-ctl index /path/to/docs
doc-svr-ctl index /path/to/docs --recursive

# Clear index
doc-svr-ctl reset --yes
```

**Global Options:**
- `--url URL` - Server URL (default: http://127.0.0.1:8000)
- `--json` - Output as JSON
- `--help` - Show help message
