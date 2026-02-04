# ag-install-local

Local build-and-install of Agent Brain server + CLI + plugin for rapid testing.

## Usage

```
/ag-install-local
```

## What it does
- Runs the `installing-local` skill end-to-end: full reset, rebuild server/CLI wheels, install via `uv tool`, clear plugin cache, deploy fresh plugin.
- Verifies Python 3.11 is available and ensures no stale processes, caches, or plugin artifacts remain.
- If the CLI is not already using a local path dependency, it will flip to path mode for this install (develop=true). If you want to force path mode, use `--use-path-deps` on the underlying script; to revert to PyPI, run `/ag-remove-local-install`.

## Steps (expected)
- Execute `.claude/skills/installing-local/install.sh --use-path-deps` from repo root.
- Follow the skill’s reset/build/install flow; ensure PATH points to the uv tool install.

## When to use
- After making local code changes and you need a clean reinstall.
- Before testing the plugin in a fresh Claude instance or ensuring marketplace cache is cleared.

## Notes
- The command performs the “Step 0: Full Reset” to guarantee a pristine environment.
- Optional state wipe (`~/.claude/agent-brain` and project `.claude/agent-brain`) is available in the skill if you need zero carryover.
