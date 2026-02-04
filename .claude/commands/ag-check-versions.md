---
context: fork
agent: version_resolver_agent
---

# ag-check-versions

Check Agent Brain package versions (read-only).

## Task

Query and compare versions:

1. **PyPI versions** (latest published):
   ```bash
   curl -s https://pypi.org/pypi/agent-brain-rag/json | python3 -c "import sys,json; print(json.load(sys.stdin)['info']['version'])"
   curl -s https://pypi.org/pypi/agent-brain-cli/json | python3 -c "import sys,json; print(json.load(sys.stdin)['info']['version'])"
   ```

2. **Local versions**:
   ```bash
   grep '^version = ' agent-brain-server/pyproject.toml | cut -d'"' -f2
   grep '^version = ' agent-brain-cli/pyproject.toml | cut -d'"' -f2
   ```

3. **CLI dependency type**:
   ```bash
   grep 'agent-brain-rag' agent-brain-cli/pyproject.toml
   ```

## Expected Result

Report in table format:
- PyPI server version
- PyPI CLI version
- Local server version
- Local CLI version
- CLI dependency: `path` or `PyPI ^X.Y.Z`
- Alignment status: aligned / misaligned / local ahead
