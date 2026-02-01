# Skill Schema Contract

**Feature**: 114-agent-brain-plugin
**Date**: 2025-01-31

## Skill File Schema

All skills in `skills/` MUST follow this schema.

### Directory Structure

```
skills/<skill-name>/
├── SKILL.md              # Required: main skill file
└── references/           # Optional: detailed documentation
    └── *.md
```

### SKILL.md Frontmatter (Required)

```yaml
---
name: <skill-name>              # Required: lowercase, hyphenated
description: |                  # Required: multi-line description
  <what-skill-does>
  <when-to-use>
license: MIT                    # Optional: license type
metadata:
  version: <semver>             # Optional: skill version
  category: <category>          # Optional: skill category
  author: <author>              # Optional: author/org
---
```

### SKILL.md Body (Required)

The body MUST contain:
1. **Title**: `# <Skill Name>`
2. **Quick Start**: Essential commands to get started
3. **Core Instructions**: Main workflow guidance
4. **Best Practices**: Usage recommendations
5. **Reference Links**: Links to references/ files

## Skill Definitions

### using-agent-brain

**Purpose**: Provide search capability guidance for Claude when users want to search documentation.

**Directory Structure**:
```
skills/using-agent-brain/
├── SKILL.md
└── references/
    ├── hybrid-search-guide.md
    ├── bm25-search-guide.md
    ├── vector-search-guide.md
    └── api_reference.md
```

**SKILL.md Outline**:
```yaml
---
name: using-agent-brain
description: |
  Agent Brain document search with BM25 keyword, semantic vector, and hybrid retrieval modes.
  Use when asked to "search documentation", "query domain", "find in docs",
  "bm25 search", "hybrid search", "semantic search", "agent-brain query",
  "brain search", "brain query", or "knowledge base search".
  Supports multi-instance architecture with automatic server discovery.
license: MIT
metadata:
  version: 1.3.0
  category: ai-tools
  author: Spillwave
---

# Agent Brain Skill

Document search with three modes: BM25 (keyword), Vector (semantic), and Hybrid (fusion).

## Quick Start

1. Check server status: `agent-brain status`
2. Search: `agent-brain query "search term" --mode hybrid`

## Search Modes

| Mode | Speed | Use For |
|------|-------|---------|
| bm25 | Fast | Technical terms, function names |
| vector | Slower | Concepts, explanations |
| hybrid | Slower | Comprehensive results |

## Best Practices

1. Use BM25 for exact matches
2. Use Vector for conceptual queries
3. Start threshold at 0.3, increase for precision

## Reference Documentation

- [Hybrid Search Guide](references/hybrid-search-guide.md)
- [BM25 Search Guide](references/bm25-search-guide.md)
- [Vector Search Guide](references/vector-search-guide.md)
- [API Reference](references/api_reference.md)
```

**Reference Files**:

| File | Content |
|------|---------|
| `hybrid-search-guide.md` | Hybrid mode details, alpha tuning, use cases |
| `bm25-search-guide.md` | BM25 algorithm, keyword matching, filters |
| `vector-search-guide.md` | Vector similarity, embedding model, threshold tuning |
| `api_reference.md` | REST API endpoints, request/response formats |

### agent-brain-setup

**Purpose**: Guide users through Agent Brain installation and configuration.

**Directory Structure**:
```
skills/agent-brain-setup/
├── SKILL.md
└── references/
    ├── installation-guide.md
    ├── configuration-guide.md
    └── troubleshooting-guide.md
```

**SKILL.md Outline**:
```yaml
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

# Agent Brain Setup

Complete guide for installing and configuring Agent Brain.

## Quick Setup

1. Install: `pip install agent-brain-rag agent-brain-cli`
2. Configure: Set `OPENAI_API_KEY` environment variable
3. Initialize: `agent-brain init`
4. Start: `agent-brain start --daemon`
5. Verify: `agent-brain status`

## Prerequisites

- Python 3.10+
- pip package manager
- OpenAI API key (for vector/hybrid search)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| OPENAI_API_KEY | Yes | OpenAI API key for embeddings |
| ANTHROPIC_API_KEY | No | Claude API key for summarization |

## Reference Documentation

- [Installation Guide](references/installation-guide.md)
- [Configuration Guide](references/configuration-guide.md)
- [Troubleshooting Guide](references/troubleshooting-guide.md)
```

**Reference Files**:

| File | Content |
|------|---------|
| `installation-guide.md` | Package installation, Python requirements, pip commands |
| `configuration-guide.md` | API keys, environment setup, project initialization |
| `troubleshooting-guide.md` | Common errors, solutions, diagnostic commands |

## Quality Requirements

Both skills MUST achieve 95% score from the improving-skills grading rubric:

1. **Progressive Disclosure Architecture (PDA)**: SKILL.md under 500 lines, references for details
2. **Trigger Accuracy**: Description covers all relevant use cases
3. **Reference Organization**: Clear file names, logical grouping
4. **Workflow Clarity**: Step-by-step instructions, error handling
5. **Best Practices**: Following skill-creator guidelines
