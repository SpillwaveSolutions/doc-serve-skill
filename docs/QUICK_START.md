# Doc-Serve Quick Start

Get up and running with Doc-Serve in minutes using the command-line tools.

## 1. Installation

Install Doc-Serve and the management tool globally using the Task runner:

```bash
# Clone the repository
git clone git@github.com:SpillwaveSolutions/doc-serve.git
cd doc-serve

# Install tools globally (makes 'doc-serve' and 'agent-brain' available)
task install:global
```

## 2. Configuration

Create a `.env` file in the `agent-brain-server` directory with your API keys:

```bash
cd agent-brain-server
cp .env.example .env
# Edit .env and add:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

## 3. Launch the Server

### Option A: Multi-Instance Mode (Recommended)

Initialize and start a project-specific server with auto-port allocation:

```bash
cd /path/to/your/project
agent-brain init      # Creates .claude/doc-serve/ directory
agent-brain start --daemon   # Starts server with auto-assigned port
```

The server runs in the background with isolated indexes for this project.

### Option B: Legacy Single-Instance Mode

Start the Doc-Serve API server directly:

```bash
doc-serve
```
*Keep this terminal open or run in the background with `doc-serve &`.*

## 4. Index Documents and Code

Doc-Serve can index both documentation and source code for unified search:

### Index Documentation Only (Default)
```bash
# Index documentation files (Markdown, TXT, PDF, etc.)
agent-brain index ./docs
```

### Index Code + Documentation (Recommended)
```bash
# Index both documentation and source code files
agent-brain index ./my-project --include-code
```

### Advanced Indexing Options
```bash
# Index specific programming languages
agent-brain index ./src --include-code --languages python,typescript

# Use AST-aware chunking for better code understanding
agent-brain index ./src --include-code --code-strategy ast_aware

# Generate LLM summaries for code chunks (improves semantic search)
agent-brain index ./src --include-code --generate-summaries
```

Check the status to ensure indexing is complete:
```bash
agent-brain status
```

## 5. Query Knowledge

Doc-Serve supports three powerful search modes:

### Semantic Search (Vector - Default)
```bash
# Search for espresso information using semantic similarity
agent-brain query "espresso brewing techniques"
```

### Keyword Search (BM25)
```bash
# Search for exact word matches (great for function names, error codes)
agent-brain query "espresso" --mode bm25
```

### Hybrid Search (Recommended)
```bash
# Combine semantic and keyword search (best of both worlds)
agent-brain query "espresso vs french press" --mode hybrid --alpha 0.7
```

### Advanced Options
```bash
# Show individual scores for hybrid results
agent-brain query "brewing methods" --mode hybrid --scores

# Adjust result count and similarity threshold
agent-brain query "coffee temperature" --top-k 10 --threshold 0.3
```

### Code-Aware Search (with Code Ingestion)

When code is indexed, you can perform cross-reference searches with AST-aware metadata:

```bash
# Search across both documentation and code
agent-brain query "authentication implementation"

# Filter results by source type
agent-brain query "API endpoints" --source-types code      # Code only
agent-brain query "API usage" --source-types doc           # Docs only

# Filter by programming language
agent-brain query "database connection" --languages python,typescript

# Combine filters for precise results
agent-brain query "error handling" --source-types code --languages go

# Search by specific function or class name (BM25 recommended for identifiers)
agent-brain query "authenticate_user" --mode bm25 --source-types code
```

### Supported Languages
Doc-Serve supports AST-aware code ingestion for: **Python, TypeScript, JavaScript, Java, Go, Rust, C, C++, C#**. Other languages are supported via intelligent text-based chunking.

**C# Support:** Files with `.cs` and `.csx` extensions are parsed with AST-aware chunking, extracting classes, methods, interfaces, and XML documentation comments.

## Common Commands Summary

### Multi-Instance Commands (Recommended)

| Task | Command |
|------|---------|
| **Initialize Project** | `agent-brain init` |
| **Start Server** | `agent-brain start --daemon` |
| **Stop Server** | `agent-brain stop` |
| **List All Instances** | `agent-brain list` |
| **Check Status** | `agent-brain status` |

### Data Commands

| Task | Command |
|------|---------|
| **Index Docs Only** | `agent-brain index /path/to/docs` |
| **Index Code + Docs** | `agent-brain index /path --include-code` |
| **Semantic Search** | `agent-brain query "your question"` |
| **Keyword Search** | `agent-brain query "keyword" --mode bm25` |
| **Hybrid Search** | `agent-brain query "question" --mode hybrid --alpha 0.5` |
| **Filter by Source** | `agent-brain query "term" --source-types code` |
| **Filter by Language** | `agent-brain query "term" --languages python,csharp` |
| **Reset Index** | `agent-brain reset --yes` |
