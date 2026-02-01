# Hybrid Search Guide

## Overview

Hybrid search combines the best of both vector semantic search and BM25 keyword search using Relative Score Fusion. It provides the most robust retrieval by leveraging both semantic understanding and exact term matching, then intelligently combining the results.

## When to Use Hybrid Search

**Choose hybrid search when:**
- You want the most comprehensive and accurate results
- The query combines both conceptual elements and specific technical terms
- You're unsure which search mode would work better
- You need high-quality results for critical applications
- The query involves both natural language and technical jargon

**Example hybrid queries:**
- `"how to implement OAuth2 authentication with JWT tokens"` - Combines concept + technical terms
- `"troubleshooting HTTP 500 errors in production"` - Error codes + troubleshooting concepts
- `"best practices for recursive text splitting algorithms"` - Methodology + specific algorithms
- `"configuring database connection pooling for high traffic"` - Configuration + technical terms

## How to Use Hybrid Search

### CLI Usage

```bash
# Basic hybrid search (default mode)
agent-brain query "implement authentication with error handling"

# With alpha weighting (70% vector, 30% BM25)
agent-brain query "oauth flow implementation" --alpha 0.7

# Show individual scores for debugging
agent-brain query "troubleshooting guide" --scores

# Custom settings for precision
agent-brain query "api documentation" --alpha 0.8 --threshold 0.6 --top-k 8
```

### API Usage

```bash
# POST /query endpoint (default hybrid)
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "authentication implementation guide",
    "alpha": 0.6,
    "threshold": 0.5
  }'

# Explicit hybrid mode
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "error handling patterns",
    "mode": "hybrid",
    "alpha": 0.7,
    "top_k": 10
  }'
```

## Hybrid Search Options

| Option | Default | Description | Use Case |
|--------|---------|-------------|----------|
| `--mode hybrid` | Default | Combines vector + BM25 | Best overall results |
| `--alpha F` | 0.5 | Weight balance (0.0=BM25, 1.0=vector) | Tune semantic vs keyword focus |
| `--threshold F` | 0.7 | Minimum combined score | Higher precision, fewer results |
| `--top-k N` | 5 | Maximum results | More comprehensive results |
| `--scores` | Optional | Show individual vector/BM25 scores | Debugging and transparency |

## Alpha Weighting System

The `alpha` parameter controls the balance between vector and BM25 search:

| Alpha Value | Vector Weight | BM25 Weight | Best For |
|-------------|---------------|-------------|----------|
| `1.0` | 100% | 0% | Pure semantic search |
| `0.8` | 80% | 20% | Conceptual guides |
| `0.5` | 50% | 50% | Balanced (recommended) |
| `0.3` | 30% | 70% | Technical documentation |
| `0.0` | 0% | 100% | Pure keyword search |

**Choosing Alpha Values:**
- **Technical documentation**: Try `alpha = 0.3-0.4` (favor BM25 for exact terms)
- **Conceptual guides**: Try `alpha = 0.7-0.8` (favor vector for meaning)
- **Mixed content**: Keep `alpha = 0.5` (balanced approach)
- **API references**: Try `alpha = 0.4` (technical terms + some context)
- **Tutorials**: Try `alpha = 0.6` (explanations + specific code)

## Fusion Algorithm Details

Hybrid search uses **Relative Score Fusion**:

1. **Execute Both Searches**: Run vector and BM25 searches in parallel
2. **Normalize Scores**: Convert both score ranges to 0.0-1.0 scale
3. **Weighted Combination**: `final_score = alpha * vector_score + (1-alpha) * bm25_score`
4. **Re-rank Results**: Sort by combined scores
5. **Deduplication**: Remove duplicate results from overlapping matches

## Example Results

### Example: Technical Implementation Query

**Query:** `agent-brain query "implement OAuth2 authentication with JWT tokens" --alpha 0.6 --scores`

**Response:**
```json
{
  "results": [
    {
      "text": "OAuth2 implementation guide: 1) Register application with OAuth provider, 2) Implement authorization code flow, 3) Handle token refresh, 4) Validate JWT tokens...",
      "source": "/docs/security/oauth-implementation.md",
      "score": 0.89,
      "vector_score": 0.85,
      "bm25_score": 0.93,
      "chunk_id": "chunk_123"
    }
  ],
  "query_time_ms": 1450.8,
  "total_results": 1
}
```

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Response Time | 1000-1800ms |
| CPU Usage | High (two algorithms + fusion) |
| Memory Usage | High (both indexes loaded) |
| API Costs | Requires OpenAI credits |
| Scalability | Good (parallel execution) |

## Best Practices

1. **Start with defaults**: Use `alpha = 0.5` and `threshold = 0.7` initially
2. **Tune alpha for content type**: Adjust based on whether your docs are more technical or conceptual
3. **Use scores for debugging**: `--scores` flag helps understand result quality
4. **Combine with domain knowledge**: Know whether your docs favor technical terms or explanations

## Comparison with Other Modes

| Aspect | BM25 | Vector | Hybrid |
|--------|------|--------|--------|
| **Accuracy** | High (exact) | High (semantic) | Highest (both) |
| **Speed** | Fastest | Slow | Slow-Medium |
| **API Required** | No | Yes | Yes |
| **Best For** | Technical terms | Concepts | General use |
| **Tuning** | Threshold only | Threshold only | Alpha + threshold |
| **Cost** | Free | API credits | API credits |
