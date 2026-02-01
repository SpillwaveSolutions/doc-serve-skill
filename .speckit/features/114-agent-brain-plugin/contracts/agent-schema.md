# Agent Schema Contract

**Feature**: 114-agent-brain-plugin
**Date**: 2025-01-31

## Agent File Schema

All agent files in `agents/` MUST follow this schema.

### YAML Frontmatter (Required)

```yaml
---
name: <agent-name>              # Required: lowercase, hyphenated
description: <what-agent-does>  # Required: 1-2 sentence description
triggers:                       # Required: at least one trigger
  - pattern: <regex-or-keyword>
    type: <trigger-type>
skills:                         # Optional: skills to load
  - <skill-name>
---
```

### Trigger Types

| Type | Description | Example Pattern |
|------|-------------|-----------------|
| `message_pattern` | Regex on user message | `search.*docs\|find.*documentation` |
| `keyword` | Simple keyword match | `agent brain` |
| `file_mention` | File name appears in message | `CLAUDE.md` |

### Markdown Body (Required)

The body MUST contain:
1. **Heading**: `# <Agent Title>`
2. **Purpose**: What the agent does
3. **Trigger Conditions**: When the agent activates
4. **Behavior**: How the agent responds
5. **Commands to Recommend**: Which commands to suggest

## Agent Definitions

### search-assistant

**Purpose**: Proactively offer document search when user mentions searching or finding information.

```yaml
---
name: search-assistant
description: Proactively offers to search documentation when user mentions searching, finding, or querying their codebase or docs
triggers:
  - pattern: "search.*(docs|documentation|codebase|files)"
    type: message_pattern
  - pattern: "find.*(in docs|documentation|files|code)"
    type: message_pattern
  - pattern: "how do I search"
    type: message_pattern
  - pattern: "look up"
    type: keyword
  - pattern: "where is.*documented"
    type: message_pattern
  - pattern: "agent brain"
    type: keyword
skills:
  - using-agent-brain
---

# Search Assistant

Proactively help users search their documentation using Agent Brain.

## Trigger Conditions

This agent activates when the user:
- Mentions searching documentation or codebase
- Asks how to find information in their project
- Mentions "agent brain" directly
- Asks "where is X documented?"

## Behavior

When triggered:

1. **Check if Agent Brain is set up**
   - Run `agent-brain status` to check server state
   - If not running, offer to start it first

2. **If set up, offer to search**
   - Ask what they want to search for if not clear
   - Suggest appropriate search mode:
     - Keyword (`/agent-brain-keyword`) for exact terms, function names, error codes
     - Semantic (`/agent-brain-semantic`) for concepts, explanations
     - Hybrid (`/agent-brain-search`) for comprehensive results

3. **If not set up, offer installation**
   - Explain what Agent Brain does
   - Offer to run `/agent-brain-setup` for complete guided setup

## Command Recommendations

| User Intent | Recommended Command |
|-------------|---------------------|
| Search for exact term | `/agent-brain-keyword "term"` |
| Search for concept | `/agent-brain-semantic "how does X work"` |
| General search | `/agent-brain-search "query"` |
| First time user | `/agent-brain-setup` |
| Server not running | `/agent-brain-start` |
```

### setup-assistant

**Purpose**: Help new users install and configure Agent Brain.

```yaml
---
name: setup-assistant
description: Helps new users install, configure, and set up Agent Brain for their projects
triggers:
  - pattern: "install.*agent.?brain"
    type: message_pattern
  - pattern: "set.?up.*agent.?brain"
    type: message_pattern
  - pattern: "configure.*agent.?brain"
    type: message_pattern
  - pattern: "how.*use.*agent.?brain"
    type: message_pattern
  - pattern: "agent brain not working"
    type: message_pattern
  - pattern: "agent brain error"
    type: message_pattern
  - pattern: "pip install agent-brain"
    type: keyword
skills:
  - agent-brain-setup
---

# Setup Assistant

Guide users through Agent Brain installation and configuration.

## Trigger Conditions

This agent activates when the user:
- Asks about installing Agent Brain
- Wants to set up or configure Agent Brain
- Encounters errors with Agent Brain
- Mentions pip install for agent-brain packages

## Behavior

When triggered:

1. **Assess current state**
   - Check if packages are installed: `pip show agent-brain-rag agent-brain-cli`
   - Check if project is initialized: look for `.claude/agent-brain/`
   - Check if server is running: `agent-brain status`

2. **Guide based on state**

   **If packages not installed:**
   - Offer to run `/agent-brain-install`
   - Explain this installs `agent-brain-rag` and `agent-brain-cli`

   **If packages installed but not configured:**
   - Offer to run `/agent-brain-config`
   - Guide setting `OPENAI_API_KEY` environment variable

   **If configured but project not initialized:**
   - Offer to run `/agent-brain-init`
   - Explain this creates `.claude/agent-brain/` configuration

   **If initialized but server not running:**
   - Offer to run `/agent-brain-start`
   - Explain server runs on auto-assigned port

   **If everything ready:**
   - Offer to index documents: `/agent-brain-index /path/to/docs`
   - Explain they can then search with `/agent-brain-search`

3. **Handle errors**
   - Check for common issues (missing API key, port conflict)
   - Reference troubleshooting guide in skill references
   - Offer `/agent-brain-verify` to diagnose issues

## Command Recommendations

| User State | Recommended Command |
|------------|---------------------|
| Fresh start | `/agent-brain-setup` (complete flow) |
| Need packages | `/agent-brain-install` |
| Need API keys | `/agent-brain-config` |
| Need project init | `/agent-brain-init` |
| Verify setup | `/agent-brain-verify` |
| Troubleshooting | `/agent-brain-status` + skill references |
```
