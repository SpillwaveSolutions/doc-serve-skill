# Plan: Server-Side Indexing Job Queue

## Problem Statement

The Agent Brain server currently rejects concurrent indexing requests with 409 errors and returns 500 errors on status endpoints during indexing. This forces users to manually orchestrate sequential requests with sleeps and retries.

**Observed Issues (from user session)**:
- `agent-brain index ./dir1` → Success
- `agent-brain index ./dir2` → 409 "Indexing already in progress"
- `agent-brain status` → 500 Internal Server Error (during indexing)
- Timeouts on index requests when server is busy

## Solution Overview

Implement a server-side job queue with JSONL persistence that:
1. Accepts all valid indexing requests immediately (202 Accepted)
2. Queues jobs for FIFO processing by a background worker
3. Provides status endpoints that never block or error during indexing
4. Persists queue state for crash recovery
5. Handles edge cases: deduplication, backpressure, timeouts, cancellation

---

## Architecture

```
POST /index (202) → JobQueueService.enqueue() → JobQueueStore (JSONL+flock)
                                                      ↓
                                              JobWorker (background)
                                                      ↓
                                              IndexingService._run_indexing_pipeline()
                                                      ↓
                                              Verify Chroma collection → DONE
```

**Key Components**:
- `JobQueueStore` - JSONL persistence with atomic writes + file locking
- `JobWorker` - Background asyncio task, FIFO, concurrency=1, timeout-aware
- `JobQueueService` - API-facing service with deduplication + backpressure

---

## Robustness Features

### 1. Atomic Persistence (Crash Safety)

**Strategy**: Append-only JSONL + checkpoint snapshot + file lock

```python
class JobQueueStore:
    QUEUE_FILE = "index_queue.jsonl"       # Append-only writes
    SNAPSHOT_FILE = "index_queue.snapshot" # Periodic full state
    LOG_FILE = "index_queue.log"           # Human-readable audit

    def __init__(self, state_dir: Path):
        self._asyncio_lock = asyncio.Lock()  # In-process lock
        self._file_lock_path = state_dir / "jobs" / ".queue.lock"

    async def _write_atomic(self, job: JobRecord):
        """Append + fsync for durability."""
        async with self._asyncio_lock:
            with open(self._file_lock_path, "w") as lock_file:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                try:
                    with open(self.queue_path, "a") as f:
                        f.write(job.model_dump_json() + "\n")
                        f.flush()
                        os.fsync(f.fileno())
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    async def _compact(self):
        """Periodic compaction: write snapshot, truncate JSONL."""
        # Write full state to .snapshot.tmp
        # Rename .snapshot.tmp → .snapshot (atomic on POSIX)
        # Truncate JSONL
```

### 2. Deduplication & Idempotency

**Dedupe Key**: `hash(normalize(folder_path) + include_code + patterns)`

```python
class JobRecord(BaseModel):
    dedupe_key: str  # SHA256 of normalized params

class JobQueueService:
    async def enqueue_job(self, request: IndexRequest, force: bool = False):
        dedupe_key = self._compute_dedupe_key(request)

        if not force:
            existing = await self.store.find_by_dedupe_key(dedupe_key)
            if existing and existing.status in (PENDING, RUNNING):
                return JobEnqueueResponse(
                    job_id=existing.id,
                    status=existing.status,
                    message=f"Duplicate: job {existing.id} already {existing.status}",
                    dedupe_hit=True,
                )

        # Normalize path before storing
        normalized_path = str(Path(request.folder_path).resolve())
        # On macOS, also casefold for case-insensitive FS
```

**CLI**: `agent-brain index ./docs --force` to bypass deduplication

### 3. Backpressure (Queue Limits)

```python
MAX_QUEUE_LENGTH = 100  # Configurable via env

@router.post("/", status_code=202)
async def index_documents(request_body: IndexRequest, request: Request):
    stats = await job_service.get_queue_stats()
    if stats["pending"] >= MAX_QUEUE_LENGTH:
        raise HTTPException(
            status_code=429,
            detail=f"Queue full ({stats['pending']} pending). Try again later.",
        )
    # ... enqueue
```

### 4. Timeout / Stuck Jobs

```python
class JobWorker:
    MAX_RUNTIME_SECONDS = 7200  # 2 hours default

    async def _process_job(self, job: JobRecord):
        job.started_at = datetime.now(timezone.utc)
        await self.store.update_job(job)

        try:
            await asyncio.wait_for(
                self._execute_indexing(job),
                timeout=self.MAX_RUNTIME_SECONDS,
            )
        except asyncio.TimeoutError:
            job.status = JobStatus.FAILED
            job.error = f"Timeout after {self.MAX_RUNTIME_SECONDS}s"
            await self.store.update_job(job)
            logger.error(f"Job {job.id} timed out")
```

### 5. Progress Checkpointing

```python
class JobProgress(BaseModel):
    files_processed: int = 0
    files_total: int = 0
    chunks_created: int = 0
    current_file: str = ""
    percent_complete: float = 0.0
    updated_at: datetime

# Persist every N files (e.g., 50)
PROGRESS_CHECKPOINT_INTERVAL = 50

async def progress_callback(current: int, total: int, current_file: str):
    job.progress = JobProgress(
        files_processed=current,
        files_total=total,
        percent_complete=(current / total * 100) if total > 0 else 0,
        current_file=current_file,
        updated_at=datetime.now(timezone.utc),
    )
    if current % PROGRESS_CHECKPOINT_INTERVAL == 0:
        await store.update_job(job)  # Persist checkpoint
```

### 6. Non-Blocking Status Endpoint

```python
@router.get("/status")
async def indexing_status(request: Request) -> IndexingStatus:
    """Never blocks. Reads queue state only."""
    job_service = request.app.state.job_service

    # Get queue stats (reads in-memory or cached)
    queue_status = await job_service.get_queue_status_nonblocking()

    return IndexingStatus(
        indexing_in_progress=queue_status["running"] > 0,
        current_job_id=queue_status["current_job_id"],
        running_time_ms=queue_status.get("running_time_ms"),
        queue_length=queue_status["pending"],
        # ... other fields from vector store (read-only)
    )
```

### 7. Collection Readiness Verification

```python
async def _process_job(self, job: JobRecord):
    # ... execute indexing ...

    # Verify collection exists and has chunks before marking DONE
    try:
        count = await self.indexing_service.vector_store.get_count()
        if count == 0:
            raise RuntimeError("Collection empty after indexing")
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error = f"Collection verification failed: {e}"
        await self.store.update_job(job)
        return

    job.status = JobStatus.DONE
    job.total_chunks = count
    await self.store.update_job(job)
```

### 8. Cancel Semantics

```python
class JobRecord(BaseModel):
    cancel_requested: bool = False  # Flag checked by worker

@router.delete("/{job_id}")
async def cancel_job(job_id: str):
    job = await job_service.get_job(job_id)

    if job.status == JobStatus.PENDING:
        job.status = JobStatus.CANCELLED
        await store.update_job(job)
        return {"status": "cancelled"}

    if job.status == JobStatus.RUNNING:
        job.cancel_requested = True
        await store.update_job(job)
        return {"status": "cancel_requested", "message": "Worker will stop at next checkpoint"}

    raise HTTPException(409, f"Cannot cancel job with status: {job.status}")

# In worker, check periodically:
if job.cancel_requested:
    job.status = JobStatus.CANCELLED
    job.error = "Cancelled by user"
    await self.store.update_job(job)
    return
```

### 9. Path Safety

```python
async def enqueue_job(self, request: IndexRequest, allow_external: bool = False):
    resolved_path = Path(request.folder_path).resolve()
    project_root = self.project_root

    # Check if path is inside project
    if not allow_external:
        try:
            resolved_path.relative_to(project_root)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Path '{request.folder_path}' is outside project. Use --allow-external to override.",
            )
```

**CLI**: `agent-brain index /external/path --allow-external`

### 10. Restart Recovery

```python
async def initialize(self):
    """Load jobs and handle stale RUNNING jobs."""
    await self._load_jobs()

    for job in self._jobs.values():
        if job.status == JobStatus.RUNNING:
            job.retry_count += 1

            if job.retry_count > self.MAX_RETRIES:
                job.status = JobStatus.FAILED
                job.error = f"Max retries ({self.MAX_RETRIES}) exceeded after restart"
                logger.warning(f"Job {job.id} permanently failed after {job.retry_count} retries")
            else:
                job.status = JobStatus.PENDING
                job.started_at = None
                logger.info(f"Job {job.id} reset to PENDING (retry {job.retry_count})")

            await self._persist_job(job)
```

---

## Implementation

### Phase 1: Models & Queue Store

**New File**: `agent-brain-server/agent_brain_server/models/job.py`

```python
class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobProgress(BaseModel):
    files_processed: int = 0
    files_total: int = 0
    chunks_created: int = 0
    current_file: str = ""
    percent_complete: float = 0.0
    updated_at: Optional[datetime] = None

class JobRecord(BaseModel):
    id: str                           # job_<uuid12>
    dedupe_key: str                   # SHA256 for deduplication
    folder_path: str                  # Normalized, resolved path
    include_code: bool = False
    operation: str = "index"          # "index" or "add"
    status: JobStatus = JobStatus.PENDING
    cancel_requested: bool = False    # For graceful cancellation
    enqueued_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    error: Optional[str]
    retry_count: int = 0
    progress: Optional[JobProgress]
    total_chunks: int = 0
    execution_time_ms: Optional[int]
    # Plus: chunk_size, chunk_overlap, recursive, etc.

class JobEnqueueResponse(BaseModel):
    job_id: str
    status: str = "pending"
    queue_position: int
    queue_length: int
    message: str
    dedupe_hit: bool = False
```

**New File**: `agent-brain-server/agent_brain_server/queue/job_store.py`

```python
class JobQueueStore:
    """JSONL-based persistent job queue with atomic writes."""

    QUEUE_FILE = "index_queue.jsonl"
    SNAPSHOT_FILE = "index_queue.snapshot"
    LOG_FILE = "index_queue.log"
    MAX_RETRIES = 3
    COMPACT_THRESHOLD = 100  # Compact after N updates

    def __init__(self, state_dir: Path):
        self._asyncio_lock = asyncio.Lock()
        self._file_lock_path = state_dir / "jobs" / ".queue.lock"
        # ...

    async def initialize(self):
        """Load jobs, reset stale RUNNING→PENDING with retry cap."""

    async def append_job(self, job: JobRecord) -> int:
        """Atomic append with fsync, return queue position."""

    async def update_job(self, job: JobRecord):
        """Update job, compact if threshold exceeded."""

    async def find_by_dedupe_key(self, key: str) -> Optional[JobRecord]:
        """Find existing job for deduplication."""

    async def get_pending_jobs(self) -> list[JobRecord]:
        """Get pending jobs in FIFO order."""
```

### Phase 2: Background Worker

**New File**: `agent-brain-server/agent_brain_server/queue/job_worker.py`

```python
class JobWorker:
    """Background worker with timeout, progress, cancellation support."""

    MAX_RETRIES = 3
    POLL_INTERVAL = 2.0
    MAX_RUNTIME_SECONDS = 7200  # 2 hours
    PROGRESS_CHECKPOINT_INTERVAL = 50

    async def start(self):
        """Start background task."""

    async def stop(self):
        """Graceful shutdown."""

    async def _run_loop(self):
        """Poll for pending jobs, process one at a time."""

    async def _process_job(self, job: JobRecord):
        """Execute with timeout, progress updates, cancellation checks."""

    async def _verify_collection(self, job: JobRecord) -> bool:
        """Verify Chroma collection exists and has chunks."""
```

### Phase 3: API Changes

**Modify**: `agent-brain-server/agent_brain_server/api/routers/index.py`

```python
MAX_QUEUE_LENGTH = 100

@router.post("/", status_code=202)
async def index_documents(
    request_body: IndexRequest,
    request: Request,
    force: bool = Query(False, description="Bypass deduplication"),
    allow_external: bool = Query(False, description="Allow paths outside project"),
):
    """Enqueue indexing job. Returns 429 if queue full."""
    job_service = request.app.state.job_service

    # Backpressure check
    stats = await job_service.get_queue_stats()
    if stats["pending"] >= MAX_QUEUE_LENGTH:
        raise HTTPException(429, f"Queue full ({stats['pending']} pending)")

    result = await job_service.enqueue_job(
        request_body,
        operation="index",
        force=force,
        allow_external=allow_external,
    )
    return IndexResponse(...)
```

**New File**: `agent-brain-server/agent_brain_server/api/routers/jobs.py`

```python
@router.get("/")
async def list_jobs(limit: int = 50, offset: int = 0) -> JobListResponse:
    """List jobs with pagination."""

@router.get("/{job_id}")
async def get_job(job_id: str) -> JobDetailResponse:
    """Get job detail including progress and running time."""

@router.delete("/{job_id}")
async def cancel_job(job_id: str):
    """Cancel PENDING immediately, set flag for RUNNING."""
```

### Phase 4: CLI Changes

**New File**: `agent-brain-cli/agent_brain_cli/commands/jobs.py`

```python
@click.command("jobs")
@click.argument("job_id", required=False)
@click.option("--watch", is_flag=True, help="Poll every 3 seconds")
@click.option("--limit", default=20, help="Max jobs to show")
def jobs_command(job_id, watch, limit):
    """View job queue and status.

    Without JOB_ID: List all jobs
    With JOB_ID: Show job details
    """
    if watch:
        while True:
            # Clear screen, show jobs, sleep 3s
```

**Modify**: `agent-brain-cli/agent_brain_cli/commands/index.py`

```python
@click.option("--force", is_flag=True, help="Bypass deduplication")
@click.option("--allow-external", is_flag=True, help="Allow paths outside project")

# Update output:
console.print("[green]Job queued![/]")  # "queued" not "started"
console.print(f"Job ID: {response.job_id}")
if response.dedupe_hit:
    console.print(f"[yellow]Duplicate detected - watching existing job[/]")
console.print(f"Queue Position: {response.queue_position} of {response.queue_length}")
console.print("[dim]Use 'agent-brain jobs' or 'agent-brain jobs --watch' to monitor.[/]")
```

**Modify**: `agent-brain-cli/agent_brain_cli/client/api_client.py`

```python
# Increase default timeout for index operations
INDEX_TIMEOUT = 120.0  # 2 minutes
QUERY_TIMEOUT = 30.0   # 30 seconds (unchanged)
```

---

## Files Summary

### New Files (7)
| File | Purpose |
|------|---------|
| `agent-brain-server/.../models/job.py` | Pydantic models with dedupe_key, cancel_requested |
| `agent-brain-server/.../queue/__init__.py` | Queue module |
| `agent-brain-server/.../queue/job_store.py` | JSONL persistence with flock + atomic writes |
| `agent-brain-server/.../queue/job_worker.py` | Background worker with timeout + progress |
| `agent-brain-server/.../queue/job_service.py` | API service with deduplication + backpressure |
| `agent-brain-server/.../api/routers/jobs.py` | Job endpoints |
| `agent-brain-cli/.../commands/jobs.py` | CLI jobs command with --watch |

### Modified Files (9)
| File | Changes |
|------|---------|
| `agent-brain-server/.../models/__init__.py` | Export job models |
| `agent-brain-server/.../models/index.py` | Add queue_position, dedupe_hit |
| `agent-brain-server/.../models/health.py` | Add queue fields, running_time_ms |
| `agent-brain-server/.../api/routers/index.py` | Enqueue + backpressure + path validation |
| `agent-brain-server/.../api/routers/health.py` | Non-blocking queue status |
| `agent-brain-server/.../api/main.py` | Initialize queue system |
| `agent-brain-cli/.../commands/index.py` | --force, --allow-external, 120s timeout |
| `agent-brain-cli/.../commands/status.py` | Show queue info |
| `agent-brain-cli/.../client/api_client.py` | Separate timeouts for index vs query |

---

## API Changes Summary

| Endpoint | Before | After |
|----------|--------|-------|
| `POST /index` | 409 if busy | 202 (queued), 429 if full |
| `GET /health/status` | 500 during indexing | 200 always (non-blocking) |
| `GET /index/jobs` | N/A | List with pagination |
| `GET /index/jobs/{id}` | N/A | Detail + progress |
| `DELETE /index/jobs/{id}` | N/A | Cancel (flag for running) |

---

## Configuration

| Setting | Default | Environment Variable |
|---------|---------|---------------------|
| Max queue length | 100 | `AGENT_BRAIN_MAX_QUEUE` |
| Max job runtime | 7200s (2h) | `AGENT_BRAIN_JOB_TIMEOUT` |
| Max retries | 3 | `AGENT_BRAIN_MAX_RETRIES` |
| Progress checkpoint | 50 files | `AGENT_BRAIN_CHECKPOINT_INTERVAL` |
| Compact threshold | 100 updates | Internal |

---

## Recovery Behavior

| Scenario | Behavior |
|----------|----------|
| Server restart with RUNNING job | Reset to PENDING, retry_count++ |
| retry_count > MAX_RETRIES | Mark FAILED permanently |
| Job exceeds MAX_RUNTIME | Mark FAILED with timeout error |
| Cancel PENDING job | Immediate CANCELLED |
| Cancel RUNNING job | Set flag, worker checks at checkpoint |
| Collection empty after indexing | Mark FAILED, don't mark DONE |

---

## Verification

### Manual Testing
```bash
# 1. Start server
agent-brain start

# 2. Enqueue multiple jobs (all should return 202)
agent-brain index ./docs &
agent-brain index ./code --include-code &
agent-brain index ./docs  # Should dedupe, return existing job_id

# 3. Watch queue
agent-brain jobs --watch

# 4. Check status (should never 500)
agent-brain status

# 5. Cancel a pending job
agent-brain jobs job_abc123  # Get ID
curl -X DELETE http://localhost:8001/index/jobs/job_abc123

# 6. Test backpressure (fill queue)
for i in {1..101}; do agent-brain index ./test$i &; done
# 101st should return 429
```

### Automated Tests
- **Unit**: JobQueueStore persistence, FIFO ordering, stale job reset, deduplication
- **Integration**: POST /index returns 202, backpressure returns 429
- **E2E**: Enqueue 3 jobs, restart server mid-run, verify all complete after restart
- **Timeout**: Enqueue job with MAX_RUNTIME=5s, verify it fails with timeout

---

## Success Criteria

| Metric | Target |
|--------|--------|
| POST /index returns 202 | Always (valid paths, queue not full) |
| POST /index returns 429 | When queue >= MAX_QUEUE_LENGTH |
| GET /health/status during indexing | 200 (never 500) |
| Jobs processed FIFO | Yes |
| Crash recovery works | RUNNING→PENDING on restart |
| Duplicate requests | Return existing job_id |
| Stuck jobs | Timeout after MAX_RUNTIME |
| Collection verification | DONE only if chunks > 0 |
| CLI shows queue status | Yes, with --watch option |
