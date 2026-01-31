#!/usr/bin/env python3
"""
Main E2E test runner script.

This script orchestrates the full E2E testing workflow:
1. Start the doc-serve server
2. Wait for server to be healthy
3. Index test documents using the CLI
4. Wait for indexing to complete
5. Run query tests using the CLI
6. Validate results
7. Clean up (reset index, stop server)

Usage:
    python run_e2e.py [--keep-server] [--verbose]

Exit codes:
    0: All tests passed
    1: Tests failed
    2: Setup failed (server didn't start)
    3: Indexing failed
"""

import argparse
import subprocess
import sys
import time
import json
import os
import signal
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.e2e_config import (
    SERVER_DIR, CLI_DIR, TEST_DOCS_DIR,
    SERVER_STARTUP_TIMEOUT, INDEXING_TIMEOUT, HEALTH_POLL_INTERVAL,
    EXIT_SUCCESS, EXIT_TEST_FAILURE, EXIT_SETUP_FAILURE, EXIT_INDEXING_FAILURE
)


@dataclass
class TestCase:
    """A single query test case."""
    query: str
    expected_terms: List[str]
    min_results: int
    description: str


class E2ETestRunner:
    """Orchestrates E2E test execution."""

    # Test cases for semantic queries
    TEST_CASES = [
        TestCase(
            query="How do I make espresso?",
            expected_terms=["espresso", "pressure"],
            min_results=1,
            description="Espresso basics query"
        ),
        TestCase(
            query="What water temperature for coffee?",
            expected_terms=["temperature", "fahrenheit"],
            min_results=1,
            description="Water temperature query"
        ),
        TestCase(
            query="french press grind size",
            expected_terms=["coarse"],
            min_results=1,
            description="French press grind query"
        ),
        TestCase(
            query="pour over technique bloom",
            expected_terms=["bloom"],
            min_results=1,
            description="Pour over bloom technique"
        ),
        TestCase(
            query="coffee brewing methods comparison",
            expected_terms=["espresso"],
            min_results=1,
            description="Cross-document query"
        ),
        TestCase(
            query="9 bars pressure extraction",
            expected_terms=["espresso", "pressure"],
            min_results=1,
            description="Technical espresso query"
        ),
    ]

    def __init__(self, verbose: bool = False, keep_server: bool = False):
        self.verbose = verbose
        self.keep_server = keep_server
        self.server_process: Optional[subprocess.Popen] = None
        self.passed = 0
        self.failed = 0

    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        if level == "DEBUG" and not self.verbose:
            return
        prefix = {
            "INFO": "\033[34m[*]\033[0m",
            "ERROR": "\033[31m[!]\033[0m",
            "DEBUG": "\033[90m[.]\033[0m",
            "OK": "\033[32m[+]\033[0m",
            "FAIL": "\033[31m[-]\033[0m"
        }
        print(f"{prefix.get(level, '[?]')} {message}")

    def run_cli(self, *args, timeout: int = 30) -> Tuple[int, str, str]:
        """Run a CLI command and return (exit_code, stdout, stderr)."""
        cmd = ["poetry", "run", "agent-brain", *args]
        self.log(f"Running: {' '.join(cmd)}", "DEBUG")

        try:
            result = subprocess.run(
                cmd,
                cwd=CLI_DIR,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"

    def start_server(self) -> bool:
        """Start the doc-serve server."""
        self.log("Starting doc-serve server...")

        # Note: Server loads OPENAI_API_KEY from its own .env file
        if not os.environ.get("OPENAI_API_KEY"):
            self.log("OPENAI_API_KEY not in env (server will use .env file)", "DEBUG")

        env = os.environ.copy()

        try:
            self.server_process = subprocess.Popen(
                ["poetry", "run", "doc-serve"],
                cwd=SERVER_DIR,
                env=env,
                stdout=subprocess.PIPE if not self.verbose else None,
                stderr=subprocess.PIPE if not self.verbose else None,
                preexec_fn=os.setsid  # Create new process group for clean shutdown
            )
        except Exception as e:
            self.log(f"Failed to start server: {e}", "ERROR")
            return False

        # Wait for server to be healthy
        return self.wait_for_health(timeout=SERVER_STARTUP_TIMEOUT)

    def wait_for_health(self, timeout: int = 30) -> bool:
        """Wait for server to become healthy."""
        self.log("Waiting for server health...")
        start = time.time()

        while time.time() - start < timeout:
            code, stdout, _ = self.run_cli("status", "--json")
            if code == 0:
                try:
                    data = json.loads(stdout)
                    status = data.get("health", {}).get("status")
                    if status in ["healthy", "indexing"]:
                        self.log(f"Server status: {status}", "OK")
                        return True
                except json.JSONDecodeError:
                    pass
            time.sleep(1)

        self.log("Server failed to become healthy", "ERROR")
        return False

    def index_documents(self) -> bool:
        """Index the test documents."""
        self.log(f"Indexing documents from {TEST_DOCS_DIR}...")

        if not TEST_DOCS_DIR.exists():
            self.log(f"Test documents directory not found: {TEST_DOCS_DIR}", "ERROR")
            return False

        code, stdout, stderr = self.run_cli(
            "index", str(TEST_DOCS_DIR),
            timeout=60
        )

        if code != 0:
            self.log(f"Indexing command failed: {stderr}", "ERROR")
            return False

        self.log("Index command accepted", "OK")
        return True

    def wait_for_indexing(self, timeout: int = INDEXING_TIMEOUT) -> bool:
        """Wait for indexing to complete."""
        self.log("Waiting for indexing to complete...")
        start = time.time()

        while time.time() - start < timeout:
            code, stdout, _ = self.run_cli("status", "--json")
            if code == 0:
                try:
                    data = json.loads(stdout)
                    indexing = data.get("indexing", {})
                    in_progress = indexing.get("indexing_in_progress", False)
                    total_docs = indexing.get("total_documents", 0)
                    total_chunks = indexing.get("total_chunks", 0)

                    if not in_progress and total_docs > 0:
                        self.log(
                            f"Indexing complete: {total_docs} documents, "
                            f"{total_chunks} chunks",
                            "OK"
                        )
                        return True

                    if in_progress:
                        progress = indexing.get("progress_percent", 0)
                        self.log(f"Indexing progress: {progress:.1f}%", "DEBUG")

                except json.JSONDecodeError:
                    pass

            time.sleep(HEALTH_POLL_INTERVAL)

        self.log("Indexing timed out", "ERROR")
        return False

    def run_query_test(self, test_case: TestCase) -> bool:
        """Run a single query test."""
        self.log(f"Test: {test_case.description}", "DEBUG")

        code, stdout, stderr = self.run_cli(
            "query", test_case.query,
            "--json", "--top-k", "5", "--threshold", "0.3"
        )

        if code != 0:
            self.log(f"FAIL: {test_case.description} - CLI error: {stderr}", "FAIL")
            self.failed += 1
            return False

        try:
            data = json.loads(stdout)
            results = data.get("results", [])

            # Check minimum results
            if len(results) < test_case.min_results:
                self.log(
                    f"FAIL: {test_case.description} - Expected at least "
                    f"{test_case.min_results} results, got {len(results)}",
                    "FAIL"
                )
                self.failed += 1
                return False

            # Check for expected terms in results
            all_text = " ".join(r.get("text", "").lower() for r in results)
            missing_terms = [
                t for t in test_case.expected_terms
                if t.lower() not in all_text
            ]

            if missing_terms:
                self.log(
                    f"FAIL: {test_case.description} - Missing expected terms: {missing_terms}",
                    "FAIL"
                )
                if self.verbose:
                    self.log(f"  Results text: {all_text[:200]}...", "DEBUG")
                self.failed += 1
                return False

            self.log(f"PASS: {test_case.description}", "OK")
            self.passed += 1
            return True

        except json.JSONDecodeError:
            self.log(f"FAIL: {test_case.description} - Invalid JSON response", "FAIL")
            self.failed += 1
            return False

    def run_all_query_tests(self) -> bool:
        """Run all query test scenarios."""
        self.log("Running query tests...")
        self.log("")

        all_passed = True
        for test_case in self.TEST_CASES:
            if not self.run_query_test(test_case):
                all_passed = False

        return all_passed

    def reset_index(self) -> bool:
        """Reset the index (cleanup)."""
        self.log("Resetting index...")
        code, _, stderr = self.run_cli("reset", "--yes")

        if code != 0:
            self.log(f"Reset failed: {stderr}", "ERROR")
            return False

        self.log("Index reset complete", "OK")
        return True

    def stop_server(self):
        """Stop the server process."""
        if self.server_process:
            self.log("Stopping server...")
            try:
                # Send SIGTERM to process group
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)
                self.server_process.wait()
            except ProcessLookupError:
                pass  # Process already terminated
            self.server_process = None
            self.log("Server stopped", "OK")

    def run(self) -> int:
        """Run the full E2E test suite."""
        self.log("=" * 50)
        self.log("Doc-Serve E2E Integration Tests")
        self.log("=" * 50)
        self.log("")

        try:
            # Phase 1: Setup
            if not self.start_server():
                return EXIT_SETUP_FAILURE

            # Phase 2: Index documents
            if not self.index_documents():
                return EXIT_INDEXING_FAILURE

            if not self.wait_for_indexing():
                return EXIT_INDEXING_FAILURE

            # Phase 3: Run tests
            self.log("")
            self.run_all_query_tests()

            # Phase 4: Report
            total = self.passed + self.failed
            self.log("")
            self.log("=" * 50)
            self.log(f"Results: {self.passed}/{total} tests passed")
            self.log("=" * 50)

            return EXIT_SUCCESS if self.failed == 0 else EXIT_TEST_FAILURE

        finally:
            # Cleanup
            if not self.keep_server:
                self.log("")
                self.reset_index()
                self.stop_server()
            else:
                self.log("")
                self.log("Server kept running (--keep-server flag)")


def main():
    parser = argparse.ArgumentParser(
        description="Run E2E integration tests for doc-serve"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--keep-server",
        action="store_true",
        help="Keep server running after tests"
    )
    args = parser.parse_args()

    runner = E2ETestRunner(verbose=args.verbose, keep_server=args.keep_server)
    sys.exit(runner.run())


if __name__ == "__main__":
    main()
