# Feature Specification: Server-Side Indexing Job Queue

**Feature Branch**: `115-job-queue`
**Created**: 2026-02-03
**Status**: Draft
**Input**: User request for non-blocking indexing with FIFO job queue

## User Scenarios & Testing

### User Story 1 - Submit Indexing Request Without Blocking (Priority: P1)

A user wants to submit multiple indexing requests without waiting for each to complete. The API should accept all valid requests immediately and process them in order.

**Why this priority**: Core value proposition. Currently, submitting a request while indexing returns 409 Conflict, blocking users from queuing work.

**Independent Test**: Submit 3 indexing requests in rapid succession, verify all return 202 Accepted with job IDs, then poll status to confirm FIFO processing order.

**Acceptance Scenarios**:

1. **Given** server is idle, **When** POST /index with valid path, **Then** returns 202 Accepted with job_id and status "queued"
2. **Given** indexing is in progress, **When** POST /index with valid path, **Then** returns 202 Accepted (not 409), job added to queue
3. **Given** 3 jobs submitted (A, B, C), **When** processing completes, **Then** jobs complete in FIFO order (A then B then C)
4. **Given** invalid folder path, **When** POST /index, **Then** returns 400 Bad Request immediately (validation before queueing)

---

### User Story 2 - Monitor Job Status (Priority: P1)

A user wants to check the status of their indexing job, including position in queue, progress, and completion state.

**Why this priority**: Essential for usability. Users need to know if their job is pending, running, or complete.

**Independent Test**: Submit a job, poll GET /index/jobs/{id}, verify state transitions from "queued" to "running" to "completed".

**Acceptance Scenarios**:

1. **Given** job in queue, **When** GET /index/jobs/{job_id}, **Then** returns status "queued" with queue_position
2. **Given** job is running, **When** GET /index/jobs/{job_id}, **Then** returns status "running" with progress_percent
3. **Given** job completed, **When** GET /index/jobs/{job_id}, **Then** returns status "completed" with completed_at and stats
4. **Given** job failed, **When** GET /index/jobs/{job_id}, **Then** returns status "failed" with error message
5. **Given** unknown job_id, **When** GET /index/jobs/{job_id}, **Then** returns 404 Not Found

---

### User Story 3 - List All Jobs (Priority: P1)

A user wants to see all pending and recent jobs to understand system state.

**Why this priority**: Complements status endpoint. Users need queue visibility to plan submissions.

**Independent Test**: Submit multiple jobs, call GET /index/jobs, verify list includes all jobs with correct states.

**Acceptance Scenarios**:

1. **Given** 5 jobs (2 queued, 1 running, 2 completed), **When** GET /index/jobs, **Then** returns list of all 5 with states
2. **Given** no jobs, **When** GET /index/jobs, **Then** returns empty list (not error)
3. **Given** jobs exist, **When** GET /index/jobs?status=queued, **Then** returns only queued jobs
4. **Given** jobs exist, **When** GET /index/jobs, **Then** jobs are ordered by created_at (newest first for completed, queue order for pending)

---

### User Story 4 - Cancel Pending Job (Priority: P2)

A user wants to cancel a job that is still in the queue before it starts processing.

**Why this priority**: Important for usability but not critical for MVP. Users may submit jobs by mistake.

**Independent Test**: Submit 2 jobs, cancel the second while first is running, verify second is removed from queue.

**Acceptance Scenarios**:

1. **Given** job in queue (status: queued), **When** DELETE /index/jobs/{job_id}, **Then** returns 200 OK, job removed
2. **Given** job is running, **When** DELETE /index/jobs/{job_id}, **Then** returns 409 Conflict (cannot cancel running job)
3. **Given** job completed, **When** DELETE /index/jobs/{job_id}, **Then** returns 410 Gone (job already finished)
4. **Given** unknown job_id, **When** DELETE /index/jobs/{job_id}, **Then** returns 404 Not Found

---

### User Story 5 - Server Crash Recovery (Priority: P2)

The system should recover gracefully if the server crashes or restarts, preserving pending jobs.

**Why this priority**: Important for reliability but complex to implement. Acceptable for MVP to lose queue on restart.

**Independent Test**: Submit jobs, kill server process, restart, verify queue is restored and processing resumes.

**Acceptance Scenarios**:

1. **Given** jobs in queue, **When** server restarts, **Then** pending jobs are recovered from persistent queue
2. **Given** job was "running" when crash occurred, **When** server restarts, **Then** job state reset to "queued" (retry from start)
3. **Given** server restarts, **When** first job completes, **Then** queue file is updated atomically

---

### User Story 6 - Backpressure Protection (Priority: P2)

The system should protect itself from unbounded queue growth by rejecting requests when queue is full.

**Why this priority**: Important for stability but queue of 100+ jobs is unlikely in normal usage.

**Independent Test**: Submit 101 jobs, verify 101st returns 503 Service Unavailable.

**Acceptance Scenarios**:

1. **Given** queue has 99 jobs, **When** POST /index, **Then** returns 202 Accepted (job #100)
2. **Given** queue has 100 jobs, **When** POST /index, **Then** returns 503 Service Unavailable with "queue full" message
3. **Given** queue was full but job completed, **When** POST /index, **Then** returns 202 Accepted

---

### User Story 7 - Job Timeout Handling (Priority: P3)

Long-running jobs should be detected and marked as failed to prevent queue stalls.

**Why this priority**: Edge case protection. Most jobs complete in minutes; 2-hour timeout is safety net.

**Independent Test**: Configure short timeout (30s), submit job on large folder, verify timeout triggers after 30s.

**Acceptance Scenarios**:

1. **Given** job running for > 2 hours, **When** timeout checked, **Then** job marked as "failed" with error "timeout"
2. **Given** job timed out, **When** next job in queue, **Then** processing continues with next job
3. **Given** job within timeout, **When** timeout checked, **Then** no action taken, job continues

---

### User Story 8 - CLI Job Monitoring (Priority: P2)

Users want a CLI command to monitor job queue status, with optional watch mode.

**Why this priority**: CLI parity with API. Users expect `agent-brain jobs` similar to `agent-brain status`.

**Independent Test**: Run `agent-brain jobs --watch`, submit job in another terminal, verify watch updates in real-time.

**Acceptance Scenarios**:

1. **Given** jobs exist, **When** `agent-brain jobs`, **Then** displays table of jobs with ID, status, folder, progress
2. **Given** jobs exist, **When** `agent-brain jobs --watch`, **Then** updates display every 2 seconds until Ctrl+C
3. **Given** specific job_id, **When** `agent-brain jobs <job_id>`, **Then** displays detailed status for that job
4. **Given** job in queue, **When** `agent-brain jobs --cancel <job_id>`, **Then** cancels the job

---

### User Story 9 - Duplicate Job Prevention (Priority: P2)

The system should detect and reject duplicate requests for the same folder path within a time window.

**Why this priority**: Prevents accidental double-submissions. Users often click submit multiple times.

**Independent Test**: Submit same folder twice within 5 seconds, verify second returns 409 with "duplicate detected".

**Acceptance Scenarios**:

1. **Given** job for /path/a queued, **When** POST /index for same /path/a, **Then** returns 409 Conflict "duplicate job"
2. **Given** job for /path/a completed, **When** POST /index for /path/a, **Then** returns 202 (re-indexing allowed)
3. **Given** job for /path/a queued, **When** POST /index for /path/b, **Then** returns 202 (different path is allowed)

---

### Edge Cases

- What happens when two jobs target the same folder simultaneously? (Only one runs at a time via queue)
- How does system handle extremely large folder (100k files)? (Progress updates, no special handling)
- What happens when disk is full during queue persistence? (Log error, continue in-memory, retry on next operation)
- How does system handle queue file corruption? (Validate on load, start fresh if corrupted, log warning)
- What happens when API key expires mid-job? (Job fails with error, next job attempts with potentially valid key)

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept indexing requests immediately (202) and queue for FIFO processing
- **FR-002**: System MUST persist job queue state to disk for crash recovery
- **FR-003**: System MUST provide endpoint to list all jobs (GET /index/jobs)
- **FR-004**: System MUST provide endpoint to get job status (GET /index/jobs/{id})
- **FR-005**: System MUST provide endpoint to cancel queued jobs (DELETE /index/jobs/{id})
- **FR-006**: System MUST process jobs sequentially (concurrency=1) to avoid resource contention
- **FR-007**: System MUST enforce queue size limit (max 100) and return 503 when full
- **FR-008**: System MUST timeout jobs exceeding 2 hours and mark as failed
- **FR-009**: System MUST prevent duplicate jobs for same folder path (when queued or running)
- **FR-010**: CLI MUST provide `agent-brain jobs` command with list, status, cancel, and watch functionality
- **FR-011**: System MUST use atomic writes with file locking for queue persistence
- **FR-012**: Status endpoints (GET /health/status, GET /index/jobs) MUST never block or error during indexing

### Non-Functional Requirements

- **NFR-001**: Queue operations (add, remove, status) MUST complete in <10ms
- **NFR-002**: Queue persistence MUST use JSONL format for append-only efficiency
- **NFR-003**: File locking MUST use fcntl for cross-process safety (consistent with existing locking.py)
- **NFR-004**: Job status polling MUST be efficient (no file reads on every call, use in-memory cache)
- **NFR-005**: Background worker MUST be a single asyncio task (not a separate process)

### Key Entities

- **IndexJob**: Represents a single indexing job with id, status, folder_path, created_at, started_at, completed_at, error, progress
- **JobStatus**: Enum of "queued", "running", "completed", "failed", "cancelled"
- **JobQueueStore**: Persistence layer for queue state using JSONL + file locking
- **JobWorker**: Background asyncio task that processes jobs FIFO with concurrency=1
- **JobQueueService**: API-facing service with deduplication, backpressure, and status queries

## Success Criteria

### Measurable Outcomes

- **SC-001**: All indexing requests return 202 Accepted (not 409) when queue is not full
- **SC-002**: Jobs process in FIFO order with no race conditions
- **SC-003**: Server restart preserves pending jobs and resumes processing
- **SC-004**: Queue operations complete in <10ms p99
- **SC-005**: No data loss on crash (atomic writes)
- **SC-006**: CLI `agent-brain jobs` provides parity with API endpoints
- **SC-007**: All existing tests continue to pass (backward compatible)
- **SC-008**: Status endpoints never return errors during active indexing
