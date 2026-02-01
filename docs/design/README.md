# Agent Brain Architecture Documentation

Comprehensive architectural documentation for Agent Brain, a RAG-based document indexing and semantic search system.

## Overview

Agent Brain is a production-grade RAG (Retrieval-Augmented Generation) system that combines:

- **Hybrid Search**: BM25 keyword matching + vector semantic search
- **GraphRAG**: Knowledge graph-based retrieval with entity relationships
- **AST-Aware Code Indexing**: Multi-language support with tree-sitter parsing
- **Multi-Instance Architecture**: Per-project isolation with automatic port allocation
- **RRF Fusion**: Reciprocal Rank Fusion for combining multiple retrieval results

## Documentation Index

| Document | Description |
|----------|-------------|
| [Architecture Overview](./architecture-overview.md) | C4 diagrams, component architecture, technology stack |
| [Query Architecture](./query-architecture.md) | Query routing, search modes (VECTOR, BM25, HYBRID, GRAPH, MULTI) |
| [Indexing Pipeline](./indexing-pipeline.md) | Document loading, chunking, embedding, graph extraction |
| [Storage Architecture](./storage-architecture.md) | ChromaDB, BM25 index, graph store, state management |
| [Class Diagrams](./class-diagrams.md) | Detailed class relationships and interfaces |
| [Deployment Architecture](./deployment-architecture.md) | Local, multi-instance, Docker, Kubernetes deployments |

## Quick Reference

### System Components

```
agent-brain-server/     # FastAPI REST API (core RAG functionality)
agent-brain-cli/        # Click CLI for management
agent-brain-plugin/     # Claude Code plugin (15 commands, 2 agents, 2 skills)
agent-brain-skill/      # Claude Code skill integration
```

### Query Modes

| Mode | Algorithm | Best For |
|------|-----------|----------|
| `VECTOR` | Cosine similarity | Conceptual queries, "how does X work" |
| `BM25` | TF-IDF + BM25 | Exact terms, error messages, symbols |
| `HYBRID` | Vector + BM25 (alpha blend) | General search (default) |
| `GRAPH` | Knowledge graph traversal | Entity relationships |
| `MULTI` | RRF over all modes | Maximum recall |

### Storage Systems

| System | Purpose | Technology |
|--------|---------|------------|
| **Vector Store** | Semantic similarity | ChromaDB (HNSW, cosine) |
| **BM25 Index** | Keyword retrieval | LlamaIndex BM25Retriever |
| **Graph Store** | Entity relationships | SimplePropertyGraphStore / Kuzu |

### Key Configurations

| Setting | Default | Description |
|---------|---------|-------------|
| `EMBEDDING_MODEL` | text-embedding-3-large | OpenAI embedding model |
| `EMBEDDING_DIMENSIONS` | 3072 | Vector dimensions |
| `DEFAULT_CHUNK_SIZE` | 512 | Tokens per chunk |
| `DEFAULT_TOP_K` | 5 | Results per query |
| `ENABLE_GRAPH_INDEX` | false | GraphRAG toggle |

## Diagram Types

This documentation uses Mermaid diagrams throughout:

- **C4 Diagrams**: System context and component relationships
- **Flowcharts**: Process flows and decision trees
- **Sequence Diagrams**: API interactions and data flow
- **Class Diagrams**: Object model and interfaces
- **Gantt Charts**: Pipeline timing

## Architecture Decision Records

Key architectural decisions:

1. **Hybrid Search First**: Default to combining BM25 and vector search
2. **Optional GraphRAG**: Graph indexing is opt-in to minimize resource usage
3. **Per-Project Isolation**: Each project gets its own server instance and storage
4. **Singleton Services**: Shared service instances within a process
5. **Async Throughout**: All I/O operations are async for performance

## Contributing

When updating this documentation:

1. Keep diagrams up-to-date with code changes
2. Use consistent styling (high-contrast colors)
3. Include step-by-step explanations
4. Explain WHY decisions were made, not just WHAT

---

*Last Updated: 2025-01-31*
*Version: 1.2.0*
