# Interactive Setup Guide

Guide for configuring Agent Brain through interactive prompts.

## Configuration Profile Selection

When setting up Agent Brain, choose a configuration profile based on requirements:

### Profile Options

| Profile | Use Case | API Keys Required |
|---------|----------|-------------------|
| Fully Local (Ollama) | Privacy, air-gapped environments | None |
| Cloud (OpenAI + Anthropic) | Best quality vectors and summaries | OpenAI, Anthropic |
| Mixed (OpenAI + Ollama) | Quality embeddings, local summaries | OpenAI only |
| Custom | Specific provider requirements | Varies |

### Profile 1: Fully Local (Ollama)

No API keys required. Requires Ollama installed locally.

```bash
export EMBEDDING_PROVIDER=ollama
export EMBEDDING_MODEL=nomic-embed-text
export SUMMARIZATION_PROVIDER=ollama
export SUMMARIZATION_MODEL=llama3.2
export OLLAMA_BASE_URL=http://localhost:11434
```

Prerequisites:
1. Install Ollama: https://ollama.ai
2. Pull models: `ollama pull nomic-embed-text && ollama pull llama3.2`
3. Start Ollama: `ollama serve`

### Profile 2: Cloud (Best Quality)

Requires OpenAI and Anthropic API keys.

```bash
export EMBEDDING_PROVIDER=openai
export EMBEDDING_MODEL=text-embedding-3-large
export SUMMARIZATION_PROVIDER=anthropic
export SUMMARIZATION_MODEL=claude-3-5-haiku
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Profile 3: Mixed

Requires OpenAI API key only.

```bash
export EMBEDDING_PROVIDER=openai
export EMBEDDING_MODEL=text-embedding-3-large
export SUMMARIZATION_PROVIDER=ollama
export SUMMARIZATION_MODEL=llama3.2
export OPENAI_API_KEY="sk-proj-..."
```

### Profile 4: Custom

Choose embedding and summarization providers independently.

**Embedding Provider Options**:
| Provider | Model | Characteristics |
|----------|-------|-----------------|
| OpenAI | text-embedding-3-large | High quality, cloud-based |
| Cohere | embed-english-v3.0 | Multi-language support |
| Ollama | nomic-embed-text | Local, no API key |

**Summarization Provider Options**:
| Provider | Model | Characteristics |
|----------|-------|-----------------|
| Anthropic | claude-3-5-haiku | High quality |
| OpenAI | gpt-4o-mini | Fast, cost-effective |
| Gemini | gemini-1.5-flash | Google's model |
| Grok | grok-beta | xAI's model |
| Ollama | llama3.2 | Local, no API key |

## API Key Configuration

### Required Keys by Provider

| Provider | Environment Variable | Get Key From |
|----------|---------------------|--------------|
| OpenAI | `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| Anthropic | `ANTHROPIC_API_KEY` | https://console.anthropic.com/ |
| Cohere | `COHERE_API_KEY` | https://dashboard.cohere.com/api-keys |
| Gemini | `GOOGLE_API_KEY` | https://aistudio.google.com/apikey |
| Grok | `XAI_API_KEY` | https://console.x.ai/ |

### Setting Environment Variables

**Temporary (current session)**:
```bash
export OPENAI_API_KEY="sk-proj-..."
```

**Persistent (shell profile)**:
```bash
echo 'export OPENAI_API_KEY="sk-proj-..."' >> ~/.bashrc
source ~/.bashrc
```

## Verification Steps

After configuration, verify setup:

```bash
# 1. Check provider configuration
echo "Embedding: ${EMBEDDING_PROVIDER:-openai}"
echo "Summarization: ${SUMMARIZATION_PROVIDER:-anthropic}"

# 2. Check API keys (if using cloud providers)
echo "OpenAI: ${OPENAI_API_KEY:+SET}"
echo "Anthropic: ${ANTHROPIC_API_KEY:+SET}"

# 3. Full verification
agent-brain verify
```
