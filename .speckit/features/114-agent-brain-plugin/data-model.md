# Data Model: Agent Brain Plugin

**Feature**: 114-agent-brain-plugin
**Date**: 2025-01-31

## Overview

This plugin is a collection of markdown files with YAML frontmatter. There are no database entities. The "data model" describes the file structures and their relationships.

## Entity: Plugin Manifest

**File**: `.claude-plugin/marketplace.json`

```json
{
  "name": "agent-brain-plugin",
  "description": "Document search with hybrid BM25/semantic retrieval",
  "version": "1.0.0",
  "owner": {
    "name": "Spillwave Solutions",
    "email": "support@spillwave.com"
  },
  "metadata": {
    "category": "ai-tools",
    "tags": ["search", "documentation", "rag", "semantic"]
  },
  "plugins": [
    {
      "name": "agent-brain",
      "description": "Document indexing and semantic search",
      "source": "./",
      "strict": false,
      "skills": [
        "./skills/using-agent-brain",
        "./skills/agent-brain-setup"
      ],
      "commands": [
        "./commands/agent-brain-search.md",
        "./commands/agent-brain-semantic.md",
        "./commands/agent-brain-keyword.md",
        "./commands/agent-brain-install.md",
        "./commands/agent-brain-setup.md",
        "./commands/agent-brain-config.md",
        "./commands/agent-brain-init.md",
        "./commands/agent-brain-verify.md",
        "./commands/agent-brain-start.md",
        "./commands/agent-brain-stop.md",
        "./commands/agent-brain-status.md",
        "./commands/agent-brain-list.md",
        "./commands/agent-brain-index.md",
        "./commands/agent-brain-reset.md",
        "./commands/agent-brain-help.md"
      ],
      "agents": [
        "./agents/search-assistant.md",
        "./agents/setup-assistant.md"
      ]
    }
  ]
}
```

## Entity: Command

**Location**: `commands/<command-name>.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Command name (without slash prefix) |
| `description` | string | Yes | Short description for help menu |
| `parameters` | array | No | Command parameters |
| `skills` | array | No | Skills this command uses |

### Parameter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Parameter name (e.g., `query`, `top-k`) |
| `description` | string | Yes | Parameter description |
| `required` | boolean | No | Whether parameter is required (default: false) |
| `default` | any | No | Default value if not provided |

### Command Body

The markdown body contains instructions Claude follows when the command is invoked. It should include:
- What the command does
- How to execute the underlying CLI command
- How to format and present results
- Error handling guidance

## Entity: Agent

**Location**: `agents/<agent-name>.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Agent identifier |
| `description` | string | Yes | What the agent does |
| `triggers` | array | Yes | Activation triggers |
| `skills` | array | No | Skills this agent can use |

### Trigger Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pattern` | string | Yes | Regex pattern or keyword |
| `type` | string | Yes | Trigger type: `file_mention`, `message_pattern`, `keyword` |

### Agent Body

The markdown body contains instructions for agent behavior:
- When to activate (beyond trigger patterns)
- How to offer assistance
- What commands to recommend
- How to handle various scenarios

## Entity: Skill

**Location**: `skills/<skill-name>/SKILL.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Skill name (lowercase, hyphenated) |
| `description` | string | Yes | When to use this skill |
| `license` | string | No | License type (e.g., MIT) |
| `metadata.version` | string | No | Skill version |
| `metadata.category` | string | No | Skill category |
| `metadata.author` | string | No | Author/organization |

### Skill Body

The markdown body contains:
- Quick start guide
- Core instructions
- Best practices
- Links to references/ files

### Reference Files

**Location**: `skills/<skill-name>/references/`

Each reference file is a standalone markdown document containing detailed documentation on a specific topic. Files are loaded on-demand when Claude needs detailed information.

## Relationships

```
marketplace.json
    ├── commands/
    │   └── *.md (references skills in frontmatter)
    ├── agents/
    │   └── *.md (references skills in frontmatter)
    └── skills/
        └── <skill-name>/
            ├── SKILL.md (main entry point)
            └── references/
                └── *.md (detailed docs)
```

## File Count Summary

| Entity Type | Count | Files |
|-------------|-------|-------|
| Plugin Manifest | 1 | marketplace.json |
| Commands | 15 | agent-brain-*.md |
| Agents | 2 | search-assistant.md, setup-assistant.md |
| Skills | 2 | using-agent-brain, agent-brain-setup |
| Skill References | 7 | hybrid-search-guide.md, bm25-search-guide.md, vector-search-guide.md, api_reference.md, installation-guide.md, configuration-guide.md, troubleshooting-guide.md |
| Other | 2 | README.md, .gitignore |
| **Total** | **29** | |
