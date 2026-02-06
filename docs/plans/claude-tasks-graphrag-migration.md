# Plan: Migrate Speckit Feature 113 to Claude Tasks (2026-02-05)

## Goal
Move Feature 113 (GraphRAG Integration) from Speckit plans/tasks into Claude Code tasks DAG, keep source-of-truth synced, and validate implementation coverage.

## Steps
1) Artifact audit: Review Speckit spec, plan, tasks, research, data-model, quickstart, checklists/contracts, roadmap links to capture scope and open items (T052, T053).
2) Task schema: Define Claude tasks file layout (DAG YAML) and agent assignments using available .claude/skills; align statuses with Speckit IDs.
3) DAG creation: Write Claude tasks DAG for Feature 113 including dependencies, statuses, file access scopes, and subagent skill mapping; add README/bridge note.
4) Speckit sync: Update .speckit plan/tasks to point to Claude tasks, note migration, and ensure constitution references remain intact.
5) Validation & grading: Spot-check key code artifacts vs plan (query_service, graph_index, graph_store, CLI query/status) and record completion grade with rationale.

## Deliverables
- Claude tasks DAG files for Feature 113 under `.claude/tasks/113-graphrag/`
- Updated Speckit plan/tasks noting Claude tasks migration and status alignment
- Validation notes + completion grade (0–100%)
