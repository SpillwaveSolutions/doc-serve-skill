---
name: agent-brain-setup
description: |
  Installation and configuration guide for Agent Brain.
  Use when users need to install packages, configure API keys,
  initialize projects, or troubleshoot setup issues.
  Covers pip installation, environment variables, and server management.
license: MIT
metadata:
  version: 1.0.0
  category: ai-tools
  author: Spillwave
---

# Agent Brain Setup Skill

Complete guide for installing and configuring Agent Brain for document search.

## Contents

- [Quick Setup](#quick-setup)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Verification](#verification)
- [Reference Documentation](#reference-documentation)

---

## Quick Setup

```bash
# 1. Install packages
pip install agent-brain-rag agent-brain-cli

# 2. Configure API key
export OPENAI_API_KEY="sk-proj-..."

# 3. Initialize project
agent-brain init

# 4. Start server
agent-brain start --daemon

# 5. Verify setup
agent-brain status
```

---

## Prerequisites

### Required
- **Python 3.10+**: Check with `python --version`
- **pip**: Python package manager
- **OpenAI API Key**: Required for vector/hybrid search modes

### Optional
- **Anthropic API Key**: For code summarization features

### System Requirements
- ~500MB RAM for typical document collections
- Disk space for ChromaDB vector store

---

## Installation

### Step 1: Install Packages

```bash
# Install both packages
pip install agent-brain-rag agent-brain-cli

# Verify installation
agent-brain --help
```

### Step 2: Verify Python Version

```bash
python --version
# Should be 3.10 or higher
```

### Upgrade Existing Installation

```bash
pip install --upgrade agent-brain-rag agent-brain-cli
```

### Installation Troubleshooting

| Problem | Solution |
|---------|----------|
| `pip not found` | Install pip: `python -m ensurepip` |
| Permission denied | Use `pip install --user` or virtual env |
| Module not found | Ensure pip installed to correct Python |

---

## Configuration

### Required: OpenAI API Key

The OpenAI API key is required for vector and hybrid search modes.

**Option 1: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY="sk-proj-..."
```

**Option 2: Shell Profile (Persistent)**
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export OPENAI_API_KEY="sk-proj-..."' >> ~/.bashrc
source ~/.bashrc
```

**Get API Key:**
- Visit: https://platform.openai.com/account/api-keys
- Create new secret key
- Copy and save securely

### Optional: Anthropic API Key

For code summarization features:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Get API Key:**
- Visit: https://console.anthropic.com/
- Create API key

### Verify Keys Are Set

```bash
# Check if keys are configured
echo "OpenAI: ${OPENAI_API_KEY:+SET}"
echo "Anthropic: ${ANTHROPIC_API_KEY:+SET}"
```

---

## Project Initialization

### Initialize Project

```bash
cd /path/to/your/project
agent-brain init
```

This creates `.claude/agent-brain/` directory with:
- `config.json` - Project configuration
- `runtime.json` - Server state (created on start)

### Start Server

```bash
# Start in daemon mode (background)
agent-brain start --daemon

# Or start in foreground
agent-brain start
```

### Index Documents

```bash
# Index documentation
agent-brain index /path/to/docs

# Index with code files
agent-brain index /path/to/project --include-code
```

### Stop Server

```bash
agent-brain stop
```

---

## Verification

### Check Installation

```bash
# Verify CLI is installed
agent-brain --help

# Check version
agent-brain --version
```

### Check Server Status

```bash
agent-brain status
```

Expected output:
```
Server Status: healthy
Port: 49321
Documents: 150
Chunks: 750
Mode: project
```

### Test Search

```bash
# Quick test with BM25 (no API needed)
agent-brain query "test" --mode bm25

# Test with hybrid (requires OpenAI key)
agent-brain query "test" --mode hybrid
```

### Full Verification Checklist

- [ ] `agent-brain --help` shows commands
- [ ] `OPENAI_API_KEY` is set
- [ ] `agent-brain init` succeeds
- [ ] `agent-brain start --daemon` starts server
- [ ] `agent-brain status` shows healthy
- [ ] Documents indexed (count > 0)
- [ ] Query returns results

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for embeddings |
| `ANTHROPIC_API_KEY` | No | - | Anthropic key for summarization |
| `DOC_SERVE_URL` | No | Auto-detect | Override server URL |
| `DOC_SERVE_STATE_DIR` | No | `.claude/agent-brain` | State directory |
| `DOC_SERVE_MODE` | No | `project` | Instance mode |

---

## Reference Documentation

| Guide | Description |
|-------|-------------|
| [Installation Guide](references/installation-guide.md) | Detailed installation steps |
| [Configuration Guide](references/configuration-guide.md) | API keys and settings |
| [Troubleshooting Guide](references/troubleshooting-guide.md) | Common issues and solutions |

---

## Common Setup Issues

### Issue: Module Not Found

```bash
# Reinstall packages
pip install --force-reinstall agent-brain-rag agent-brain-cli
```

### Issue: API Key Not Working

```bash
# Test OpenAI key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Issue: Server Won't Start

```bash
# Check for port conflicts
lsof -i :8000

# Clean up stale state
rm -rf .claude/agent-brain/runtime.json
rm -rf .claude/agent-brain/lock.json
agent-brain start --daemon
```

### Issue: No Search Results

```bash
# Check if documents are indexed
agent-brain status

# If count is 0, index documents
agent-brain index /path/to/docs
```

---

## Support

- Issues: https://github.com/SpillwaveSolutions/agent-brain-plugin/issues
- Documentation: See reference guides in this skill
