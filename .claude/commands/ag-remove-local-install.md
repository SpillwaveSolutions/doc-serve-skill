---
context: fork
agent: uninstall_agent
---

# ag-remove-local-install

Remove all local Agent Brain installations, caches, and plugin artifacts.

## Arguments

- `--zero-state` - Also remove `~/.claude/agent-brain` and `./.claude/agent-brain` state directories (back up first!)

## Task

Run the removal script with the appropriate flags:

**If `--zero-state` was passed:**
```bash
.claude/skills/installing-local/remove.sh --restore-pypi --zero-state
```

**Otherwise (default):**
```bash
.claude/skills/installing-local/remove.sh --restore-pypi
```

## Expected Result

Report what was cleaned up:
- Servers killed
- Tools uninstalled
- Caches cleared
- Plugins removed
- State directories removed (if --zero-state)
- Verification status
