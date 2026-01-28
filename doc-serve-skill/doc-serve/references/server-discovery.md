# Server Discovery Guide

Automatic discovery and management of doc-serve instances.

## Contents

- [Runtime File](#runtime-file)
- [Discovery Process](#discovery-process)
- [Python Discovery Script](#python-discovery-script)
- [Cross-Agent Sharing](#cross-agent-sharing)
- [Troubleshooting](#troubleshooting)

---

## Runtime File

Doc-serve writes connection details to `.claude/doc-serve/runtime.json`:

```json
{
  "schema_version": "1.0",
  "mode": "project",
  "project_root": "/path/to/project",
  "instance_id": "a1b2c3d4e5f6",
  "base_url": "http://127.0.0.1:54321",
  "port": 54321,
  "pid": 12345,
  "started_at": "2026-01-28T10:30:00+00:00"
}
```

| Field | Description |
|-------|-------------|
| `base_url` | Server URL for API calls |
| `port` | Auto-assigned port number |
| `instance_id` | Unique instance identifier |
| `pid` | Process ID for health checks |
| `mode` | "project" (per-project) or "shared" |

---

## Discovery Process

1. **Project Root Resolution**: `git rev-parse --show-toplevel` or marker files (`.claude/`, `pyproject.toml`)
2. **Runtime File Check**: Look for `.claude/doc-serve/runtime.json`
3. **Health Validation**: Verify server via `/health/` endpoint
4. **URL Extraction**: Use `base_url` for API calls

---

## Python Discovery Script

```python
import json
import subprocess
from pathlib import Path
import urllib.request

def discover_server():
    """Discover a running doc-serve instance for the current project.

    Returns:
        str: Server base URL if found and healthy, None otherwise.
    """
    # Find project root
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True
        )
        project_root = Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        project_root = Path.cwd()

    # Check for runtime.json
    runtime_path = project_root / ".claude" / "doc-serve" / "runtime.json"
    if not runtime_path.exists():
        return None

    # Read and parse runtime state
    try:
        state = json.loads(runtime_path.read_text())
    except json.JSONDecodeError:
        return None

    # Validate server is alive
    base_url = state.get("base_url", "")
    if not base_url:
        return None

    try:
        req = urllib.request.Request(f"{base_url}/health/", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                return base_url
    except Exception:
        pass

    return None


def get_server_url():
    """Get server URL, starting server if needed.

    Returns:
        str: Server base URL.
    """
    url = discover_server()
    if url:
        return url

    # Start server and wait
    subprocess.run(["doc-svr-ctl", "start", "--daemon"], check=True)

    # Re-discover after startup
    import time
    for _ in range(10):
        time.sleep(1)
        url = discover_server()
        if url:
            return url

    raise RuntimeError("Failed to start doc-serve server")


# Usage
if __name__ == "__main__":
    server_url = discover_server()
    if server_url:
        print(f"Connected to: {server_url}")
    else:
        print("No running server found - starting one...")
        subprocess.run(["doc-svr-ctl", "start", "--daemon"])
```

---

## Cross-Agent Sharing

Multiple Claude agents in the same project share one instance:

1. **First agent** starts server: `doc-svr-ctl start --daemon`
2. **Other agents** discover via `runtime.json`
3. **All agents** use same `base_url`
4. **Any agent** can stop when work complete

Lock file protocol prevents race conditions during concurrent startup attempts.

---

## Troubleshooting

### Server Not Found

```
Error: No running doc-serve instance found for this project
```

**Solution**: `doc-svr-ctl start --daemon`

### Stale Server State

```
Warning: Server not responding, cleaning up stale state
```

**Solution**: CLI auto-cleans stale files. Manual cleanup:
```bash
rm .claude/doc-serve/runtime.json
doc-svr-ctl start --daemon
```

### Port Conflict

**Solution**: Use auto-port (default): `doc-svr-ctl start --daemon`

### Multiple Agents Racing

Lock file prevents double-start. If blocked, run `doc-svr-ctl status` to discover existing instance.

### Finding Server Port

```bash
doc-svr-ctl status                              # Recommended
cat .claude/doc-serve/runtime.json | jq '.port' # Direct read
doc-svr-ctl list                                # All instances
```

### Environment Override

```bash
export DOC_SERVE_URL="http://127.0.0.1:8000"
doc-svr-ctl query "search term"
```
