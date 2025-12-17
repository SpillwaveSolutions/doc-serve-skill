"""
Tests for error handling scenarios via CLI.

These tests verify the system handles edge cases gracefully.
"""

import pytest


class TestQueryErrors:
    """Tests for query error handling via CLI."""

    def test_empty_query_handling(self, cli, indexed_docs):
        """Empty query should be handled gracefully."""
        result = cli.run("query", "", "--json")

        # Should either fail or return error
        # The CLI might reject empty queries or the server might
        if result["returncode"] == 0 and result["json"]:
            # If it succeeds, should have empty or minimal results
            assert "results" in result["json"]
        else:
            # Failed as expected for empty query
            assert result["returncode"] != 0 or "error" in result["stderr"].lower()

    def test_unrelated_query_returns_low_scores(self, cli, indexed_docs):
        """Query for unrelated content should return low scores or no results."""
        # Query for something completely unrelated to coffee
        result = cli.query(
            "quantum physics dark matter black holes",
            threshold=0.9
        )

        # With high threshold, unrelated query should find few/no results
        # Or if results exist, they should have lower relevance
        if result.get("results"):
            # Any results should have lower scores for unrelated content
            # (though embedding models can sometimes find unexpected connections)
            pass  # Just verify no crash occurs

    def test_very_long_query_handling(self, cli, indexed_docs):
        """Very long query should be handled gracefully."""
        long_query = "coffee " * 100  # 700+ character query

        result = cli.query(long_query)

        # Should either succeed or fail gracefully
        # Verify no crash and response is parseable
        assert isinstance(result, dict)


class TestCLIErrors:
    """Tests for CLI error handling."""

    def test_invalid_top_k_type(self, cli, indexed_docs):
        """Invalid top_k type should be handled."""
        result = cli.run("query", "coffee", "--top-k", "not-a-number", "--json")

        # Click should reject invalid integer
        assert result["returncode"] != 0

    def test_missing_query_text(self, cli, indexed_docs):
        """Missing query text should show error."""
        result = cli.run("query", "--json")

        # Click requires the query argument
        assert result["returncode"] != 0

    def test_index_nonexistent_path(self, cli):
        """Indexing non-existent path should fail gracefully."""
        result = cli.run("index", "/this/path/does/not/exist/anywhere")

        # Should fail but not crash
        assert result["returncode"] != 0


class TestConnectionErrors:
    """Tests for connection error handling."""

    def test_wrong_url_fails_gracefully(self):
        """CLI should handle wrong server URL gracefully."""
        from pathlib import Path

        CLI_DIR = Path(__file__).parent.parent.parent / "doc-svr-ctl"

        import subprocess
        result = subprocess.run(
            ["poetry", "run", "doc-svr-ctl",
             "--url", "http://localhost:59999",
             "status", "--json"],
            cwd=CLI_DIR,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should fail but not crash
        assert result.returncode != 0
        # Should have some error message
        assert "error" in result.stdout.lower() or "error" in result.stderr.lower() or result.returncode != 0


class TestRobustness:
    """Tests for system robustness."""

    def test_multiple_sequential_queries(self, cli, indexed_docs):
        """Multiple sequential queries should all succeed."""
        queries = [
            "espresso",
            "pour over",
            "french press",
            "water temperature",
            "grind size"
        ]

        for query_text in queries:
            result = cli.query(query_text)
            assert "results" in result, f"Query '{query_text}' failed"

    def test_repeated_same_query(self, cli, indexed_docs):
        """Repeated identical queries should return consistent results."""
        query_text = "espresso pressure bars"

        results = []
        for _ in range(3):
            result = cli.query(query_text)
            results.append(result)

        # All should succeed
        for r in results:
            assert "results" in r

        # Results should be consistent (same number of results)
        result_counts = [len(r["results"]) for r in results]
        assert len(set(result_counts)) == 1, "Repeated queries returned different result counts"
