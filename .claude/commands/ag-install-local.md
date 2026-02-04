---
context: fork
agent: install_agent
---

# ag-install-local

Local build-and-install of Agent Brain server + CLI + plugin for rapid testing.

## Arguments

- `--restore-pypi` - Use PyPI dependency instead of local path (for release prep)

## Task

Run the install script with the appropriate flags:

**If `--restore-pypi` was passed:**
```bash
.claude/skills/installing-local/install.sh --restore-pypi
```

**Otherwise (default - local dev mode):**
```bash
.claude/skills/installing-local/install.sh --use-path-deps
```

## Expected Result

Report:
- Python 3.11 verification
- Servers killed
- Old versions uninstalled
- Dependency mode (path or PyPI)
- Build success
- Install verification (new code confirmed)
- Plugin deployed
- Final version and path
