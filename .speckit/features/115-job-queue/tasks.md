# Tasks: Server-Side Indexing Job Queue

**Input**: Design documents from `.speckit/features/115-job-queue/`
**Prerequisites**: plan.md, spec.md

**Tests**: Tests are REQUIRED per constitution principle III (Test-Alongside). Unit tests for store, worker, service; integration tests for queue flow.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

**Server paths** (relative to `agent-brain-server/`):
- Source: `agent_brain_server/`
- Tests: `tests/`

**CLI paths** (relative to `agent-brain-cli/`):
- Source: `agent_brain_cli/`
- Tests: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and package structure

- [ ] T001 Create queue package structure in `agent_brain_server/queue/__init__.py`
- [ ] T002 [P] Create tests directory structure in `agent-brain-server/tests/unit/queue/`
- [ ] T003 [P] Create integration tests directory in `agent-brain-server/tests/integration/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and persistence infrastructure that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

### Data Models (from plan.md)

- [ ] T004 [P] Create `JobStatus` enum in `agent_brain_server/models/index_job.py`:
  - QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED values
  - Inherit from str, Enum for JSON serialization
- [ ] T005 [P] Create `IndexJob` Pydantic model in `agent_brain_server/models/index_job.py`:
  - Fields: id, status, folder_path, request (IndexRequest), created_at, started_at, completed_at, error, progress_percent, total_documents, processed_documents, queue_position
  - Validators for datetime fields
  - `to_jsonl()` and `from_jsonl()` methods for persistence
- [ ] T006 [P] Create `JobListResponse` Pydantic model in `agent_brain_server/models/index_job.py`:
  - Fields: jobs (list[IndexJob]), total, queued_count, running_count
- [ ] T007 Export new models from `agent_brain_server/models/__init__.py`

### Persistence Layer

- [ ] T008 Create `JobQueueStore` class in `agent_brain_server/queue/store.py`:
  - Constructor accepts `persist_dir: Path` (defaults to state_dir/queue/)
  - `JOBS_FILE = "jobs.jsonl"` constant
  - `_jobs: dict[str, IndexJob]` in-memory cache
  - `_lock: asyncio.Lock` for thread safety
- [ ] T009 Implement `JobQueueStore._acquire_file_lock()` in `agent_brain_server/queue/store.py`:
  - Use fcntl.LOCK_EX for exclusive write lock
  - Use fcntl.LOCK_SH for shared read lock
  - Consistent pattern with existing `locking.py`
- [ ] T010 Implement `JobQueueStore.load()` in `agent_brain_server/queue/store.py`:
  - Read jobs.jsonl on startup
  - Filter to active jobs (queued, running)
  - Reset "running" jobs to "queued" (crash recovery)
  - Compact: remove completed jobs older than 24h
  - Populate in-memory cache
- [ ] T011 Implement `JobQueueStore.add()` in `agent_brain_server/queue/store.py`:
  - Append new job to JSONL file
  - Atomic write: write to .tmp, then rename
  - Update in-memory cache
  - Return job ID
- [ ] T012 Implement `JobQueueStore.update()` in `agent_brain_server/queue/store.py`:
  - Update job status in file (rewrite with updated entry)
  - Use file locking during write
  - Update in-memory cache
- [ ] T013 Implement `JobQueueStore.get()` in `agent_brain_server/queue/store.py`:
  - Return job from in-memory cache (fast, no file I/O)
  - Return None if not found
- [ ] T014 Implement `JobQueueStore.list()` in `agent_brain_server/queue/store.py`:
  - Return all jobs from in-memory cache
  - Support optional status filter
  - Calculate queue_position for queued jobs
- [ ] T015 Implement `JobQueueStore.remove()` in `agent_brain_server/queue/store.py`:
  - Mark job as CANCELLED in file
  - Update in-memory cache
  - Return True if removed, False if not found or not cancellable

### Unit Tests for Foundation

- [ ] T016 [P] Unit test for `IndexJob` serialization in `tests/unit/queue/test_models.py`:
  - Test to_jsonl() produces valid JSON
  - Test from_jsonl() reconstructs model
  - Test datetime handling
- [ ] T017 [P] Unit test for `JobQueueStore.add()` in `tests/unit/queue/test_store.py`:
  - Test job added to file and cache
  - Test file contains valid JSONL
- [ ] T018 [P] Unit test for `JobQueueStore.load()` in `tests/unit/queue/test_store.py`:
  - Test loading from existing file
  - Test empty file handling
  - Test corrupted line skipping
  - Test running -> queued reset
- [ ] T019 [P] Unit test for `JobQueueStore.update()` in `tests/unit/queue/test_store.py`:
  - Test status transition
  - Test file is updated correctly
- [ ] T020 [P] Unit test for `JobQueueStore.remove()` in `tests/unit/queue/test_store.py`:
  - Test cancellation of queued job
  - Test rejection of running job
  - Test not found handling

**Checkpoint**: Foundation ready - models and persistence in place

---

## Phase 3: User Story 1 - Submit Indexing Request Without Blocking (Priority: P1)

**Goal**: Users can submit multiple indexing requests that are queued for FIFO processing

**Independent Test**: Submit 3 requests rapidly, verify all return 202, verify FIFO processing order

### Tests for User Story 1

- [ ] T021 [P] [US1] Integration test for FIFO ordering in `tests/integration/test_job_queue_flow.py`:
  - Submit jobs A, B, C
  - Verify completion order is A, B, C
- [ ] T022 [P] [US1] Unit test for `JobQueueService.submit_job()` in `tests/unit/queue/test_service.py`:
  - Test valid request returns job with "queued" status
  - Test invalid path rejected before queueing

### Implementation for User Story 1

- [ ] T023 [US1] Create `JobQueueService` class in `agent_brain_server/services/job_queue_service.py`:
  - Constructor accepts `store: JobQueueStore`, `indexing_service: IndexingService`
  - `MAX_QUEUE_SIZE = 100` constant
  - `_worker_event: asyncio.Event` for signaling new jobs
- [ ] T024 [US1] Implement `JobQueueService.submit_job()` in `agent_brain_server/services/job_queue_service.py`:
  - Validate folder path exists (raise HTTPException 400 if not)
  - Check queue size (raise HTTPException 503 if full - US6)
  - Check for duplicate (raise HTTPException 409 if duplicate - US9)
  - Create IndexJob with status=QUEUED
  - Call store.add()
  - Signal worker via event
  - Return job
- [ ] T025 [US1] Create `JobWorker` class in `agent_brain_server/queue/worker.py`:
  - Constructor accepts `store: JobQueueStore`, `indexing_service: IndexingService`
  - `_running: bool` flag for graceful shutdown
  - `_event: asyncio.Event` for job notification
  - `TIMEOUT_HOURS = 2` constant
- [ ] T026 [US1] Implement `JobWorker.start()` in `agent_brain_server/queue/worker.py`:
  - Start background asyncio task via `asyncio.create_task()`
  - Set _running = True
- [ ] T027 [US1] Implement `JobWorker.stop()` in `agent_brain_server/queue/worker.py`:
  - Set _running = False
  - Set event to wake up blocked wait
  - Wait for current job to complete (graceful)
- [ ] T028 [US1] Implement `JobWorker._run()` in `agent_brain_server/queue/worker.py`:
  - Main loop: while _running
  - Get next queued job from store
  - If no job, wait on event with timeout
  - If job, process it via _process_job()
- [ ] T029 [US1] Implement `JobWorker._process_job()` in `agent_brain_server/queue/worker.py`:
  - Update job status to RUNNING
  - Create progress callback that updates job progress
  - Call indexing_service.start_indexing() with progress callback
  - On success: update status to COMPLETED
  - On failure: update status to FAILED with error
  - Handle timeout (US7) via asyncio.wait_for()
- [ ] T030 [US1] Modify `POST /index` in `agent_brain_server/api/routers/index.py`:
  - Remove `is_indexing` check (no more 409)
  - Delegate to `job_queue_service.submit_job()`
  - Return 202 with job_id from new job
- [ ] T031 [US1] Modify `POST /index/add` in `agent_brain_server/api/routers/index.py`:
  - Same changes as POST /index
  - Delegate to job_queue_service.submit_job()
- [ ] T032 [US1] Initialize JobQueueService and JobWorker in `agent_brain_server/api/main.py`:
  - Create JobQueueStore with state_dir
  - Create JobQueueService with store and indexing_service
  - Create JobWorker with store and indexing_service
  - Call store.load() on startup
  - Call worker.start() on startup
  - Call worker.stop() on shutdown
  - Store service on app.state for DI

**Checkpoint**: User Story 1 complete - indexing requests queue without blocking

---

## Phase 4: User Story 2 - Monitor Job Status (Priority: P1)

**Goal**: Users can check job status including queue position and progress

**Independent Test**: Submit job, poll GET /index/jobs/{id}, verify state transitions

### Tests for User Story 2

- [ ] T033 [P] [US2] Unit test for `GET /index/jobs/{id}` in `tests/unit/api/test_jobs_router.py`:
  - Test queued job returns status with queue_position
  - Test running job returns progress_percent
  - Test completed job returns completed_at
  - Test 404 for unknown job_id

### Implementation for User Story 2

- [ ] T034 [US2] Create jobs router in `agent_brain_server/api/routers/jobs.py`:
  - `router = APIRouter()`
- [ ] T035 [US2] Implement `GET /index/jobs/{job_id}` in `agent_brain_server/api/routers/jobs.py`:
  - Get job from job_queue_service.get_job(job_id)
  - Return 404 if not found
  - Return IndexJob model
- [ ] T036 [US2] Implement `JobQueueService.get_job()` in `agent_brain_server/services/job_queue_service.py`:
  - Delegate to store.get()
  - Return None if not found
- [ ] T037 [US2] Register jobs router in `agent_brain_server/api/main.py`:
  - Import jobs_router from routers
  - Include with prefix="/index/jobs"
- [ ] T038 [US2] Export jobs_router from `agent_brain_server/api/routers/__init__.py`

**Checkpoint**: User Story 2 complete - job status endpoint works

---

## Phase 5: User Story 3 - List All Jobs (Priority: P1)

**Goal**: Users can see all pending and recent jobs

**Independent Test**: Submit multiple jobs, call GET /index/jobs, verify list

### Tests for User Story 3

- [ ] T039 [P] [US3] Unit test for `GET /index/jobs` in `tests/unit/api/test_jobs_router.py`:
  - Test returns all jobs
  - Test status filter works
  - Test empty list when no jobs

### Implementation for User Story 3

- [ ] T040 [US3] Implement `GET /index/jobs` in `agent_brain_server/api/routers/jobs.py`:
  - Optional query param: status (filter by job status)
  - Get jobs from job_queue_service.list_jobs()
  - Return JobListResponse
- [ ] T041 [US3] Implement `JobQueueService.list_jobs()` in `agent_brain_server/services/job_queue_service.py`:
  - Delegate to store.list()
  - Calculate queue_position for each queued job
  - Return JobListResponse with counts

**Checkpoint**: User Story 3 complete - job list endpoint works

---

## Phase 6: User Story 4 - Cancel Pending Job (Priority: P2)

**Goal**: Users can cancel jobs that are still in the queue

**Independent Test**: Submit 2 jobs, cancel second, verify removed

### Tests for User Story 4

- [ ] T042 [P] [US4] Unit test for `DELETE /index/jobs/{id}` in `tests/unit/api/test_jobs_router.py`:
  - Test cancel queued job returns 200
  - Test cancel running job returns 409
  - Test cancel completed job returns 410
  - Test unknown job returns 404

### Implementation for User Story 4

- [ ] T043 [US4] Implement `DELETE /index/jobs/{job_id}` in `agent_brain_server/api/routers/jobs.py`:
  - Get job from service
  - Return 404 if not found
  - Return 409 if running (cannot cancel)
  - Return 410 if completed/failed (already done)
  - Call job_queue_service.cancel_job()
  - Return 200 on success
- [ ] T044 [US4] Implement `JobQueueService.cancel_job()` in `agent_brain_server/services/job_queue_service.py`:
  - Validate job is cancellable (status == QUEUED)
  - Delegate to store.remove()
  - Return success

**Checkpoint**: User Story 4 complete - job cancellation works

---

## Phase 7: User Story 5 - Server Crash Recovery (Priority: P2)

**Goal**: Pending jobs survive server restarts

**Independent Test**: Submit jobs, kill server, restart, verify recovery

### Tests for User Story 5

- [ ] T045 [US5] Integration test for crash recovery in `tests/integration/test_job_queue_flow.py`:
  - Submit job to queue
  - Simulate server restart (reinitialize store)
  - Verify job is recovered with status "queued"
  - Verify running job reset to queued

### Implementation for User Story 5

- [ ] T046 [US5] Enhance `JobQueueStore.load()` crash recovery in `agent_brain_server/queue/store.py`:
  - Reset any "running" jobs to "queued" (was mid-processing)
  - Log recovered jobs for observability
  - Handle corrupted JSONL lines gracefully (skip, log warning)

**Checkpoint**: User Story 5 complete - crash recovery works

---

## Phase 8: User Story 6 - Backpressure Protection (Priority: P2)

**Goal**: System rejects requests when queue is full

**Independent Test**: Submit 101 jobs, verify 101st returns 503

### Tests for User Story 6

- [ ] T047 [P] [US6] Unit test for backpressure in `tests/unit/queue/test_service.py`:
  - Mock store with 100 jobs
  - Verify submit_job raises HTTPException 503

### Implementation for User Story 6

- [ ] T048 [US6] Add backpressure check in `JobQueueService.submit_job()`:
  - Check len(store.list(status=QUEUED)) >= MAX_QUEUE_SIZE
  - Raise HTTPException 503 "Queue full, try again later"

**Checkpoint**: User Story 6 complete - backpressure protection works

---

## Phase 9: User Story 7 - Job Timeout Handling (Priority: P3)

**Goal**: Long-running jobs are detected and marked as failed

**Independent Test**: Configure short timeout, verify job fails after timeout

### Tests for User Story 7

- [ ] T049 [P] [US7] Unit test for timeout in `tests/unit/queue/test_worker.py`:
  - Mock slow indexing service
  - Verify job marked as FAILED with timeout error

### Implementation for User Story 7

- [ ] T050 [US7] Add timeout handling in `JobWorker._process_job()`:
  - Wrap indexing call with asyncio.wait_for(timeout=TIMEOUT_HOURS*3600)
  - On TimeoutError: update job status to FAILED with "Job timed out after 2 hours"

**Checkpoint**: User Story 7 complete - timeout handling works

---

## Phase 10: User Story 8 - CLI Job Monitoring (Priority: P2)

**Goal**: CLI command for job queue management

**Independent Test**: Run `agent-brain jobs`, verify output

### Tests for User Story 8

- [ ] T051 [P] [US8] Unit test for `agent-brain jobs` in `agent-brain-cli/tests/test_jobs_command.py`:
  - Test list output format
  - Test --watch flag
  - Test --cancel flag
  - Test job_id argument for details

### Implementation for User Story 8

- [ ] T052 [US8] Create `jobs_command` in `agent_brain_cli/commands/jobs.py`:
  - `@click.command()` with options: --watch, --cancel
  - Optional argument: job_id
- [ ] T053 [US8] Implement job list display in `agent_brain_cli/commands/jobs.py`:
  - Call GET /index/jobs
  - Display table with ID, Status, Folder, Progress, Created
  - Use Rich for formatting
- [ ] T054 [US8] Implement job detail display in `agent_brain_cli/commands/jobs.py`:
  - When job_id provided, call GET /index/jobs/{job_id}
  - Display detailed job info with all fields
- [ ] T055 [US8] Implement --watch mode in `agent_brain_cli/commands/jobs.py`:
  - Loop with 2-second interval
  - Clear and redraw table
  - Handle Ctrl+C gracefully
- [ ] T056 [US8] Implement --cancel in `agent_brain_cli/commands/jobs.py`:
  - Call DELETE /index/jobs/{job_id}
  - Display result message
- [ ] T057 [US8] Register jobs command in `agent_brain_cli/cli.py`:
  - Import jobs_command
  - Add to CLI group

**Checkpoint**: User Story 8 complete - CLI jobs command works

---

## Phase 11: User Story 9 - Duplicate Job Prevention (Priority: P2)

**Goal**: Prevent duplicate jobs for same folder path

**Independent Test**: Submit same folder twice, verify second returns 409

### Tests for User Story 9

- [ ] T058 [P] [US9] Unit test for deduplication in `tests/unit/queue/test_service.py`:
  - Submit job for /path/a
  - Submit again for /path/a
  - Verify 409 Conflict

### Implementation for User Story 9

- [ ] T059 [US9] Add deduplication check in `JobQueueService.submit_job()`:
  - Check if any job with same normalized folder_path is QUEUED or RUNNING
  - Raise HTTPException 409 "Duplicate job for this folder already in queue"

**Checkpoint**: User Story 9 complete - deduplication works

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [ ] T060 [P] Update OpenAPI documentation for new endpoints in `agent_brain_server/api/routers/jobs.py`:
  - Add docstrings with response descriptions
  - Add example responses
- [ ] T061 [P] Update health endpoint to include queue status in `agent_brain_server/api/routers/health.py`:
  - Add queued_jobs_count to status response
  - Add running_job_id if applicable
- [ ] T062 [P] Update USER_GUIDE.md with job queue section in `docs/USER_GUIDE.md`
- [ ] T063 [P] Update CLI help text for jobs command
- [ ] T064 Run `task before-push` to validate all tests pass
- [ ] T065 Run existing integration tests to verify backward compatibility
- [ ] T066 Manual validation: submit multiple jobs, verify FIFO, test crash recovery

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──────────────────────────────────────────────────────┐
                                                                       │
Phase 2 (Foundational - Models + Store) ◀─────────────────────────────┘
    │
    ├───► Phase 3 (US1: Submit + Worker) ─────────────────────────────┐
    │                                                                   │
    ├───► Phase 4 (US2: Status Endpoint) ─────────────────────────────┤
    │                                                                   │
    └───► Phase 5 (US3: List Endpoint) ───────────────────────────────┤
                                                                       │
                                                                       ▼
    Phase 6 (US4: Cancel) ◀───────────────────────────────────────────┤
                                                                       │
    Phase 7 (US5: Crash Recovery) ◀───────────────────────────────────┤
                                                                       │
    Phase 8 (US6: Backpressure) ◀─────────────────────────────────────┤
                                                                       │
    Phase 9 (US7: Timeout) ◀──────────────────────────────────────────┤
                                                                       │
    Phase 10 (US8: CLI) ◀─────────────────────────────────────────────┤
                                                                       │
    Phase 11 (US9: Deduplication) ◀───────────────────────────────────┘
        │
        ▼
    Phase 12 (Polish)
```

### User Story Dependencies

- **US1 (Submit + Queue)**: Depends on Phase 2 (Models + Store) - Core functionality
- **US2 (Status Endpoint)**: Depends on Phase 2 - Can run parallel with US1
- **US3 (List Endpoint)**: Depends on Phase 2 - Can run parallel with US1
- **US4 (Cancel)**: Depends on US1 (need jobs to cancel)
- **US5 (Crash Recovery)**: Depends on US1 (need store.load() to test)
- **US6 (Backpressure)**: Depends on US1 (enhancement to submit_job)
- **US7 (Timeout)**: Depends on US1 (enhancement to worker)
- **US8 (CLI)**: Depends on US2, US3, US4 (needs API endpoints)
- **US9 (Deduplication)**: Depends on US1 (enhancement to submit_job)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints/CLI
- Core implementation before enhancements

### Parallel Opportunities

**Phase 1 (Setup):**
```bash
T002, T003  # Directory creation can run in parallel
```

**Phase 2 (Foundational):**
```bash
T004, T005, T006  # Models can run in parallel
T016, T017, T018, T019, T020  # Unit tests can run in parallel
```

**Phase 3-5 (US1, US2, US3):**
```bash
# US2 and US3 endpoint implementations can run in parallel after Phase 2
T034-T041  # Endpoints don't depend on each other
```

**Phase 10 (CLI):**
```bash
T052, T053, T054, T055, T056  # CLI commands can be developed in parallel
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: US1 - Submit + Worker
4. Complete Phase 4: US2 - Status Endpoint
5. Complete Phase 5: US3 - List Endpoint
6. **STOP and VALIDATE**: All core queue functionality works
7. Deploy/demo if ready

**MVP delivers**: Non-blocking indexing with FIFO queue, status monitoring

### Full Feature (Add US4-US9)

1. Complete MVP (Phases 1-5)
2. Complete Phase 6: US4 - Cancel
3. Complete Phase 7: US5 - Crash Recovery
4. Complete Phase 8: US6 - Backpressure
5. Complete Phase 9: US7 - Timeout
6. Complete Phase 10: US8 - CLI
7. Complete Phase 11: US9 - Deduplication
8. Complete Phase 12: Polish

### Parallel Team Strategy

With 2 developers after Phase 2:

- **Developer A**: US1 (Worker) → US4 (Cancel) → US7 (Timeout)
- **Developer B**: US2 (Status) + US3 (List) → US5 (Recovery) → US8 (CLI)

---

## Task Summary

| Phase | Description | Task Count | Blocking |
|-------|-------------|------------|----------|
| 1 | Setup | 3 | No |
| 2 | Foundational (Models + Store) | 17 | YES |
| 3 | US1: Submit + Worker | 12 | YES (for US4-9) |
| 4 | US2: Status Endpoint | 6 | No |
| 5 | US3: List Endpoint | 3 | No |
| 6 | US4: Cancel | 3 | No |
| 7 | US5: Crash Recovery | 2 | No |
| 8 | US6: Backpressure | 2 | No |
| 9 | US7: Timeout | 2 | No |
| 10 | US8: CLI | 7 | No |
| 11 | US9: Deduplication | 2 | No |
| 12 | Polish | 7 | No |
| **Total** | | **66** | |

### Tasks per User Story

- **US1 (Submit + Worker)**: 12 tasks (core)
- **US2 (Status Endpoint)**: 6 tasks
- **US3 (List Endpoint)**: 3 tasks
- **US4 (Cancel)**: 3 tasks
- **US5 (Crash Recovery)**: 2 tasks
- **US6 (Backpressure)**: 2 tasks
- **US7 (Timeout)**: 2 tasks
- **US8 (CLI)**: 7 tasks
- **US9 (Deduplication)**: 2 tasks

### Parallel Opportunities

- **Phase 2**: 8 of 17 tasks can run in parallel
- **Phase 3-5**: US2 and US3 can run parallel with US1 after endpoints are ready
- **Phase 10**: 5 of 7 CLI tasks can run in parallel

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing (Test-Alongside principle)
- Commit after each task or logical group
- Run `task before-push` before pushing any changes
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
