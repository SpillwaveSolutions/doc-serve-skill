"""Contract tests for QueryMode enum values.

These tests ensure API stability by verifying that QueryMode enum values
remain consistent across releases. Changing these values would be a
breaking change for API consumers.

Feature 113: GraphRAG Integration
"""

import pytest

from agent_brain_server.models.query import QueryMode


class TestQueryModeContract:
    """Contract tests for QueryMode enum values."""

    def test_query_mode_has_required_values(self) -> None:
        """Verify all required QueryMode values exist.

        These values are part of the API contract and must not be removed.
        """
        required_modes = ["vector", "bm25", "hybrid", "graph", "multi"]

        for mode in required_modes:
            assert hasattr(
                QueryMode, mode.upper()
            ), f"QueryMode.{mode.upper()} must exist"

    def test_query_mode_vector_value(self) -> None:
        """Verify QueryMode.VECTOR has the correct string value."""
        assert QueryMode.VECTOR.value == "vector"

    def test_query_mode_bm25_value(self) -> None:
        """Verify QueryMode.BM25 has the correct string value."""
        assert QueryMode.BM25.value == "bm25"

    def test_query_mode_hybrid_value(self) -> None:
        """Verify QueryMode.HYBRID has the correct string value."""
        assert QueryMode.HYBRID.value == "hybrid"

    def test_query_mode_graph_value(self) -> None:
        """Verify QueryMode.GRAPH has the correct string value (Feature 113)."""
        assert QueryMode.GRAPH.value == "graph"

    def test_query_mode_multi_value(self) -> None:
        """Verify QueryMode.MULTI has the correct string value (Feature 113)."""
        assert QueryMode.MULTI.value == "multi"

    def test_query_mode_is_string_enum(self) -> None:
        """Verify QueryMode values can be used as strings via .value."""
        # String enum values should be accessible via .value
        assert QueryMode.VECTOR.value == "vector"
        assert QueryMode.BM25.value == "bm25"
        assert QueryMode.HYBRID.value == "hybrid"
        assert QueryMode.GRAPH.value == "graph"
        assert QueryMode.MULTI.value == "multi"

        # String enum should inherit from str for direct comparison
        assert QueryMode.VECTOR == "vector"
        assert QueryMode.BM25 == "bm25"
        assert QueryMode.HYBRID == "hybrid"
        assert QueryMode.GRAPH == "graph"
        assert QueryMode.MULTI == "multi"

    def test_query_mode_from_string(self) -> None:
        """Verify QueryMode can be created from string values."""
        assert QueryMode("vector") == QueryMode.VECTOR
        assert QueryMode("bm25") == QueryMode.BM25
        assert QueryMode("hybrid") == QueryMode.HYBRID
        assert QueryMode("graph") == QueryMode.GRAPH
        assert QueryMode("multi") == QueryMode.MULTI

    def test_query_mode_minimum_count(self) -> None:
        """Verify QueryMode has at least 5 values (original 3 + 2 from Feature 113)."""
        mode_count = len(QueryMode)
        assert mode_count >= 5, f"Expected at least 5 query modes, got {mode_count}"

    @pytest.mark.parametrize(
        "mode_name,mode_value",
        [
            ("VECTOR", "vector"),
            ("BM25", "bm25"),
            ("HYBRID", "hybrid"),
            ("GRAPH", "graph"),
            ("MULTI", "multi"),
        ],
    )
    def test_query_mode_name_value_pairs(
        self, mode_name: str, mode_value: str
    ) -> None:
        """Verify all query mode name-value pairs are correct."""
        mode = getattr(QueryMode, mode_name)
        assert mode.value == mode_value
        assert mode.name == mode_name


class TestQueryModeGraphRAGContract:
    """Contract tests specifically for GraphRAG query modes (Feature 113)."""

    def test_graph_mode_exists_and_valid(self) -> None:
        """Verify GRAPH mode is available for graph-only queries."""
        graph_mode = QueryMode.GRAPH

        # Must be a valid string enum
        assert isinstance(graph_mode.value, str)
        assert graph_mode.value == "graph"

        # Must be case-insensitive comparable
        assert QueryMode("graph") == graph_mode

    def test_multi_mode_exists_and_valid(self) -> None:
        """Verify MULTI mode is available for multi-retrieval fusion."""
        multi_mode = QueryMode.MULTI

        # Must be a valid string enum
        assert isinstance(multi_mode.value, str)
        assert multi_mode.value == "multi"

        # Must be case-insensitive comparable
        assert QueryMode("multi") == multi_mode

    def test_graphrag_modes_are_distinct(self) -> None:
        """Verify GraphRAG modes are distinct from each other and existing modes."""
        all_modes = list(QueryMode)
        all_values = [m.value for m in all_modes]

        # No duplicate values
        assert len(all_values) == len(set(all_values))

        # GRAPH and MULTI are different
        assert QueryMode.GRAPH != QueryMode.MULTI
        assert QueryMode.GRAPH.value != QueryMode.MULTI.value

    def test_graphrag_modes_in_enumeration(self) -> None:
        """Verify GraphRAG modes appear in enumeration of all modes."""
        all_modes = list(QueryMode)

        assert QueryMode.GRAPH in all_modes
        assert QueryMode.MULTI in all_modes

    def test_invalid_mode_raises_error(self) -> None:
        """Verify invalid mode values raise ValueError."""
        with pytest.raises(ValueError):
            QueryMode("invalid_mode")

        with pytest.raises(ValueError):
            QueryMode("graphrag")  # Not a valid mode name

        with pytest.raises(ValueError):
            QueryMode("GRAPH")  # Case sensitive - must be lowercase
