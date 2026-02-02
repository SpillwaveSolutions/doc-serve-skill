---
name: agent-brain-summarizer
description: Configure the summarization provider for code summaries
parameters:
  - name: provider
    description: Summarization provider (anthropic, openai, gemini, grok, ollama)
    required: false
  - name: model
    description: Model name for the provider
    required: false
skills:
  - using-agent-brain
---

# Agent Brain Summarizer Configuration

## Purpose

Configures the summarization provider used during document indexing. Summarization generates concise descriptions of code and documents to improve search relevance.

## Usage

```
/agent-brain-summarizer [provider] [--model <model>]
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| provider | No | - | Provider: anthropic, openai, gemini, grok, ollama |
| --model | No | Provider default | Specific model to use |

## Available Providers

### Anthropic

High-quality code-aware summarization.

| Model | Speed | Use Case |
|-------|-------|----------|
| claude-3-5-haiku | Fast | Cost-effective, good quality |
| claude-sonnet-4 | Medium | Balanced quality/speed |
| claude-opus-4 | Slower | Highest quality |

**Configuration:**
```bash
export SUMMARIZATION_PROVIDER=anthropic
export SUMMARIZATION_MODEL=claude-3-5-haiku
export ANTHROPIC_API_KEY=sk-ant-...
```

### OpenAI

Versatile summarization with good code understanding.

| Model | Speed | Use Case |
|-------|-------|----------|
| gpt-4o-mini | Fast | Cost-effective |
| gpt-4o | Medium | High quality |
| gpt-4-turbo | Medium | Large contexts |

**Configuration:**
```bash
export SUMMARIZATION_PROVIDER=openai
export SUMMARIZATION_MODEL=gpt-4o-mini
export OPENAI_API_KEY=sk-proj-...
```

### Gemini

Google's models with large context windows.

| Model | Speed | Use Case |
|-------|-------|----------|
| gemini-1.5-flash | Fast | Cost-effective |
| gemini-1.5-pro | Medium | Higher quality |
| gemini-2.0-flash-exp | Fast | Experimental features |

**Configuration:**
```bash
export SUMMARIZATION_PROVIDER=gemini
export SUMMARIZATION_MODEL=gemini-1.5-flash
export GOOGLE_API_KEY=...
```

### Grok

xAI's conversational model.

| Model | Speed | Use Case |
|-------|-------|----------|
| grok-beta | Medium | General use |

**Configuration:**
```bash
export SUMMARIZATION_PROVIDER=grok
export SUMMARIZATION_MODEL=grok-beta
export XAI_API_KEY=...
```

### Ollama (Local)

Privacy-first local summarization.

| Model | Speed | Use Case |
|-------|-------|----------|
| llama3.2 | Varies | General purpose |
| mistral | Fast | Efficient |
| codellama | Medium | Code-focused |
| deepseek-coder | Medium | Code-optimized |

**Configuration:**
```bash
export SUMMARIZATION_PROVIDER=ollama
export SUMMARIZATION_MODEL=llama3.2
export OLLAMA_BASE_URL=http://localhost:11434
```

**Setup:**
```bash
# Pull the model first
ollama pull llama3.2
```

## Execution

### Interactive Configuration

If no provider is specified, use AskUserQuestion:

```
Which summarization provider would you like to use?

Options:
1. Anthropic (claude-3-5-haiku) - High quality, code-aware (Recommended)
2. OpenAI (gpt-4o-mini) - Fast, cost-effective
3. Gemini (gemini-1.5-flash) - Large context support
4. Grok (grok-beta) - xAI's model
5. Ollama (llama3.2) - Local, no API key required
```

### Direct Configuration

```bash
# Set to Anthropic
/agent-brain-summarizer anthropic --model claude-3-5-haiku

# Set to OpenAI
/agent-brain-summarizer openai --model gpt-4o-mini

# Set to Ollama
/agent-brain-summarizer ollama --model llama3.2
```

### Apply Configuration

Generate the export commands:

```bash
# Add to your shell profile or .env file:
export SUMMARIZATION_PROVIDER=anthropic
export SUMMARIZATION_MODEL=claude-3-5-haiku
```

Or update the project configuration:

```bash
agent-brain config set summarization_provider anthropic
agent-brain config set summarization_model claude-3-5-haiku
```

## Post-Configuration

After changing summarization providers, you may want to re-index to use the new summarizer:

```bash
# Re-index to apply new summarization
agent-brain reset --yes
agent-brain index /path/to/docs
```

**Note:** Changing summarization provider doesn't require re-indexing for existing searches to work, but new summaries won't be generated until re-indexing.

## Verification

```bash
# Verify summarization provider is working
agent-brain verify

# Test summarization
agent-brain test-summarize "def hello_world():\n    print('Hello, World!')"
```

## Output

### Configuration Applied

```
Summarization Provider Configuration
====================================
Provider: anthropic
Model: claude-3-5-haiku
API Key: ANTHROPIC_API_KEY (configured)

Configuration saved. Re-index recommended for new summaries.
```

### Provider Comparison

```
Summarization Provider Comparison
=================================
                  | Anthropic     | OpenAI        | Gemini        | Ollama
------------------|---------------|---------------|---------------|-------------
Quality           | Excellent     | Very Good     | Good          | Good
Code Awareness    | Excellent     | Very Good     | Good          | Varies
Speed             | Fast          | Fast          | Fast          | Varies
Cost (1M tokens)  | $0.25 input   | $0.15 input   | $0.075 input  | Free
Privacy           | Cloud         | Cloud         | Cloud         | Local
```

## Error Handling

### Invalid Provider

```
Error: Unknown provider 'xyz'.
Valid options: anthropic, openai, gemini, grok, ollama
```

### Model Not Available

```
Error: Model 'invalid-model' not available for provider 'anthropic'.
Available models: claude-3-5-haiku, claude-sonnet-4, claude-opus-4
```

### Ollama Not Running

```
Error: Cannot connect to Ollama at http://localhost:11434
Resolution: Start Ollama with 'ollama serve' or check OLLAMA_BASE_URL
```

### Missing API Key

```
Error: ANTHROPIC_API_KEY not set for Anthropic provider.
Resolution: export ANTHROPIC_API_KEY="sk-ant-..."
```

## Related Commands

- `/agent-brain-providers` - List all available providers
- `/agent-brain-embeddings` - Configure embedding provider
- `/agent-brain-verify` - Verify configuration
