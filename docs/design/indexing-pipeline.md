# Indexing Pipeline Architecture

This document details how Agent Brain processes, chunks, embeds, and stores documents and source code.

## Pipeline Overview

The indexing pipeline transforms raw files into searchable vector embeddings with rich metadata.

```mermaid
flowchart TB
    subgraph Input["Input Layer"]
        Folder[/Folder Path/]
        Request[IndexRequest]
    end

    subgraph Loading["Document Loading"]
        direction TB
        Discover[File Discovery]
        Filter[Extension Filter]
        Classify[Content Classification]
        Load[Content Loading]
    end

    subgraph Chunking["Chunking Layer"]
        direction TB
        DocChunker[Document Chunker<br/>ContextAwareChunker]
        CodeChunker[Code Chunker<br/>AST-Aware]
    end

    subgraph Processing["Processing Layer"]
        direction TB
        Metadata[Metadata Extraction]
        Summary[Summary Generation<br/>Claude Haiku]
        Embedding[Embedding Generation<br/>OpenAI]
    end

    subgraph Storage["Storage Layer"]
        direction TB
        VectorStore[(ChromaDB)]
        BM25Index[(BM25 Index)]
        GraphStore[(Graph Store)]
    end

    Folder --> Request
    Request --> Discover
    Discover --> Filter
    Filter --> Classify
    Classify -->|"Doc Files"| Load
    Classify -->|"Code Files"| Load

    Load -->|"Documents"| DocChunker
    Load -->|"Source Code"| CodeChunker

    DocChunker --> Metadata
    CodeChunker --> Metadata
    Metadata --> Summary
    Summary --> Embedding

    Embedding --> VectorStore
    Metadata --> BM25Index
    Metadata --> GraphStore

    classDef input fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef loading fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef chunking fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black
    classDef processing fill:#DDA0DD,stroke:#333,stroke-width:2px,color:black
    classDef storage fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue

    class Folder,Request input
    class Discover,Filter,Classify,Load loading
    class DocChunker,CodeChunker chunking
    class Metadata,Summary,Embedding processing
    class VectorStore,BM25Index,GraphStore storage
```

## Indexing Service Orchestration

The IndexingService coordinates the entire pipeline with progress tracking.

```mermaid
sequenceDiagram
    participant Client
    participant IndexService as IndexingService
    participant DocLoader as DocumentLoader
    participant Chunkers
    participant EmbedGen as EmbeddingGenerator
    participant Vector as VectorStore
    participant BM25 as BM25Index
    participant Graph as GraphIndex

    Client->>IndexService: start_indexing(request)
    IndexService->>IndexService: Generate job_id
    IndexService-->>Client: job_id

    Note over IndexService: Async background task

    rect rgb(200, 230, 200)
        Note over IndexService: Step 1: Load Documents (0-20%)
        IndexService->>DocLoader: load_files(folder, recursive, include_code)
        DocLoader->>DocLoader: Discover files
        DocLoader->>DocLoader: Filter by extension
        DocLoader->>DocLoader: Classify content type
        DocLoader-->>IndexService: List[LoadedDocument]
    end

    rect rgb(200, 200, 230)
        Note over IndexService: Step 2: Chunk Documents (20-50%)
        IndexService->>Chunkers: chunk_documents(docs)
        Chunkers->>Chunkers: Context-aware splitting
        Chunkers->>Chunkers: AST-aware code splitting
        Chunkers-->>IndexService: List[TextChunk | CodeChunk]
    end

    rect rgb(230, 200, 230)
        Note over IndexService: Step 3: Generate Embeddings (50-90%)
        IndexService->>EmbedGen: embed_chunks(chunks)
        EmbedGen->>EmbedGen: Batch API calls
        EmbedGen-->>IndexService: List[embedding]
    end

    rect rgb(230, 230, 200)
        Note over IndexService: Step 4: Store Vectors (90-95%)
        IndexService->>Vector: upsert_documents(ids, embeddings, docs, metadata)
        Vector-->>IndexService: Success
    end

    rect rgb(200, 230, 230)
        Note over IndexService: Step 5: Build BM25 Index (95-97%)
        IndexService->>BM25: build_index(nodes)
        BM25-->>IndexService: Success
    end

    rect rgb(230, 210, 200)
        Note over IndexService: Step 6: Build Graph Index (97-100%)
        IndexService->>Graph: build_from_documents(chunks)
        Graph-->>IndexService: triplet_count
    end

    IndexService->>IndexService: Update state to COMPLETED
```

## Document Loading

The DocumentLoader discovers and classifies files for processing.

```mermaid
flowchart TB
    FolderPath[/Folder Path/]

    subgraph Discovery["File Discovery"]
        direction TB
        Walk[Walk Directory Tree]
        CheckRecursive{Recursive?}
        Single[Single Level]
        Deep[Deep Traversal]
    end

    FolderPath --> Walk
    Walk --> CheckRecursive
    CheckRecursive -->|Yes| Deep
    CheckRecursive -->|No| Single
    Single --> Filter
    Deep --> Filter

    subgraph Filter["Extension Filter"]
        direction TB
        DocExt[".md, .txt, .rst, .html"]
        CodeExt[".py, .ts, .js, .java, .go, .rs, .c, .cpp, .cs"]
        Ignore["Skip: __pycache__, node_modules, .git, etc."]
    end

    Filter --> Classify

    subgraph Classify["Content Classification"]
        direction TB
        IsDoc{Is Document?}
        IsCode{Is Source Code?}
        IsTest{Is Test File?}

        DocType[source_type = 'doc']
        CodeType[source_type = 'code']
        TestType[source_type = 'test']

        IsDoc -->|Yes| DocType
        IsDoc -->|No| IsCode
        IsCode -->|Yes| IsTest
        IsTest -->|"test_, _test.py"| TestType
        IsTest -->|No| CodeType
    end

    DocType --> LangDetect
    CodeType --> LangDetect
    TestType --> LangDetect

    subgraph LangDetect["Language Detection"]
        direction TB
        ExtMap["Extension Mapping<br/>.py -> python<br/>.ts -> typescript<br/>.java -> java"]
    end

    LangDetect --> LoadContent

    subgraph LoadContent["Content Loading"]
        direction TB
        ReadFile[Read File Content]
        BuildMeta[Build Metadata]
        CreateDoc[Create LoadedDocument]
    end

    ReadFile --> BuildMeta
    BuildMeta --> CreateDoc
    CreateDoc --> Output[/List of LoadedDocument/]

    classDef input fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef discovery fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef filter fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black
    classDef classify fill:#DDA0DD,stroke:#333,stroke-width:2px,color:black
    classDef output fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue

    class FolderPath,Output input
    class Walk,CheckRecursive,Single,Deep discovery
    class DocExt,CodeExt,Ignore filter
    class IsDoc,IsCode,IsTest,DocType,CodeType,TestType classify
```

### Supported File Types

| Category | Extensions | Language |
|----------|------------|----------|
| **Documentation** | .md, .txt, .rst, .html | markdown, plaintext, rst, html |
| **Python** | .py | python |
| **TypeScript** | .ts, .tsx | typescript, tsx |
| **JavaScript** | .js, .jsx | javascript, jsx |
| **Java** | .java | java |
| **Go** | .go | go |
| **Rust** | .rs | rust |
| **C/C++** | .c, .cpp, .h, .hpp | c, cpp |
| **C#** | .cs | csharp |

### Ignored Patterns

```python
IGNORED_DIRS = {
    "__pycache__", ".git", ".svn", ".hg",
    "node_modules", ".next", ".nuxt",
    "venv", ".venv", "env", ".env",
    "dist", "build", "target", "out",
    ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "coverage", ".coverage", "htmlcov",
}

IGNORED_FILES = {
    ".DS_Store", "Thumbs.db",
    "*.pyc", "*.pyo", "*.class",
    "*.lock", "*.log",
}
```

## Document Chunking

The ContextAwareChunker splits text documents using semantic boundaries.

```mermaid
flowchart TB
    Document[/LoadedDocument/]

    subgraph Splitting["Text Splitting Strategy"]
        direction TB
        SentenceSplitter[LlamaIndex SentenceSplitter]

        Primary["Primary Split: Paragraphs<br/>(\\n\\n)"]
        Secondary["Secondary Split: Sentences<br/>([.!?]\\s+)"]
        Fallback["Fallback: Characters"]

        SentenceSplitter --> Primary
        Primary --> Secondary
        Secondary --> Fallback
    end

    Document --> SentenceSplitter

    subgraph ChunkProcessing["Chunk Processing"]
        direction TB
        GenID["Generate Stable ID<br/>MD5(source + index)"]
        TokenCount[Count Tokens]
        ExtractMeta[Extract Metadata]
    end

    Fallback --> GenID
    GenID --> TokenCount
    TokenCount --> ExtractMeta

    subgraph Metadata["ChunkMetadata"]
        direction TB
        ChunkID[chunk_id]
        Source[source path]
        ChunkIdx[chunk_index]
        TotalChunks[total_chunks]
        SourceType["source_type = 'doc'"]
        Language[language]
        HeadingPath[heading_path]
        SectionTitle[section_title]
    end

    ExtractMeta --> Metadata

    Metadata --> Output[/List of TextChunk/]

    classDef input fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef split fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef process fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black
    classDef meta fill:#DDA0DD,stroke:#333,stroke-width:2px,color:black
    classDef output fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue

    class Document,Output input
    class SentenceSplitter,Primary,Secondary,Fallback split
    class GenID,TokenCount,ExtractMeta process
    class ChunkID,Source,ChunkIdx,TotalChunks,SourceType,Language,HeadingPath,SectionTitle meta
```

### Chunking Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `DEFAULT_CHUNK_SIZE` | 512 | Target tokens per chunk |
| `DEFAULT_CHUNK_OVERLAP` | 50 | Overlap between chunks |
| `MAX_CHUNK_SIZE` | 2048 | Maximum allowed chunk size |
| `MIN_CHUNK_SIZE` | 128 | Minimum chunk size |

### Stable Chunk IDs

Chunk IDs are deterministic based on file path and index:

```python
id_seed = f"{document.source}_{chunk_index}"
stable_id = hashlib.md5(id_seed.encode()).hexdigest()
chunk_id = f"chunk_{stable_id[:16]}"
```

This ensures:
- Re-indexing the same file produces the same IDs
- Chunks can be updated rather than duplicated
- Consistent references across sessions

## Code Chunking (AST-Aware)

The CodeChunker uses tree-sitter for AST-aware splitting.

```mermaid
flowchart TB
    CodeFile[/LoadedDocument<br/>source_type='code'/]

    subgraph TreeSitter["Tree-Sitter Parsing"]
        direction TB
        LoadLang[Load Language Grammar]
        ParseAST[Parse to AST]
        QuerySymbols["Query Symbols<br/>(functions, classes, methods)"]
    end

    CodeFile --> LoadLang
    LoadLang --> ParseAST
    ParseAST --> QuerySymbols

    subgraph CodeSplitter["LlamaIndex CodeSplitter"]
        direction TB
        SplitLines["Split by Lines<br/>(chunk_lines=40)"]
        Overlap["Overlap<br/>(chunk_lines_overlap=15)"]
        MaxChars["Max Characters<br/>(max_chars=1500)"]
    end

    QuerySymbols --> SplitLines
    SplitLines --> Overlap
    Overlap --> MaxChars

    subgraph Enrichment["Metadata Enrichment"]
        direction TB
        MapSymbols[Map Chunks to Symbols]
        FindBest["Find Dominant Symbol<br/>(prefer symbols starting in chunk)"]
        ExtractDocstring[Extract Docstrings]
        GenSummary["Generate Summary<br/>(optional, Claude Haiku)"]
    end

    MaxChars --> MapSymbols
    MapSymbols --> FindBest
    FindBest --> ExtractDocstring
    ExtractDocstring --> GenSummary

    subgraph CodeMeta["CodeChunk Metadata"]
        direction TB
        SymbolName[symbol_name]
        SymbolKind["symbol_kind<br/>(function, class, method)"]
        StartLine[start_line]
        EndLine[end_line]
        Docstring[docstring]
        Summary[section_summary]
        Params[parameters]
        ReturnType[return_type]
        Decorators[decorators]
        Imports[imports]
    end

    GenSummary --> CodeMeta

    CodeMeta --> Output[/List of CodeChunk/]

    classDef input fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef parser fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef splitter fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black
    classDef enrich fill:#DDA0DD,stroke:#333,stroke-width:2px,color:black
    classDef meta fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue
    classDef output fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen

    class CodeFile,Output input
    class LoadLang,ParseAST,QuerySymbols parser
    class SplitLines,Overlap,MaxChars splitter
    class MapSymbols,FindBest,ExtractDocstring,GenSummary enrich
    class SymbolName,SymbolKind,StartLine,EndLine,Docstring,Summary,Params,ReturnType,Decorators,Imports meta
```

### AST Query Patterns by Language

```mermaid
flowchart LR
    subgraph Python["Python Queries"]
        PyFunc["function_definition<br/>@name: identifier"]
        PyClass["class_definition<br/>@name: identifier"]
    end

    subgraph TypeScript["TypeScript/JS Queries"]
        TSFunc["function_declaration<br/>@name: identifier"]
        TSMethod["method_definition<br/>@name: property_identifier"]
        TSClass["class_declaration<br/>@name: type_identifier"]
        TSArrow["variable_declarator<br/>@name + arrow_function"]
    end

    subgraph Java["Java Queries"]
        JMethod["method_declaration<br/>@name: identifier"]
        JClass["class_declaration<br/>@name: identifier"]
    end

    subgraph Go["Go Queries"]
        GoFunc["function_declaration<br/>@name: identifier"]
        GoMethod["method_declaration<br/>@name: field_identifier"]
        GoType["type_declaration<br/>type_spec @name"]
    end

    classDef python fill:#3572A5,stroke:#333,stroke-width:2px,color:white
    classDef typescript fill:#3178C6,stroke:#333,stroke-width:2px,color:white
    classDef java fill:#B07219,stroke:#333,stroke-width:2px,color:white
    classDef go fill:#00ADD8,stroke:#333,stroke-width:2px,color:white

    class PyFunc,PyClass python
    class TSFunc,TSMethod,TSClass,TSArrow typescript
    class JMethod,JClass java
    class GoFunc,GoMethod,GoType go
```

### Symbol Selection Strategy

When multiple symbols overlap a chunk:

1. **Prefer symbols that START within the chunk** - These are the primary content
2. **Pick the most specific (latest start line)** - Nested functions/methods over classes
3. **If none start in chunk, use the enclosing symbol** - Maintains context

## Embedding Generation

Batch embedding generation with rate limiting and progress tracking.

```mermaid
sequenceDiagram
    participant IndexService
    participant EmbedGen as EmbeddingGenerator
    participant OpenAI as OpenAI API

    IndexService->>EmbedGen: embed_chunks(chunks, progress_callback)

    loop For each batch (100 chunks)
        EmbedGen->>EmbedGen: Collect batch texts
        EmbedGen->>OpenAI: Create embeddings<br/>(model=text-embedding-3-large)
        OpenAI-->>EmbedGen: List of 3072-dim vectors

        EmbedGen->>IndexService: progress_callback(processed, total)
    end

    EmbedGen-->>IndexService: List[embedding]
```

### Embedding Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| `EMBEDDING_MODEL` | text-embedding-3-large | OpenAI model |
| `EMBEDDING_DIMENSIONS` | 3072 | Vector dimensions |
| `EMBEDDING_BATCH_SIZE` | 100 | Chunks per API call |

### Batch Processing

```python
async def embed_chunks(self, chunks: list[TextChunk], progress_callback):
    embeddings = []
    batch_size = settings.EMBEDDING_BATCH_SIZE  # 100

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_texts = [chunk.text for chunk in batch]

        response = await self.client.embeddings.create(
            input=batch_texts,
            model=settings.EMBEDDING_MODEL,
        )

        batch_embeddings = [e.embedding for e in response.data]
        embeddings.extend(batch_embeddings)

        if progress_callback:
            await progress_callback(i + len(batch), len(chunks))

    return embeddings
```

## Graph Extraction Pipeline

Knowledge graph construction from documents and code.

```mermaid
flowchart TB
    Chunks[/Document Chunks/]

    subgraph Extraction["Entity Extraction"]
        direction TB
        CodeMeta["Code Metadata Extractor<br/>(fast, deterministic)"]
        TextPattern["Text Pattern Extractor<br/>(regex-based)"]
        LLMExtract["LLM Extractor<br/>(Claude Haiku)"]
    end

    Chunks --> CodeMeta
    Chunks --> TextPattern
    Chunks --> LLMExtract

    subgraph CodeEntities["Code Entities"]
        direction TB
        Classes["Classes / Types"]
        Functions["Functions / Methods"]
        Imports["Import Relationships"]
        Calls["Call Relationships"]
    end

    CodeMeta --> Classes
    CodeMeta --> Functions
    CodeMeta --> Imports
    CodeMeta --> Calls

    subgraph TextEntities["Text Entities"]
        direction TB
        Concepts["Concepts / Topics"]
        References["Cross-References"]
    end

    TextPattern --> Concepts
    LLMExtract --> References

    subgraph Triplets["GraphTriple"]
        direction TB
        Subject[subject]
        SubjectType[subject_type]
        Predicate[predicate]
        Object[object]
        ObjectType[object_type]
        SourceChunk[source_chunk_id]
    end

    Classes --> Triplets
    Functions --> Triplets
    Imports --> Triplets
    Calls --> Triplets
    Concepts --> Triplets
    References --> Triplets

    Triplets --> GraphStore[(Graph Store)]

    classDef input fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef extract fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef entity fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black
    classDef triplet fill:#DDA0DD,stroke:#333,stroke-width:2px,color:black
    classDef storage fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue

    class Chunks input
    class CodeMeta,TextPattern,LLMExtract extract
    class Classes,Functions,Imports,Calls,Concepts,References entity
    class Subject,SubjectType,Predicate,Object,ObjectType,SourceChunk triplet
    class GraphStore storage
```

### Example Triplets

| Source | Subject | Predicate | Object | Type |
|--------|---------|-----------|--------|------|
| Code | `QueryService` | `uses` | `VectorStoreManager` | Class dependency |
| Code | `execute_query` | `defined_in` | `query_service.py` | Function location |
| Code | `agent_brain_server` | `imports` | `chromadb` | Import |
| Doc | `Hybrid Search` | `combines` | `BM25` | Concept relation |

### Graph Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `ENABLE_GRAPH_INDEX` | false | Master switch |
| `GRAPH_STORE_TYPE` | "simple" | Backend (simple or kuzu) |
| `GRAPH_MAX_TRIPLETS_PER_CHUNK` | 10 | Triplet limit per chunk |
| `GRAPH_USE_CODE_METADATA` | true | Use AST metadata |
| `GRAPH_USE_LLM_EXTRACTION` | true | Use LLM extraction |

## Storage Operations

Final storage across all backends.

```mermaid
sequenceDiagram
    participant IndexService
    participant VectorStore
    participant ChromaDB
    participant BM25Manager
    participant GraphStore

    Note over IndexService: Step 4: Store in Vector Database

    loop Batch of 40,000 chunks
        IndexService->>VectorStore: upsert_documents(ids, embeddings, docs, metadata)
        VectorStore->>ChromaDB: collection.upsert()
        ChromaDB-->>VectorStore: Success
    end

    Note over IndexService: Step 5: Build BM25 Index

    IndexService->>IndexService: Convert chunks to TextNodes
    IndexService->>BM25Manager: build_index(nodes)
    BM25Manager->>BM25Manager: BM25Retriever.from_defaults(nodes)
    BM25Manager->>BM25Manager: persist(persist_dir)

    Note over IndexService: Step 6: Build Graph Index (if enabled)

    opt ENABLE_GRAPH_INDEX is True
        IndexService->>GraphStore: build_from_documents(chunks, callback)
        loop For each chunk
            GraphStore->>GraphStore: Extract triplets
            GraphStore->>GraphStore: add_triplet()
        end
        GraphStore->>GraphStore: persist()
    end

    IndexService->>IndexService: Update state to COMPLETED
```

### ChromaDB Batch Size

ChromaDB has a maximum batch size of ~41,666 items. Agent Brain uses batches of 40,000 for safety:

```python
chroma_batch_size = 40000

for batch_start in range(0, len(chunks), chroma_batch_size):
    batch_end = min(batch_start + chroma_batch_size, len(chunks))
    batch_chunks = chunks[batch_start:batch_end]
    batch_embeddings = embeddings[batch_start:batch_end]

    await self.vector_store.upsert_documents(
        ids=[chunk.chunk_id for chunk in batch_chunks],
        embeddings=batch_embeddings,
        documents=[chunk.text for chunk in batch_chunks],
        metadatas=[chunk.metadata.to_dict() for chunk in batch_chunks],
    )
```

## Complete Pipeline Timing

Typical timing for indexing 1000 documents:

```mermaid
gantt
    title Indexing Pipeline Timing (1000 docs)
    dateFormat X
    axisFormat %s

    section Loading
    File Discovery     :0, 2
    Content Loading    :2, 5

    section Chunking
    Document Chunking  :5, 8
    Code Chunking      :8, 15

    section Embedding
    Batch 1-10        :15, 25
    Batch 11-20       :25, 35
    Batch 21-30       :35, 45

    section Storage
    Vector Upsert      :45, 48
    BM25 Build         :48, 50
    Graph Build        :50, 55
```

| Phase | Typical Time | Dominant Factor |
|-------|--------------|-----------------|
| Loading | 5-10s | Disk I/O |
| Chunking | 10-30s | AST parsing |
| Embedding | 30-60s | OpenAI API rate limits |
| Vector Storage | 3-5s | ChromaDB batch insert |
| BM25 Build | 2-5s | Tokenization |
| Graph Build | 5-15s | LLM extraction |

## Error Handling

The pipeline handles failures gracefully:

```mermaid
flowchart TB
    Start([Start Indexing])

    Start --> LoadDocs

    subgraph LoadDocs["Document Loading"]
        Load[Load Files]
        LoadErr{Error?}
        Load --> LoadErr
        LoadErr -->|Yes| LogSkip["Log & Skip File"]
        LoadErr -->|No| Continue1[Continue]
        LogSkip --> Continue1
    end

    Continue1 --> ChunkDocs

    subgraph ChunkDocs["Chunking"]
        Chunk[Chunk Document]
        ChunkErr{AST Error?}
        Chunk --> ChunkErr
        ChunkErr -->|Yes| Fallback["Fallback to Text Chunking"]
        ChunkErr -->|No| Continue2[Continue]
        Fallback --> Continue2
    end

    Continue2 --> GenEmbed

    subgraph GenEmbed["Embedding"]
        Embed[Generate Embeddings]
        EmbedErr{API Error?}
        Embed --> EmbedErr
        EmbedErr -->|Yes| Retry["Retry with Backoff"]
        EmbedErr -->|No| Continue3[Continue]
        Retry --> RetryFail{Still Failing?}
        RetryFail -->|Yes| Fail[Fail Pipeline]
        RetryFail -->|No| Continue3
    end

    Continue3 --> Store

    subgraph Store["Storage"]
        VectorStore[Store Vectors]
        StoreErr{Error?}
        VectorStore --> StoreErr
        StoreErr -->|Yes| Fail
        StoreErr -->|No| Complete
    end

    Complete([Indexing Complete])
    Fail([Indexing Failed])

    classDef start fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef error fill:#FFB6C1,stroke:#DC143C,stroke-width:2px,color:black
    classDef decision fill:#FFD700,stroke:#333,stroke-width:2px,color:black
    classDef process fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue

    class Start,Complete start
    class Fail error
    class LoadErr,ChunkErr,EmbedErr,StoreErr,RetryFail decision
    class Load,Chunk,Embed,VectorStore process
```

### Fallback Strategies

1. **AST Parsing Failure**: Fall back to text-based chunking
2. **Language Detection Failure**: Skip code-specific metadata
3. **Embedding API Failure**: Exponential backoff retry
4. **Graph Extraction Failure**: Continue without graph (non-critical)
