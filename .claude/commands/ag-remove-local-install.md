# ag-remove-local-install

Remove all local Agent Brain installations, caches, and plugin artifacts to prepare for a fresh install.

## Usage

```
/ag-remove-local-install
```

## What it does
- Executes the “Step 0: Full Reset” portion of the `installing-local` skill:
  - Kills running agent-brain/uvicorn processes (ports 8000–8010).
  - Uninstalls CLI/server from `uv` and `pipx`, removes tool dirs, clears `uv`/`pip` caches.
  - Deletes plugin cache and deployed plugin (`~/.claude/plugins/cache/agent-brain-marketplace`, `~/.claude/plugins/agent-brain`).
- Leaves build/reinstall steps to be run separately (e.g., via `/ag-install-local`).
- Ensures the CLI dependency is restored to PyPI (`^<server_version>`) if it was previously flipped to a local path.

## Steps (expected)
- Run `.claude/skills/installing-local/install.sh --restore-pypi` from repo root to revert dependency, relock, and clean prior installs/caches.
- Optionally follow with `/ag-install-local` if you need a fresh local install immediately after.

## Optional zero-state cleanup
- If you need absolutely no carryover, the skill includes optional removal of `~/.claude/agent-brain` and project `.claude/agent-brain` (back up first).
