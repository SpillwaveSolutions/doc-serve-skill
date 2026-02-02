# Agent Brain Release Command

Release automation for Agent Brain packages.

## Usage

```
/agent-brain-release <bump> [--dry-run]
```

## Arguments

- `bump` (required): Version bump type
  - `major` - Breaking changes (1.2.0 → 2.0.0)
  - `minor` - New features (1.2.0 → 1.3.0)
  - `patch` - Bug fixes (1.2.0 → 1.2.1)

- `--dry-run` (optional): Preview changes without executing

## Examples

```bash
# Create a patch release (bug fixes)
/agent-brain-release patch

# Create a minor release (new features)
/agent-brain-release minor

# Create a major release (breaking changes)
/agent-brain-release major

# Preview a release without making changes
/agent-brain-release minor --dry-run
```

## What It Does

1. Validates pre-conditions (clean repo, on main, synced)
2. Calculates new version based on bump type
3. Updates version in 4 files:
   - `agent-brain-server/pyproject.toml`
   - `agent-brain-server/agent_brain_server/__init__.py`
   - `agent-brain-cli/pyproject.toml`
   - `agent-brain-cli/agent_brain_cli/__init__.py`
4. Generates release notes from commits
5. Creates git commit and tag
6. Pushes to remote
7. Creates GitHub release (triggers PyPI publish)

## Output

```
/agent-brain-release minor

[1/8] Validating pre-conditions...
      Working directory: clean ✓
      Branch: main ✓
      Remote sync: up to date ✓

[2/8] Calculating version...
      Current: 1.2.0 → New: 1.3.0

[3/8] Updating version files...
      4 files updated ✓

[4/8] Generating release notes...
      Found 12 commits since v1.2.0

[5/8] Committing version bump...
      chore(release): bump version to 1.3.0

[6/8] Creating git tag...
      Tag: v1.3.0

[7/8] Pushing to remote...
      Branch and tag pushed ✓

[8/8] Creating GitHub release...
      https://github.com/SpillwaveSolutions/agent-brain/releases/tag/v1.3.0

✓ Release complete! PyPI publish triggered automatically.

PyPI packages (available in ~5 minutes):
  https://pypi.org/project/agent-brain-rag/1.3.0/
  https://pypi.org/project/agent-brain-cli/1.3.0/

Install:
  pip install agent-brain-rag==1.3.0
  pip install agent-brain-cli==1.3.0
```

## Pre-requisites

- Clean working directory (no uncommitted changes)
- On `main` branch
- Local branch synced with remote
- `gh` CLI authenticated (`gh auth login`)

## Related

- [GitHub Action: publish-to-pypi.yml](/.github/workflows/publish-to-pypi.yml)
- [Skill Reference](/.claude/skills/agent-brain-release/SKILL.md)
