# Agent Brain Roadmap

**Created:** 2026-02-07
**Core Value:** Developers can semantically search their entire codebase and documentation through a single, fast, local-first API

## Milestones

- ✅ **v3.0 Advanced RAG** — Phases 1-4 (shipped 2026-02-10)

## Phases

<details>
<summary>✅ v3.0 Advanced RAG (Phases 1-4) — SHIPPED 2026-02-10</summary>

- [x] Phase 1: Two-Stage Reranking (7/7 plans) — Feature 123
- [x] Phase 2: Pluggable Providers (4/4 plans) — Feature 103
- [x] Phase 3: Schema-Based GraphRAG (2/2 plans) — Feature 122
- [x] Phase 4: Provider Integration Testing (2/2 plans) — Feature 124

**Full details:** [v3.0-ROADMAP.md](milestones/v3.0-ROADMAP.md)

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|---------------|--------|-----------|
| 1. Two-Stage Reranking | v3.0 | 7/7 | Complete | 2026-02-08 |
| 2. Pluggable Providers | v3.0 | 4/4 | Complete | 2026-02-09 |
| 3. Schema-Based GraphRAG | v3.0 | 2/2 | Complete | 2026-02-10 |
| 4. Provider Integration Testing | v3.0 | 2/2 | Complete | 2026-02-10 |

## Future Phases

### Phase 5: PostgreSQL/AlloyDB Backend (Feature 104)

- pgvector for similarity search
- tsvector for full-text (replaces BM25)
- JSONB for graph storage
- Migration tool from ChromaDB

### Phase 6: AWS Bedrock Provider (Feature 105)

- Bedrock embeddings (Titan, Cohere)
- Bedrock summarization (Claude, Llama, Mistral)

### Phase 7: Vertex AI Provider (Feature 106)

- Vertex embeddings (textembedding-gecko)
- Vertex summarization (Gemini)

### Future Optimizations

- Embedding cache with content hashing
- File watcher for auto-indexing
- Background incremental updates
- Query caching with LRU
- UDS transport for sub-ms latency

---

## Completed Phases (Legacy Archive)

### Phase 1 (Legacy): Core Document RAG — COMPLETED
Features 001-005: Document ingestion, vector search, REST API, CLI

### Phase 2 (Legacy): BM25 & Hybrid Retrieval — COMPLETED
Feature 100: BM25 keyword search, hybrid retrieval with RRF

### Phase 3 (Legacy): Source Code Ingestion — COMPLETED
Feature 101: AST-aware code ingestion, code summaries

### Phase 3.1-3.6 (Legacy): Extensions — COMPLETED
- 109: Multi-instance architecture
- 110: C# code indexing
- 111: Skill instance discovery
- 112: Agent Brain naming
- 113: GraphRAG integration
- 114: Agent Brain plugin
- 115: Server-side job queue

---
*Roadmap created: 2026-02-07*
*Last updated: 2026-02-10 — v3.0 milestone shipped*
