# Provider Configuration Guide

Agent Brain 2.0 supports pluggable providers for embeddings and summarization. This guide covers all configuration options.

## Provider Overview

### Embedding Providers

Embeddings convert text into vector representations for semantic search.

| Provider | Models | API Key | Characteristics |
|----------|--------|---------|-----------------|
| OpenAI | text-embedding-3-large, text-embedding-3-small, text-embedding-ada-002 | OPENAI_API_KEY | High quality, 3072 dimensions (large), industry standard |
| Cohere | embed-english-v3.0, embed-multilingual-v3.0, embed-english-light-v3.0 | COHERE_API_KEY | Multi-language, 1024 dimensions, good for international content |
| Ollama | nomic-embed-text, mxbai-embed-large, all-minilm | None (local) | Privacy-first, no API costs, runs on your machine |

### Summarization Providers

Summarization generates concise descriptions of code and documents during indexing.

| Provider | Models | API Key | Characteristics |
|----------|--------|---------|-----------------|
| Anthropic | claude-3-5-haiku, claude-sonnet-4, claude-opus-4 | ANTHROPIC_API_KEY | High quality, code-aware, fast |
| OpenAI | gpt-4o, gpt-4o-mini, gpt-4-turbo | OPENAI_API_KEY | Versatile, good code understanding |
| Gemini | gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash-exp | GOOGLE_API_KEY | Fast, good for large contexts |
| Grok | grok-beta | XAI_API_KEY | xAI's model, conversational style |
| Ollama | llama3.2, mistral, codellama, deepseek-coder | None (local) | Privacy-first, no API costs |

## Configuration Methods

### Method 1: Environment Variables

Set variables in your shell or `.env` file:

```bash
# Embedding configuration
export EMBEDDING_PROVIDER=openai
export EMBEDDING_MODEL=text-embedding-3-large

# Summarization configuration
export SUMMARIZATION_PROVIDER=anthropic
export SUMMARIZATION_MODEL=claude-3-5-haiku

# API keys (as needed)
export OPENAI_API_KEY=sk-proj-...
export ANTHROPIC_API_KEY=sk-ant-...
```

### Method 2: .env File

Create `.claude/agent-brain/.env` in your project:

```bash
# Provider settings
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-large
SUMMARIZATION_PROVIDER=anthropic
SUMMARIZATION_MODEL=claude-3-5-haiku

# API keys
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Method 3: CLI Configuration

```bash
# Configure embedding provider
agent-brain config set embedding_provider openai
agent-brain config set embedding_model text-embedding-3-large

# Configure summarization provider
agent-brain config set summarization_provider anthropic
agent-brain config set summarization_model claude-3-5-haiku
```

## Configuration Profiles

### Fully Local (No API Keys)

Best for: Privacy, air-gapped environments, no API costs

```bash
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text
SUMMARIZATION_PROVIDER=ollama
SUMMARIZATION_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434
```

**Requirements:**
1. Install Ollama: https://ollama.ai
2. Pull required models:
   ```bash
   ollama pull nomic-embed-text
   ollama pull llama3.2
   ```

### Cloud (Best Quality)

Best for: Production use, highest quality results

```bash
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-large
SUMMARIZATION_PROVIDER=anthropic
SUMMARIZATION_MODEL=claude-3-5-haiku
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Mixed (Quality + Privacy)

Best for: Quality embeddings with local summarization

```bash
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-large
SUMMARIZATION_PROVIDER=ollama
SUMMARIZATION_MODEL=llama3.2
OPENAI_API_KEY=sk-proj-...
OLLAMA_BASE_URL=http://localhost:11434
```

### Budget-Conscious

Best for: Lower API costs while maintaining quality

```bash
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
SUMMARIZATION_PROVIDER=openai
SUMMARIZATION_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-proj-...
```

### Multi-Language

Best for: International content, multiple languages

```bash
EMBEDDING_PROVIDER=cohere
EMBEDDING_MODEL=embed-multilingual-v3.0
SUMMARIZATION_PROVIDER=anthropic
SUMMARIZATION_MODEL=claude-3-5-haiku
COHERE_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...
```

## Provider-Specific Configuration

### OpenAI Configuration

```bash
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-large  # or text-embedding-3-small
OPENAI_API_KEY=sk-proj-...
OPENAI_ORG_ID=org-...                   # Optional: organization ID
OPENAI_BASE_URL=https://api.openai.com  # Optional: custom endpoint
```

**Available Models:**
- `text-embedding-3-large`: 3072 dimensions, highest quality
- `text-embedding-3-small`: 1536 dimensions, faster, cheaper
- `text-embedding-ada-002`: 1536 dimensions, legacy

### Cohere Configuration

```bash
EMBEDDING_PROVIDER=cohere
EMBEDDING_MODEL=embed-english-v3.0
COHERE_API_KEY=...
```

**Available Models:**
- `embed-english-v3.0`: English-optimized, 1024 dimensions
- `embed-multilingual-v3.0`: 100+ languages, 1024 dimensions
- `embed-english-light-v3.0`: Faster, smaller model

### Ollama Configuration

```bash
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text
SUMMARIZATION_PROVIDER=ollama
SUMMARIZATION_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434  # Default Ollama URL
```

**Setup:**
```bash
# Install Ollama (macOS)
brew install ollama

# Install Ollama (Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull embedding model
ollama pull nomic-embed-text

# Pull summarization model
ollama pull llama3.2
```

**Available Embedding Models:**
- `nomic-embed-text`: General purpose, 768 dimensions
- `mxbai-embed-large`: High quality, 1024 dimensions
- `all-minilm`: Lightweight, fast

**Available Summarization Models:**
- `llama3.2`: General purpose, good balance
- `mistral`: Fast, efficient
- `codellama`: Code-optimized
- `deepseek-coder`: Code-focused

### Anthropic Configuration

```bash
SUMMARIZATION_PROVIDER=anthropic
SUMMARIZATION_MODEL=claude-3-5-haiku
ANTHROPIC_API_KEY=sk-ant-...
```

**Available Models:**
- `claude-3-5-haiku`: Fast, cost-effective
- `claude-sonnet-4`: Balanced quality/speed
- `claude-opus-4`: Highest quality

### Gemini Configuration

```bash
SUMMARIZATION_PROVIDER=gemini
SUMMARIZATION_MODEL=gemini-1.5-flash
GOOGLE_API_KEY=...
```

**Available Models:**
- `gemini-1.5-flash`: Fast, efficient
- `gemini-1.5-pro`: Higher quality
- `gemini-2.0-flash-exp`: Experimental features

### Grok Configuration

```bash
SUMMARIZATION_PROVIDER=grok
SUMMARIZATION_MODEL=grok-beta
XAI_API_KEY=...
```

## Verifying Configuration

```bash
# Show current configuration
agent-brain config show

# Verify providers are working
agent-brain verify

# Test embedding provider
agent-brain test-embedding "sample text"

# Test summarization provider
agent-brain test-summarize "sample code content"
```

## Switching Providers

When switching providers, you may need to re-index documents if the embedding dimensions differ:

```bash
# Check current embedding dimensions
agent-brain status

# If switching embedding providers with different dimensions:
agent-brain reset --yes
agent-brain index /path/to/docs
```

## Troubleshooting

### API Key Issues

```
Error: Invalid API key
```

**Resolution:** Verify your API key is correct and has the necessary permissions.

### Ollama Connection Failed

```
Error: Could not connect to Ollama at http://localhost:11434
```

**Resolution:**
```bash
# Check if Ollama is running
ollama list

# Start Ollama
ollama serve
```

### Model Not Found

```
Error: Model 'model-name' not found
```

**Resolution:**
```bash
# For Ollama, pull the model
ollama pull model-name

# For cloud providers, verify model name spelling
```

### Rate Limiting

```
Error: Rate limit exceeded
```

**Resolution:**
- Wait and retry
- Use a different provider temporarily
- Upgrade your API plan

## Cost Considerations

### Embedding Costs (per 1M tokens)

| Provider | Model | Approximate Cost |
|----------|-------|------------------|
| OpenAI | text-embedding-3-large | $0.13 |
| OpenAI | text-embedding-3-small | $0.02 |
| Cohere | embed-english-v3.0 | $0.10 |
| Ollama | Any | Free (local compute) |

### Summarization Costs (per 1M tokens)

| Provider | Model | Input | Output |
|----------|-------|-------|--------|
| Anthropic | claude-3-5-haiku | $0.25 | $1.25 |
| OpenAI | gpt-4o-mini | $0.15 | $0.60 |
| Gemini | gemini-1.5-flash | $0.075 | $0.30 |
| Ollama | Any | Free (local compute) |

*Prices as of 2024, subject to change.*
