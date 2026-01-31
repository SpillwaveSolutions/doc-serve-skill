"""
Configuration settings for E2E tests.
"""

from pathlib import Path
import os

# Paths
E2E_DIR = Path(__file__).parent.parent
PROJECT_ROOT = E2E_DIR.parent
SERVER_DIR = PROJECT_ROOT / "agent-brain-server"
CLI_DIR = PROJECT_ROOT / "agent-brain-cli"
TEST_DOCS_DIR = E2E_DIR / "fixtures" / "test_docs" / "coffee_brewing"

# Server settings
SERVER_HOST = os.environ.get("E2E_SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.environ.get("E2E_SERVER_PORT", "8000"))
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# Timeouts (seconds)
SERVER_STARTUP_TIMEOUT = 30
INDEXING_TIMEOUT = 120
QUERY_TIMEOUT = 30
HEALTH_POLL_INTERVAL = 2

# Test parameters
DEFAULT_TOP_K = 5
# Lower threshold for E2E tests - semantic similarity between natural language
# queries and technical documents typically scores 0.4-0.6
DEFAULT_THRESHOLD = 0.3

# Exit codes
EXIT_SUCCESS = 0
EXIT_TEST_FAILURE = 1
EXIT_SETUP_FAILURE = 2
EXIT_INDEXING_FAILURE = 3
