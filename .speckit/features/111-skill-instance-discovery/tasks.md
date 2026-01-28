# Implementation Tasks: Skill Instance Discovery

**Feature**: 111-skill-instance-discovery
**Status**: Pending

## Task Overview

| Task | Description | Status | Priority |
|------|-------------|--------|----------|
| T1 | Create discovery module for runtime.json reading | Pending | P1 |
| T2 | Update SKILL.md with multi-instance workflow | Pending | P1 |
| T3 | Add auto-initialization logic to skill | Pending | P1 |
| T4 | Add server auto-start capability | Pending | P1 |
| T5 | Add status reporting to skill | Pending | P2 |
| T6 | Add stop server capability | Pending | P2 |
| T7 | Add list instances capability | Pending | P2 |
| T8 | Validate skill using skill-improving skill | Pending | P3 |

---

## T1: Create Discovery Module for runtime.json Reading

**Priority**: P1
**Status**: Pending
**Depends On**: None

### Description

Create a Python module (or shell script section in SKILL.md) that:
1. Resolves the project root using git or marker-based detection
2. Constructs the path to `.claude/doc-serve/runtime.json`
3. Reads and parses the runtime state
4. Validates the server is alive by calling the health endpoint
5. Returns the base URL for API calls

### Acceptance Criteria

- [ ] Project root resolution matches server behavior (`git rev-parse --show-toplevel`)
- [ ] Handles missing `runtime.json` gracefully (returns None/empty)
- [ ] Handles corrupted JSON gracefully (logs error, returns None)
- [ ] Validates server health before returning URL
- [ ] Returns base_url from runtime.json when server is healthy

### Implementation Notes

The skill can include Python snippets in SKILL.md or reference the `scripts/query_domain.py` script. Consider adding a `discover_server()` function that returns the server URL.

---

## T2: Update SKILL.md with Multi-Instance Workflow

**Priority**: P1
**Status**: Pending
**Depends On**: T1

### Description

Update the skill's main documentation to reflect the new multi-instance architecture:
1. Update "Core Workflow" section with init/start/stop/list commands
2. Add "Server Discovery" section explaining automatic discovery
3. Update examples to use dynamic port discovery
4. Add troubleshooting for multi-instance scenarios
5. Update triggers if needed

### Acceptance Criteria

- [ ] SKILL.md documents `doc-svr-ctl init` command
- [ ] SKILL.md documents `doc-svr-ctl start --daemon` with auto-port
- [ ] SKILL.md documents `doc-svr-ctl stop` command
- [ ] SKILL.md documents `doc-svr-ctl list` command
- [ ] SKILL.md explains runtime.json discovery mechanism
- [ ] SKILL.md examples use discovered port instead of hardcoded 8000
- [ ] SKILL.md includes troubleshooting for stale server detection

### File Changes

- `doc-serve-skill/doc-serve/SKILL.md` - Major update

---

## T3: Add Auto-Initialization Logic to Skill

**Priority**: P1
**Status**: Pending
**Depends On**: T2

### Description

Add logic to the skill workflow that:
1. Checks if `.claude/doc-serve/` exists in the project
2. If not, runs `doc-svr-ctl init` to initialize the project
3. Reports initialization result to the user

### Acceptance Criteria

- [ ] Skill detects uninitialized projects
- [ ] Skill runs init command when needed
- [ ] Skill reports success/failure of initialization
- [ ] Skill skips init for already-initialized projects

### Implementation Notes

This can be a conditional step at the beginning of any skill operation.

---

## T4: Add Server Auto-Start Capability

**Priority**: P1
**Status**: Pending
**Depends On**: T1, T3

### Description

Add logic to automatically start the server when no running instance is discovered:
1. If runtime.json doesn't exist or server is unhealthy, start server
2. Use `doc-svr-ctl start --daemon` for background operation
3. Wait for server to become ready (poll health endpoint)
4. Report the server URL once ready

### Acceptance Criteria

- [ ] Skill starts server when no instance is running
- [ ] Skill uses daemon mode for background operation
- [ ] Skill waits for server readiness before proceeding
- [ ] Skill reports server URL after successful start
- [ ] Skill handles start failures with clear error messages

### Implementation Notes

Use `doc-svr-ctl start --daemon --wait` if available, or poll health endpoint.

---

## T5: Add Status Reporting to Skill

**Priority**: P2
**Status**: Pending
**Depends On**: T1

### Description

Add a status reporting capability to the skill:
1. Read runtime.json for instance details
2. Call health endpoint for current status
3. Format and display: port, mode, instance_id, document count, indexing status

### Acceptance Criteria

- [ ] Skill can report server status on request
- [ ] Status includes port, mode, instance_id
- [ ] Status includes document count and indexing state
- [ ] Handles "no server running" case gracefully

### Implementation Notes

Add a "status" trigger or integrate into existing workflow.

---

## T6: Add Stop Server Capability

**Priority**: P2
**Status**: Pending
**Depends On**: T2

### Description

Add capability to stop the running server:
1. Run `doc-svr-ctl stop` command
2. Report shutdown result
3. Handle "no server running" case

### Acceptance Criteria

- [ ] Skill can stop server on user request
- [ ] Reports successful shutdown
- [ ] Handles "no server" case gracefully

---

## T7: Add List Instances Capability

**Priority**: P2
**Status**: Pending
**Depends On**: T2

### Description

Add capability to list all running doc-serve instances:
1. Run `doc-svr-ctl list` command
2. Parse and format output
3. Display instance details for each project

### Acceptance Criteria

- [ ] Skill can list all running instances
- [ ] Shows project root, port, and status for each
- [ ] Handles "no instances" case gracefully

---

## T8: Validate Skill Using Skill-Improving Skill

**Priority**: P3
**Status**: Pending
**Depends On**: T1-T7

### Description

Run the skill through the skill-improving skill validation:
1. Check SKILL.md follows best practices
2. Verify triggers are comprehensive
3. Ensure examples are working
4. Fix any issues identified

### Acceptance Criteria

- [ ] Skill passes all validation checks
- [ ] Any identified issues are resolved
- [ ] Documentation is clear and comprehensive

---

## Dependencies Diagram

```
T1 (Discovery Module)
  └── T4 (Auto-Start) ──┬── T5 (Status)
                        │
T2 (SKILL.md Update) ───┼── T6 (Stop)
  └── T3 (Auto-Init) ──┘    │
                            └── T7 (List)
                                 │
                                 └── T8 (Validation)
```

## Notes

- P1 tasks (T1-T4) are required for MVP functionality
- P2 tasks (T5-T7) provide complete lifecycle management
- P3 task (T8) ensures quality and best practices
- All work is in `doc-serve-skill/doc-serve/` directory
