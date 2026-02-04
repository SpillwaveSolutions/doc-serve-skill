# Plan: Content Injector Stage with CLI LLM Providers

## Goal
Add an optional “content injection” stage to the indexing pipeline that can refine chunks (summaries/context) using local CLI-based LLM tools, without destabilizing the new job queue or existing flows.

## Key Requirements
- Remain **optional** (feature flag + per-job opt-in).
- **Fail-open**: indexing must still succeed if the injector/CLI is unavailable.
- **Safe & bounded**: capped concurrency, timeouts, and no secret leakage.
- **Backward compatible**: metadata additions must not break existing consumers.
- **Observable**: surface injector activity in job status.

## Architecture Overview
1) New provider family: CLI-based summarization/refinement (wrapping local tools).
2) New service: `ContentInjector` to post-process chunks after chunking, before embedding.
3) IndexingService integration point: optional stage gated by settings/job flags.
4) Config + metrics + tests to keep the queue stable.

## Work Breakdown

### A. CLI Provider Infrastructure
- Create `agent_brain_server/providers/cli/`:
  - `base.py`: safe subprocess wrapper (no shell=True, timeouts, max output size, stderr capture, return-code checks).
  - `claude_cli.py`, `opencode_cli.py`, `gemini_cli.py`: implement `SummarizationProvider` protocol (generate / summarize).
  - `factory.py`: register providers; detect missing binaries and raise a typed `ProviderUnavailable` used to fail-open.
- Settings:
  - `CLI_TIMEOUT_SECONDS` (default 30)
  - `MAX_CLI_CONCURRENCY` (default 4–5)
  - `CLI_MAX_OUTPUT_CHARS` (default 4096)
  - Provider selector `CLI_PROVIDER` (claude|opencode|gemini)

### B. Content Injector Service
- File: `agent_brain_server/indexing/content_injector.py`
- API: `process_chunks(chunks: list[Chunk]) -> list[Chunk]`
- Behavior:
  - Skip immediately if feature flag off or provider unavailable.
  - Process in batches with bounded concurrency (async semaphore).
  - For each chunk, request a brief bullet summary/self-contained hint; store in metadata.
  - On timeout/error: log warning, keep original chunk.
- Metadata handling:
  - Prefer `chunk.metadata["bullet_summary"]` to avoid schema churn.
  - Do not mutate text; add fields only.

### C. Pipeline Integration
- In `IndexingService._run_indexing_pipeline` after chunking:
  ```
  if settings.ENABLE_CONTENT_INJECTION or request.enable_content_injection:
      chunks = await content_injector.process_chunks(chunks)
  ```
- Provide `enable_content_injection` in `IndexRequest` (optional, default False).
- Ensure Graph/BM25 build still uses enriched metadata.

### D. Config & Discovery
- Defaults in `settings.py`:
  - `ENABLE_CONTENT_INJECTION = False`
  - `CONTENT_INJECTOR_PROVIDER = "cli"`
  - `CLI_*` settings from (A)
- Respect existing config search order and runtime.json; no new env var side effects.

### E. Observability & Status
- Add per-job counters in `JobRecord`:
  - `injector_attempted`, `injector_success`, `injector_failed`, `injector_skipped`
- Surface in `/index/jobs/{id}` and `/health/status` progress percent unchanged.
- Log per-job summary at INFO: “content_injection=on chunks=123 ok=118 fail=5”.

### F. Testing
- Unit:
  - CLI providers mock subprocess to assert command construction, timeout, and max-output enforcement.
  - ContentInjector with a stub provider to ensure fail-open and metadata attachment.
- Integration:
  - Run indexing with ENABLE_CONTENT_INJECTION=True and stub provider; assert job stats updated and chunks carry `bullet_summary`.
  - Verify 202 enqueue and job status remain stable (no 409s).
- Non-regression:
  - Ensure indexing without injector is unchanged.

### G. Safety & Limits
- Concurrency semaphore for CLI calls.
- Per-call timeout; kill process on timeout.
- Max output size; truncate with “[truncated]” marker.
- Detect missing binaries up front; log once and skip injector.
- Do not block queue worker: injector failures must not fail the job.

### H. Documentation
- Add README section and plugin command help:
  - How to enable: set ENABLE_CONTENT_INJECTION=true
  - How to choose provider and install needed CLI
  - Performance note: injector adds latency; lower `MAX_CLI_CONCURRENCY` if needed.

## Open Decisions (to confirm)
1) Concurrency default: propose 4 (safe for local CLIs).
2) Should summaries be kept only in metadata or also persisted to a sidecar file? (default: metadata only).
3) Per-job flag name: `enable_content_injection` on `IndexRequest`.

## Risks & Mitigations
- **Latency**: bounded concurrency, timeouts.
- **Binary missing**: detect and skip.
- **Schema breakage**: keep metadata additive.
- **Queue starvation**: injector never raises; continues on error.

## Acceptance Criteria
- Index runs succeed with injector on or off.
- `/index/jobs/{id}` shows injector stats.
- CLI providers handle missing binaries and timeouts gracefully.
- Unit + integration tests added and passing.
