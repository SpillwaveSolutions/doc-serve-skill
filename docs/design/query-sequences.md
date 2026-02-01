# Query Sequence Diagrams

This document contains PlantUML sequence diagrams for all query modes in Agent Brain.
Each diagram shows the complete flow from client request to response.

## Table of Contents

1. [Vector Query Sequence](#1-vector-query-sequence)
2. [BM25 Query Sequence](#2-bm25-query-sequence)
3. [Hybrid Query Sequence](#3-hybrid-query-sequence)
4. [Graph Query Sequence](#4-graph-query-sequence)
5. [Multi-Mode Query Sequence](#5-multi-mode-query-sequence)

---

## 1. Vector Query Sequence

### Diagram

```plantuml
@startuml Vector Query Sequence
!theme plain
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

title Vector Query Sequence - Semantic Similarity Search

actor Client
participant "FastAPI\n/query" as API
participant "QueryService" as QS
participant "EmbeddingGenerator" as EG
participant "OpenAI API" as OpenAI
participant "VectorStoreManager" as VS
database "ChromaDB" as Chroma

== Request Validation ==

Client -> API : POST /query\n{query, mode: "vector", top_k, threshold}
activate API

API -> API : Validate query not empty
API -> QS : Check is_ready()
activate QS
QS --> API : ready = true
deactivate QS

alt Query Empty
    API --> Client : 400 Bad Request\n"Query cannot be empty"
end

alt Service Not Ready
    API --> Client : 503 Service Unavailable\n"Index not ready"
end

== Query Execution ==

API -> QS : execute_query(request)
activate QS
note right of QS: Start timing

QS -> QS : Check mode == VECTOR
QS -> QS : _execute_vector_query()

group Embedding Generation
    QS -> EG : embed_query(query_text)
    activate EG
    EG -> OpenAI : Create embedding\nmodel: text-embedding-3-large
    activate OpenAI
    OpenAI --> EG : embedding[3072 dimensions]
    deactivate OpenAI
    EG --> QS : query_embedding[]
    deactivate EG
end

group Vector Similarity Search
    QS -> VS : similarity_search(\n  query_embedding,\n  top_k,\n  similarity_threshold,\n  where_clause)
    activate VS

    VS -> Chroma : query(\n  query_embeddings,\n  n_results,\n  where,\n  include)
    activate Chroma
    note right of Chroma: Cosine distance search\nusing HNSW index
    Chroma --> VS : {ids, documents,\n metadatas, distances}
    deactivate Chroma

    VS -> VS : Convert distances to\nsimilarity scores\n(1 - distance)
    VS -> VS : Filter by threshold
    VS -> VS : Sort by score DESC
    VS --> QS : SearchResult[]
    deactivate VS
end

group Result Transformation
    QS -> QS : Convert SearchResult[]\nto QueryResult[]
    note right of QS
        For each result:
        - Extract text, source, score
        - Set vector_score = score
        - Extract source_type, language
        - Build metadata dict
    end note
end

QS -> QS : Apply content filters\n(source_types, languages, file_paths)
QS -> QS : Calculate query_time_ms

QS --> API : QueryResponse(\n  results,\n  query_time_ms,\n  total_results)
deactivate QS

API --> Client : 200 OK\n{results[], query_time_ms, total_results}
deactivate API

@enduml
```

### Walkthrough

1. **Request Validation Phase**
   - Client sends POST request to `/query` endpoint with query text and mode="vector"
   - FastAPI validates the request body against `QueryRequest` Pydantic model
   - API checks if query is non-empty (returns 400 if empty)
   - API checks if QueryService is ready (returns 503 if indexing or not initialized)

2. **Embedding Generation Phase**
   - QueryService delegates to EmbeddingGenerator
   - EmbeddingGenerator calls OpenAI API with model `text-embedding-3-large`
   - Returns a 3072-dimensional embedding vector
   - **Performance**: ~100-200ms per query (OpenAI API latency)

3. **Vector Similarity Search Phase**
   - VectorStoreManager queries ChromaDB with the embedding
   - ChromaDB uses HNSW (Hierarchical Navigable Small World) algorithm for efficient ANN search
   - Cosine distance is used, then converted to similarity score (1 - distance)
   - Results are filtered by similarity threshold and sorted descending
   - **Performance**: ~10-50ms for typical corpus sizes

4. **Result Transformation Phase**
   - SearchResults are converted to QueryResult objects with enriched metadata
   - vector_score field is populated with the similarity score
   - Content filters (source_types, languages, file_paths) are applied post-retrieval

### Error Handling

- **Empty Query**: Returns 400 with "Query cannot be empty"
- **Service Not Ready**: Returns 503 with appropriate message
- **OpenAI API Failure**: Propagates as 500 Internal Server Error
- **ChromaDB Failure**: Propagates as 500 Internal Server Error

### Performance Considerations

- Embedding generation is the primary latency contributor
- Consider caching embeddings for repeated queries
- ChromaDB HNSW provides O(log n) search complexity
- Threshold filtering happens after retrieval (not optimized in ChromaDB query)

---

## 2. BM25 Query Sequence

### Diagram

```plantuml
@startuml BM25 Query Sequence
!theme plain
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

title BM25 Query Sequence - Keyword-Based Search

actor Client
participant "FastAPI\n/query" as API
participant "QueryService" as QS
participant "BM25IndexManager" as BM25
participant "BM25Retriever\n(LlamaIndex)" as Retriever
database "BM25 Index\n(disk)" as Index

== Request Validation ==

Client -> API : POST /query\n{query, mode: "bm25", top_k}
activate API

API -> API : Validate query
API -> QS : Check is_ready()
activate QS
QS --> API : ready = true
deactivate QS

== Query Execution ==

API -> QS : execute_query(request)
activate QS
note right of QS: Start timing

QS -> QS : Check mode == BM25
QS -> QS : _execute_bm25_query()

group BM25 Index Check
    QS -> BM25 : Check is_initialized
    activate BM25

    alt BM25 Not Initialized
        BM25 --> QS : RuntimeError("BM25 index not initialized")
        QS --> API : 500 Internal Server Error
        API --> Client : Error response
    end

    BM25 --> QS : initialized = true
    deactivate BM25
end

group BM25 Retrieval
    QS -> BM25 : get_retriever(top_k)
    activate BM25
    BM25 -> BM25 : Set similarity_top_k = top_k
    BM25 --> QS : BM25Retriever
    deactivate BM25

    QS -> Retriever : aretrieve(query)
    activate Retriever

    Retriever -> Retriever : Tokenize query
    note right of Retriever
        Tokenization:
        - Lowercase
        - Remove punctuation
        - Split on whitespace
    end note

    Retriever -> Index : Load index data
    activate Index
    Index --> Retriever : corpus, doc_freqs, idf
    deactivate Index

    Retriever -> Retriever : Calculate BM25 scores
    note right of Retriever
        BM25 Score =
        sum of IDF * (tf * (k1+1)) /
        (tf + k1 * (1 - b + b * dl/avgdl))

        Where:
        - tf = term frequency in doc
        - dl = document length
        - avgdl = average doc length
        - k1, b = tuning parameters
    end note

    Retriever -> Retriever : Sort by score, take top_k
    Retriever --> QS : NodeWithScore[]
    deactivate Retriever
end

group Result Transformation
    QS -> QS : Convert NodeWithScore[]\nto QueryResult[]
    note right of QS
        For each node:
        - Get text via get_content()
        - Extract source from metadata
        - Set bm25_score = node.score
        - Extract source_type, language
    end note
end

QS -> QS : Calculate query_time_ms

QS --> API : QueryResponse(\n  results,\n  query_time_ms,\n  total_results)
deactivate QS

API --> Client : 200 OK\n{results[], query_time_ms, total_results}
deactivate API

@enduml
```

### Walkthrough

1. **Request Validation Phase**
   - Client sends POST request with mode="bm25"
   - Standard validation for non-empty query and service readiness

2. **BM25 Index Check Phase**
   - Verifies the BM25 index has been initialized
   - Index is built during document indexing and persisted to disk
   - **Error**: Throws RuntimeError if index not initialized

3. **BM25 Retrieval Phase**
   - BM25Retriever is obtained with configured top_k
   - Query is tokenized (lowercase, remove punctuation, split)
   - BM25 scores are calculated using the classic formula
   - Results are sorted by score and top_k are returned
   - **Performance**: ~5-20ms (all in-memory after initial load)

4. **Result Transformation Phase**
   - NodeWithScore objects are converted to QueryResult
   - bm25_score field is populated with the BM25 relevance score

### BM25 Algorithm Details

The BM25 (Best Matching 25) algorithm scores documents based on:
- **Term Frequency (tf)**: How often query terms appear in the document
- **Inverse Document Frequency (IDF)**: Rarity of terms across corpus
- **Document Length Normalization**: Penalizes long documents

Key parameters:
- **k1** (default 1.2): Controls term frequency saturation
- **b** (default 0.75): Controls document length normalization

### Performance Considerations

- BM25 is extremely fast after initial index load
- Index is loaded from disk on first query
- Consider memory usage for large corpora (entire index in RAM)
- No network calls (unlike vector search)

---

## 3. Hybrid Query Sequence

### Diagram

```plantuml
@startuml Hybrid Query Sequence
!theme plain
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

title Hybrid Query Sequence - Combined Vector + BM25 with Score Fusion

actor Client
participant "FastAPI\n/query" as API
participant "QueryService" as QS
participant "EmbeddingGenerator" as EG
participant "VectorStoreManager" as VS
participant "BM25IndexManager" as BM25

== Request Validation ==

Client -> API : POST /query\n{query, mode: "hybrid", alpha: 0.5, top_k}
activate API

API -> QS : execute_query(request)
activate QS
note right of QS: alpha = 0.5 means\n50% vector, 50% BM25

== Parallel Search Execution ==

QS -> QS : Get corpus_size for\neffective_top_k
QS -> VS : get_count()
activate VS
VS --> QS : corpus_size
deactivate VS

QS -> QS : effective_top_k = min(top_k, corpus_size)

par Vector Search
    QS -> EG : embed_query(query)
    activate EG
    EG --> QS : query_embedding
    deactivate EG

    QS -> VS : similarity_search(\n  query_embedding,\n  effective_top_k,\n  threshold,\n  where_clause)
    activate VS
    VS --> QS : vector_results[]
    deactivate VS
end

par BM25 Search
    QS -> BM25 : search_with_filters(\n  query,\n  effective_top_k,\n  source_types,\n  languages)
    activate BM25
    BM25 --> QS : bm25_results[]
    deactivate BM25
end

== Score Normalization ==

group Normalize Scores
    QS -> QS : max_vector_score = max(vector_results.scores)
    QS -> QS : max_bm25_score = max(bm25_results.scores)

    note right of QS
        Normalization brings both
        score types to 0-1 range:

        normalized_score = raw_score / max_score
    end note
end

== Relative Score Fusion ==

group Combine Results
    QS -> QS : Create combined_results map

    loop For each vector result
        QS -> QS : Add to map with:\n  vector_score = score/max_vector\n  bm25_score = 0.0\n  total = alpha * vector_score
    end

    loop For each BM25 result
        QS -> QS : If chunk_id exists:\n  Add bm25_score, update total\nElse:\n  Create new entry with bm25 only
        note right of QS
            total_score =
              alpha * vector_score +
              (1-alpha) * bm25_score
        end note
    end
end

== Final Ranking ==

QS -> QS : Sort by total_score DESC
QS -> QS : Take top_k results
QS -> QS : Apply content filters

QS --> API : QueryResponse
deactivate QS

API --> Client : 200 OK\n{results with both vector_score and bm25_score}
deactivate API

@enduml
```

### Walkthrough

1. **Request Validation Phase**
   - Client sends POST with mode="hybrid" and alpha parameter
   - Alpha controls the weighting: 1.0 = pure vector, 0.0 = pure BM25
   - Default alpha is 0.5 (equal weight)

2. **Parallel Search Execution Phase**
   - Vector and BM25 searches can conceptually run in parallel
   - Both use effective_top_k to avoid requesting more than corpus size
   - **Vector path**: embedding generation + ChromaDB query
   - **BM25 path**: tokenization + BM25 scoring with metadata filters

3. **Score Normalization Phase**
   - Scores from different systems have different ranges
   - Vector similarity: typically 0.0-1.0
   - BM25 scores: unbounded positive values
   - Normalization divides by max score to bring both to 0-1 range

4. **Relative Score Fusion Phase**
   - Results are merged by chunk_id into a combined map
   - Documents found by both systems get combined scores
   - Documents found by only one system use zero for the missing score
   - **Formula**: `total = alpha * vector_normalized + (1-alpha) * bm25_normalized`

5. **Final Ranking Phase**
   - Combined results are sorted by total_score descending
   - Top_k results are returned
   - Both vector_score and bm25_score are preserved in response

### Alpha Parameter Guide

| Alpha | Behavior |
|-------|----------|
| 1.0 | Pure vector search (semantic) |
| 0.7 | Vector-dominant hybrid |
| 0.5 | Equal weight (default) |
| 0.3 | BM25-dominant hybrid |
| 0.0 | Pure BM25 search (keyword) |

### Performance Considerations

- Total latency is dominated by vector search (embedding generation)
- BM25 adds minimal overhead (~5-20ms)
- Consider caching embeddings for repeated queries
- Fusion computation is O(n) where n = combined result count

---

## 4. Graph Query Sequence

### Diagram

```plantuml
@startuml Graph Query Sequence
!theme plain
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

title Graph Query Sequence - Knowledge Graph Traversal

actor Client
participant "FastAPI\n/query" as API
participant "QueryService" as QS
participant "GraphIndexManager" as GIM
participant "GraphStoreManager" as GSM
participant "VectorStoreManager" as VS
database "Property Graph" as Graph
database "ChromaDB" as Chroma

== Request Validation ==

Client -> API : POST /query\n{query, mode: "graph", top_k}
activate API

API -> QS : execute_query(request)
activate QS

== Graph Query Execution ==

QS -> QS : Check ENABLE_GRAPH_INDEX setting

alt GraphRAG Disabled
    QS --> API : ValueError\n"GraphRAG not enabled"
    API --> Client : 500 Error
end

QS -> GIM : query(query_text, top_k, traversal_depth)
activate GIM

group Entity Extraction from Query
    GIM -> GIM : _extract_query_entities(query_text)
    note right of GIM
        Entity detection heuristics:
        - CamelCase words
        - ALL_CAPS constants
        - Capitalized words (class names)
        - snake_case functions
        - Significant lowercase terms
    end note
    GIM -> GIM : Limit to 10 entities
end

group Graph Traversal
    loop For each extracted entity
        GIM -> GIM : _find_entity_relationships(\n  entity, depth, max_results)

        GIM -> GSM : Get graph_store
        activate GSM
        GSM --> GIM : PropertyGraphStore
        deactivate GSM

        GIM -> Graph : get_triplets()
        activate Graph
        Graph --> GIM : all triplets[]
        deactivate Graph

        GIM -> GIM : Search for matching entities\n(case-insensitive substring match)

        GIM -> GIM : Build result entries with:\n  - entity, subject, predicate, object\n  - source_chunk_id\n  - relationship_path\n  - graph_score = 1.0
    end
end

group Deduplication
    GIM -> GIM : Deduplicate by source_chunk_id\nor relationship_path
    GIM -> GIM : Limit to top_k unique results
end

GIM --> QS : graph_results[]
deactivate GIM

== Document Retrieval ==

alt No Graph Results
    QS -> QS : Fall back to vector search
    QS --> API : QueryResponse from vector
else Has Graph Results

    group Retrieve Source Documents
        loop For each graph result with source_chunk_id
            QS -> VS : get_by_id(chunk_id)
            activate VS
            VS -> Chroma : get(ids=[chunk_id])
            activate Chroma
            Chroma --> VS : {text, metadata}
            deactivate Chroma
            VS --> QS : document or None
            deactivate VS

            alt Document Found
                QS -> QS : Create QueryResult with:\n  - text from document\n  - graph_score\n  - related_entities\n  - relationship_path
            end
        end
    end

    alt No Documents Retrieved
        QS -> QS : Fall back to vector search
    end

end

QS -> QS : Apply content filters
QS --> API : QueryResponse
deactivate QS

API --> Client : 200 OK\n{results with graph context}
deactivate API

@enduml
```

### Walkthrough

1. **Graph Feature Check**
   - Verifies ENABLE_GRAPH_INDEX environment variable is true
   - Returns error if GraphRAG is not enabled
   - Graph queries require the knowledge graph to be built during indexing

2. **Entity Extraction from Query Phase**
   - Query text is analyzed for potential entity names
   - Heuristics detect: CamelCase, ALL_CAPS, Capitalized, snake_case words
   - Stop words are filtered out (what, where, when, etc.)
   - Limited to 10 entities to prevent query explosion

3. **Graph Traversal Phase**
   - For each extracted entity, the graph is searched
   - Matches are found via case-insensitive substring matching
   - Triplets are retrieved with subject-predicate-object structure
   - Each match gets a graph_score of 1.0 (direct match)
   - Relationship paths are formatted as "subject -> predicate -> object"

4. **Deduplication Phase**
   - Results are deduplicated by source_chunk_id (preferred) or relationship_path
   - Ensures no duplicate documents in final results

5. **Document Retrieval Phase**
   - For each graph result with a source_chunk_id
   - The actual document text is retrieved from ChromaDB
   - Documents not found are skipped
   - **Fallback**: If no documents found, falls back to vector search

6. **Result Enrichment Phase**
   - QueryResults include graph-specific fields:
     - `related_entities`: Subject and object from triplet
     - `relationship_path`: Formatted triplet string
     - `graph_score`: Relevance score from graph

### Graph Entities

The knowledge graph stores:
- **Subjects**: Functions, classes, modules, concepts
- **Predicates**: Relationships (defines, uses, imports, calls, etc.)
- **Objects**: Target entities of relationships
- **Source Chunk ID**: Links triplets back to source documents

### Performance Considerations

- Graph traversal is in-memory after initial load
- Document retrieval is O(n) ChromaDB lookups
- Consider caching frequently accessed documents
- Large graphs may require more efficient indexing

---

## 5. Multi-Mode Query Sequence

### Diagram

```plantuml
@startuml Multi-Mode Query Sequence
!theme plain
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

title Multi-Mode Query Sequence - RRF Fusion of Vector + BM25 + Graph

actor Client
participant "FastAPI\n/query" as API
participant "QueryService" as QS
participant "EmbeddingGenerator" as EG
participant "VectorStoreManager" as VS
participant "BM25IndexManager" as BM25
participant "GraphIndexManager" as GIM

== Request ==

Client -> API : POST /query\n{query, mode: "multi", top_k}
activate API

API -> QS : execute_query(request)
activate QS

== Parallel Retrieval from All Sources ==

note over QS: Execute all three retrieval\nmethods in parallel

par Vector Search
    QS -> QS : _execute_vector_query(request)
    activate QS #lightblue
    QS -> EG : embed_query
    EG --> QS : embedding
    QS -> VS : similarity_search
    VS --> QS : vector_results[]
    deactivate QS
end

par BM25 Search
    QS -> QS : _execute_bm25_query(request)
    activate QS #lightgreen
    QS -> BM25 : get_retriever + aretrieve
    BM25 --> QS : bm25_results[]
    deactivate QS
end

par Graph Search (if enabled)
    alt ENABLE_GRAPH_INDEX = true
        QS -> QS : _execute_graph_query(request)
        activate QS #lightyellow
        QS -> GIM : query
        GIM --> QS : graph_results[]
        deactivate QS
    else GraphRAG Disabled
        QS -> QS : graph_results = []
    end
end

== Reciprocal Rank Fusion (RRF) ==

QS -> QS : Initialize combined_scores map
QS -> QS : Set rrf_k = 60 (from settings)

group Process Vector Results
    loop For rank, result in enumerate(vector_results)
        QS -> QS : rrf_score = 1.0 / (rrf_k + rank + 1)
        QS -> QS : Add to combined_scores:\n  chunk_id -> {result, rrf_score, vector_rank}
    end
end

group Process BM25 Results
    loop For rank, result in enumerate(bm25_results)
        QS -> QS : rrf_score = 1.0 / (rrf_k + rank + 1)
        alt chunk_id exists in map
            QS -> QS : Add rrf_score to existing
            QS -> QS : Set bm25_rank
        else chunk_id is new
            QS -> QS : Create new entry
        end
    end
end

group Process Graph Results
    loop For rank, result in enumerate(graph_results)
        QS -> QS : rrf_score = 1.0 / (rrf_k + rank + 1)
        alt chunk_id exists in map
            QS -> QS : Add rrf_score to existing
            QS -> QS : Set graph_rank
            QS -> QS : Preserve related_entities,\nrelationship_path, graph_score
        else chunk_id is new
            QS -> QS : Create new entry with\ngraph-specific fields
        end
    end
end

note right of QS
    RRF Formula:
    RRF(d) = sum over all rankers r of:
             1 / (k + rank_r(d))

    Documents ranked highly by
    multiple systems get boosted
end note

== Final Ranking ==

QS -> QS : Sort by total rrf_score DESC
QS -> QS : Take top_k results
QS -> QS : Update result.score = rrf_score

QS --> API : QueryResponse
deactivate QS

API --> Client : 200 OK\n{results with combined scores}
deactivate API

@enduml
```

### Walkthrough

1. **Parallel Retrieval Phase**
   - All three retrieval methods are executed:
     - **Vector**: Semantic similarity via embeddings
     - **BM25**: Keyword matching via term frequency
     - **Graph**: Knowledge graph traversal (if enabled)
   - Graph search is optional based on ENABLE_GRAPH_INDEX setting
   - Each method returns its own ranked list

2. **Reciprocal Rank Fusion (RRF) Phase**
   - RRF is a proven rank aggregation algorithm
   - Each document gets a score based on its rank in each list
   - Formula: `RRF(d) = 1 / (k + rank(d))` where k=60 (default)
   - Documents appearing in multiple lists accumulate scores
   - **Key benefit**: Requires no score normalization

3. **Score Accumulation Phase**
   - combined_scores map tracks each document's contributions
   - Stores individual ranks (vector_rank, bm25_rank, graph_rank)
   - Graph-specific fields are preserved (related_entities, relationship_path)
   - Documents found by all three systems get highest RRF scores

4. **Final Ranking Phase**
   - Documents are sorted by total RRF score descending
   - Top_k results are selected
   - Final score is the RRF score

### RRF Algorithm Details

Reciprocal Rank Fusion (Cormack et al., 2009):

```
RRF(d) = sum over all rankers r of: 1 / (k + rank_r(d))
```

Where:
- **k** = 60 (prevents high-ranked documents from dominating)
- **rank_r(d)** = rank of document d in ranker r (1-indexed)

**Example**:
- Document A ranked #1 in vector, #3 in BM25, #2 in graph
- RRF(A) = 1/(60+1) + 1/(60+3) + 1/(60+2) = 0.0164 + 0.0159 + 0.0161 = 0.0484

### Why RRF Works Well

1. **No Normalization Needed**: Unlike weighted fusion, RRF doesn't require normalizing scores
2. **Robust to Outliers**: The k parameter prevents any single ranker from dominating
3. **Rewards Consensus**: Documents ranked highly by multiple systems get boosted
4. **Simple and Fast**: O(n) computation where n = total results

### Performance Considerations

- Multi-mode is the slowest due to three retrieval passes
- Consider caching results for repeated queries
- Graph search may add significant overhead with large graphs
- Total latency: vector_time + max(bm25_time, graph_time) + fusion_time

---

## Summary of Query Modes

| Mode | Algorithm | Best For | Latency |
|------|-----------|----------|---------|
| VECTOR | Semantic similarity | Conceptual/meaning-based queries | Medium |
| BM25 | Term frequency | Exact keyword matching | Low |
| HYBRID | Weighted fusion | Balanced semantic + keyword | Medium |
| GRAPH | Knowledge graph | Entity relationships | Variable |
| MULTI | RRF fusion | Maximum recall | High |

---

## Common Error Scenarios

### 1. Service Not Ready (503)

```
POST /query -> 503 Service Unavailable
{
  "detail": "Index not ready. Please index documents first."
}
```

**Cause**: Vector store not initialized or indexing in progress.

### 2. Empty Query (400)

```
POST /query -> 400 Bad Request
{
  "detail": "Query cannot be empty"
}
```

**Cause**: Query text is empty or whitespace only.

### 3. BM25 Not Initialized (500)

```
POST /query -> 500 Internal Server Error
{
  "detail": "Query failed: BM25 index not initialized"
}
```

**Cause**: BM25 index file not found or corrupted.

### 4. GraphRAG Not Enabled (500)

```
POST /query -> 500 Internal Server Error
{
  "detail": "Query failed: GraphRAG not enabled. Set ENABLE_GRAPH_INDEX=true"
}
```

**Cause**: Graph query requested but feature flag is false.
