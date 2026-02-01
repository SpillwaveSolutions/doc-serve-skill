# Feature Specification: Skill Instance Discovery

**Feature Branch**: `111-skill-instance-discovery`
**Created**: 2026-01-28
**Status**: Draft
**Input**: User description: "Update Agent Brain-skill to know about the new multi-instance architecture features including init, start, stop, list commands, auto-port discovery, and runtime.json reading for sharing instances among coding agents"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Project Initialization via Skill (Priority: P1)

As a Claude Code user, I want the Agent Brain skill to automatically initialize a project for Agent Brain when I first use it, so that I don't need to manually run CLI commands before I can search my documentation.

**Why this priority**: This is the foundational capability. Without automatic initialization, users must know about and run `agent-brain init` manually, which defeats the purpose of having a skill.

**Independent Test**: Invoke the skill in a project without existing Agent Brain configuration, verify it creates the `.claude/Agent Brain/` directory and `config.json`, and confirm the skill reports successful initialization.

**Acceptance Scenarios**:

1. **Given** a project without `.claude/Agent Brain/` directory, **When** the user invokes the Agent Brain skill, **Then** the skill initializes the project by running `agent-brain init` and reports the result.
2. **Given** a project already initialized, **When** the user invokes the skill, **Then** the skill detects the existing configuration and skips initialization.
3. **Given** initialization fails (e.g., read-only directory), **When** the skill attempts to initialize, **Then** it reports a clear error with suggested remediation steps.

---

### User Story 2 - Automatic Server Discovery and Startup (Priority: P1)

As a Claude Code user, I want the skill to automatically discover running Agent Brain instances or start one if needed, so that I can immediately search my documentation without manual server management.

**Why this priority**: This is the core value proposition. The skill must connect to a working server to provide any search functionality.

**Independent Test**: In a project with no running server, invoke a search query via the skill, verify it starts the server with auto-port, reads the port from `runtime.json`, and successfully executes the query.

**Acceptance Scenarios**:

1. **Given** a running Agent Brain instance for the project, **When** the skill is invoked, **Then** it discovers the instance via `runtime.json` and connects to it.
2. **Given** no running Agent Brain instance, **When** the skill is invoked, **Then** it starts a server with `agent-brain start --daemon`, waits for readiness, and then proceeds with the operation.
3. **Given** a stale `runtime.json` (server crashed), **When** the skill is invoked, **Then** it detects the stale state, starts a fresh instance, and reports recovery.
4. **Given** the server fails to start, **When** the skill is invoked, **Then** it reports the failure with diagnostic information (log path, error message).

---

### User Story 3 - Instance Status Reporting (Priority: P2)

As a Claude Code user, I want the skill to report the status of Agent Brain instances including port, mode, and indexing state, so that I can understand the current state of my search infrastructure.

**Why this priority**: Status visibility is essential for troubleshooting and understanding the system state, but search functionality is more critical.

**Independent Test**: With a running server, invoke the skill's status capability, verify it reports the server's port, mode (per-project), document count, and instance ID.

**Acceptance Scenarios**:

1. **Given** a running Agent Brain instance, **When** the user asks for status, **Then** the skill reports: port, mode, instance ID, project ID, document count, and indexing status.
2. **Given** no running instance, **When** the user asks for status, **Then** the skill reports that no server is running for this project.
3. **Given** multiple instances across different projects, **When** the user asks for a list, **Then** the skill runs `agent-brain list` and presents all instances with their project roots.

---

### User Story 4 - Instance Lifecycle Management (Priority: P2)

As a Claude Code user, I want the skill to stop Agent Brain instances when requested, so that I can free resources when I'm done working on a project.

**Why this priority**: Lifecycle management is important for resource cleanup but secondary to core search functionality.

**Independent Test**: Start a server, invoke the skill to stop it, verify the server process terminates and `runtime.json` is removed.

**Acceptance Scenarios**:

1. **Given** a running Agent Brain instance, **When** the user asks to stop the server, **Then** the skill runs `agent-brain stop` and confirms shutdown.
2. **Given** no running instance, **When** the user asks to stop, **Then** the skill reports that no server is running.
3. **Given** multiple instances, **When** the user asks to stop a specific project's server, **Then** the skill stops only that project's instance.

---

### User Story 5 - Cross-Agent Instance Sharing (Priority: P3)

As a team of Claude Code agents working on the same project, I want to share a single Agent Brain instance, so that multiple agents can query the same indexed documentation without resource duplication.

**Why this priority**: Multi-agent scenarios are advanced use cases. Per-project isolation (P1) already enables this naturally through `runtime.json` discovery.

**Independent Test**: Start a Agent Brain instance from one agent context, invoke the skill from a different agent context in the same project, verify both agents connect to the same instance by checking the instance ID.

**Acceptance Scenarios**:

1. **Given** a Agent Brain instance started by Agent A, **When** Agent B invokes the skill in the same project, **Then** Agent B discovers and uses the existing instance.
2. **Given** agents in different subdirectories of the same project, **When** any agent invokes the skill, **Then** all agents connect to the same instance (project root is resolved consistently).
3. **Given** the original agent terminates, **When** other agents continue to use the skill, **Then** they remain connected to the shared server instance.

---

### Edge Cases

- What happens when the skill is invoked outside any project? The skill MUST report that it cannot determine the project root and suggest running from within a project directory.
- What happens when `runtime.json` is corrupted? The skill MUST handle JSON parse errors gracefully, remove the corrupted file, and attempt fresh server startup.
- What happens when the port in `runtime.json` is in use by a different process? The skill MUST validate via health endpoint, not just port availability.
- What happens when the user has multiple shells/agents racing to start servers? The lock file protocol in the server MUST prevent double-start; the skill should retry discovery after a brief wait.
- What happens when OPENAI_API_KEY is not set? The skill MUST detect missing API keys and report the issue before attempting server startup.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Skill MUST automatically initialize projects by creating `.claude/Agent Brain/` directory and `config.json` when invoked in an uninitialized project.
- **FR-002**: Skill MUST discover running Agent Brain instances by reading `runtime.json` from the project's state directory (`.claude/Agent Brain/runtime.json`).
- **FR-003**: Skill MUST start a Agent Brain server automatically when no running instance is discovered, using `agent-brain start --daemon` with auto-port allocation.
- **FR-004**: Skill MUST validate discovered instances by calling the health endpoint before attempting operations.
- **FR-005**: Skill MUST handle stale `runtime.json` files (server crashed) by detecting health check failure, cleaning up, and starting fresh.
- **FR-006**: Skill MUST report instance status including port, mode, instance ID, project ID, and document count when requested.
- **FR-007**: Skill MUST support stopping servers via `agent-brain stop` when requested by the user.
- **FR-008**: Skill MUST support listing all running Agent Brain instances via `agent-brain list`.
- **FR-009**: Skill MUST resolve project root consistently using the same algorithm as the server (`git rev-parse --show-toplevel` or marker-based fallback).
- **FR-010**: Skill MUST handle missing API keys by checking environment variables and reporting clear setup instructions.
- **FR-011**: Skill MUST update the base URL dynamically based on discovered server port rather than using hardcoded localhost:8000.
- **FR-012**: Skill MUST support explicit server URL override via environment variable `DOC_SERVE_URL` for advanced use cases.
- **FR-013**: Skill MUST document the new multi-instance workflow in SKILL.md with clear examples.

### Key Entities

- **Runtime State**: JSON file at `.claude/Agent Brain/runtime.json` containing mode, port, base_url, pid, instance_id, project_id, and started_at timestamp.
- **Project Configuration**: JSON file at `.claude/Agent Brain/config.json` containing optional settings like preferred_mode and custom paths.
- **Server Discovery**: The process of finding a running server by reading `runtime.json` and validating via health endpoint.
- **Auto-Start**: Automatic server startup when no running instance is discovered, with daemon mode and port 0 (auto-assign).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can invoke the Agent Brain skill and perform searches without any manual CLI commands for server management.
- **SC-002**: The skill successfully discovers running instances 100% of the time when a valid `runtime.json` exists with a healthy server.
- **SC-003**: The skill automatically starts a server within 10 seconds when no running instance is discovered.
- **SC-004**: Multiple agents in the same project share the same server instance 100% of the time.
- **SC-005**: The skill gracefully handles all edge cases (stale state, missing keys, corrupted files) with clear error messages.
- **SC-006**: SKILL.md is updated to document multi-instance capabilities with working examples.
- **SC-007**: The skill passes validation using the skill-improving skill rubric.

## Assumptions

- The CLI tool (`agent-brain`) is installed and available in PATH.
- Users have set required API keys (`OPENAI_API_KEY`) in their environment.
- Projects are typically under version control (git) or have standard project markers.
- Per-project mode is the default; shared daemon mode is not addressed in this feature.
- The skill operates in the context of a single project at a time.

## Out of Scope

- Shared daemon mode support (Feature 109 future work)
- Authentication between agents and server
- Remote server connections (non-localhost)
- GUI or web-based management
- Automatic indexing on skill invocation (user must explicitly request indexing)
