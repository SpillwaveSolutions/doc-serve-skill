# Server State Diagrams

This document contains PlantUML state diagrams for Agent Brain server lifecycle,
index management, and health monitoring.

## Table of Contents

1. [Server Lifecycle States](#1-server-lifecycle-states)
2. [Index States](#2-index-states)
3. [Health States](#3-health-states)

---

## 1. Server Lifecycle States

### Diagram

```plantuml
@startuml Server Lifecycle States
!theme plain
skinparam state {
    BackgroundColor<<active>> LightGreen
    BackgroundColor<<transitioning>> LightYellow
    BackgroundColor<<error>> LightCoral
}

title Agent Brain Server Lifecycle States

[*] --> Stopped

state Stopped {
    Stopped : No process running
    Stopped : No runtime.json exists
    Stopped : Port is available
}

Stopped --> Starting : CLI "start" command

state Starting <<transitioning>> {
    Starting : Resolving project root
    Starting : Reading configuration
    Starting : Finding available port
    Starting : Spawning uvicorn process
    Starting : Writing runtime.json
    Starting : Waiting for health check
}

Starting --> Running : Health check passes
Starting --> Failed : Timeout or process crash

state Running <<active>> {
    Running : Process alive (PID tracked)
    Running : runtime.json exists
    Running : Health endpoint responds
    Running : Ready for queries
    ---
    Running : Monitoring indexing state
    Running : Serving API requests
}

Running --> Stopping : CLI "stop" command
Running --> Stopping : SIGTERM received
Running --> Failed : Process crash
Running --> Failed : Unhandled exception

state Stopping <<transitioning>> {
    Stopping : SIGTERM sent to process
    Stopping : Waiting for graceful shutdown
    Stopping : Cleaning up state files
    Stopping : Removing from registry
}

Stopping --> Stopped : Process exits gracefully
Stopping --> ForceKilling : Timeout reached (with --force)

state ForceKilling <<transitioning>> {
    ForceKilling : SIGKILL sent to process
    ForceKilling : Waiting for process death
    ForceKilling : Force cleanup
}

ForceKilling --> Stopped : Process killed
ForceKilling --> Failed : SIGKILL ignored

state Failed <<error>> {
    Failed : Error logged
    Failed : Stale runtime.json may exist
    Failed : Manual cleanup may be needed
}

Failed --> Stopped : Stale cleanup on next start
Failed --> Stopped : Manual intervention

note right of Starting
    Startup Timeout: 30 seconds (configurable)
    Health check interval: 500ms
end note

note right of Stopping
    Graceful Timeout: 10 seconds (configurable)
    Force flag: --force to use SIGKILL
end note

@enduml
```

### State Descriptions

| State | Description | Triggers |
|-------|-------------|----------|
| **Stopped** | No server process running. Port is available. No runtime.json. | Initial state, after clean stop |
| **Starting** | Server is being initialized. Spawning process, waiting for health. | `agent-brain start` command |
| **Running** | Server is operational. Accepting requests. Health check passes. | Health check success |
| **Stopping** | Graceful shutdown in progress. SIGTERM sent. | `agent-brain stop`, SIGTERM |
| **ForceKilling** | Forced shutdown. SIGKILL sent after timeout. | `--force` flag, SIGTERM timeout |
| **Failed** | Error state. Stale files may exist. | Crash, timeout, unhandled error |

### Transitions

1. **Stopped -> Starting**
   - Trigger: `agent-brain start` command
   - Actions:
     - Resolve project root (git root or marker detection)
     - Read config.json from state directory
     - Find available port (auto-detect or explicit)
     - Spawn uvicorn subprocess with environment variables
     - Write runtime.json with PID, port, base_url
     - Poll health endpoint until ready

2. **Starting -> Running**
   - Trigger: Health check returns 200 OK
   - Timeout: 30 seconds (configurable with `--timeout`)
   - Actions:
     - Update global registry at `~/.doc-serve/registry.json`
     - Display success message with URL

3. **Starting -> Failed**
   - Trigger: Health check timeout or process crash
   - Actions:
     - Kill orphaned process (if still alive)
     - Delete runtime.json
     - Log error message

4. **Running -> Stopping**
   - Trigger: `agent-brain stop` or SIGTERM signal
   - Actions:
     - Send SIGTERM to process
     - Wait for graceful shutdown (10 seconds default)

5. **Stopping -> Stopped**
   - Trigger: Process exits cleanly
   - Actions:
     - Delete runtime.json, lock file, PID file
     - Remove from global registry

6. **Stopping -> ForceKilling**
   - Trigger: Graceful timeout with `--force` flag
   - Actions:
     - Send SIGKILL to process

7. **ForceKilling -> Stopped**
   - Trigger: Process killed
   - Actions:
     - Force cleanup all state files

### runtime.json Structure

```json
{
    "schema_version": "1.0",
    "mode": "project",
    "project_root": "/path/to/project",
    "instance_id": "a1b2c3d4e5f6",
    "base_url": "http://127.0.0.1:8042",
    "bind_host": "127.0.0.1",
    "port": 8042,
    "pid": 12345,
    "started_at": "2024-01-15T10:30:00Z"
}
```

---

## 2. Index States

### Diagram

```plantuml
@startuml Index States
!theme plain
skinparam state {
    BackgroundColor<<ready>> LightGreen
    BackgroundColor<<busy>> LightYellow
    BackgroundColor<<error>> LightCoral
}

title Agent Brain Index States

[*] --> Empty

state Empty {
    Empty : No documents indexed
    Empty : Vector store not initialized
    Empty : BM25 index empty
    Empty : Graph index empty
    ---
    Empty : Queries return 503
}

Empty --> Indexing : POST /index request

state Indexing <<busy>> {
    state "Loading" as Loading
    state "Chunking" as Chunking
    state "Embedding" as Embedding
    state "Storing" as Storing
    state "BuildingBM25" as BM25
    state "BuildingGraph" as BuildingGraph

    Loading : Reading files from disk
    Loading : Detecting languages
    Loading : Creating Document objects

    Chunking : Splitting text documents
    Chunking : AST parsing code files
    Chunking : Extracting symbols
    Chunking : Generating summaries

    Embedding : Calling OpenAI API
    Embedding : Batching chunks
    Embedding : Creating 3072-dim vectors

    Storing : Upserting to ChromaDB
    Storing : Batching (40k limit)

    BM25 : Building BM25Retriever
    BM25 : Persisting to disk

    BuildingGraph : Extracting entities
    BuildingGraph : Storing triplets
    BuildingGraph : Persisting graph

    [*] --> Loading
    Loading --> Chunking : Documents loaded
    Chunking --> Embedding : Chunks created
    Embedding --> Storing : Embeddings generated
    Storing --> BM25 : Vectors stored
    BM25 --> BuildingGraph : BM25 ready
    BuildingGraph --> [*] : Graph built
}

Indexing --> Ready : Indexing completed successfully
Indexing --> Failed : Error during indexing

state Ready <<ready>> {
    Ready : All indexes populated
    Ready : Vector store ready
    Ready : BM25 index ready
    Ready : Graph index ready (if enabled)
    ---
    Ready : Queries return results
    Ready : Health returns "healthy"
}

Ready --> Updating : POST /index/add request

state Updating <<busy>> {
    Updating : Adding new documents
    Updating : Preserving existing index
    Updating : Incremental updates
    ---
    Updating : Queries still served
    Updating : May return partial results
}

Updating --> Ready : Update completed
Updating --> Ready : Update failed (rollback)

Ready --> Resetting : DELETE /index request

state Resetting <<busy>> {
    Resetting : Deleting ChromaDB collection
    Resetting : Clearing BM25 index
    Resetting : Clearing graph index
    Resetting : Resetting state counters
}

Resetting --> Empty : Reset completed

state Failed <<error>> {
    Failed : error field populated
    Failed : Partial index may exist
    Failed : Manual cleanup may be needed
    ---
    Failed : Health returns "degraded"
}

Failed --> Empty : DELETE /index (reset)
Failed --> Indexing : POST /index (retry)

note right of Indexing
    Progress tracked via:
    - /health/status endpoint
    - progress_percent field
    - current stage in status
end note

note right of Ready
    Index statistics:
    - total_chunks
    - total_doc_chunks
    - total_code_chunks
    - supported_languages
    - indexed_folders
end note

@enduml
```

### State Descriptions

| State | Description | Health Status |
|-------|-------------|---------------|
| **Empty** | No documents indexed. Fresh start. | degraded |
| **Indexing** | Active indexing operation. | indexing |
| **Ready** | All indexes populated and ready. | healthy |
| **Updating** | Adding documents to existing index. | indexing |
| **Resetting** | Clearing all indexes. | indexing |
| **Failed** | Error occurred during indexing. | degraded |

### Indexing Sub-States

1. **Loading** (0-20%)
   - Reading files from disk
   - Detecting file types and languages
   - Creating Document objects with metadata

2. **Chunking** (20-50%)
   - Text documents: ContextAwareChunker splits by sections
   - Code files: CodeChunker uses AST parsing
   - Summary generation (optional, Claude API)

3. **Embedding** (50-90%)
   - Batching chunks (100 per batch)
   - OpenAI API calls for embeddings
   - Rate limiting and retry logic

4. **Storing** (90-95%)
   - ChromaDB upsert operations
   - Batching (40,000 limit per batch)

5. **BuildingBM25** (95-97%)
   - Creating BM25Retriever from nodes
   - Persisting to disk

6. **BuildingGraph** (97-100%)
   - Entity extraction (code metadata + LLM)
   - Triplet storage
   - Graph persistence

### Query Behavior by State

| State | Query Behavior |
|-------|----------------|
| Empty | 503 Service Unavailable |
| Indexing | 503 Service Unavailable |
| Ready | Normal query processing |
| Updating | Queries served (may be partial) |
| Resetting | 503 Service Unavailable |
| Failed | 503 Service Unavailable |

---

## 3. Health States

### Diagram

```plantuml
@startuml Health States
!theme plain
skinparam state {
    BackgroundColor<<healthy>> LightGreen
    BackgroundColor<<warning>> LightYellow
    BackgroundColor<<error>> LightCoral
}

title Agent Brain Health States

[*] --> Initializing

state Initializing {
    Initializing : Server starting
    Initializing : Services loading
    Initializing : Vector store connecting
}

Initializing --> Healthy : All services ready
Initializing --> Degraded : Partial initialization

state Healthy <<healthy>> {
    Healthy : All systems operational
    Healthy : Vector store initialized
    Healthy : No active errors
    Healthy : Ready for all query modes
    ---
    Healthy : GET /health returns 200
    Healthy : status: "healthy"
}

Healthy --> Indexing : Indexing starts

state Indexing <<warning>> {
    Indexing : Background indexing active
    Indexing : Queries blocked
    Indexing : Progress tracked
    ---
    Indexing : GET /health returns 200
    Indexing : status: "indexing"
    Indexing : message shows progress
}

Indexing --> Healthy : Indexing completes successfully
Indexing --> Degraded : Indexing fails

Healthy --> Degraded : Error occurs
Healthy --> Unhealthy : Critical failure

state Degraded <<warning>> {
    state "VectorStoreNotInit" as VSNotInit
    state "LastIndexingFailed" as IndexFailed
    state "GraphNotEnabled" as GraphOff
    state "BM25NotReady" as BM25Off

    VSNotInit : Vector store not connected
    VSNotInit : Needs initialization

    IndexFailed : Previous indexing errored
    IndexFailed : Error message available

    GraphOff : GraphRAG disabled
    GraphOff : Graph queries fail

    BM25Off : BM25 index not built
    BM25Off : BM25 queries fail

    ---
    Degraded : GET /health returns 200
    Degraded : status: "degraded"
    Degraded : Partial functionality
}

Degraded --> Healthy : Issue resolved
Degraded --> Indexing : New indexing started
Degraded --> Unhealthy : Further degradation

state Unhealthy <<error>> {
    Unhealthy : Critical system failure
    Unhealthy : Unable to process any requests
    Unhealthy : Requires restart
    ---
    Unhealthy : GET /health may fail
    Unhealthy : status: "unhealthy"
}

Unhealthy --> Stopped : Process terminated
Unhealthy --> Initializing : Restart

note right of Healthy
    Health Check Response:
    {
        "status": "healthy",
        "message": "Server is running and ready for queries",
        "timestamp": "2024-01-15T10:30:00Z",
        "version": "1.2.0",
        "mode": "project",
        "instance_id": "abc123"
    }
end note

note right of Degraded
    Degraded Conditions:
    - Vector store not initialized
    - Last indexing failed
    - BM25 index not built
    - Optional features disabled
end note

@enduml
```

### State Descriptions

| State | HTTP Status | Meaning |
|-------|-------------|---------|
| **Initializing** | 200 (pending) | Server starting up |
| **Healthy** | 200 | All systems operational |
| **Indexing** | 200 | Background indexing active |
| **Degraded** | 200 | Partial functionality |
| **Unhealthy** | 500/503 | Critical failure |

### Health Check Response

```json
{
    "status": "healthy",
    "message": "Server is running and ready for queries",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.2.0",
    "mode": "project",
    "instance_id": "a1b2c3d4e5f6",
    "project_id": "/path/to/project",
    "active_projects": null
}
```

### Status Values

| Status | Condition | Query Impact |
|--------|-----------|--------------|
| `healthy` | All ready, no errors | Full query support |
| `indexing` | Active indexing job | Queries blocked (503) |
| `degraded` | Partial functionality | Some query modes fail |
| `unhealthy` | Critical failure | All queries fail |

### Degraded Conditions

1. **Vector Store Not Initialized**
   - Message: "Vector store not initialized"
   - Impact: All query modes fail
   - Resolution: Run indexing

2. **Last Indexing Failed**
   - Message: "Last indexing failed: {error}"
   - Impact: May have partial index
   - Resolution: Fix error, re-index

3. **BM25 Index Not Ready**
   - Message: "BM25 index not initialized"
   - Impact: BM25 and hybrid queries fail
   - Resolution: Run indexing

4. **GraphRAG Not Enabled**
   - Not degraded (feature disabled by choice)
   - Impact: Graph and multi queries skip graph
   - Resolution: Enable ENABLE_GRAPH_INDEX

### Health Check Endpoint Details

**Endpoint**: `GET /health/`

**Response Model**: `HealthStatus`

```python
class HealthStatus(BaseModel):
    status: Literal["healthy", "indexing", "degraded", "unhealthy"]
    message: str
    timestamp: datetime
    version: str
    mode: str  # "project" or "shared"
    instance_id: Optional[str]
    project_id: Optional[str]
    active_projects: Optional[list[str]]
```

---

## State Machine Summary

```plantuml
@startuml State Machine Summary
!theme plain
left to right direction

package "Server Lifecycle" {
    [Stopped] --> [Starting]
    [Starting] --> [Running]
    [Running] --> [Stopping]
    [Stopping] --> [Stopped]
}

package "Index Lifecycle" {
    [Empty] --> [Indexing]
    [Indexing] --> [Ready]
    [Ready] --> [Updating]
    [Updating] --> [Ready]
    [Ready] --> [Resetting]
    [Resetting] --> [Empty]
}

package "Health Status" {
    [Healthy] --> [Indexing_H]
    [Indexing_H] --> [Healthy]
    [Healthy] --> [Degraded]
    [Degraded] --> [Healthy]
    [Degraded] --> [Unhealthy]
}

note bottom of "Server Lifecycle"
    Managed by CLI:
    - start, stop, list
end note

note bottom of "Index Lifecycle"
    Managed by API:
    - POST /index
    - POST /index/add
    - DELETE /index
end note

note bottom of "Health Status"
    Monitored by:
    - GET /health/
    - GET /health/status
end note

@enduml
```

### Interaction Between State Machines

| Server State | Index State | Health State |
|--------------|-------------|--------------|
| Stopped | N/A | N/A |
| Starting | Empty | Initializing |
| Running | Empty | Degraded |
| Running | Indexing | Indexing |
| Running | Ready | Healthy |
| Running | Updating | Indexing |
| Running | Failed | Degraded |
| Stopping | Any | N/A |
