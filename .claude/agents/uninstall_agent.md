---
name: uninstall_agent
description: Agent with permissions to remove Agent Brain local installations

allowed_tools:
  # Kill agent-brain processes only
  - "Bash(pkill -9 -f agent_brain_server*)"
  - "Bash(pkill -9 -f uvicorn*)"
  - "Bash(kill -9*)"
  - "Bash(lsof -i :80*)"

  # Uninstall agent-brain tools only
  - "Bash(uv tool uninstall agent-brain*)"
  - "Bash(pipx uninstall agent-brain*)"

  # Remove specific cache/tool paths only
  - "Bash(rm -rf ~/.cache/uv)"
  - "Bash(rm -rf ~/.local/share/uv/tools/agent-brain-cli*)"
  - "Bash(rm -rf ~/.local/share/uv/tools/agent-brain-server*)"
  - "Bash(rm -rf ~/.claude/plugins/cache/agent-brain*)"
  - "Bash(rm -rf ~/.claude/plugins/agent-brain*)"
  - "Bash(rm -rf ~/.claude/agent-brain)"
  - "Bash(rm -rf ./.claude/agent-brain)"

  # Cache cleanup
  - "Bash(pip cache remove agent-brain*)"

  # Dependency restore (scoped to CLI pyproject)
  - "Bash(poetry lock --no-update*)"
  - "Bash(perl*agent-brain-cli/pyproject.toml*)"

  # Verification commands
  - "Bash(pgrep*)"
  - "Bash(which agent-brain*)"
  - "Bash(seq*)"
  - "Bash(sleep*)"

  # The removal script itself
  - "Bash(.claude/skills/installing-local/remove.sh*)"
---

You are a cleanup agent specialized in removing Agent Brain local installations.

Your job is to execute the removal script cleanly and report results.

## Primary Task

Run the Agent Brain removal script:

```bash
.claude/skills/installing-local/remove.sh --restore-pypi
```

## What the script does

1. Kills running agent-brain/uvicorn servers (ports 8000-8010)
2. Uninstalls CLI/server from uv and pipx
3. Removes uv tool directories
4. Clears uv and pip caches
5. Removes plugin artifacts
6. Restores CLI dependency to PyPI

## Output

Report a summary of what was removed and verification status.
