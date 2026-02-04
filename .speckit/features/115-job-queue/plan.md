# Implementation Plan: Server-Side Indexing Job Queue

**Branch**: `115-job-queue` | **Date**: 2026-02-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `.speckit/features/115-job-queue/spec.md`

## Summary

Implement a server-side job queue for indexing operations that accepts all valid requests immediately (202 Accepted), queues them for FIFO processing by a background asyncio worker, and provides status/management endpoints. The queue uses JSONL persistence with fcntl file locking for crash recovery. Key features include deduplication, backpressure (max 100 jobs), timeout handling (2h), and a CLI `agent-brain jobs` command.

## Technical Context

**Language/Version**: Python 3.10+ (existing: ^3.10 in pyproject.toml)
**Primary Dependencies**: FastAPI, Pydantic, asyncio (no new external dependencies)
**Storage**: JSONL file with fcntl locking (consistent with existing locking.py pattern)
**Testing**: pytest with pytest-asyncio
**Target Platform**: Linux/macOS server, local development
**Project Type**: Monorepo with agent-brain-server and agent-brain-cli packages
**Performance Goals**: Queue operations <10ms, no blocking on status endpoints
**Constraints**: Must maintain backward compatibility with existing /index endpoint behavior
**Scale/Scope**: Max 100 queued jobs, concurrency=1, 2-hour timeout per job

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence/Notes |
|-----------|--------|----------------|
| **I. Monorepo Modularity** | PASS | JobQueueService lives in server; CLI adds new command without importing server internals |
| **II. OpenAPI-First** | PASS | New endpoints documented in OpenAPI; existing POST /index maintains 202 contract |
| **III. Test-Alongside** | PASS | Plan includes unit tests for store, worker, service; integration tests for queue flow |
| **IV. Observability** | PASS | Jobs expose status, progress, timing; existing /health/status enhanced |
| **V. Simplicity** | PASS | Uses existing asyncio patterns, no new dependencies, JSONL is simplest persistence |

**Technology Stack Compliance**:
- FastAPI: PASS - New router for /index/jobs endpoints
- Pydantic: PASS - New models for IndexJob, JobStatus
- asyncio: PASS - Background worker uses existing patterns from IndexingService
- File locking: PASS - Reuses fcntl pattern from existing locking.py
- No new dependencies: PASS - All functionality achievable with stdlib + existing deps

## Project Structure

### Documentation (this feature)

```text
.speckit/features/115-job-queue/
├── plan.md              # This file
├── spec.md              # Feature specification
├── data-model.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   └── api-extensions.md
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
agent-brain-server/
├── agent_brain_server/
│   ├── models/
│   │   ├── __init__.py         # Export new models
│   │   ├── index_job.py        # NEW: IndexJob, JobStatus, JobListResponse
│   │   └── ...
│   ├── services/
│   │   ├── __init__.py         # Export new service
│   │   ├── job_queue_service.py    # NEW: JobQueueService (API-facing)
│   │   ├── indexing_service.py # MODIFIED: Remove single-job constraint
│   │   └── ...
│   ├── queue/                  # NEW: Job queue subsystem
│   │   ├── __init__.py
│   │   ├── store.py            # JobQueueStore (JSONL persistence)
│   │   └── worker.py           # JobWorker (background asyncio task)
│   ├── api/
│   │   ├── routers/
│   │   │   ├── __init__.py     # Export new router
│   │   │   ├── jobs.py         # NEW: /index/jobs endpoints
│   │   │   └── index.py        # MODIFIED: Delegate to JobQueueService
│   │   └── main.py             # MODIFIED: Initialize JobWorker on startup
│   └── ...
└── tests/
    ├── unit/
    │   ├── queue/              # NEW: Queue subsystem tests
    │   │   ├── test_store.py
    │   │   ├── test_worker.py
    │   │   └── test_service.py
    │   └── ...
    └── integration/
        └── test_job_queue_flow.py  # NEW: End-to-end queue tests

agent-brain-cli/
├── agent_brain_cli/
│   ├── commands/
│   │   ├── __init__.py         # Export new command
│   │   └── jobs.py             # NEW: agent-brain jobs command
│   └── cli.py                  # MODIFIED: Register jobs command
└── tests/
    └── test_jobs_command.py    # NEW: CLI command tests
```

**Structure Decision**: New `queue/` package isolates persistence and worker logic from the API-facing service. This separation enables independent testing and potential future extraction to a shared library.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| New `queue/` package (3 files) | Separation of concerns: store (persistence), worker (processing), service (API) | Single file would exceed 400 LOC and mix persistence, concurrency, and API concerns |
| JSONL + fcntl instead of SQLite | Consistent with existing locking.py pattern; simpler for append-only queue | SQLite would add dependency and complexity for simple FIFO queue |

## Phase 0: Research Summary

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| JSONL persistence | Append-only, human-readable, trivial to implement | SQLite (overkill), Redis (new dependency), pickle (not human-readable) |
| fcntl file locking | Consistent with existing locking.py, cross-process safe | Advisory locks only (less safe), separate lock manager (more complex) |
| Asyncio background task | Consistent with existing IndexingService pattern | Celery (overkill), multiprocessing (coordination overhead) |
| In-memory cache + periodic sync | Fast status queries without file I/O on every call | Read-through cache (more complex), no cache (slow) |
| Concurrency=1 | Avoids resource contention (embeddings, vector store writes) | Thread pool (race conditions), multiple workers (coordination) |

### Persistence Format

**JSONL File Structure** (`queue/jobs.jsonl`):
```jsonl
{"id": "job_abc123", "status": "completed", "folder_path": "/docs", "created_at": "...", ...}
{"id": "job_def456", "status": "queued", "folder_path": "/code", "created_at": "...", ...}
```

Operations:
- **Add job**: Append new line (O(1))
- **Update status**: Rewrite file with updated entry (O(n), acceptable for n<=100)
- **Load on startup**: Read all lines, filter to active jobs
- **Compaction**: Remove completed jobs older than 24h on startup

### Concurrency Model

```
API Request → JobQueueService.submit_job() → JobQueueStore.add() → queue.jsonl
                                                    ↓
                                            in-memory job list
                                                    ↓
                    JobWorker ← asyncio.Event (notify) ← new job added
                        ↓
                IndexingService.start_indexing()
                        ↓
                JobQueueStore.update_status()
```

## Phase 1: Design Artifacts

### Data Model

**IndexJob** (Pydantic model):
```python
class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class IndexJob(BaseModel):
    id: str                          # UUID-based, e.g., "job_abc123"
    status: JobStatus
    folder_path: str                 # Absolute path
    request: IndexRequest            # Original request for replay on restart
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error: Optional[str]
    progress_percent: int = 0
    total_documents: int = 0
    processed_documents: int = 0
    queue_position: Optional[int]    # Only for queued jobs
```

**JobListResponse**:
```python
class JobListResponse(BaseModel):
    jobs: list[IndexJob]
    total: int
    queued_count: int
    running_count: int
```

### API Contracts

**New Endpoints**:

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/index/jobs` | GET | List all jobs | JobListResponse |
| `/index/jobs/{id}` | GET | Get job by ID | IndexJob |
| `/index/jobs/{id}` | DELETE | Cancel queued job | 200/404/409/410 |

**Modified Endpoint**:

| Endpoint | Method | Change |
|----------|--------|--------|
| `/index` | POST | Always returns 202, delegates to queue (removes 409 Conflict) |

### CLI Commands

```bash
# List all jobs
agent-brain jobs

# Get specific job details
agent-brain jobs <job_id>

# Watch mode (updates every 2s)
agent-brain jobs --watch

# Cancel a queued job
agent-brain jobs --cancel <job_id>
```

## Implementation Phases

### Phase 2: Tasks (Generated by /speckit.tasks)

Tasks will be generated covering:
1. Create IndexJob and JobStatus models
2. Implement JobQueueStore with JSONL persistence + fcntl locking
3. Implement JobWorker as background asyncio task
4. Implement JobQueueService with deduplication + backpressure
5. Add /index/jobs router with GET, DELETE endpoints
6. Modify /index endpoint to delegate to JobQueueService
7. Initialize JobWorker in server lifespan
8. Add CLI jobs command with list, status, cancel, watch
9. Write unit tests for store, worker, service
10. Write integration tests for full queue flow

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| File corruption on crash mid-write | Low | Medium | Atomic write pattern (write to .tmp, rename) |
| Race condition between API and worker | Medium | High | Asyncio lock on job list, single-threaded worker |
| Queue grows unbounded | Low | Medium | Enforce max 100 limit, 503 when full |
| Job stuck forever | Low | Medium | 2-hour timeout, health check detects stuck worker |
| Backward compatibility broken | Low | High | Existing tests verify /index still returns 202 |

## Dependencies

**No new Python packages required.**

Uses existing:
- `pydantic` - Job models
- `asyncio` - Background worker
- `fcntl` - File locking (consistent with locking.py)
- `click` + `rich` - CLI jobs command

## Success Metrics

- [ ] POST /index always returns 202 Accepted (not 409)
- [ ] Jobs process in FIFO order (verified by integration test)
- [ ] Server restart recovers pending jobs (verified by test)
- [ ] Queue operations complete in <10ms (verified by benchmark)
- [ ] CLI `agent-brain jobs` works with list, status, cancel, watch
- [ ] All existing tests pass (backward compatibility)
- [ ] Test coverage does not decrease
