"""
Pytest fixtures for E2E integration tests.

These fixtures manage the server lifecycle and provide helpers for CLI interaction.
"""

import pytest
import subprocess
import time
import json
import os
import signal
from pathlib import Path
from typing import Generator, Optional

# Load environment from server's .env file
try:
    from dotenv import load_dotenv
    E2E_DIR = Path(__file__).parent.parent
    PROJECT_ROOT = E2E_DIR.parent
    SERVER_ENV = PROJECT_ROOT / "doc-serve-server" / ".env"
    if SERVER_ENV.exists():
        load_dotenv(SERVER_ENV)
except ImportError:
    E2E_DIR = Path(__file__).parent.parent
    PROJECT_ROOT = E2E_DIR.parent

# Paths
if 'E2E_DIR' not in dir():
    E2E_DIR = Path(__file__).parent.parent
    PROJECT_ROOT = E2E_DIR.parent
SERVER_DIR = PROJECT_ROOT / "doc-serve-server"
CLI_DIR = PROJECT_ROOT / "doc-svr-ctl"
TEST_DOCS_DIR = E2E_DIR / "fixtures" / "test_docs" / "coffee_brewing"

# Timeouts
SERVER_STARTUP_TIMEOUT = 30
INDEXING_TIMEOUT = 120
HEALTH_POLL_INTERVAL = 2


class CLIRunner:
    """Helper class to run CLI commands."""

    def __init__(self, cli_dir: Path):
        self.cli_dir = cli_dir

    def run(self, *args, timeout: int = 30) -> dict:
        """Run CLI command and return parsed result."""
        cmd = ["poetry", "run", "doc-svr-ctl", *args]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.cli_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "json": self._parse_json(result.stdout) if "--json" in args else None
            }
        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out",
                "json": None
            }

    def _parse_json(self, stdout: str) -> Optional[dict]:
        """Parse JSON from stdout."""
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            return None

    def status(self) -> dict:
        """Get server status as JSON."""
        result = self.run("status", "--json")
        return result.get("json") or {}

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        threshold: float = 0.3
    ) -> dict:
        """Run a query and return results."""
        result = self.run(
            "query", query_text,
            "--json",
            "--top-k", str(top_k),
            "--threshold", str(threshold)
        )
        return result.get("json") or {}

    def index(self, folder_path: str) -> dict:
        """Start indexing a folder."""
        result = self.run("index", folder_path, "--json")
        return result.get("json") or {}

    def reset(self) -> dict:
        """Reset the index."""
        result = self.run("reset", "--yes", "--json")
        return result.get("json") or {}


@pytest.fixture(scope="session")
def check_api_key():
    """Check that OPENAI_API_KEY is set."""
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set - skipping E2E tests")


@pytest.fixture(scope="session")
def server_process(check_api_key) -> Generator[subprocess.Popen, None, None]:
    """Start the doc-serve server for the test session."""
    env = os.environ.copy()

    process = subprocess.Popen(
        ["poetry", "run", "doc-serve"],
        cwd=SERVER_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Wait for server to start
    cli = CLIRunner(CLI_DIR)
    start_time = time.time()

    while time.time() - start_time < SERVER_STARTUP_TIMEOUT:
        status = cli.status()
        health_status = status.get("health", {}).get("status")
        if health_status in ["healthy", "indexing"]:
            break
        time.sleep(1)
    else:
        # Server didn't start in time
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            process.wait(timeout=5)
        except Exception:
            pass
        pytest.fail("Server failed to start within timeout")

    yield process

    # Cleanup - stop server
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        process.wait()
    except ProcessLookupError:
        pass  # Already terminated


@pytest.fixture(scope="session")
def cli(server_process) -> CLIRunner:
    """Provide a CLI runner connected to the running server."""
    return CLIRunner(CLI_DIR)


@pytest.fixture(scope="session")
def indexed_docs(cli: CLIRunner) -> dict:
    """Index test documents and wait for completion.

    This fixture indexes the coffee brewing test documents and waits
    for indexing to complete before returning status information.
    """
    # Reset any existing index first
    cli.reset()
    time.sleep(1)

    # Start indexing
    result = cli.index(str(TEST_DOCS_DIR))
    if not result or "error" in str(result).lower():
        pytest.fail(f"Indexing command failed: {result}")

    # Wait for completion
    start_time = time.time()
    while time.time() - start_time < INDEXING_TIMEOUT:
        status = cli.status()
        indexing = status.get("indexing", {})

        in_progress = indexing.get("indexing_in_progress", True)
        total_docs = indexing.get("total_documents", 0)

        if not in_progress and total_docs > 0:
            return indexing

        time.sleep(HEALTH_POLL_INTERVAL)

    pytest.fail("Indexing did not complete within timeout")


@pytest.fixture(scope="function")
def clean_index(cli: CLIRunner) -> Generator[None, None, None]:
    """Reset index before and after test.

    Use this fixture for tests that need a clean slate.
    """
    cli.reset()
    time.sleep(1)
    yield
    cli.reset()


# Test document path fixture
@pytest.fixture(scope="session")
def test_docs_path() -> Path:
    """Return the path to test documents."""
    return TEST_DOCS_DIR
