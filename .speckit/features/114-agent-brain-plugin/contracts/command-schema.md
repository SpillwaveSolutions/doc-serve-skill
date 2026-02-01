# Command Schema Contract

**Feature**: 114-agent-brain-plugin
**Date**: 2025-01-31

## Command File Schema

All command files in `commands/` MUST follow this schema.

### YAML Frontmatter (Required)

```yaml
---
name: <command-name>           # Required: lowercase, hyphenated
description: <short-desc>       # Required: 1-2 sentence description
parameters:                     # Optional: command parameters
  - name: <param-name>
    description: <param-desc>
    required: <true|false>
    default: <default-value>
skills:                         # Optional: skills to load
  - <skill-name>
---
```

### Markdown Body (Required)

The body MUST contain:
1. **Heading**: `# <Command Title>`
2. **Purpose**: What the command does
3. **Usage**: Command syntax with parameters
4. **Execution**: CLI command(s) to run
5. **Output**: How to format and present results
6. **Error Handling**: Common errors and guidance

## Command Definitions

### Search Commands

#### /agent-brain-search

```yaml
---
name: agent-brain-search
description: Search indexed documentation using hybrid BM25+semantic retrieval
parameters:
  - name: query
    description: The search query text
    required: true
  - name: top-k
    description: Number of results to return (1-20)
    required: false
    default: 5
  - name: threshold
    description: Minimum relevance score (0.0-1.0)
    required: false
    default: 0.3
  - name: alpha
    description: Hybrid blend (0=BM25 only, 1=semantic only)
    required: false
    default: 0.5
skills:
  - using-agent-brain
---
```

#### /agent-brain-semantic

```yaml
---
name: agent-brain-semantic
description: Search using semantic vector similarity for conceptual queries
parameters:
  - name: query
    description: The conceptual search query
    required: true
  - name: top-k
    description: Number of results (1-20)
    required: false
    default: 5
  - name: threshold
    description: Minimum similarity score (0.0-1.0)
    required: false
    default: 0.3
skills:
  - using-agent-brain
---
```

#### /agent-brain-keyword

```yaml
---
name: agent-brain-keyword
description: Search using BM25 keyword matching for exact terms
parameters:
  - name: query
    description: The exact search terms
    required: true
  - name: top-k
    description: Number of results (1-20)
    required: false
    default: 5
skills:
  - using-agent-brain
---
```

### Setup Commands

#### /agent-brain-install

```yaml
---
name: agent-brain-install
description: Install Agent Brain packages (agent-brain-rag and agent-brain-cli)
parameters: []
skills:
  - agent-brain-setup
---
```

#### /agent-brain-setup

```yaml
---
name: agent-brain-setup
description: Complete guided setup for Agent Brain (install, config, init, verify)
parameters: []
skills:
  - agent-brain-setup
---
```

#### /agent-brain-config

```yaml
---
name: agent-brain-config
description: Configure API keys for Agent Brain (OPENAI_API_KEY, ANTHROPIC_API_KEY)
parameters: []
skills:
  - agent-brain-setup
---
```

#### /agent-brain-init

```yaml
---
name: agent-brain-init
description: Initialize Agent Brain for the current project
parameters: []
skills:
  - agent-brain-setup
---
```

#### /agent-brain-verify

```yaml
---
name: agent-brain-verify
description: Verify Agent Brain installation and configuration
parameters: []
skills:
  - agent-brain-setup
---
```

### Server Commands

#### /agent-brain-start

```yaml
---
name: agent-brain-start
description: Start the Agent Brain server for this project
parameters:
  - name: daemon
    description: Run in background (default: true)
    required: false
    default: true
skills:
  - using-agent-brain
---
```

#### /agent-brain-stop

```yaml
---
name: agent-brain-stop
description: Stop the Agent Brain server for this project
parameters: []
skills:
  - using-agent-brain
---
```

#### /agent-brain-status

```yaml
---
name: agent-brain-status
description: Show Agent Brain server status (port, documents, health)
parameters:
  - name: json
    description: Output in JSON format
    required: false
    default: false
skills:
  - using-agent-brain
---
```

#### /agent-brain-list

```yaml
---
name: agent-brain-list
description: List all running Agent Brain instances across projects
parameters: []
skills:
  - using-agent-brain
---
```

### Indexing Commands

#### /agent-brain-index

```yaml
---
name: agent-brain-index
description: Index documents for semantic search
parameters:
  - name: path
    description: Path to documents to index
    required: true
  - name: include-code
    description: Include code files in indexing
    required: false
    default: false
skills:
  - using-agent-brain
---
```

#### /agent-brain-reset

```yaml
---
name: agent-brain-reset
description: Clear the document index (requires confirmation)
parameters:
  - name: yes
    description: Skip confirmation prompt
    required: false
    default: false
skills:
  - using-agent-brain
---
```

### Help Command

#### /agent-brain-help

```yaml
---
name: agent-brain-help
description: Show available Agent Brain commands and usage
parameters:
  - name: command
    description: Specific command to get help for
    required: false
skills:
  - using-agent-brain
  - agent-brain-setup
---
```
