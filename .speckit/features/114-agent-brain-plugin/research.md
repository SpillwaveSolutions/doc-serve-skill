# Research: Agent Brain Plugin Conversion

**Feature**: 114-agent-brain-plugin
**Date**: 2025-01-31

## Research Topics

### 1. Claude Code Plugin Structure (marketplace.json format)

**Decision**: Use full marketplace.json format with commands/, agents/, skills/ folders

**Rationale**:
- The spec requires separate slash commands (not subcommands), which requires the full plugin format
- Agents for proactive assistance require the agents/ folder
- Skills for reference documentation require the skills/ folder
- marketplace.json provides full manifest capabilities

**Alternatives Considered**:
- Simple plugin.json format: Rejected - doesn't support explicit commands or agents
- Skill-only approach: Rejected - user requested explicit commands for discoverability

**Source**: `~/.claude/skills/creating-plugin-from-skill/SKILL.md` and `references/commands-agents.md`

### 2. Command File Format

**Decision**: Use markdown files with YAML frontmatter

**Format**:
```yaml
---
name: agent-brain-search
description: Search indexed documentation using hybrid retrieval
parameters:
  - name: query
    description: The search query text
    required: true
  - name: top-k
    description: Number of results to return
    required: false
    default: 5
skills:
  - using-agent-brain
---

# Agent Brain Search

[Command instructions for Claude...]
```

**Rationale**:
- YAML frontmatter defines command metadata (name, description, parameters)
- Markdown body provides detailed instructions for Claude
- `skills:` field links to reference skills for domain knowledge

**Source**: `~/.claude/skills/creating-plugin-from-skill/references/commands-agents.md`

### 3. Agent File Format

**Decision**: Use markdown files with triggers array in frontmatter

**Format**:
```yaml
---
name: search-assistant
description: Proactively offers to search documentation
triggers:
  - pattern: "search.*docs|find.*documentation"
    type: message_pattern
  - pattern: "how do I search"
    type: keyword
skills:
  - using-agent-brain
---

# Search Assistant Agent

[Agent behavior instructions...]
```

**Rationale**:
- Triggers define when agent activates (patterns, keywords, file mentions)
- Linked skills provide domain knowledge
- Natural language interaction without requiring exact commands

**Source**: `~/.claude/skills/creating-plugin-from-skill/references/commands-agents.md`

### 4. Skill File Format

**Decision**: Use SKILL.md with references/ folder

**Format**:
```yaml
---
name: using-agent-brain
description: |
  Agent Brain document search with BM25 keyword, semantic vector, and hybrid retrieval modes.
  Use when asked to "search documentation", "query domain", "find in docs".
license: MIT
metadata:
  version: 1.3.0
  category: ai-tools
  author: Spillwave
---

# Using Agent Brain Skill

[Core instructions, quick start, best practices...]
```

**Rationale**:
- SKILL.md provides main instructions (loaded when skill triggers)
- references/ folder contains detailed documentation (loaded on demand)
- Description field determines when Claude invokes the skill

**Source**: `~/.claude/skills/skill-creator/SKILL.md`

### 5. Quality Scoring Process

**Decision**: Use improving-skills workflow with iterative grading

**Process**:
1. Create initial skill using skill-creator best practices
2. Grade with improving-skills rubric
3. Identify issues and implement fixes
4. Re-grade until 95% score achieved

**Grading Categories** (from improving-skills skill):
- Progressive Disclosure Architecture (PDA)
- Trigger accuracy and description quality
- Reference file organization
- Workflow clarity and error handling
- Best practices compliance

**Target**: 95% score for both using-agent-brain and agent-brain-setup skills

**Source**: `~/.claude/skills/improving-skills/SKILL.md`

### 6. Existing Skill Content Migration

**Decision**: Migrate existing using-agent-brain skill content with enhancements

**Current skill location**: `agent-brain-skill/using-agent-brain/`

**Migration approach**:
- Copy existing SKILL.md content as base
- Copy existing references/ folder content
- Update for new plugin structure
- Add any missing content for command/agent integration

**Existing references** to migrate:
- hybrid-search-guide.md
- bm25-search-guide.md
- vector-search-guide.md
- api_reference.md
- server-discovery.md
- troubleshooting-guide.md
- integration-guide.md

**Source**: Repository `agent-brain-skill/using-agent-brain/`

### 7. CLI Command Mapping

**Decision**: Map each plugin command to underlying CLI command

| Plugin Command | CLI Command | Purpose |
|----------------|-------------|---------|
| `/agent-brain-search` | `agent-brain query --mode hybrid` | Hybrid search |
| `/agent-brain-semantic` | `agent-brain query --mode vector` | Vector search |
| `/agent-brain-keyword` | `agent-brain query --mode bm25` | BM25 search |
| `/agent-brain-install` | `pip install agent-brain-rag agent-brain-cli` | Install packages |
| `/agent-brain-setup` | Guided flow calling multiple commands | Complete setup |
| `/agent-brain-config` | Environment variable guidance | API key config |
| `/agent-brain-init` | `agent-brain init` | Project init |
| `/agent-brain-verify` | `agent-brain status` | Verify installation |
| `/agent-brain-start` | `agent-brain start --daemon` | Start server |
| `/agent-brain-stop` | `agent-brain stop` | Stop server |
| `/agent-brain-status` | `agent-brain status` | Check status |
| `/agent-brain-list` | `agent-brain list` | List instances |
| `/agent-brain-index` | `agent-brain index <path>` | Index documents |
| `/agent-brain-reset` | `agent-brain reset --yes` | Clear index |
| `/agent-brain-help` | Display command list | Show help |

**Source**: Repository `agent-brain-cli/` and existing skill documentation

### 8. GitHub Repository Setup

**Decision**: Create new GitHub repository for plugin

**Repository name**: `agent-brain-plugin` (or `agent-brain-agentic-plugin`)
**Organization**: SpillwaveSolutions
**Installation URL**: `https://github.com/SpillwaveSolutions/agent-brain-plugin`

**Plugin installation** (user perspective):
```bash
cd ~/.claude/plugins
git clone https://github.com/SpillwaveSolutions/agent-brain-plugin.git
```

**Source**: `~/.claude/skills/creating-plugin-from-skill/SKILL.md`

## Resolved Clarifications

All technical clarifications have been resolved through research. No remaining NEEDS CLARIFICATION items.

## Next Steps

1. Phase 1: Create data-model.md with entity definitions
2. Phase 1: Create contracts/ with command and agent schemas
3. Phase 1: Create quickstart.md for developer onboarding
4. Update agent context with new technology decisions
