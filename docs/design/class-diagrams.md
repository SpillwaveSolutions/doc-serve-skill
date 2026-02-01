# Class Diagrams

This document provides detailed class diagrams for Agent Brain's core components.

## Service Layer Classes

The service layer implements the core business logic for indexing and querying.

### QueryService

```mermaid
classDiagram
    class QueryService {
        -VectorStoreManager vector_store
        -EmbeddingGenerator embedding_generator
        -BM25IndexManager bm25_manager
        -GraphIndexManager graph_index_manager

        +is_ready() bool
        +execute_query(QueryRequest) QueryResponse
        +get_document_count() int

        -_execute_vector_query(QueryRequest) list~QueryResult~
        -_execute_bm25_query(QueryRequest) list~QueryResult~
        -_execute_hybrid_query(QueryRequest) list~QueryResult~
        -_execute_graph_query(QueryRequest) list~QueryResult~
        -_execute_multi_query(QueryRequest) list~QueryResult~
        -_filter_results(list~QueryResult~, QueryRequest) list~QueryResult~
        -_build_where_clause(list~str~, list~str~) dict
    }

    class QueryRequest {
        +str query
        +int top_k
        +float similarity_threshold
        +QueryMode mode
        +float alpha
        +list~str~ source_types
        +list~str~ languages
        +list~str~ file_paths
    }

    class QueryResponse {
        +list~QueryResult~ results
        +float query_time_ms
        +int total_results
    }

    class QueryResult {
        +str text
        +str source
        +float score
        +float vector_score
        +float bm25_score
        +float graph_score
        +str chunk_id
        +str source_type
        +str language
        +list~str~ related_entities
        +list~str~ relationship_path
        +dict metadata
    }

    class QueryMode {
        <<enumeration>>
        VECTOR
        BM25
        HYBRID
        GRAPH
        MULTI
    }

    QueryService --> QueryRequest : receives
    QueryService --> QueryResponse : returns
    QueryResponse --> QueryResult : contains
    QueryRequest --> QueryMode : uses

    class VectorStoreManager {
        <<interface>>
    }
    class EmbeddingGenerator {
        <<interface>>
    }
    class BM25IndexManager {
        <<interface>>
    }
    class GraphIndexManager {
        <<interface>>
    }

    QueryService --> VectorStoreManager : uses
    QueryService --> EmbeddingGenerator : uses
    QueryService --> BM25IndexManager : uses
    QueryService --> GraphIndexManager : uses
```

### IndexingService

```mermaid
classDiagram
    class IndexingService {
        -VectorStoreManager vector_store
        -DocumentLoader document_loader
        -ContextAwareChunker chunker
        -EmbeddingGenerator embedding_generator
        -BM25IndexManager bm25_manager
        -GraphIndexManager graph_index_manager
        -IndexingState _state
        -asyncio.Lock _lock
        -set~str~ _indexed_folders
        -int _total_doc_chunks
        -int _total_code_chunks
        -set~str~ _supported_languages

        +state IndexingState
        +is_indexing bool
        +is_ready bool

        +start_indexing(IndexRequest, ProgressCallback) str
        +get_status() dict
        +reset() None

        -_run_indexing_pipeline(IndexRequest, str, ProgressCallback) None
    }

    class IndexRequest {
        +str folder_path
        +bool recursive
        +bool include_code
        +bool generate_summaries
        +int chunk_size
        +int chunk_overlap
    }

    class IndexingState {
        +str current_job_id
        +IndexingStatusEnum status
        +bool is_indexing
        +str folder_path
        +int total_documents
        +int processed_documents
        +int total_chunks
        +int progress_percent
        +datetime started_at
        +datetime completed_at
        +str error
    }

    class IndexingStatusEnum {
        <<enumeration>>
        IDLE
        INDEXING
        COMPLETED
        FAILED
    }

    IndexingService --> IndexRequest : receives
    IndexingService --> IndexingState : maintains
    IndexingState --> IndexingStatusEnum : uses
```

## Storage Layer Classes

### VectorStoreManager

```mermaid
classDiagram
    class VectorStoreManager {
        -str persist_dir
        -str collection_name
        -PersistentClient _client
        -Collection _collection
        -asyncio.Lock _lock
        -bool _initialized

        +is_initialized bool

        +initialize() None
        +add_documents(ids, embeddings, documents, metadatas) int
        +upsert_documents(ids, embeddings, documents, metadatas) int
        +similarity_search(query_embedding, top_k, threshold, where) list~SearchResult~
        +get_by_id(chunk_id) dict
        +get_count(where) int
        +delete_collection() None
        +reset() None
        +close() None
    }

    class SearchResult {
        +str text
        +dict metadata
        +float score
        +str chunk_id
    }

    class PersistentClient {
        <<chromadb>>
        +get_or_create_collection(name, metadata) Collection
        +delete_collection(name) None
    }

    class Collection {
        <<chromadb>>
        +add(ids, embeddings, documents, metadatas) None
        +upsert(ids, embeddings, documents, metadatas) None
        +query(query_embeddings, n_results, where, include) dict
        +get(ids, where, include) dict
        +count() int
    }

    VectorStoreManager --> SearchResult : returns
    VectorStoreManager --> PersistentClient : uses
    VectorStoreManager --> Collection : manages
```

### BM25IndexManager

```mermaid
classDiagram
    class BM25IndexManager {
        -str persist_dir
        -BM25Retriever _retriever

        +is_initialized bool

        +initialize() None
        +build_index(nodes) None
        +persist() None
        +get_retriever(top_k) BM25Retriever
        +search_with_filters(query, top_k, source_types, languages, max_results) list~NodeWithScore~
        +reset() None
    }

    class BM25Retriever {
        <<llama_index>>
        +int similarity_top_k
        +from_defaults(nodes) BM25Retriever
        +from_persist_dir(path) BM25Retriever
        +persist(path) None
        +aretrieve(query) list~NodeWithScore~
    }

    class NodeWithScore {
        <<llama_index>>
        +BaseNode node
        +float score
    }

    class BaseNode {
        <<llama_index>>
        +str node_id
        +dict metadata
        +get_content() str
    }

    BM25IndexManager --> BM25Retriever : uses
    BM25Retriever --> NodeWithScore : returns
    NodeWithScore --> BaseNode : contains
```

### GraphStoreManager

```mermaid
classDiagram
    class GraphStoreManager {
        -Path persist_dir
        -str store_type
        -Any _graph_store
        -bool _initialized
        -int _entity_count
        -int _relationship_count
        -datetime _last_updated

        +is_initialized bool
        +entity_count int
        +relationship_count int
        +last_updated datetime
        +graph_store Any

        +get_instance(persist_dir, store_type)$ GraphStoreManager
        +reset_instance()$ None
        +initialize() None
        +persist() None
        +load() bool
        +add_triplet(subject, predicate, obj, subject_type, object_type, source_chunk_id) bool
        +clear() None

        -_initialize_simple_store() None
        -_initialize_kuzu_store() None
        -_persist_simple_store() None
        -_load_simple_store() bool
        -_update_counts() None
    }

    class SimplePropertyGraphStore {
        <<llama_index>>
        +persist(path) None
        +from_persist_path(path)$ SimplePropertyGraphStore
        +upsert_triplet(subject, predicate, object_) None
        +get_triplets() list
    }

    class KuzuPropertyGraphStore {
        <<llama_index_graph_stores>>
        +database_path str
    }

    class _MinimalGraphStore {
        -dict _data
        -dict _entities
        -list _relationships
        +_add_triplet(subject, predicate, obj, ...) None
        +clear() None
    }

    GraphStoreManager --> SimplePropertyGraphStore : uses
    GraphStoreManager --> KuzuPropertyGraphStore : uses
    GraphStoreManager --> _MinimalGraphStore : fallback
```

## Indexing Pipeline Classes

### Document Loading

```mermaid
classDiagram
    class DocumentLoader {
        -LanguageDetector language_detector

        +load_files(folder_path, recursive, include_code) list~LoadedDocument~
        +load_single_file(file_path) LoadedDocument

        -_discover_files(folder_path, recursive, include_code) list~Path~
        -_should_skip_dir(dir_name) bool
        -_classify_file(file_path) tuple
    }

    class LoadedDocument {
        +str text
        +str source
        +str file_name
        +dict metadata
    }

    class LanguageDetector {
        -dict _extension_map

        +detect_language(file_path) str
        +get_supported_languages() list~str~
        +is_code_file(file_path) bool
        +is_test_file(file_path) bool
    }

    DocumentLoader --> LoadedDocument : creates
    DocumentLoader --> LanguageDetector : uses
```

### Chunking

```mermaid
classDiagram
    class ContextAwareChunker {
        -int chunk_size
        -int chunk_overlap
        -Encoding tokenizer
        -SentenceSplitter splitter

        +count_tokens(text) int
        +chunk_documents(documents, progress_callback) list~TextChunk~
        +chunk_single_document(document) list~TextChunk~
        +rechunk_with_config(documents, chunk_size, chunk_overlap) list~TextChunk~
        +get_chunk_stats(chunks) dict
    }

    class CodeChunker {
        -str language
        -int chunk_lines
        -int chunk_lines_overlap
        -int max_chars
        -bool generate_summaries
        -CodeSplitter code_splitter
        -Language ts_language
        -Parser parser
        -Encoding tokenizer

        +count_tokens(text) int
        +chunk_code_document(document) list~CodeChunk~
        +get_code_chunk_stats(chunks) dict

        -_setup_language() None
        -_get_symbols(text) list~dict~
        -_extract_xml_doc_comment(text, line) str
    }

    class TextChunk {
        +str chunk_id
        +str text
        +str source
        +int chunk_index
        +int total_chunks
        +int token_count
        +ChunkMetadata metadata
    }

    class CodeChunk {
        +str chunk_id
        +str text
        +str source
        +int chunk_index
        +int total_chunks
        +int token_count
        +ChunkMetadata metadata

        +create(...)$ CodeChunk
    }

    class ChunkMetadata {
        +str chunk_id
        +str source
        +str file_name
        +int chunk_index
        +int total_chunks
        +str source_type
        +datetime created_at
        +str language
        +str heading_path
        +str section_title
        +str content_type
        +str symbol_name
        +str symbol_kind
        +int start_line
        +int end_line
        +str section_summary
        +str prev_section_summary
        +str docstring
        +list~str~ parameters
        +str return_type
        +list~str~ decorators
        +list~str~ imports
        +dict extra

        +to_dict() dict
    }

    ContextAwareChunker --> TextChunk : creates
    CodeChunker --> CodeChunk : creates
    TextChunk --> ChunkMetadata : contains
    CodeChunk --> ChunkMetadata : contains
```

### Embedding Generation

```mermaid
classDiagram
    class EmbeddingGenerator {
        -AsyncOpenAI client
        -str model
        -int dimensions
        -int batch_size
        -AsyncAnthropic anthropic_client
        -str claude_model

        +embed_query(query_text) list~float~
        +embed_chunks(chunks, progress_callback) list~list~float~~
        +generate_summary(text) str

        -_create_batch_embeddings(texts) list~list~float~~
    }

    class AsyncOpenAI {
        <<openai>>
        +embeddings Embeddings
    }

    class AsyncAnthropic {
        <<anthropic>>
        +messages Messages
    }

    EmbeddingGenerator --> AsyncOpenAI : uses
    EmbeddingGenerator --> AsyncAnthropic : uses
```

## GraphRAG Classes

### Graph Indexing

```mermaid
classDiagram
    class GraphIndexManager {
        -GraphStoreManager graph_store
        -LLMEntityExtractor llm_extractor
        -CodeMetadataExtractor code_extractor
        -datetime _last_build_time
        -int _last_triplet_count

        +build_from_documents(documents, progress_callback) int
        +query(query_text, top_k, traversal_depth) list~dict~
        +get_graph_context(query_text, top_k, traversal_depth) GraphQueryContext
        +get_status() GraphIndexStatus
        +clear() None

        -_extract_from_document(doc) list~GraphTriple~
        -_get_document_text(doc) str
        -_get_document_metadata(doc) dict
        -_get_document_id(doc) str
        -_extract_query_entities(query_text) list~str~
        -_find_entity_relationships(entity, depth, max_results) list~dict~
        -_get_triplet_field(triplet, field, default) Any
        -_format_relationship_path(triplet) str
    }

    class LLMEntityExtractor {
        -AsyncAnthropic client
        -str model
        -int max_triplets

        +extract_triplets(text, source_chunk_id) list~GraphTriple~

        -_parse_extraction_response(response, source_chunk_id) list~GraphTriple~
    }

    class CodeMetadataExtractor {
        +extract_from_metadata(metadata, source_chunk_id) list~GraphTriple~
        +extract_from_text(text, language, source_chunk_id) list~GraphTriple~

        -_extract_python_patterns(text, source_chunk_id) list~GraphTriple~
        -_extract_typescript_patterns(text, source_chunk_id) list~GraphTriple~
    }

    GraphIndexManager --> LLMEntityExtractor : uses
    GraphIndexManager --> CodeMetadataExtractor : uses
    GraphIndexManager --> GraphStoreManager : uses
```

### Graph Models

```mermaid
classDiagram
    class GraphTriple {
        <<frozen>>
        +str subject
        +str subject_type
        +str predicate
        +str object
        +str object_type
        +str source_chunk_id
    }

    class GraphEntity {
        <<frozen>>
        +str name
        +str entity_type
        +str description
        +list~str~ source_chunk_ids
        +dict properties
    }

    class GraphIndexStatus {
        <<frozen>>
        +bool enabled
        +bool initialized
        +int entity_count
        +int relationship_count
        +datetime last_updated
        +str store_type
    }

    class GraphQueryContext {
        <<frozen>>
        +list~str~ related_entities
        +list~str~ relationship_paths
        +list~GraphTriple~ subgraph_triplets
        +float graph_score
    }

    GraphQueryContext --> GraphTriple : contains
```

## API Layer Classes

### FastAPI Application

```mermaid
classDiagram
    class FastAPI {
        <<fastapi>>
        +str title
        +str description
        +str version
        +Lifespan lifespan
        +add_middleware(CORSMiddleware)
        +include_router(APIRouter)
    }

    class AppState {
        +VectorStoreManager vector_store
        +BM25IndexManager bm25_manager
        +IndexingService indexing_service
        +QueryService query_service
        +str mode
        +str instance_id
        +str project_id
        +dict active_projects
    }

    class HealthRouter {
        +GET /health
        +GET /health/status
    }

    class IndexRouter {
        +POST /index
        +POST /index/add
        +DELETE /index
    }

    class QueryRouter {
        +POST /query
        +GET /query/count
    }

    FastAPI --> AppState : stores
    FastAPI --> HealthRouter : includes
    FastAPI --> IndexRouter : includes
    FastAPI --> QueryRouter : includes
```

## CLI Classes

```mermaid
classDiagram
    class AgentBrainCLI {
        <<click.Group>>
        +init()
        +start()
        +stop()
        +list()
        +status()
        +index()
        +query()
        +reset()
    }

    class AgentBrainClient {
        -str base_url
        -httpx.AsyncClient client

        +health() dict
        +status() dict
        +index(folder_path, recursive, include_code) dict
        +query(query_text, top_k, mode, ...) dict
        +reset() dict
        +count() int
    }

    class StartCommand {
        +invoke(daemon, port, project_dir)
    }

    class StopCommand {
        +invoke(project_dir)
    }

    class IndexCommand {
        +invoke(path, recursive, include_code)
    }

    class QueryCommand {
        +invoke(query, top_k, mode)
    }

    AgentBrainCLI --> StartCommand : includes
    AgentBrainCLI --> StopCommand : includes
    AgentBrainCLI --> IndexCommand : includes
    AgentBrainCLI --> QueryCommand : includes
    StartCommand --> AgentBrainClient : creates
    IndexCommand --> AgentBrainClient : uses
    QueryCommand --> AgentBrainClient : uses
```

## Configuration Classes

```mermaid
classDiagram
    class Settings {
        <<pydantic_settings.BaseSettings>>
        +str API_HOST
        +int API_PORT
        +bool DEBUG
        +str OPENAI_API_KEY
        +str EMBEDDING_MODEL
        +int EMBEDDING_DIMENSIONS
        +str ANTHROPIC_API_KEY
        +str CLAUDE_MODEL
        +str CHROMA_PERSIST_DIR
        +str BM25_INDEX_PATH
        +str COLLECTION_NAME
        +int DEFAULT_CHUNK_SIZE
        +int DEFAULT_CHUNK_OVERLAP
        +int MAX_CHUNK_SIZE
        +int MIN_CHUNK_SIZE
        +int DEFAULT_TOP_K
        +int MAX_TOP_K
        +float DEFAULT_SIMILARITY_THRESHOLD
        +int EMBEDDING_BATCH_SIZE
        +str DOC_SERVE_STATE_DIR
        +str DOC_SERVE_MODE
        +bool ENABLE_GRAPH_INDEX
        +str GRAPH_STORE_TYPE
        +str GRAPH_INDEX_PATH
        +str GRAPH_EXTRACTION_MODEL
        +int GRAPH_MAX_TRIPLETS_PER_CHUNK
        +bool GRAPH_USE_CODE_METADATA
        +bool GRAPH_USE_LLM_EXTRACTION
        +int GRAPH_TRAVERSAL_DEPTH
        +int GRAPH_RRF_K
    }

    class RuntimeState {
        +str mode
        +str project_root
        +str bind_host
        +int port
        +int pid
        +str base_url
        +str instance_id
        +str project_id
        +datetime started_at
    }

    Settings <-- RuntimeState : configured_by
```

## Class Relationships Overview

```mermaid
flowchart TB
    subgraph API["API Layer"]
        FastAPI[FastAPI]
        Routers[Routers]
    end

    subgraph Services["Service Layer"]
        QueryService[QueryService]
        IndexingService[IndexingService]
    end

    subgraph Indexing["Indexing Layer"]
        DocLoader[DocumentLoader]
        Chunkers[Chunkers]
        EmbedGen[EmbeddingGenerator]
        GraphExtract[GraphExtractors]
    end

    subgraph Storage["Storage Layer"]
        VectorStore[VectorStoreManager]
        BM25Manager[BM25IndexManager]
        GraphStore[GraphStoreManager]
    end

    subgraph Models["Model Layer"]
        QueryModels[Query Models]
        IndexModels[Index Models]
        GraphModels[Graph Models]
    end

    FastAPI --> Routers
    Routers --> Services
    QueryService --> Storage
    QueryService --> EmbedGen
    IndexingService --> Indexing
    IndexingService --> Storage
    Services --> Models
    Indexing --> Models

    classDef api fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef service fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef indexing fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black
    classDef storage fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue
    classDef model fill:#DDA0DD,stroke:#333,stroke-width:2px,color:black

    class FastAPI,Routers api
    class QueryService,IndexingService service
    class DocLoader,Chunkers,EmbedGen,GraphExtract indexing
    class VectorStore,BM25Manager,GraphStore storage
    class QueryModels,IndexModels,GraphModels model
```
