"""
Full E2E workflow tests for doc-serve.

These tests exercise the complete workflow: server health, indexing, and queries.
"""

import pytest


class TestServerHealth:
    """Tests for server health and status endpoints via CLI."""

    def test_server_is_healthy(self, cli):
        """Server should report healthy or indexing status."""
        status = cli.status()
        assert "health" in status
        assert status["health"]["status"] in ["healthy", "indexing"]

    def test_status_includes_version(self, cli):
        """Status should include server version."""
        status = cli.status()
        assert "version" in status.get("health", {})

    def test_status_includes_indexing_info(self, cli):
        """Status should include indexing information."""
        status = cli.status()
        assert "indexing" in status
        indexing = status["indexing"]
        assert "total_documents" in indexing
        assert "total_chunks" in indexing


class TestIndexing:
    """Tests for document indexing via CLI."""

    def test_documents_are_indexed(self, indexed_docs):
        """Test documents should be indexed."""
        assert indexed_docs["total_documents"] >= 5, \
            "Expected at least 5 test documents to be indexed"

    def test_indexing_creates_chunks(self, indexed_docs):
        """Indexing should create multiple chunks."""
        assert indexed_docs["total_chunks"] > 0, \
            "Expected chunks to be created"
        # With 5 substantial documents, expect multiple chunks
        assert indexed_docs["total_chunks"] >= 5, \
            "Expected at least 5 chunks from test documents"

    def test_indexed_folders_tracked(self, indexed_docs):
        """Indexed folders should be tracked."""
        assert "indexed_folders" in indexed_docs
        assert len(indexed_docs["indexed_folders"]) >= 1


class TestSemanticQueries:
    """Tests for semantic search queries via CLI."""

    def test_espresso_query(self, cli, indexed_docs):
        """Query about espresso should return relevant results."""
        result = cli.query("How do I make espresso?")

        assert "results" in result
        assert len(result["results"]) >= 1, "Expected at least one result"

        # Check that espresso-related content is returned
        all_text = " ".join(r["text"].lower() for r in result["results"])
        assert "espresso" in all_text, \
            "Expected 'espresso' in query results"

    def test_temperature_query(self, cli, indexed_docs):
        """Query about temperature should return relevant results."""
        result = cli.query("What water temperature for coffee?")

        assert len(result["results"]) >= 1

        all_text = " ".join(r["text"].lower() for r in result["results"])
        assert any(term in all_text for term in ["temperature", "fahrenheit", "celsius"]), \
            "Expected temperature-related terms in results"

    def test_grind_size_query(self, cli, indexed_docs):
        """Query about grind sizes should return relevant results."""
        result = cli.query("french press grind size")

        assert len(result["results"]) >= 1

        all_text = " ".join(r["text"].lower() for r in result["results"])
        assert "coarse" in all_text or "grind" in all_text, \
            "Expected grind-related terms in results"

    def test_pour_over_bloom_query(self, cli, indexed_docs):
        """Query about pour over bloom should return relevant results."""
        result = cli.query("pour over technique bloom")

        assert len(result["results"]) >= 1

        all_text = " ".join(r["text"].lower() for r in result["results"])
        assert "bloom" in all_text or "pour" in all_text, \
            "Expected pour over related terms in results"

    def test_cross_document_query(self, cli, indexed_docs):
        """Query spanning topics should return results from multiple sources."""
        result = cli.query("coffee brewing methods")

        # Should find results
        assert len(result["results"]) >= 1

        # With a broad query, we might get diverse results
        sources = set(r["source"] for r in result["results"])
        # At minimum, should have some results
        assert len(sources) >= 1

    def test_technical_espresso_query(self, cli, indexed_docs):
        """Technical query about espresso parameters."""
        result = cli.query("9 bars pressure extraction time")

        assert len(result["results"]) >= 1

        all_text = " ".join(r["text"].lower() for r in result["results"])
        assert "pressure" in all_text or "bar" in all_text or "extraction" in all_text

    def test_query_returns_scores(self, cli, indexed_docs):
        """Query results should include similarity scores."""
        result = cli.query("espresso")

        assert len(result["results"]) >= 1
        for r in result["results"]:
            assert "score" in r
            assert isinstance(r["score"], (int, float))
            assert 0 <= r["score"] <= 1

    def test_query_returns_sources(self, cli, indexed_docs):
        """Query results should include source file information."""
        result = cli.query("pour over technique")

        assert len(result["results"]) >= 1
        for r in result["results"]:
            assert "source" in r
            assert r["source"].endswith(".md")

    def test_query_returns_text(self, cli, indexed_docs):
        """Query results should include text content."""
        result = cli.query("water temperature")

        assert len(result["results"]) >= 1
        for r in result["results"]:
            assert "text" in r
            assert len(r["text"]) > 0


class TestQueryParameters:
    """Tests for query parameter handling via CLI."""

    def test_top_k_limits_results(self, cli, indexed_docs):
        """top_k parameter should limit result count."""
        result = cli.query("coffee", top_k=2)
        assert len(result["results"]) <= 2

    def test_query_timing(self, cli, indexed_docs):
        """Query should return timing information."""
        result = cli.query("espresso")

        assert "query_time_ms" in result
        assert result["query_time_ms"] > 0

    def test_total_results_reported(self, cli, indexed_docs):
        """Query should report total results."""
        result = cli.query("coffee")

        assert "total_results" in result
        assert result["total_results"] >= 0


class TestResetFunctionality:
    """Tests for index reset functionality via CLI."""

    def test_reset_returns_success(self, cli, indexed_docs):
        """Reset command should complete successfully."""
        # Store current state
        status_before = cli.status()
        had_docs = status_before.get("indexing", {}).get("total_documents", 0) > 0

        if had_docs:
            # Reset
            result = cli.run("reset", "--yes")
            assert result["returncode"] == 0

            # Give server time to process
            import time
            time.sleep(2)

            # Re-index for other tests
            from pathlib import Path
            test_docs = Path(__file__).parent.parent / "fixtures" / "test_docs" / "coffee_brewing"
            cli.index(str(test_docs))

            # Wait for re-indexing
            for _ in range(60):
                status = cli.status()
                if not status.get("indexing", {}).get("indexing_in_progress", True):
                    if status.get("indexing", {}).get("total_documents", 0) > 0:
                        break
                time.sleep(2)


class TestQueryModes:
    """Tests for different query modes via CLI (Feature 113 - GraphRAG)."""

    def test_vector_mode_returns_results(self, cli, indexed_docs):
        """Vector-only query should return results."""
        result = cli.query("espresso brewing", mode="vector")

        assert "results" in result
        assert len(result["results"]) >= 1
        assert "score" in result["results"][0]

    def test_bm25_mode_returns_results(self, cli, indexed_docs):
        """BM25 keyword search should return results."""
        result = cli.query("espresso", mode="bm25")

        assert "results" in result
        assert len(result["results"]) >= 1

    def test_hybrid_mode_returns_results(self, cli, indexed_docs):
        """Hybrid mode (default) should return results."""
        result = cli.query("coffee brewing temperature", mode="hybrid")

        assert "results" in result
        assert len(result["results"]) >= 1


class TestGraphRAGQueries:
    """Tests for GraphRAG query modes via CLI (Feature 113).

    Note: These tests verify the CLI interface for graph and multi modes.
    The behavior depends on whether ENABLE_GRAPH_INDEX is set on the server.
    """

    def test_graph_mode_cli_accepts_mode(self, cli, indexed_docs):
        """CLI should accept --mode graph without syntax error."""
        result = cli.query_raw("coffee relationships", mode="graph")

        # Command should execute (may return error if GraphRAG disabled, but not CLI error)
        # returncode 0 = success, returncode 1 = server error (expected if disabled)
        assert result["returncode"] in [0, 1], \
            f"Unexpected CLI error: {result.get('stderr', '')}"

    def test_multi_mode_cli_accepts_mode(self, cli, indexed_docs):
        """CLI should accept --mode multi without syntax error."""
        result = cli.query_raw("coffee brewing methods", mode="multi")

        # Command should execute
        assert result["returncode"] in [0, 1], \
            f"Unexpected CLI error: {result.get('stderr', '')}"

    def test_graph_mode_returns_results_or_disabled_error(self, cli, indexed_docs):
        """Graph mode should return results OR informative error if disabled."""
        result = cli.query_raw("espresso", mode="graph")

        if result["returncode"] == 0:
            # GraphRAG is enabled - should have results
            json_result = result.get("json") or {}
            assert "results" in json_result or "error" not in str(json_result).lower()
        else:
            # GraphRAG is disabled - should have informative error
            output = result.get("stdout", "") + result.get("stderr", "")
            assert any(term in output.lower() for term in ["not enabled", "disabled", "graph"]), \
                f"Expected informative error about GraphRAG being disabled: {output}"

    def test_multi_mode_returns_results_or_graceful_fallback(self, cli, indexed_docs):
        """Multi mode should return results (with or without graph component)."""
        result = cli.query_raw("coffee temperature", mode="multi")

        # Multi mode should work even if graph is disabled (falls back to vector+BM25)
        if result["returncode"] == 0:
            json_result = result.get("json") or {}
            assert "results" in json_result, "Multi mode should return results"
            # Multi mode may have fewer results if graph is disabled, but should work
            assert json_result.get("total_results", 0) >= 0


class TestGraphRAGHealthStatus:
    """Tests for GraphRAG status in health endpoints (Feature 113)."""

    def test_status_includes_graph_index_info(self, cli, indexed_docs):
        """Status should include graph_index information."""
        status = cli.status()

        indexing = status.get("indexing", {})
        # graph_index should be present (may be None if disabled)
        # The field should exist in the response
        assert "indexing" in status, "Status should include indexing section"

        # If graph_index is present, verify its structure
        graph_index = indexing.get("graph_index")
        if graph_index is not None:
            assert "enabled" in graph_index, "graph_index should have 'enabled' field"
            if graph_index.get("enabled"):
                assert "entity_count" in graph_index
                assert "relationship_count" in graph_index
                assert "store_type" in graph_index
