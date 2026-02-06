# Tasks: GraphRAG Integration

**Input**: Design documents from `.speckit/features/113-graphrag-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Claude Tasks DAG**: Active tracking is in `.claude/tasks/113-graphrag/dag.yaml` (see `README.md` there). Keep this file and the DAG in sync when statuses change.

**Tests**: Tests included per Constitution III (Test-Alongside)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Server**: `agent-brain-server/agent_brain_server/`
- **CLI**: `agent-brain-cli/agent_brain_cli/`
- **Tests**: `agent-brain-server/tests/`, `agent-brain-cli/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and configuration

- [x] T001 Add GraphRAG configuration settings to agent-brain-server/agent_brain_server/config/settings.py ✅ COMPLETE
- [x] T002 [P] Update agent-brain-server/agent_brain_server/storage_paths.py to include graph_index directory ✅ COMPLETE
- [x] T003 [P] Add optional dependency groups to agent-brain-server/pyproject.toml for graphrag and graphrag-kuzu ✅ COMPLETE
- [x] T004 [P] Add GRAPH and MULTI to QueryMode enum in agent-brain-server/agent_brain_server/models/query.py ✅ COMPLETE

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core graph infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create GraphStoreManager class in agent-brain-server/agent_brain_server/storage/graph_store.py ✅ COMPLETE
- [x] T006 Implement SimplePropertyGraphStore initialization and persistence in graph_store.py ✅ COMPLETE
- [x] T007 Add Kuzu store factory with fallback in agent-brain-server/agent_brain_server/storage/graph_store.py ✅ COMPLETE
- [x] T008 [P] Create GraphIndexStatus model in agent-brain-server/agent_brain_server/models/graph.py ✅ COMPLETE
- [x] T009 [P] Create GraphTriple model in agent-brain-server/agent_brain_server/models/graph.py ✅ COMPLETE
- [x] T010 [P] Extend QueryResult model with graph_score, related_entities, relationship_path in agent-brain-server/agent_brain_server/models/query.py ✅ COMPLETE
- [x] T011 [P] Unit test for GraphStoreManager in agent-brain-server/tests/unit/test_graph_store.py ✅ COMPLETE (31 tests)
- [x] T012 Export graph models from agent-brain-server/agent_brain_server/models/__init__.py ✅ COMPLETE
- [x] T013 Export graph store from agent-brain-server/agent_brain_server/storage/__init__.py ✅ COMPLETE

**Checkpoint**: Graph storage foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Enable Graph-Based Document Retrieval (Priority: P1) 🎯 MVP

**Goal**: Enable optional GraphRAG with graph-only query mode

**Independent Test**: Enable GraphRAG, index documents, query with `--mode graph`

**Status**: ✅ COMPLETE (2026-02-05) - All tests passing (117 tests)

### Tests for User Story 1

- [x] T014 [P] [US1] Unit test for DynamicLLMPathExtractor wrapper in agent-brain-server/tests/unit/test_graph_extractors.py ✅ COMPLETE (26 tests)
- [x] T015 [P] [US1] Unit test for GraphIndexManager in agent-brain-server/tests/unit/test_graph_index.py ✅ COMPLETE (22 tests)
- [x] T016 [P] [US1] Integration test for graph query execution in agent-brain-server/tests/integration/test_graph_query.py ✅ COMPLETE (17 tests)

### Implementation for User Story 1

- [x] T017 [P] [US1] Create LLM entity extractor wrapper in agent-brain-server/agent_brain_server/indexing/graph_extractors.py ✅ COMPLETE
- [x] T018 [P] [US1] Create GraphIndexManager class in agent-brain-server/agent_brain_server/indexing/graph_index.py ✅ COMPLETE
- [x] T019 [US1] Implement graph index building from documents in graph_index.py ✅ COMPLETE (build_from_documents)
- [x] T020 [US1] Implement graph index persistence and loading in graph_index.py ✅ COMPLETE (persist/clear via GraphStoreManager)
- [x] T021 [US1] Add _execute_graph_query method to agent-brain-server/agent_brain_server/services/query_service.py ✅ COMPLETE
- [x] T022 [US1] Update execute_query to route GRAPH mode in query_service.py ✅ COMPLETE
- [x] T023 [US1] Add GraphRAG disabled check with informative error in query_service.py ✅ COMPLETE
- [x] T024 [US1] Integrate graph building into agent-brain-server/agent_brain_server/services/indexing_service.py ✅ COMPLETE (line 402)
- [x] T025 [US1] Add progress callback for graph building stage in indexing_service.py ✅ COMPLETE
- [x] T026 [US1] Update /query endpoint to accept graph parameters in agent-brain-server/agent_brain_server/api/routers/query.py ✅ COMPLETE
- [x] T027 [US1] Add graph_index to health status in agent-brain-server/agent_brain_server/api/routers/health.py ✅ COMPLETE (line 160)
- [x] T028 [US1] Add --mode graph option to agent-brain-cli/agent_brain_cli/commands/query.py ✅ COMPLETE
- [x] T029 [US1] Add graph status to agent-brain-cli/agent_brain_cli/commands/status.py ✅ COMPLETE (line 101-112)

**Checkpoint**: ✅ User Story 1 complete - GraphRAG enabled, graph-only queries working

---

## Phase 4: User Story 2 - Query with Multi-Mode Fusion (Priority: P2)

**Goal**: Combine vector, BM25, and graph results using RRF

**Independent Test**: Query with `--mode multi`, verify results include all three retrieval sources

### Tests for User Story 2

- [x] T030 [P] [US2] Unit test for RRF fusion in agent-brain-server/tests/unit/test_rrf_fusion.py (11 tests)
- [x] T031 [P] [US2] Integration test for multi-mode query in agent-brain-server/tests/integration/test_graph_query.py (4 tests)

### Implementation for User Story 2

- [x] T032 [US2] Implement RRF fusion helper function in agent-brain-server/agent_brain_server/services/query_service.py (in _execute_multi_query)
- [x] T033 [US2] Add _execute_multi_query method with parallel execution in query_service.py (already implemented in US1)
- [x] T034 [US2] Update execute_query to route MULTI mode in query_service.py (already implemented in US1)
- [x] T035 [US2] Add --mode multi option to agent-brain-cli/agent_brain_cli/commands/query.py (already implemented in US1)

**Checkpoint**: User Story 2 complete - multi-mode fusion queries working

---

## Phase 5: User Story 3 - Configure Graph Store Backend (Priority: P3)

**Goal**: Support both SimplePropertyGraphStore and Kuzu backends

**Independent Test**: Set GRAPH_STORE_TYPE=kuzu, verify indexing and queries work

**Status**: ✅ COMPLETE (2026-02-05) - Kuzu backend with automatic fallback implemented

### Tests for User Story 3

- [x] T036 [P] [US3] Unit test for Kuzu store initialization in agent-brain-server/tests/unit/test_graph_store.py ✅ COMPLETE (12 tests in TestKuzuStoreInitialization and TestKuzuWithMockedImport)
- [x] T037 [P] [US3] Integration test for store type switching in agent-brain-server/tests/integration/test_graph_query.py ✅ COMPLETE (existing tests cover store operations)

### Implementation for User Story 3

- [x] T038 [US3] Implement Kuzu store initialization in agent-brain-server/agent_brain_server/storage/graph_store.py ✅ COMPLETE (_initialize_kuzu_store method at line 145)
- [x] T039 [US3] Add store type detection and fallback warning in graph_store.py ✅ COMPLETE (line 160 logs warning, falls back to simple)
- [x] T040 [US3] Add store_type to GraphIndexStatus in health responses ✅ COMPLETE (already in GraphIndexStatus model)

**Checkpoint**: ✅ User Story 3 complete - Kuzu backend configurable

---

## Phase 6: User Story 4 - Extract Code Relationships from AST Metadata (Priority: P3)

**Goal**: Extract import and hierarchy relationships from code without LLM calls

**Independent Test**: Index a Python codebase, query for import relationships

**Status**: ✅ COMPLETE (2026-02-05) - CodeMetadataExtractor fully implemented with multi-language support

### Tests for User Story 4

- [x] T041 [P] [US4] Unit test for code metadata extraction in agent-brain-server/tests/unit/test_graph_extractors.py ✅ COMPLETE (tests for Python, JS, Java, Go)
- [x] T042 [P] [US4] Integration test for code relationship queries in agent-brain-server/tests/integration/test_graph_query.py ✅ COMPLETE

### Implementation for User Story 4

- [x] T043 [US4] Create code metadata extractor in agent-brain-server/agent_brain_server/indexing/graph_extractors.py ✅ COMPLETE (CodeMetadataExtractor class)
- [x] T044 [US4] Extract import relationships from chunk.metadata.imports in graph_extractors.py ✅ COMPLETE (extract_from_metadata, extract_from_text)
- [x] T045 [US4] Extract containment relationships from symbol hierarchies in graph_extractors.py ✅ COMPLETE (contains, defined_in predicates)
- [x] T046 [US4] Integrate code extractor into GraphIndexManager in graph_index.py ✅ COMPLETE (line 66, _extract_from_document)
- [x] T047 [US4] Add source_type-based extraction routing (doc vs code) in graph_index.py ✅ COMPLETE (line 155)

**Checkpoint**: ✅ User Story 4 complete - code relationships extracted from AST

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

**Status**: ✅ MOSTLY COMPLETE (2026-02-05) - 6/7 tasks done (T053 deferred as optional)

- [x] T048 [P] Add graph rebuild endpoint parameter to agent-brain-server/agent_brain_server/api/routers/index.py ✅ COMPLETE
- [x] T049 [P] Add structured logging for graph operations across all modules ✅ COMPLETE
- [x] T050 Contract test for QueryMode enum values in agent-brain-server/tests/contract/test_query_modes.py ✅ COMPLETE (19 tests)
- [x] T051 [P] Update agent-brain-server README with GraphRAG configuration section ✅ COMPLETE
- [x] T052 Add E2E tests for GraphRAG query modes ✅ COMPLETE (2026-02-05)
  - Added `TestQueryModes` class (3 tests: vector, bm25, hybrid modes)
  - Added `TestGraphRAGQueries` class (4 tests: graph/multi CLI acceptance, results/error handling)
  - Added `TestGraphRAGHealthStatus` class (1 test: graph_index status verification)
  - Updated `conftest.py` with `query()` mode parameter and `query_raw()` method
  - Added shell script tests (Query 5, 6, 7) for graph, multi modes, and status
- [ ] T053 Performance testing for graph queries on sample dataset (DEFERRED - benchmarks optional)
- [x] T054 Update CLI help text for new query modes in agent-brain-cli ✅ COMPLETE

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3-6 (User Stories)**: All depend on Phase 2 completion
  - US1 (P1): No dependencies on other stories
  - US2 (P2): Depends on US1 (needs graph query infrastructure)
  - US3 (P3): No dependencies on other stories (parallel with US4)
  - US4 (P3): No dependencies on other stories (parallel with US3)
- **Phase 7 (Polish)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1 (Setup)
     │
     ▼
Phase 2 (Foundational) ─────────────────────┐
     │                                       │
     ▼                                       │
Phase 3: US1 (P1) 🎯 MVP                    │
     │                                       │
     ▼                                       │
Phase 4: US2 (P2)                           │
                                             │
     ┌──────────────────┬────────────────────┘
     │                  │
     ▼                  ▼
Phase 5: US3 (P3)   Phase 6: US4 (P3)
     │                  │
     └──────────────────┘
             │
             ▼
     Phase 7 (Polish)
```

### Parallel Opportunities

**Within Phase 1**:
- T002, T003, T004 can run in parallel

**Within Phase 2**:
- T008, T009, T010, T011 can run in parallel after T005-T007

**Within User Stories**:
- All tests can be written in parallel before implementation
- Models within a story marked [P] can run in parallel

**Across User Stories**:
- US3 and US4 can be implemented in parallel (both P3)

---

## Parallel Example: User Story 1

```bash
# Launch tests in parallel:
Task: "Unit test for DynamicLLMPathExtractor wrapper"
Task: "Unit test for GraphIndexManager"
Task: "Integration test for graph query execution"

# Launch extractors in parallel:
Task: "Create LLM entity extractor wrapper"
Task: "Create GraphIndexManager class"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test GraphRAG enable/disable, graph queries
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy (MVP!)
3. Add User Story 2 → Test independently → Deploy (MULTI mode)
4. Add User Stories 3 & 4 in parallel → Deploy (Kuzu + Code relationships)
5. Polish → Final release

### Parallel Team Strategy

With 2 developers after Foundational:
- Developer A: User Story 1 → User Story 2
- Developer B: User Story 3 + User Story 4 (can start after US1 foundation)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Constitution III: Tests written alongside implementation
- Constitution V: Complexity justified (optional feature, follows existing patterns)
- All graph features skip execution when ENABLE_GRAPH_INDEX=false
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
