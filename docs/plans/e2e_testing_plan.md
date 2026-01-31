# E2E Integration Testing Plan for Doc-Serve

## Summary

True end-to-end integration testing system that starts a real server, indexes real documents, and validates query results using the CLI - exactly as a user would interact with the system.

**Implemented:** December 2024

---

## Directory Structure

```
doc-serve/
└── e2e/
    ├── integration/
    │   ├── __init__.py
    │   ├── conftest.py              # Pytest fixtures (server lifecycle, CLI runner)
    │   ├── test_full_workflow.py    # Main E2E test scenarios
    │   └── test_error_handling.py   # Error case testing
    ├── fixtures/
    │   └── test_docs/
    │       └── coffee_brewing/      # Domain: Coffee brewing knowledge
    │           ├── espresso_basics.md
    │           ├── pour_over_guide.md
    │           ├── french_press_tips.md
    │           ├── water_temperature.md
    │           └── grind_sizes.md
    ├── scripts/
    │   ├── run_e2e.py               # Main orchestrator script
    │   ├── run_e2e.sh               # Shell wrapper for CI/CD
    │   └── wait_for_health.py       # Health polling utility
    └── config/
        └── e2e_config.py            # Configuration settings
```

---

## Test Domain: Coffee Brewing

The test documents cover coffee brewing methods with distinct, non-overlapping concepts that enable semantic search validation:

| File | Content |
|------|---------|
| `espresso_basics.md` | Pressure (9 bars), temperature, extraction time, common drinks |
| `pour_over_guide.md` | Equipment, bloom technique, spiral pour patterns |
| `french_press_tips.md` | Immersion method, coarse grind, 4-minute steep time |
| `water_temperature.md` | Ideal range (195-205°F), method-specific temperatures |
| `grind_sizes.md` | Grind by method (fine for espresso, coarse for French press) |

---

## Query Test Scenarios

| Query | Expected Terms | Purpose |
|-------|---------------|---------|
| "How do I make espresso?" | espresso, pressure | Basic retrieval |
| "What water temperature for coffee?" | temperature, fahrenheit | Cross-topic |
| "french press grind size" | coarse | Specific concept |
| "pour over technique bloom" | bloom | Technical term |
| "coffee brewing methods" | multiple sources | Cross-document |
| "9 bars pressure extraction" | pressure, espresso | Technical query |

---

## Running Tests

### Option 1: Python Script (Recommended)

```bash
cd e2e
python scripts/run_e2e.py --verbose
```

### Option 2: Pytest

```bash
cd e2e
python -m pytest integration/ -v
```

### Option 3: Shell Script (CI/CD)

```bash
cd e2e
./scripts/run_e2e.sh --verbose
```

---

## Environment Requirements

- `OPENAI_API_KEY` - Required for embeddings. Pytest tests auto-load from `agent-brain-server/.env`. Shell scripts require manual sourcing or export.
- Python 3.10+
- Poetry installed
- Server and CLI dependencies installed

## Similarity Threshold Configuration

The CLI's default similarity threshold is 0.7. However, semantic similarity between natural language queries and technical documents typically scores 0.4-0.6. E2E tests use `--threshold 0.3` to ensure results are returned.

If queries return empty results, verify the threshold is set appropriately in:
- `e2e/scripts/run_e2e.py:242` (run_query_test method)
- `e2e/integration/conftest.py:85` (CLIRunner.query method)
- `e2e/config/e2e_config.py:30` (DEFAULT_THRESHOLD constant)

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | Tests failed |
| 2 | Setup failed (server didn't start, missing API key) |
| 3 | Indexing failed |

---

## Test Workflow

1. **Start Server** - Launch doc-serve in background
2. **Wait for Health** - Poll `/health` until status is "healthy"
3. **Index Documents** - Use CLI to index coffee brewing docs
4. **Wait for Indexing** - Poll until `indexing_in_progress` is false
5. **Run Query Tests** - Execute semantic queries via CLI
6. **Validate Results** - Check for expected terms in results
7. **Cleanup** - Reset index and stop server

---

## CI/CD Integration

The shell script (`run_e2e.sh`) is designed for CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run E2E Tests
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    cd e2e
    ./scripts/run_e2e.sh
```

---

## Test Classes

### TestServerHealth
- Server reports healthy status
- Status includes version
- Status includes indexing info

### TestIndexing
- Documents are indexed (5+ docs)
- Chunks are created
- Indexed folders are tracked

### TestSemanticQueries
- Espresso query returns espresso content
- Temperature query returns temp info
- Grind size query returns grind info
- Cross-document queries work
- Results include scores, sources, text

### TestQueryParameters
- top_k limits results
- Query timing is reported
- Total results are reported

### TestErrorHandling
- Empty queries handled
- Unrelated queries return low scores
- Invalid parameters rejected
- Connection errors handled gracefully

### TestRobustness
- Multiple sequential queries succeed
- Repeated queries are consistent
