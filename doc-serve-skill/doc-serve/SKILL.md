---
name: doc-serve
description: |
  This skill should be used when the user wants to search domain-specific documentation
  that has been indexed by the Doc-Serve server. It enriches conversation context with
  relevant information from a specific knowledge domain. Trigger phrases include
  "search the domain X", "look up in domain X", "find in X docs", or "query X documentation"
  where X is the name of the indexed domain (e.g., "python", "kubernetes", "api-docs").
version: 1.0.0
category: ai-tools
triggers:
  - doc-serve
  - search the domain
  - search domain
  - query domain
  - look up in domain
  - find in docs
  - search documentation
  - domain search
  - semantic search
  - RAG query
  - knowledge search
author: Spillwave
license: MIT
tags:
  - documentation
  - semantic-search
  - RAG
  - knowledge-retrieval
  - context-enrichment
  - vector-search
---

# Doc-Serve Domain Search

## Overview

Doc-Serve enables semantic search over indexed documentation to enrich your context with domain-specific knowledge. When a user wants to learn more about a topic within a specific domain, this skill queries the Doc-Serve server to retrieve the most relevant document chunks.

## When to Use This Skill

Use this skill when the user:
- Says "search the domain X" where X is a domain name (e.g., "search the domain kubernetes")
- Wants to find information in pre-indexed documentation
- Needs context from domain-specific knowledge bases
- Asks to "look up", "find", or "query" documentation

## Workflow Decision Tree

```
User Request
    │
    ▼
┌─────────────────────────────────┐
│ Does request mention "search    │
│ the domain X" or similar?       │
└─────────────────────────────────┘
    │
    ├─ Yes ──► Extract domain name and query
    │              │
    │              ▼
    │         Check server health (GET /health)
    │              │
    │              ├─ Healthy ──► Execute query (POST /query)
    │              │                   │
    │              │                   ▼
    │              │              Return results with sources
    │              │
    │              ├─ Indexing ──► Wait or inform user
    │              │
    │              └─ Unhealthy ──► Report server status
    │
    └─ No ──► This skill may not be applicable
```

## Quick Start

### 1. Check Server Health

Before querying, verify the Doc-Serve server is available:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Server is running and ready for queries",
  "version": "1.0.0",
  "timestamp": "2024-12-15T10:00:00Z"
}
```

### 2. Query the Domain

Execute a semantic search:

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how to configure authentication",
    "top_k": 5,
    "similarity_threshold": 0.7
  }'
```

### 3. Interpret Results

Response includes relevant document chunks:
```json
{
  "results": [
    {
      "text": "Authentication can be configured using...",
      "source": "docs/auth/config.md",
      "score": 0.92,
      "chunk_id": "chunk_abc123",
      "metadata": {}
    }
  ],
  "query_time_ms": 45.2,
  "total_results": 1
}
```

## Using the CLI Tool

The `doc-svr-ctl` CLI provides convenient commands:

```bash
# Check server status
doc-svr-ctl status

# Query documents
doc-svr-ctl query "how to configure authentication" --top-k 5

# Get JSON output for programmatic use
doc-svr-ctl query "deployment strategies" --json
```

## API Reference

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Basic health check |
| `/health/status` | GET | Detailed indexing status |

### Query Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | Semantic search |
| `/query/count` | GET | Document count |

### Query Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Search query text |
| `top_k` | integer | 5 | Number of results to return |
| `similarity_threshold` | float | 0.7 | Minimum similarity score (0.0-1.0) |

## Integration Example

When processing a user request like "search the domain kubernetes for pod networking":

1. **Extract domain**: "kubernetes" (identifies the indexed documentation)
2. **Extract query**: "pod networking"
3. **Check health**: Verify server is ready
4. **Execute query**: POST to /query with the search text
5. **Present results**: Format the relevant chunks with sources

### Python Integration

```python
import httpx

def search_domain(query: str, top_k: int = 5) -> dict:
    """Search the indexed domain documentation."""
    base_url = "http://127.0.0.1:8000"

    # Check health first
    health = httpx.get(f"{base_url}/health").json()
    if health["status"] != "healthy":
        return {"error": f"Server not ready: {health['message']}"}

    # Execute query
    response = httpx.post(
        f"{base_url}/query",
        json={
            "query": query,
            "top_k": top_k,
            "similarity_threshold": 0.7
        }
    )

    return response.json()

# Usage
results = search_domain("pod networking configuration")
for result in results.get("results", []):
    print(f"Source: {result['source']}")
    print(f"Score: {result['score']:.2f}")
    print(f"Content: {result['text'][:200]}...")
    print("---")
```

## Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Process results |
| 400 | Invalid query | Check query is not empty |
| 503 | Service unavailable | Wait for indexing to complete |
| 500 | Server error | Check server logs |

## Best Practices

1. **Always check health first** - Ensure the server is ready before querying
2. **Use appropriate top_k** - Start with 5 results, adjust based on needs
3. **Adjust similarity threshold** - Lower for broader results, higher for precision
4. **Cite sources** - Always include the source file in responses to users
5. **Handle empty results** - Inform users when no matching documents are found

## Environment Configuration

Set the server URL via environment variable:

```bash
export DOC_SERVE_URL=http://localhost:8000
```

Or use the default: `http://127.0.0.1:8000`
