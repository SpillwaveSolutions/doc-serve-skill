# Feature Specification: Agent Brain Plugin Conversion

**Feature Branch**: `114-agent-brain-plugin`
**Created**: 2025-01-31
**Status**: Draft
**Input**: User description: "Convert Agent Brain skill to plugin with commands for search, semantic-search, keyword-search. Include installation and setup assistance. Use skill-creating and skill-improving tools to achieve 95% quality score."

## Clarifications

### Session 2025-01-31

- Q: Command structure for plugin? → A: Use separate slash commands (`/agent-brain-search`, `/agent-brain-setup`, etc.) NOT a single command with subcommands. Follow the marketplace.json plugin format with commands/ and agents/ folders.
- Q: Plugin architecture model? → A: Full plugin with marketplace.json, commands/, agents/, and skills/ folders following the creating-plugin-from-skill pattern.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Quick Search with Plugin Commands (Priority: P1)

A Claude Code user wants to search their project documentation using natural commands. They invoke `/agent-brain-search "authentication flow"` and receive relevant document excerpts with source citations.

**Why this priority**: Core value proposition - users need intuitive search commands that work immediately without complex setup.

**Independent Test**: Can be fully tested by installing the plugin and running a search command against indexed documentation. Delivers immediate value by surfacing relevant information.

**Acceptance Scenarios**:

1. **Given** a project with indexed documentation, **When** user runs `/agent-brain-search "query"`, **Then** system returns relevant results with source file references (hybrid mode by default)
2. **Given** a project with indexed documentation, **When** user runs `/agent-brain-semantic "concept query"`, **Then** system returns conceptually related results using vector similarity
3. **Given** a project with indexed documentation, **When** user runs `/agent-brain-keyword "exact term"`, **Then** system returns exact keyword matches using BM25 algorithm
4. **Given** no server running, **When** user runs any search command, **Then** system provides clear guidance on starting the server first

---

### User Story 2 - Guided Installation and Setup (Priority: P2)

A new user wants to start using Agent Brain. They run `/agent-brain-install` and `/agent-brain-setup` to get packages installed, API keys configured, and their project initialized.

**Why this priority**: First-time experience is critical for adoption. Users who struggle with setup will abandon the tool.

**Independent Test**: Can be tested by a new user following the setup wizard from scratch. Delivers value by enabling all subsequent functionality.

**Acceptance Scenarios**:

1. **Given** a user has not installed Agent Brain, **When** they run `/agent-brain-install`, **Then** system checks prerequisites and runs pip install commands
2. **Given** missing API keys, **When** user runs `/agent-brain-config`, **Then** system explains which keys are needed and guides configuration
3. **Given** a fresh project, **When** user runs `/agent-brain-init`, **Then** system initializes project configuration in `.claude/agent-brain/`
4. **Given** installation completed, **When** user runs `/agent-brain-verify`, **Then** system runs health check and reports success or issues

---

### User Story 3 - Server Lifecycle Management (Priority: P2)

A user needs to manage the Agent Brain server for their project. They use commands to start, stop, check status, and list running instances across projects.

**Why this priority**: Server management is essential for daily use but secondary to the core search functionality.

**Independent Test**: Can be tested by starting, stopping, and checking server status. Delivers value through resource management and multi-project support.

**Acceptance Scenarios**:

1. **Given** no server running, **When** user runs `/agent-brain-start`, **Then** server starts on an available port and confirms startup
2. **Given** a running server, **When** user runs `/agent-brain-status`, **Then** system shows port, document count, indexing state, and health
3. **Given** a running server, **When** user runs `/agent-brain-stop`, **Then** server shuts down gracefully and confirms termination
4. **Given** multiple projects with servers, **When** user runs `/agent-brain-list`, **Then** system shows all running instances with their projects and ports

---

### User Story 4 - Document Indexing via Commands (Priority: P2)

A user wants to index their project documentation so it becomes searchable. They run `/agent-brain-index /docs` and the system processes and indexes all supported files.

**Why this priority**: Indexing is required before search but is a one-time or periodic operation.

**Independent Test**: Can be tested by indexing a documentation folder and verifying documents appear in status. Delivers value by making content searchable.

**Acceptance Scenarios**:

1. **Given** a path to documents, **When** user runs `/agent-brain-index /path`, **Then** system indexes all supported files and reports count
2. **Given** indexing in progress, **When** user runs `/agent-brain-status`, **Then** system shows indexing progress percentage
3. **Given** unsupported files in path, **When** indexing runs, **Then** system processes supported files and notes skipped files
4. **Given** previously indexed content, **When** user runs `/agent-brain-reset`, **Then** system clears the index after confirmation

---

### User Story 5 - Proactive Agent Assistance (Priority: P2)

A user mentions searching documentation or asks about their codebase. The Agent Brain agent proactively offers to help search or set up Agent Brain.

**Why this priority**: Agents provide discoverability and natural language interaction without requiring users to know specific commands.

**Independent Test**: Can be tested by mentioning search-related phrases and verifying the agent offers assistance.

**Acceptance Scenarios**:

1. **Given** user mentions "search docs" or "find in documentation", **When** agent detects this pattern, **Then** agent offers to search using Agent Brain
2. **Given** user asks "how do I search my codebase", **When** agent detects this pattern, **Then** agent explains Agent Brain and offers setup
3. **Given** Agent Brain not installed, **When** user asks about document search, **Then** agent offers to run installation commands

---

### User Story 6 - Interactive Help and Guidance (Priority: P3)

A user is unsure which command or search mode to use. They run `/agent-brain-help` or ask the agent for guidance, and receive contextual assistance.

**Why this priority**: Help improves discoverability but is not required for core functionality.

**Independent Test**: Can be tested by requesting help and verifying useful guidance is provided.

**Acceptance Scenarios**:

1. **Given** user runs `/agent-brain-help`, **Then** system lists all available commands with brief descriptions
2. **Given** user runs `/agent-brain-help --command search`, **Then** system explains search modes, parameters, and examples
3. **Given** user asks "when should I use keyword vs semantic search", **Then** agent provides mode selection guidance

---

### Edge Cases

- What happens when server is not running and user tries to search?
  - System displays clear error with instructions to run `/agent-brain-start`
- How does system handle network/API timeouts during search?
  - System reports timeout gracefully and suggests retry or alternative mode
- What happens when indexing very large document collections?
  - System provides progress updates and handles indexing asynchronously
- How does system handle missing or invalid API keys?
  - Setup commands detect missing keys and provide configuration guidance
- What happens when port conflicts occur during server start?
  - System automatically selects next available port and reports the assignment

## Requirements *(mandatory)*

### Functional Requirements

**Plugin Structure (using marketplace.json format):**
- **FR-001**: Plugin MUST be installable from GitHub repository using standard Claude Code plugin installation
- **FR-002**: Plugin MUST use marketplace.json format with commands/, agents/, and skills/ folders
- **FR-003**: Plugin MUST include multiple separate slash commands (not subcommands)
- **FR-004**: Plugin MUST include agent(s) that trigger on patterns for proactive assistance

**Search Commands (separate slash commands):**
- **FR-005**: Plugin MUST provide `/agent-brain-search` command for default hybrid search
- **FR-006**: Plugin MUST provide `/agent-brain-semantic` command for vector-based conceptual search
- **FR-007**: Plugin MUST provide `/agent-brain-keyword` command for BM25 exact term matching
- **FR-008**: All search commands MUST return results with source file references and relevance scores
- **FR-009**: Search commands MUST accept `--top-k`, `--threshold`, and `--alpha` parameters

**Setup and Installation Commands:**
- **FR-010**: Plugin MUST provide `/agent-brain-install` command that runs pip install commands
- **FR-011**: Plugin MUST provide `/agent-brain-setup` command for complete guided setup flow
- **FR-012**: Plugin MUST provide `/agent-brain-config` command for API key configuration
- **FR-013**: Plugin MUST provide `/agent-brain-init` command for project initialization
- **FR-014**: Plugin MUST provide `/agent-brain-verify` command for installation verification

**Server Management Commands:**
- **FR-015**: Plugin MUST provide `/agent-brain-start` command with auto-port selection
- **FR-016**: Plugin MUST provide `/agent-brain-stop` command for graceful shutdown
- **FR-017**: Plugin MUST provide `/agent-brain-status` command showing server health and statistics
- **FR-018**: Plugin MUST provide `/agent-brain-list` command showing all running instances

**Indexing Commands:**
- **FR-019**: Plugin MUST provide `/agent-brain-index` command for document ingestion
- **FR-020**: Plugin MUST provide `/agent-brain-reset` command to clear indexed content

**Help Command:**
- **FR-021**: Plugin MUST provide `/agent-brain-help` command listing all available commands
- **FR-022**: Help command MUST support `--command <name>` for contextual help

**Agent Components:**
- **FR-023**: Plugin MUST include a search-assistant agent that triggers on search-related patterns
- **FR-024**: Plugin MUST include a setup-assistant agent that triggers on setup/installation patterns
- **FR-025**: Agents MUST provide natural language interaction and command recommendations

**Skills:**
- **FR-026**: Plugin MUST include using-agent-brain skill with search mode documentation
- **FR-027**: Plugin MUST include agent-brain-setup skill with installation/configuration guides
- **FR-028**: Skills MUST include references/ folder with detailed documentation

**Quality Assurance:**
- **FR-029**: Plugin and skills MUST achieve 95% quality score from skill grading tools
- **FR-030**: Plugin MUST be created using the creating-plugin-from-skill workflow
- **FR-031**: Skills MUST be validated using skill-creator best practices
- **FR-032**: Skills MUST be improved using improving-skills workflow until 95% score achieved

### Key Entities

- **Plugin**: GitHub-hosted repository with marketplace.json, commands/, agents/, skills/ structure
- **Command**: Individual slash command file in commands/ folder (e.g., `agent-brain-search.md`)
- **Agent**: Pattern-triggered assistant file in agents/ folder (e.g., `search-assistant.md`)
- **Skill**: SKILL.md with references/ providing domain knowledge
- **Server Instance**: A running Agent Brain server bound to a specific project and port
- **Index**: The searchable collection of processed documents for a project

## Plugin Structure

The plugin follows the full marketplace.json format:

```
agent-brain-plugin/
├── .claude-plugin/
│   └── marketplace.json       # Full manifest with commands, agents, skills
├── commands/
│   ├── agent-brain-search.md      # /agent-brain-search
│   ├── agent-brain-semantic.md    # /agent-brain-semantic
│   ├── agent-brain-keyword.md     # /agent-brain-keyword
│   ├── agent-brain-install.md     # /agent-brain-install
│   ├── agent-brain-setup.md       # /agent-brain-setup
│   ├── agent-brain-config.md      # /agent-brain-config
│   ├── agent-brain-init.md        # /agent-brain-init
│   ├── agent-brain-verify.md      # /agent-brain-verify
│   ├── agent-brain-start.md       # /agent-brain-start
│   ├── agent-brain-stop.md        # /agent-brain-stop
│   ├── agent-brain-status.md      # /agent-brain-status
│   ├── agent-brain-list.md        # /agent-brain-list
│   ├── agent-brain-index.md       # /agent-brain-index
│   ├── agent-brain-reset.md       # /agent-brain-reset
│   └── agent-brain-help.md        # /agent-brain-help
├── agents/
│   ├── search-assistant.md        # Triggers on search patterns
│   └── setup-assistant.md         # Triggers on setup/install patterns
├── skills/
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

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete initial setup and run their first search in under 5 minutes
- **SC-002**: Search commands return relevant results within 3 seconds for typical queries
- **SC-003**: Plugin achieves 95% quality score from skill grading evaluation
- **SC-004**: All 15 plugin commands are discoverable via `/agent-brain-help`
- **SC-005**: New users can successfully set up Agent Brain without external documentation
- **SC-006**: 90% of search queries return at least one relevant result when documents are indexed
- **SC-007**: Server start/stop operations complete within 10 seconds
- **SC-008**: Plugin installation completes successfully on standard Claude Code environments
- **SC-009**: Both skills achieve 95% quality score individually
- **SC-010**: Agents trigger appropriately on pattern matches at least 80% of the time

## Scope

### In Scope

- Converting existing skill to GitHub-hosted plugin format with marketplace.json
- Creating 15 separate slash commands in commands/ folder
- Creating 2 agents (search-assistant, setup-assistant) in agents/ folder
- Creating 2 skills (using-agent-brain, agent-brain-setup) in skills/ folder
- Using creating-plugin-from-skill workflow for plugin creation
- Using skill-creator for skill creation
- Using improving-skills workflow to achieve 95% quality score
- Comprehensive help system for all commands

### Out of Scope

- Changes to the underlying Agent Brain server or CLI functionality
- New search algorithms or retrieval modes beyond existing BM25/vector/hybrid
- Cloud hosting or remote server management
- Multi-user authentication or access control
- Integration with external documentation platforms

## Dependencies

- Existing `agent-brain-cli` package (v1.2.0+) for CLI operations
- Existing `agent-brain-rag` package (v1.2.0+) for server functionality
- OpenAI API key for vector/hybrid search modes
- Claude Code plugin system with marketplace.json support
- `creating-plugin-from-skill` skill for plugin creation workflow
- `skill-creator` skill for skill creation
- `improving-skills` skill for quality improvement

## Assumptions

- Users have Python 3.10+ installed on their system
- Users have access to install pip packages
- Users can obtain OpenAI API keys for full functionality
- Claude Code supports marketplace.json plugin format with commands, agents, and skills
- The creating-plugin-from-skill workflow produces valid plugin structure
- The skill-creator and improving-skills tools are available and functional
- Standard plugin installation process works via GitHub repository URL
