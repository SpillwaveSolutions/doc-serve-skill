# Doc-Serve User Guide

This guide covers how to use Doc-Serve for document indexing and semantic search using the command-line interface.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Server Management](#server-management)
- [Indexing Documents](#indexing-documents)
- [Querying Knowledge](#querying-knowledge)
- [Advanced CLI Usage](#advanced-cli-usage)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Doc-Serve is a RAG (Retrieval-Augmented Generation) system. It works in three phases:
1. **Indexing**: It reads your documents, splits them into semantic chunks, and generates vector embeddings.
2. **Storage**: Chunks and embeddings are stored in a ChromaDB vector database.
3. **Retrieval**: When you query, it finds the most similar chunks based on semantic meaning, not just keyword matches.

## Server Management

The Doc-Serve server must be running to handle indexing and query requests.

### Starting the Server
```bash
doc-serve
```
By default, the server binds to `127.0.0.1:8000`. You can change this using options:
- `--host`: Bind address (e.g., `0.0.0.0`)
- `--port`: Port number (e.g., `8080`)
- `--reload`: Enable auto-reload for development

### Checking Server Health
Use the management tool to check if the server is responsive:
```bash
doc-svr-ctl status
```

## Indexing Documents

Before you can query, you must index one or more folders containing your documentation.

### Basic Indexing
```bash
doc-svr-ctl index /path/to/your/docs
```

### Advanced Indexing Options
- `--recursive` / `--no-recursive`: Whether to scan subdirectories (default: true).
- `--chunk-size`: Size of text chunks in tokens (default: 512).
- `--overlap`: Overlap between chunks (default: 50).

### Resetting the Index
If you want to start over and clear all indexed data:
```bash
doc-svr-ctl reset --yes
```

## Querying Knowledge

Once indexed, you can perform semantic searches.

### Basic Query
```bash
doc-svr-ctl query "how do I configure the system?"
```

### Refining Results
- `--top-k N`: Return top N results (default: 5).
- `--threshold F`: Minimum similarity score between 0.0 and 1.0 (default: 0.7). Lower this if you get no results.

### Programmatic Output
Use the `--json` flag to get raw data for piping into other tools like `jq`:
```bash
doc-svr-ctl query "api endpoints" --json | jq .results[0].text
```

## Troubleshooting

### Connection Error
If you see `Connection Error: Unable to connect to server`, ensure:
1. The `doc-serve` process is running.
2. You are using the correct URL (default `http://127.0.0.1:8000`).
3. If the server is on a different port, use `doc-svr-ctl --url http://127.0.0.1:PORT status`.

### No Results Found
If queries return no results:
1. Run `doc-svr-ctl status` to check the "Total Chunks" count. If 0, indexing failed or hasn't run.
2. Lower the `--threshold` (try `0.3` or `0.2`).
3. Ensure the documents you indexed contain relevant text and are in supported formats (.md, .txt, .pdf).

### Duplicated Results
If you see identical results, the stable ID logic ensures that re-indexing the same files updates existing entries. If you have moved files or indexed different paths to the same data, run `doc-svr-ctl reset --yes` and re-index.
