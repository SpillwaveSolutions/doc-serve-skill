# Quickstart: Agent Brain Plugin

**Feature**: 114-agent-brain-plugin
**Date**: 2025-01-31

## Overview

This feature converts the existing Agent Brain skill into a full Claude Code plugin with commands, agents, and skills for document search and setup assistance.

## Prerequisites

Before working on this feature:

1. **Understand the plugin structure**:
   - Read `data-model.md` for entity definitions
   - Read `contracts/command-schema.md` for command format
   - Read `contracts/agent-schema.md` for agent format
   - Read `contracts/skill-schema.md` for skill format

2. **Understand the source material**:
   - Existing skill: `agent-brain-skill/using-agent-brain/`
   - CLI commands: `agent-brain-cli/`
   - Plugin template: `~/.claude/skills/creating-plugin-from-skill/`

3. **Required skills to reference**:
   - `creating-plugin-from-skill` - Plugin creation workflow
   - `skill-creator` - Skill best practices
   - `improving-skills` - Quality grading rubric

## Quick Reference

### Plugin Structure

```
agent-brain-plugin/
├── .claude-plugin/
│   └── marketplace.json      # Plugin manifest
├── commands/                  # 15 slash commands
│   ├── agent-brain-search.md
│   ├── agent-brain-semantic.md
│   ├── agent-brain-keyword.md
│   ├── agent-brain-install.md
│   ├── agent-brain-setup.md
│   ├── agent-brain-config.md
│   ├── agent-brain-init.md
│   ├── agent-brain-verify.md
│   ├── agent-brain-start.md
│   ├── agent-brain-stop.md
│   ├── agent-brain-status.md
│   ├── agent-brain-list.md
│   ├── agent-brain-index.md
│   ├── agent-brain-reset.md
│   └── agent-brain-help.md
├── agents/                    # 2 proactive agents
│   ├── search-assistant.md
│   └── setup-assistant.md
├── skills/                    # 2 skills with references
│   ├── using-agent-brain/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── hybrid-search-guide.md
│   │       ├── bm25-search-guide.md
│   │       ├── vector-search-guide.md
│   │       └── api_reference.md
│   └── agent-brain-setup/
│       ├── SKILL.md
│       └── references/
│           ├── installation-guide.md
│           ├── configuration-guide.md
│           └── troubleshooting-guide.md
├── README.md
└── .gitignore
```

### Command Categories

| Category | Commands | Purpose |
|----------|----------|---------|
| Search | `/agent-brain-search`, `/agent-brain-semantic`, `/agent-brain-keyword` | Document search |
| Setup | `/agent-brain-install`, `/agent-brain-setup`, `/agent-brain-config`, `/agent-brain-init`, `/agent-brain-verify` | Installation & config |
| Server | `/agent-brain-start`, `/agent-brain-stop`, `/agent-brain-status`, `/agent-brain-list` | Server management |
| Indexing | `/agent-brain-index`, `/agent-brain-reset` | Document indexing |
| Help | `/agent-brain-help` | Usage help |

### CLI Command Mapping

| Plugin Command | CLI Command |
|----------------|-------------|
| `/agent-brain-search "query"` | `agent-brain query "query" --mode hybrid` |
| `/agent-brain-semantic "query"` | `agent-brain query "query" --mode vector` |
| `/agent-brain-keyword "query"` | `agent-brain query "query" --mode bm25` |
| `/agent-brain-start` | `agent-brain start --daemon` |
| `/agent-brain-status` | `agent-brain status` |
| `/agent-brain-index /path` | `agent-brain index /path` |

## Development Workflow

### Phase 1: Foundation

1. Create output directory: `agent-brain-plugin/`
2. Create marketplace.json with all references
3. Create README.md and .gitignore

### Phase 2: Commands

1. Create each command file in `commands/`
2. Use contract schemas from `contracts/command-schema.md`
3. Include CLI mapping, output formatting, error handling

### Phase 3: Agents

1. Create agent files in `agents/`
2. Use contract schemas from `contracts/agent-schema.md`
3. Test trigger patterns match intended use cases

### Phase 4: Skills

1. Create skill directories in `skills/`
2. Migrate content from existing `agent-brain-skill/`
3. Create reference files with detailed documentation

### Phase 5: Quality

1. Grade skills using `improving-skills` rubric
2. Target 95% score for both skills
3. Iterate until quality threshold met

### Phase 6: Publish

1. Create GitHub repository
2. Push plugin to `SpillwaveSolutions/agent-brain-plugin`
3. Document installation instructions

## Quality Checklist

Before completing each phase:

- [ ] Files follow contract schemas exactly
- [ ] YAML frontmatter validates correctly
- [ ] Markdown body includes all required sections
- [ ] Links between files are correct
- [ ] No duplicate or conflicting definitions

## Common Issues

### Command Parameters

- Use lowercase, hyphenated parameter names
- Mark required parameters explicitly
- Provide sensible defaults for optional parameters

### Agent Triggers

- Test regex patterns for false positives
- Ensure patterns cover common phrasings
- Avoid overly broad patterns that trigger too often

### Skill References

- Keep SKILL.md under 500 lines
- Put details in references/ folder
- Use descriptive file names for references

## Testing

After implementation:

1. Install plugin: `cd ~/.claude/plugins && git clone <url>`
2. Restart Claude Code
3. Test each command works correctly
4. Verify agents trigger on appropriate messages
5. Confirm skills load when referenced

## Resources

- [Creating Plugin from Skill](~/.claude/skills/creating-plugin-from-skill/SKILL.md)
- [Skill Creator](~/.claude/skills/skill-creator/SKILL.md)
- [Improving Skills](~/.claude/skills/improving-skills/SKILL.md)
- [Agent Brain CLI](../../agent-brain-cli/)
- [Existing Skill](../../agent-brain-skill/)
