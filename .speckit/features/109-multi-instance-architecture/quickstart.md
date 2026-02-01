# Quickstart: Multi-Instance Architecture

## Per-Project Mode (Default)

### 1. Initialize a project

```bash
cd /path/to/my-repo
agent-brain init
# Creates .claude/agent-brain/config.json with defaults
```

### 2. Start the server

```bash
agent-brain start
# → Server started at http://127.0.0.1:49321
# → State directory: /path/to/my-repo/.claude/agent-brain/
# → Discovery file: /path/to/my-repo/.claude/agent-brain/runtime.json
```

### 3. Check status (from any subdirectory)

```bash
cd /path/to/my-repo/src/deep/nested
agent-brain status
# → Agent Brain running at http://127.0.0.1:49321 (project mode)
# → Indexed: 1,234 chunks from 56 files
```

### 4. Index documents

```bash
agent-brain index /path/to/my-repo/docs
```

### 5. Query

```bash
agent-brain query "how does authentication work?"
```

### 6. Stop

```bash
agent-brain stop
# → Server stopped. Cleanup complete.
```

## Multiple Projects

```bash
# Terminal 1
cd /path/to/project-a
agent-brain start
# → Started on port 49321

# Terminal 2
cd /path/to/project-b
agent-brain start
# → Started on port 49322 (auto-assigned, no conflict)

# List all running instances
agent-brain list
# → project-a: http://127.0.0.1:49321 (project mode)
# → project-b: http://127.0.0.1:49322 (project mode)
```

## Shared Daemon Mode (Optional)

```bash
# Start shared daemon
agent-brain start --mode shared
# → Shared daemon started at http://127.0.0.1:45123

# From project A
cd /path/to/project-a
agent-brain init --mode shared
agent-brain start
# → Registered with shared daemon at http://127.0.0.1:45123

# From project B
cd /path/to/project-b
agent-brain init --mode shared
agent-brain start
# → Registered with shared daemon at http://127.0.0.1:45123
```

## For Skill Authors

```python
from doc_serve_client import discover_or_start

# Discovers running instance or starts one
runtime = discover_or_start(project_root=Path.cwd())
base_url = runtime.base_url  # e.g., "http://127.0.0.1:49321"
```

## Verification Checklist

- [ ] `agent-brain init` creates `.claude/agent-brain/config.json`
- [ ] `agent-brain start` creates `runtime.json` with actual port
- [ ] `agent-brain status` works from any subdirectory
- [ ] `agent-brain stop` removes all runtime artifacts
- [ ] Two projects can run concurrently on different ports
- [ ] Crashed instance recovers on next `agent-brain start`
- [ ] `.claude/agent-brain/runtime.json` is in `.gitignore`
