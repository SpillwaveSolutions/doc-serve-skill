# Plan: Agent Brain Install and Release 3.x Alignment

**Date:** 2026-02-04  
**Goal:** Align installer, skills, and GitHub release flow so Agent Brain defaults to 3.x, supports user overrides, and avoids CLI/server publish races.

## Findings
- Release skill (`.claude/skills/agent-brain-release/SKILL.md`) hard-codes 2.0.0 as “latest” and all examples pin to 2.0.0.
- Install command (`agent-brain-plugin/commands/agent-brain-install.md`) never asks for a version; installs whatever PyPI serves, so it can drift off 3.x.
- `publish-to-pypi.yml` runs `publish-server` and `publish-cli` in parallel after quality gate; no wait for PyPI replication. CLI depends on `agent-brain-rag` ^<current>, so a missing server version can break installs.

## Work Plan
1) **Meta/process**
   - Save this plan in `docs/plans/agent-brain-install-and-release.md`.  
   - Add a short note to `CLAUDE.md` and `AGENTS.md` stating: after planning, always save the plan to `docs/plans/<name>.md`.

2) **Version source of truth**
   - Add a small resolver (shared by release skill and install command) that fetches available PyPI versions for `agent-brain-rag` and `agent-brain-cli`, picks the newest 3.x as the recommended default, and allows explicit override.  
   - Provide a fallback to the repo version (from `pyproject.toml`) if PyPI is unreachable.

3) **Update agent-brain-release skill**
   - Replace all 2.0.0 references with dynamic version guidance from the resolver; recommended = latest 3.x.  
   - Explicitly describe version bump logic (read current from pyproject/tag, compute next) and keep server/CLI versions locked.  
   - Add a post-release checklist to confirm PyPI pages show the released version and to refresh installer docs/plugin assets.

4) **Update agent-brain-install command**
   - After the install-method question, prompt for version with default = resolver.latest (3.x) and allow user override.  
   - Pin installs (`==<version>`) for pipx/uv/pip/conda; include GraphRAG extra example.  
   - Show the installed version in the success output and remind users to align server/CLI versions.

5) **GitHub Actions: `publish-to-pypi.yml`**
   - Make `publish-cli` depend on `publish-server` (add `needs: publish-server`).  
   - Insert a wait step after server publish that polls PyPI JSON until the new version is visible, then proceed to CLI publish.  
   - Pass the release/tag version into both jobs and fail if pyproject versions don’t match the tag.  
   - (Optional) reuse built wheels via artifacts to avoid rebuild drift.

6) **Drift/QA guards**
   - Add a CI check that the resolver’s recommended version matches what the skills/command docs declare as “latest.”  
   - Add a small unit test or dry-run script for the resolver.  
   - Ensure `task before-push` / `task pr-qa-gate` runs any new checks.

## Acceptance Criteria
- Plan is saved; CLAUDE.md and AGENTS.md mention the “save the plan” policy.  
- Installer flow asks for version, defaults to latest 3.x, installs pinned versions, and supports override.  
- Release skill reflects 3.x, uses the resolver, and documents server-first publish order with PyPI verification.  
- GitHub Action publishes server, waits for PyPI visibility, then publishes CLI; fails fast on version/tag mismatches.  
- CI check prevents documentation/version drift on the recommended version.
