# Doc-Serve Quick Start

Get up and running with Doc-Serve in minutes using the command-line tools.

## 1. Installation

Install Doc-Serve and the management tool globally using the Task runner:

```bash
# Clone the repository
git clone git@github.com:SpillwaveSolutions/doc-serve.git
cd doc-serve

# Install tools globally (makes 'doc-serve' and 'doc-svr-ctl' available)
task install:global
```

## 2. Configuration

Create a `.env` file in the `doc-serve-server` directory with your API keys:

```bash
cd doc-serve-server
cp .env.example .env
# Edit .env and add:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

## 3. Launch the Server

Start the Doc-Serve API server:

```bash
# From any directory
doc-serve
```
*Keep this terminal open or run in the background with `doc-serve &`.*

## 4. Index Documents

Use the CLI tool to index a folder of documents (Markdown, TXT, PDF, etc.):

```bash
# Example: Index the coffee brewing test docs
doc-svr-ctl index ./e2e/fixtures/test_docs/coffee_brewing
```

Check the status to ensure indexing is complete:
```bash
doc-svr-ctl status
```

## 5. Query Knowledge

Perform a semantic search over your indexed documents:

```bash
# Search for espresso information
doc-svr-ctl query "espresso" --threshold 0.5

# Compare brewing methods
doc-svr-ctl query "espresso vs french press" --threshold 0.2
```

## Common Commands Summary

| Task | Command |
|------|---------|
| **Start Server** | `doc-serve` |
| **Check Status** | `doc-svr-ctl status` |
| **Index Folder** | `doc-svr-ctl index /path/to/docs` |
| **Search** | `doc-svr-ctl query "your question"` |
| **Reset Index** | `doc-svr-ctl reset --yes` |
