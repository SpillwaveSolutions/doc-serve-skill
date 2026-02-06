# Claude Tasks: Feature 113 - GraphRAG Integration (US1-4)

This directory mirrors the Speckit plan/tasks for Feature 113 and expresses them as a Claude Code task DAG. The DAG is the active checklist; keep Speckit in sync when statuses change.

## Sources
- Plan: `.speckit/features/113-graphrag-integration/plan.md`
- Tasks: `.speckit/features/113-graphrag-integration/tasks.md`
- Spec: `.speckit/features/113-graphrag-integration/spec.md`
- Constitution: `.speckit/memory/constitution.md`

## Agents & Access
- `python-core` → skill: `mastering-python-skill`; access: `agent-brain-server/**`, `agent-brain-cli/**`, `tests/**`, `.speckit/features/113-graphrag-integration/**`.
- `installer-qa` → skill: `installing-local`; access: `scripts/**`, `docs/**`, `.claude/skills/installing-local/**`, `agent-brain-server/**`, `agent-brain-cli/**` (for quickstart validation & perf).
- `doc-sync` → skill: `mastering-python-skill`; access: `.speckit/**`, `.claude/tasks/113-graphrag/**`, `docs/plans/**` (keeps docs aligned).

Grant only the access paths above when spinning up subagents.

## Usage
1. Update task status in `dag.yaml` (pending → in_progress → done).
2. When a task completes, reflect the change in both `dag.yaml` and Speckit `tasks.md` (and plan if needed).
3. Keep checkpoints: US1/2/3/4 and Polish phases must remain independently testable.
4. Open items (T052, T053) remain pending until validated.

## Validation Notes
- GraphRAG code landed in `agent-brain-server` and `agent-brain-cli` with tests; see `dag.yaml` for completion and remaining work.
- Use `installer-qa` to run `.speckit/features/113-graphrag-integration/quickstart.md` and perf tests when ready.
