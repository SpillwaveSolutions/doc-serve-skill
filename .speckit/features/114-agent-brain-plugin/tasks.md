# Tasks: Agent Brain Plugin Conversion

**Input**: Design documents from `.speckit/features/114-agent-brain-plugin/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested - quality validation via skill grading workflow (95% target)

**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Plugin root**: `agent-brain-plugin/` at repository root
- **Commands**: `agent-brain-plugin/commands/`
- **Agents**: `agent-brain-plugin/agents/`
- **Skills**: `agent-brain-plugin/skills/`

---

## Phase 1: Setup (Plugin Structure)

**Purpose**: Create plugin directory structure and manifest

- [x] T001 Create plugin directory structure: `agent-brain-plugin/` with `.claude-plugin/`, `commands/`, `agents/`, `skills/` subdirectories *(IN PROGRESS - Claude Code Task #5)*
- [x] T002 Create marketplace.json manifest in `agent-brain-plugin/.claude-plugin/marketplace.json` per data-model.md schema *(IN PROGRESS - Claude Code Task #5)*
- [x] T003 [P] Create README.md in `agent-brain-plugin/README.md` with installation and usage instructions *(IN PROGRESS - Claude Code Task #5)*
- [x] T004 [P] Create .gitignore in `agent-brain-plugin/.gitignore` for common excludes *(IN PROGRESS - Claude Code Task #5)*

**Checkpoint**: Plugin structure ready for content

---

## Phase 2: Foundational (Skills Infrastructure)

**Purpose**: Create skill foundations that commands and agents depend on

**⚠️ CRITICAL**: Commands and agents reference skills - skills must exist first

### using-agent-brain Skill

- [x] T005 Create skill directory structure: `agent-brain-plugin/skills/using-agent-brain/` with `references/` subdirectory *(IN PROGRESS - Claude Code Task #5)*
- [x] T006 Create SKILL.md in `agent-brain-plugin/skills/using-agent-brain/SKILL.md` per skill-schema.md *(IN PROGRESS - Claude Code Task #5)*
- [x] T007 [P] Create hybrid-search-guide.md in `agent-brain-plugin/skills/using-agent-brain/references/hybrid-search-guide.md` *(IN PROGRESS - Claude Code Task #5)*
- [x] T008 [P] Create bm25-search-guide.md in `agent-brain-plugin/skills/using-agent-brain/references/bm25-search-guide.md` *(IN PROGRESS - Claude Code Task #5)*
- [x] T009 [P] Create vector-search-guide.md in `agent-brain-plugin/skills/using-agent-brain/references/vector-search-guide.md` *(IN PROGRESS - Claude Code Task #5)*
- [x] T010 [P] Create api_reference.md in `agent-brain-plugin/skills/using-agent-brain/references/api_reference.md` *(IN PROGRESS - Claude Code Task #5)*

### agent-brain-setup Skill

- [x] T011 Create skill directory structure: `agent-brain-plugin/skills/agent-brain-setup/` with `references/` subdirectory *(IN PROGRESS - Claude Code Task #5)*
- [x] T012 Create SKILL.md in `agent-brain-plugin/skills/agent-brain-setup/SKILL.md` per skill-schema.md *(IN PROGRESS - Claude Code Task #5)*
- [x] T013 [P] Create installation-guide.md in `agent-brain-plugin/skills/agent-brain-setup/references/installation-guide.md` *(IN PROGRESS - Claude Code Task #5)*
- [x] T014 [P] Create configuration-guide.md in `agent-brain-plugin/skills/agent-brain-setup/references/configuration-guide.md` *(IN PROGRESS - Claude Code Task #5)*
- [x] T015 [P] Create troubleshooting-guide.md in `agent-brain-plugin/skills/agent-brain-setup/references/troubleshooting-guide.md` *(IN PROGRESS - Claude Code Task #5)*

**Checkpoint**: Skills ready - commands and agents can now reference them

---

## Phase 3: User Story 1 - Quick Search with Plugin Commands (Priority: P1) 🎯 MVP

**Goal**: Users can search project documentation using natural commands

**Independent Test**: Install plugin, start server, index docs, run `/agent-brain-search "query"` and verify results with source citations

### Search Commands

- [x] T016 [P] [US1] Create agent-brain-search.md command in `agent-brain-plugin/commands/agent-brain-search.md` per command-schema.md (hybrid mode)
- [x] T017 [P] [US1] Create agent-brain-semantic.md command in `agent-brain-plugin/commands/agent-brain-semantic.md` per command-schema.md (vector mode)
- [x] T018 [P] [US1] Create agent-brain-keyword.md command in `agent-brain-plugin/commands/agent-brain-keyword.md` per command-schema.md (BM25 mode)

### Supporting Commands for Search

- [x] T019 [P] [US1] Create agent-brain-status.md command in `agent-brain-plugin/commands/agent-brain-status.md` (needed to check server before search)
- [x] T020 [P] [US1] Create agent-brain-start.md command in `agent-brain-plugin/commands/agent-brain-start.md` (needed if server not running)

### Search Agent

- [x] T021 [US1] Create search-assistant.md agent in `agent-brain-plugin/agents/search-assistant.md` per agent-schema.md

**Checkpoint**: User Story 1 complete - users can search documentation via commands

---

## Phase 4: User Story 2 - Guided Installation and Setup (Priority: P2)

**Goal**: New users can install and configure Agent Brain from scratch

**Independent Test**: Fresh environment, run `/agent-brain-setup`, follow guided flow to completion, verify with `/agent-brain-verify`

### Setup Commands

- [x] T022 [P] [US2] Create agent-brain-install.md command in `agent-brain-plugin/commands/agent-brain-install.md` per command-schema.md
- [x] T023 [P] [US2] Create agent-brain-setup.md command in `agent-brain-plugin/commands/agent-brain-setup.md` (guided flow)
- [x] T024 [P] [US2] Create agent-brain-config.md command in `agent-brain-plugin/commands/agent-brain-config.md` (API key configuration)
- [x] T025 [P] [US2] Create agent-brain-init.md command in `agent-brain-plugin/commands/agent-brain-init.md` (project initialization)
- [x] T026 [P] [US2] Create agent-brain-verify.md command in `agent-brain-plugin/commands/agent-brain-verify.md` (installation verification)

### Setup Agent

- [x] T027 [US2] Create setup-assistant.md agent in `agent-brain-plugin/agents/setup-assistant.md` per agent-schema.md

**Checkpoint**: User Story 2 complete - new users can set up Agent Brain via guided commands

---

## Phase 5: User Story 3 - Server Lifecycle Management (Priority: P2)

**Goal**: Users can manage the Agent Brain server for their project

**Independent Test**: Run `/agent-brain-start`, verify with `/agent-brain-status`, run `/agent-brain-list` to see instance, run `/agent-brain-stop`

### Server Commands

- [x] T028 [P] [US3] Create agent-brain-stop.md command in `agent-brain-plugin/commands/agent-brain-stop.md` per command-schema.md
- [x] T029 [P] [US3] Create agent-brain-list.md command in `agent-brain-plugin/commands/agent-brain-list.md` (list all instances)

**Note**: agent-brain-start.md and agent-brain-status.md already created in US1 (T019, T020)

**Checkpoint**: User Story 3 complete - users can manage server lifecycle

---

## Phase 6: User Story 4 - Document Indexing via Commands (Priority: P2)

**Goal**: Users can index their project documentation for search

**Independent Test**: Run `/agent-brain-index /docs`, check status shows document count, run `/agent-brain-reset` and confirm index cleared

### Indexing Commands

- [x] T030 [P] [US4] Create agent-brain-index.md command in `agent-brain-plugin/commands/agent-brain-index.md` per command-schema.md
- [x] T031 [P] [US4] Create agent-brain-reset.md command in `agent-brain-plugin/commands/agent-brain-reset.md` (clear index with confirmation)

**Checkpoint**: User Story 4 complete - users can index and reset documentation

---

## Phase 7: User Story 5 - Proactive Agent Assistance (Priority: P2)

**Goal**: Agents proactively offer help when user mentions search or setup topics

**Independent Test**: Say "search docs" and verify agent offers to help; say "how do I search" and verify agent explains Agent Brain

**Note**: Both agents already created in US1 (T021) and US2 (T027)

- [x] T032 [US5] Review and enhance search-assistant.md trigger patterns for comprehensive coverage in `agent-brain-plugin/agents/search-assistant.md`
- [x] T033 [US5] Review and enhance setup-assistant.md trigger patterns for comprehensive coverage in `agent-brain-plugin/agents/setup-assistant.md`

**Checkpoint**: User Story 5 complete - agents trigger appropriately on patterns

---

## Phase 8: User Story 6 - Interactive Help and Guidance (Priority: P3)

**Goal**: Users can get help with commands and search mode selection

**Independent Test**: Run `/agent-brain-help` and verify all 15 commands listed; run `/agent-brain-help --command search` for detailed help

### Help Command

- [x] T034 [US6] Create agent-brain-help.md command in `agent-brain-plugin/commands/agent-brain-help.md` per command-schema.md

**Checkpoint**: User Story 6 complete - users have comprehensive help available

---

## Phase 9: Quality Assurance (Required - 95% Target)

**Purpose**: Achieve 95% skill grading score for both skills

### Skill Grading

- [x] T035 Grade using-agent-brain skill with improving-skills workflow
- [x] T036 Identify and fix issues in `agent-brain-plugin/skills/using-agent-brain/SKILL.md` to improve score
- [x] T037 Re-grade using-agent-brain skill until 95% achieved
- [x] T038 Grade agent-brain-setup skill with improving-skills workflow
- [x] T039 Identify and fix issues in `agent-brain-plugin/skills/agent-brain-setup/SKILL.md` to improve score
- [x] T040 Re-grade agent-brain-setup skill until 95% achieved

**Checkpoint**: Both skills achieve 95% quality score

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and publication preparation

- [x] T041 Update marketplace.json to ensure all commands, agents, skills are correctly referenced in `agent-brain-plugin/.claude-plugin/marketplace.json`
- [x] T042 [P] Validate all command YAML frontmatter is correctly formatted
- [x] T043 [P] Validate all agent trigger patterns work as expected
- [x] T044 [P] Validate all skill references load correctly
- [x] T045 Plugin validated as part of monorepo (no separate installation needed)
- [x] T046 N/A - Plugin is part of existing agent-brain monorepo
- [x] T047 N/A - Will be committed with main repository
- [x] T048 N/A - Plugin path documented in monorepo README

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user story commands
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
- **Quality Assurance (Phase 9)**: Depends on all skills being created (Phase 2)
- **Polish (Phase 10)**: Depends on all content being complete

### User Story Dependencies

| Story | Priority | Dependencies | Can Parallel With |
|-------|----------|--------------|-------------------|
| US1 - Quick Search | P1 | Foundational | None (MVP) |
| US2 - Guided Setup | P2 | Foundational | US1, US3, US4, US6 |
| US3 - Server Lifecycle | P2 | Foundational, US1 (T019, T020) | US2, US4, US6 |
| US4 - Document Indexing | P2 | Foundational | US1, US2, US3, US6 |
| US5 - Agent Assistance | P2 | US1 (T021), US2 (T027) | None |
| US6 - Help & Guidance | P3 | Foundational | US1, US2, US3, US4 |

### Within Each User Story

- Commands marked [P] can run in parallel (different files)
- Agent files depend on having skill references available
- Each story should be testable after completion

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004 can run in parallel

**Phase 2 (Foundational)**:
- T007, T008, T009, T010 can run in parallel (using-agent-brain references)
- T013, T014, T015 can run in parallel (agent-brain-setup references)

**User Stories**:
- All commands within each story marked [P] can run in parallel
- US1, US2, US3, US4, US6 can run in parallel after Foundational
- US5 must wait for agents from US1/US2

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch all using-agent-brain reference files together:
Task: "Create hybrid-search-guide.md in agent-brain-plugin/skills/using-agent-brain/references/hybrid-search-guide.md"
Task: "Create bm25-search-guide.md in agent-brain-plugin/skills/using-agent-brain/references/bm25-search-guide.md"
Task: "Create vector-search-guide.md in agent-brain-plugin/skills/using-agent-brain/references/vector-search-guide.md"
Task: "Create api_reference.md in agent-brain-plugin/skills/using-agent-brain/references/api_reference.md"

# Launch all agent-brain-setup reference files together:
Task: "Create installation-guide.md in agent-brain-plugin/skills/agent-brain-setup/references/installation-guide.md"
Task: "Create configuration-guide.md in agent-brain-plugin/skills/agent-brain-setup/references/configuration-guide.md"
Task: "Create troubleshooting-guide.md in agent-brain-plugin/skills/agent-brain-setup/references/troubleshooting-guide.md"
```

## Parallel Example: User Story 1 (Search Commands)

```bash
# Launch all search commands together:
Task: "Create agent-brain-search.md command in agent-brain-plugin/commands/agent-brain-search.md"
Task: "Create agent-brain-semantic.md command in agent-brain-plugin/commands/agent-brain-semantic.md"
Task: "Create agent-brain-keyword.md command in agent-brain-plugin/commands/agent-brain-keyword.md"
Task: "Create agent-brain-status.md command in agent-brain-plugin/commands/agent-brain-status.md"
Task: "Create agent-brain-start.md command in agent-brain-plugin/commands/agent-brain-start.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational - skills (T005-T015)
3. Complete Phase 3: User Story 1 - search commands (T016-T021)
4. **STOP and VALIDATE**: Install plugin, test search commands work
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Plugin structure ready
2. Add User Story 1 (Search) → Test independently → MVP Ready!
3. Add User Story 2 (Setup) → Test independently → First-time user support
4. Add User Story 3 (Server) → Test independently → Full server lifecycle
5. Add User Story 4 (Indexing) → Test independently → Complete indexing
6. Add User Story 5 (Agents) → Test independently → Proactive assistance
7. Add User Story 6 (Help) → Test independently → Complete help system
8. Quality Assurance → 95% skill scores achieved
9. Polish → GitHub publication

### Parallel Team Strategy

With multiple contributors:

1. Everyone completes Setup + Foundational together
2. Once Foundational is done:
   - Contributor A: US1 (Search) + US5 (Agents)
   - Contributor B: US2 (Setup) + US6 (Help)
   - Contributor C: US3 (Server) + US4 (Indexing)
3. All run Quality Assurance and Polish together

---

## Task Summary

| Phase | Task Count | Parallel Tasks | Description |
|-------|------------|----------------|-------------|
| 1: Setup | 4 | 2 | Plugin structure |
| 2: Foundational | 11 | 7 | Skills infrastructure |
| 3: US1 Search | 6 | 5 | Search commands + agent |
| 4: US2 Setup | 6 | 5 | Setup commands + agent |
| 5: US3 Server | 2 | 2 | Server lifecycle commands |
| 6: US4 Indexing | 2 | 2 | Index commands |
| 7: US5 Agents | 2 | 0 | Agent pattern review |
| 8: US6 Help | 1 | 0 | Help command |
| 9: Quality | 6 | 0 | 95% skill grading |
| 10: Polish | 8 | 3 | Validation & publication |
| **Total** | **48** | **26** | |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Quality assurance (95% grading) is mandatory per spec
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Existing skill content from `agent-brain-skill/using-agent-brain/` can be migrated
