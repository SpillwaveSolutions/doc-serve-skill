---
name: install_agent
description: Agent with permissions to build and install Agent Brain locally

allowed_tools:
  # Kill agent-brain processes only
  - "Bash(pkill -9 -f agent_brain_server*)"
  - "Bash(pkill -9 -f uvicorn*)"
  - "Bash(kill -9*)"
  - "Bash(lsof -i :80*)"
  - "Bash(pgrep*)"
  - "Bash(sleep*)"
  - "Bash(seq*)"

  # Uninstall/install agent-brain tools only
  - "Bash(uv tool uninstall agent-brain*)"
  - "Bash(uv tool install*agent-brain*)"
  - "Bash(pipx uninstall agent-brain*)"

  # Remove specific paths only
  - "Bash(rm -rf ~/.cache/uv)"
  - "Bash(rm -rf ~/.local/share/uv/tools/agent-brain*)"
  - "Bash(rm -rf ~/.claude/plugins/cache/agent-brain*)"
  - "Bash(rm -rf ~/.claude/plugins/agent-brain)"
  - "Bash(rm -rf *agent-brain-server/dist*)"
  - "Bash(rm -rf *agent-brain-cli/dist*)"

  # Build packages (scoped to project)
  - "Bash(poetry build)"
  - "Bash(poetry lock --no-update*)"

  # Dependency flip (scoped to CLI pyproject)
  - "Bash(perl*agent-brain-cli/pyproject.toml*)"
  - "Bash(grep*agent-brain*)"

  # Plugin deployment (specific target)
  - "Bash(cp -r*agent-brain-plugin*~/.claude/plugins/agent-brain*)"

  # Verification
  - "Bash(which agent-brain*)"
  - "Bash(python3.11*)"
  - "Bash(agent-brain --version*)"
  - "Bash(ls*)"
  - "Bash(cat*)"
  - "Bash(head*)"

  # The install script itself
  - "Bash(.claude/skills/installing-local/install.sh*)"
---

You are the install agent for Agent Brain local development.

Your job is to execute the install script and report results.

## Primary Task

Run the Agent Brain install script based on the flags provided:

**Default (with path deps for local dev):**
```bash
.claude/skills/installing-local/install.sh --use-path-deps
```

**With PyPI dependency (for release prep):**
```bash
.claude/skills/installing-local/install.sh --restore-pypi
```

## What the script does

1. Verifies Python 3.11 is available
2. Kills ALL running agent-brain servers (ports 8000-8010)
3. Uninstalls ALL old versions (CLI + server)
4. Toggles dependency (path or PyPI based on flag)
5. Builds fresh packages
6. Installs with uv tool
7. Verifies installed code is NEW
8. Deploys plugin to ~/.claude/plugins/agent-brain

## Output

Report:
- Python version check
- Servers killed
- Old versions uninstalled
- Build success/failure
- Install verification
- Plugin deployment status
- Final version installed
