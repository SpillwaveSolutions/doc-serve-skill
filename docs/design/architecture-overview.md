# Agent Brain System Architecture Overview

This document provides a comprehensive architectural view of Agent Brain, a RAG-based document indexing and semantic search system designed for developer productivity.

## Executive Summary

Agent Brain is a monorepo containing four interconnected packages that work together to provide intelligent document and code search capabilities. The system combines traditional BM25 keyword matching with modern semantic vector search and optional GraphRAG knowledge graph retrieval.

## C4 Context Diagram

This diagram shows Agent Brain's position in the broader ecosystem and its interactions with external systems.

```mermaid
C4Context
    title Agent Brain System Context

    Person(developer, "Developer", "Uses Claude Code for development")
    Person(devops, "DevOps Engineer", "Manages deployments and monitoring")

    System_Boundary(ab, "Agent Brain System") {
        System(plugin, "Agent Brain Plugin", "Claude Code plugin with 15 commands")
        System(server, "Agent Brain Server", "FastAPI REST API for RAG")
        System(cli, "Agent Brain CLI", "Management tool")
    }

    System_Ext(claude, "Claude Code", "AI coding assistant")
    System_Ext(openai, "OpenAI API", "Embeddings (text-embedding-3-large)")
    System_Ext(anthropic, "Anthropic API", "Summarization (Claude Haiku)")
    System_Ext(chromadb, "ChromaDB", "Vector database")
    System_Ext(filesystem, "Filesystem", "Local documents and code")

    Rel(developer, claude, "Uses", "Interactive chat")
    Rel(claude, plugin, "Invokes", "Slash commands")
    Rel(plugin, cli, "Delegates to", "Shell commands")
    Rel(cli, server, "Calls", "REST API")
    Rel(server, openai, "Generates embeddings", "HTTPS")
    Rel(server, anthropic, "Generates summaries", "HTTPS")
    Rel(server, chromadb, "Stores vectors", "Local API")
    Rel(server, filesystem, "Reads documents", "File I/O")
    Rel(devops, cli, "Manages", "Terminal")
```

### Why This Architecture?

1. **Plugin-First Design**: The Claude Code plugin provides natural language access to all functionality
2. **CLI Abstraction**: The CLI provides a stable interface that both the plugin and users can rely on
3. **REST API Foundation**: The server exposes all capabilities through a well-documented API
4. **External Service Integration**: Leverages best-in-class services (OpenAI for embeddings, Anthropic for summaries)

## Component Architecture

This diagram shows the internal structure of each package and their relationships.

```mermaid
flowchart TB
    subgraph Plugin["Agent Brain Plugin"]
        direction TB
        Commands[15 Slash Commands]
        Skills[2 Skills]
        Agents[2 Agents]
        Commands --> Skills
        Commands --> Agents
    end

    subgraph CLI["Agent Brain CLI"]
        direction TB
        CliMain[Click CLI]
        ApiClient[API Client]
        CmdIndex[IndexCommand]
        CmdQuery[QueryCommand]
        CmdServer[ServerCommands]
        CliMain --> CmdIndex
        CliMain --> CmdQuery
        CliMain --> CmdServer
        CmdIndex --> ApiClient
        CmdQuery --> ApiClient
        CmdServer --> ApiClient
    end

    subgraph Server["Agent Brain Server"]
        direction TB
        FastAPI[FastAPI App]

        subgraph Routers["API Routers"]
            HealthRouter[Health Router]
            IndexRouter[Index Router]
            QueryRouter[Query Router]
        end

        subgraph Services["Services"]
            IndexingService[Indexing Service]
            QueryService[Query Service]
        end

        subgraph Indexing["Indexing Pipeline"]
            DocLoader[Document Loader]
            CodeChunker[Code Chunker]
            TextChunker[Text Chunker]
            Embedder[Embedding Generator]
            GraphExtractor[Graph Extractors]
        end

        subgraph Storage["Storage Layer"]
            VectorStore[Vector Store Manager]
            BM25Index[BM25 Index Manager]
            GraphStore[Graph Store Manager]
        end

        FastAPI --> Routers
        Routers --> Services
        IndexingService --> Indexing
        IndexingService --> Storage
        QueryService --> Storage
    end

    subgraph External["External Systems"]
        ChromaDB[(ChromaDB)]
        OpenAI[OpenAI API]
        Anthropic[Anthropic API]
        Files[/File System/]
    end

    Plugin -->|"Shell Commands"| CLI
    CLI -->|"REST API"| Server
    VectorStore --> ChromaDB
    Embedder --> OpenAI
    GraphExtractor --> Anthropic
    DocLoader --> Files

    classDef primary fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef secondary fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef storage fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue
    classDef external fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black

    class FastAPI,IndexingService,QueryService primary
    class HealthRouter,IndexRouter,QueryRouter,DocLoader,CodeChunker,TextChunker,Embedder secondary
    class VectorStore,BM25Index,GraphStore storage
    class ChromaDB,OpenAI,Anthropic,Files external
```

### Component Descriptions

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Agent Brain Plugin** | Claude Code integration with slash commands | Markdown-based Claude plugin format |
| **Agent Brain CLI** | Command-line management tool | Python + Click + Rich |
| **Agent Brain Server** | Core RAG API server | Python + FastAPI + Uvicorn |
| **ChromaDB** | Vector similarity search | ChromaDB with cosine similarity |
| **BM25 Index** | Keyword-based retrieval | LlamaIndex BM25Retriever |
| **Graph Store** | Knowledge graph storage | SimplePropertyGraphStore / Kuzu |

## Advantages of This Architecture

### 1. Separation of Concerns
- **Plugin**: User experience and natural language interface
- **CLI**: Scripting, automation, and DevOps
- **Server**: Business logic and data management
- **Storage**: Persistence and retrieval optimization

### 2. Flexibility
- Multiple entry points (plugin, CLI, API)
- Pluggable storage backends
- Optional features (GraphRAG)
- Per-project isolation

### 3. Scalability
- Stateless server design
- Batch processing for embeddings
- Async operations throughout
- Configurable chunk sizes

### 4. Developer Experience
- Natural language search from Claude Code
- Rich CLI with progress indicators
- OpenAPI documentation
- Comprehensive error handling

## Multi-Instance Architecture

Agent Brain supports running multiple isolated instances for different projects.

```mermaid
flowchart LR
    subgraph ProjectA["Project A"]
        direction TB
        PluginA[Plugin Commands]
        CLIA[CLI]
        ServerA[Server :8001]
        StateA[".claude/agent-brain/"]
    end

    subgraph ProjectB["Project B"]
        direction TB
        PluginB[Plugin Commands]
        CLIB[CLI]
        ServerB[Server :8002]
        StateB[".claude/agent-brain/"]
    end

    subgraph SharedServices["Shared Services"]
        OpenAI[OpenAI API]
    end

    PluginA --> CLIA
    CLIA --> ServerA
    ServerA --> StateA
    ServerA --> OpenAI

    PluginB --> CLIB
    CLIB --> ServerB
    ServerB --> StateB
    ServerB --> OpenAI

    classDef project fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef shared fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black

    class PluginA,CLIA,ServerA,StateA,PluginB,CLIB,ServerB,StateB project
    class OpenAI shared
```

### Per-Project Isolation

Each project maintains its own:
- **State Directory**: `.claude/agent-brain/`
- **Vector Database**: `chroma_db/`
- **BM25 Index**: `bm25_index/`
- **Graph Index**: `graph_index/` (if enabled)
- **Runtime State**: `runtime.json` with port and PID

### Lock File Protocol

```mermaid
sequenceDiagram
    participant CLI as CLI/Plugin
    participant Server as Server Process
    participant Lock as lock.json
    participant Runtime as runtime.json

    CLI->>Lock: Check stale (PID exists?)
    alt Lock is stale
        CLI->>Lock: Clean up stale lock
    end
    CLI->>Lock: Acquire lock (write PID)
    CLI->>Server: Start server (port=0)
    Server->>Server: Find free port
    Server->>Runtime: Write runtime.json
    CLI->>Runtime: Read port from runtime.json
    CLI->>Server: Connect to server
    Note over CLI,Server: Normal operation
    Server->>Lock: Release lock on shutdown
    Server->>Runtime: Delete runtime.json
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Interface** | Claude Plugin (Markdown) | Natural language commands |
| **CLI** | Click + Rich | Terminal interface |
| **API** | FastAPI + Uvicorn | HTTP endpoints |
| **Embeddings** | OpenAI text-embedding-3-large | Semantic vectors (3072 dims) |
| **Vector DB** | ChromaDB | Similarity search |
| **Keyword Search** | LlamaIndex BM25Retriever | Term-based retrieval |
| **Graph Store** | SimplePropertyGraphStore/Kuzu | Knowledge graph |
| **AST Parsing** | tree-sitter | Code analysis |
| **Summarization** | Anthropic Claude Haiku | Code summaries |
| **Config** | Pydantic Settings | Environment-based config |

## Next Steps

For more detailed views of specific subsystems:

- [Query Flow Architecture](./query-architecture.md) - How queries are routed and processed
- [Indexing Pipeline](./indexing-pipeline.md) - Document and code processing
- [Storage Architecture](./storage-architecture.md) - Persistence and retrieval
- [Class Diagrams](./class-diagrams.md) - Object model details
- [Deployment Architecture](./deployment-architecture.md) - Production setup
