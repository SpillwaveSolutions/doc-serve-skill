---
name: install_agent
description: Agent with permissions to build and install Agent Brain locally

allowed_tools:
  # Kill agent-brain processes only
  - "Bash(pkill*)"
  - "Bash(kill*)"
  - "Bash(lsof*)"
  - "Bash(pgrep*)"
  - "Bash(sleep*)"
  - "Bash(seq*)"

  # Uninstall/install tools
  - "Bash(uv tool uninstall*)"
  - "Bash(uv tool install*)"
  - "Bash(pipx uninstall*)"

  # Remove caches and build dirs
  - "Bash(rm -rf*)"

  # Build packages
  - "Bash(poetry build*)"
  - "Bash(poetry lock*)"
  - "Bash(cd*)"

  # Dependency flip
  - "Bash(perl*)"
  - "Bash(grep*)"

  # Plugin deployment
  - "Bash(cp -r*)"

  # Verification
  - "Bash(which*)"
  - "Bash(python3.11*)"
  - "Bash(python3*)"
  - "Bash(agent-brain*)"
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
