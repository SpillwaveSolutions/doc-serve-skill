---
name: doc-serve
description: |
  Semantic search over indexed documentation. This skill enriches the conversation context with
  relevant information from specific knowledge domains. It can automatically set up the server,
  index local folders, and perform semantic queries using CLI tools.
version: 1.1.0
category: ai-tools
triggers:
  - doc-serve
  - search the domain
  - search domain
  - query domain
  - look up in domain
  - find in docs
  - search documentation
author: Spillwave
license: MIT
---

# Doc-Serve Skill

## Overview

`doc-serve` enables semantic search over indexed documentation. It provides context from local knowledge bases (Markdown, PDF, TXT) to help answer questions with domain-specific accuracy.

## Capabilities

1. **Automatic Setup**: Can clone the repository and install the global CLI tools if missing.
2. **Server Management**: Can start and stop the `doc-serve` API server.
3. **Smart Indexing**: Can index local directories into the semantic database.
4. **Context Retrieval**: Performs high-accuracy similarity search to retrieve relevant text chunks.

## When to Use

- When asked to "search the domain X" or "look up X in the docs".
- When you need accurate information from local technical documentation.
- When working on a project with its own internal knowledge base.

## Workflow

### 1. Verification
Before querying, ensure the CLI tools are available.
```bash
doc-svr-ctl --version
```
If missing, clone the repository and run `task install:global`.

### 2. Server & Indexing
Check if the server is running and has data:
```bash
doc-svr-ctl status
```
If the server is down, start it: `doc-serve &`.
If the directory needs indexing: `doc-svr-ctl index /path/to/docs`.

### 3. Querying
Execute the search:
```bash
doc-svr-ctl query "your search query" --threshold 0.4 --json
```

## Best Practices

- **Threshold Adjustment**: If no results are found, retry with a lower `--threshold` (e.g., 0.2).
- **Source Citation**: Always mention the source file name in the final answer.
- **Background Processes**: Run the server in the background to keep the terminal interactive.
- **Port Conflicts**: If the server fails to start, check for existing processes on port 8000 using `lsof -i :8000`.

## Example Usage

**User**: "What does our documentation say about espresso extraction times?"

**Skill Execution**:
1. Run `doc-svr-ctl status` to verify indexing.
2. Run `doc-svr-ctl query "espresso extraction times" --threshold 0.3 --json`.
3. Synthesize the response using the returned text chunks.

**Claude Response**: "According to `espresso_basics.md`, a standard espresso shot should extract in 25-30 seconds. Shorter times lead to sour shots, while longer times result in bitterness."
