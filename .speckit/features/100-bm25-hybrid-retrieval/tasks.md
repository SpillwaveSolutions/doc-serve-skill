# Tasks: BM25 & Hybrid Retrieval

**Input**: Design documents from `/specs/100-bm25-hybrid-retrieval/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 [P] Add `rank-bm25` and `llama-index-retrievers-bm25` to `agent-brain-server/pyproject.toml`
- [x] T002 [P] Update `agent-brain-server` dependencies by running `poetry install` in `agent-brain-server/`
- [x] T003 [P] Add `BM25_INDEX_PATH` to `agent-brain-server/agent_brain_server/config/settings.py`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T004 Implement `BM25IndexManager` in `agent_brain_server/indexing/bm25_index.py` for index persistence
- [x] T005 Update `QueryMode` enum and add it to `agent_brain_server/models/query.py`
- [x] T006 Update `QueryRequest` with `mode` and `alpha` fields in `agent_brain_server/models/query.py`
- [x] T007 Update `QueryResult` to include `vector_score` and `bm25_score` in `agent_brain_server/models/query.py`
- [x] T008 Update `IndexingService` in `agent_brain_server/services/indexing_service.py` to build BM25 index during ingestion

**Checkpoint**: Foundation ready - user story implementation can now begin.

## Phase 3: User Story 1 - BM25 Keyword Search (Priority: P1) 🎯 MVP

**Goal**: Enable exact keyword matching via `mode=bm25`.

**Independent Test**: POST to `/query` with `mode=bm25` and verify exact matches are returned.

- [x] T009 [P] [US1] Create unit test for BM25 retrieval in `agent-brain-server/tests/unit/test_bm25_retrieval.py`
- [x] T010 [US1] Implement BM25 retrieval logic in `agent_brain_server/services/query_service.py`
- [x] T011 [US1] Update `/query` endpoint in `agent_brain_server/api/routers/query.py` to handle `mode=bm25`
- [x] T012 [US1] Integration test for BM25 mode in `agent-brain-server/tests/integration/test_bm25_api.py`

**Checkpoint**: User Story 1 is functional.

## Phase 4: User Story 2 - Hybrid Search with Relative Score Fusion (Priority: P1)

**Goal**: Combine vector and BM25 results using Relative Score Fusion.

**Independent Test**: POST to `/query` with `mode=hybrid` and verify blended results.

- [x] T013 [P] [US2] Create unit test for Hybrid fusion logic in `agent-brain-server/tests/unit/test_hybrid_fusion.py`
- [x] T014 [US2] Implement Hybrid retrieval with `QueryFusionRetriever` (relative_score) in `agent_brain_server/services/query_service.py`
- [x] T015 [US2] Update `/query` endpoint in `agent_brain_server/api/routers/query.py` to handle `mode=hybrid`
- [x] T016 [US2] Integration test for Hybrid mode in `agent-brain-server/tests/integration/test_hybrid_api.py`

**Checkpoint**: Hybrid Search is functional.

## Phase 5: User Story 3 - Alpha Weight Configuration (Priority: P2)

**Goal**: Allow tuning balance between vector and BM25.

**Independent Test**: Verify results change when switching alpha between 0.0 and 1.0.

- [x] T017 [US3] Implement alpha weighting in `agent_brain_server/services/query_service.py` (use Relative Score Fusion)
- [x] T018 [US3] Add validation for alpha (0.0-1.0) in `agent_brain_server/models/query.py`
- [x] T019 [US3] Integration test for alpha weighting in `agent-brain-server/tests/integration/test_alpha_weighting.py`

**Checkpoint**: Alpha weighting is functional.

## Phase 6: User Story 4 - CLI Search Mode Selection (Priority: P2)

**Goal**: Select search mode and alpha via `agent-brain`.

**Independent Test**: Run `agent-brain query "text" --mode bm25` and check results.

- [x] T020 [US4] Add `--mode` and `--alpha` options to `agent-brain/agent_brain_cli/commands/query.py`
- [x] T021 [US4] Update `agent-brain/agent_brain_cli/client/api_client.py` to pass new parameters to API
- [x] T022 [US4] Integration test for CLI query options in `agent-brain/tests/test_cli_query_modes.py`

**Checkpoint**: CLI support is functional.

## Phase 7: User Story 5 - Enhanced Scoring Metadata (Priority: P3)

**Goal**: Expose separate scores in result metadata.

**Independent Test**: Verify `vector_score` and `bm25_score` are present in API response.

- [x] T023 [US5] Ensure `vector_score` and `bm25_score` are populated in `agent_brain_server/services/query_service.py`
- [x] T024 [US5] Update `agent_brain_cli/agent_brain_cli/commands/query.py` to display scores if requested (or in verbose mode)

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T025 [P] Update `README.md` and `docs/USER_GUIDE.md` with hybrid search instructions
- [x] T026 [P] Update `agent-brain-skill/doc-serve/references/api_reference.md`
- [x] T027 Run full test suite: `task pr-qa-gate`
- [x] T028 Validate `quickstart.md` scenarios

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
- **Polish (Final Phase)**: Depends on all user stories being complete.

### Parallel Opportunities

- T001, T002, T003 can run in parallel.
- US1 (Phase 3) and US2 (Phase 4) can be worked on in parallel after Phase 2, but US2 implementation might benefit from US1 being done first for baseline.
- T009 and T013 (unit tests) can run in parallel.
- Phase 8 documentation tasks can run in parallel.

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Complete Phase 1 & 2.
2. Complete Phase 3 (BM25).
3. Complete Phase 4 (Hybrid).
4. Validate with `quickstart.md`.
