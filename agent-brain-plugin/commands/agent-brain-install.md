---
name: agent-brain-install
description: Install Agent Brain packages using pipx, uv, pip, or conda
parameters: []
skills:
  - configuring-agent-brain
---

# Install Agent Brain Packages

## STOP - READ THIS FIRST

**DO NOT RUN ANY INSTALLATION COMMANDS YET.**

You MUST ask the user which installation method they prefer using the AskUserQuestion tool BEFORE doing anything else.

## Step 1: Ask User for Installation Method

**THIS IS MANDATORY. DO NOT SKIP THIS STEP.**

Use the AskUserQuestion tool with this exact structure:

```json
{
  "questions": [{
    "question": "Which installation method do you prefer for Agent Brain?",
    "header": "Install via",
    "options": [
      {
        "label": "pipx (Recommended)",
        "description": "Install globally in an isolated environment. No activation needed."
      },
      {
        "label": "uv",
        "description": "Fast, modern Python tool installer. Good for power users."
      },
      {
        "label": "pip (venv)",
        "description": "Install into a local virtual environment. Requires activation."
      },
      {
        "label": "conda",
        "description": "For conda users. Creates a conda environment with pip inside."
      }
    ],
    "multiSelect": false
  }]
}
```

**STOP HERE AND WAIT FOR THE USER'S RESPONSE.**

Do not proceed until you have called AskUserQuestion and received the user's selection.

---

## Step 2: Check Python Version

Only after receiving the user's installation method choice:

```bash
python --version
```

Requires Python 3.10+. If lower, tell user to upgrade first.

---

## Step 3: Execute Based on User's Selection

### If user selected "pipx (Recommended)"

1. Check/install pipx:
   ```bash
   pipx --version 2>/dev/null || python -m pip install --user pipx && python -m pipx ensurepath
   ```

2. Install Agent Brain:
   ```bash
   pipx install agent-brain-cli
   ```

3. Verify (user may need to restart terminal):
   ```bash
   agent-brain --version
   ```

### If user selected "uv"

1. Check/install uv:
   ```bash
   uv --version 2>/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install Agent Brain:
   ```bash
   uv tool install agent-brain-cli
   ```

3. Verify:
   ```bash
   agent-brain --version
   ```

### If user selected "pip (venv)"

1. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   ```

2. Install packages:
   ```bash
   pip install agent-brain-rag agent-brain-cli
   ```

3. Verify:
   ```bash
   agent-brain --version
   ```

4. **Tell user:** Must run `source .venv/bin/activate` before using agent-brain.

### If user selected "conda"

1. Create conda environment:
   ```bash
   conda create -n agent-brain python=3.12 -y
   conda activate agent-brain
   ```

2. Install packages:
   ```bash
   pip install agent-brain-rag agent-brain-cli
   ```

3. Verify:
   ```bash
   agent-brain --version
   ```

4. **Tell user:** Must run `conda activate agent-brain` before using agent-brain.

---

## Success Output

After successful installation, show:

```
Agent Brain Installation Complete
=================================

Install Method: [method user selected]
Version: [version from agent-brain --version]

Next steps:
  1. Configure: /agent-brain-config
  2. Initialize: /agent-brain-init
  3. Start server: /agent-brain-start
```

---

## Why Ask First?

Different methods have different trade-offs:

| Method | Global? | Isolated? | Needs Activation? |
|--------|---------|-----------|-------------------|
| pipx | Yes | Yes | No |
| uv | Yes | Yes | No |
| pip (venv) | No | Yes | Yes |
| conda | No | Yes | Yes |

- **pipx/uv**: Best for CLI tools - globally available, no activation
- **pip (venv)**: Best for project-specific installs
- **conda**: Best for data science users already using conda
