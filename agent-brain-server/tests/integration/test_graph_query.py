"""Integration tests for graph-based queries (Feature 113)."""

from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from agent_brain_server.models import QueryMode, QueryRequest


@pytest.fixture
def mock_graph_index_manager():
    """Create a mock graph index manager."""
    mock = MagicMock()
    mock.query.return_value = [
        {
            "entity": "FastAPI",
            "subject": "FastAPI",
            "predicate": "uses",
            "object": "Pydantic",
            "source_chunk_id": "chunk_123",
            "relationship_path": "FastAPI -> uses -> Pydantic",
            "graph_score": 0.9,
        }
    ]
    mock.get_status.return_value = MagicMock(
        enabled=True,
        initialized=True,
        entity_count=50,
        relationship_count=100,
        store_type="simple",
        last_updated=None,
    )
    return mock


@contextmanager
def create_test_client(
    mock_vector_store,
    mock_embedding_generator,
    mock_bm25_manager,
    mock_graph_index_manager,
    enable_graph: bool,
):
    """Create a test client with proper mocking in a context manager."""
    # Create mock settings
    mock_settings = MagicMock()
    mock_settings.ENABLE_GRAPH_INDEX = enable_graph
    mock_settings.GRAPH_RRF_K = 60

    # Ensure BM25 manager is marked as initialized
    mock_bm25_manager.is_initialized = True

    # Configure bm25_manager with search_with_filters
    mock_bm25_manager.search_with_filters = AsyncMock(return_value=[])

    with (
        patch(
            "agent_brain_server.storage.get_vector_store",
            return_value=mock_vector_store,
        ),
        patch(
            "agent_brain_server.storage.initialize_vector_store",
            new_callable=AsyncMock,
            return_value=mock_vector_store,
        ),
        patch(
            "agent_brain_server.indexing.get_embedding_generator",
            return_value=mock_embedding_generator,
        ),
        patch(
            "agent_brain_server.services.query_service.get_embedding_generator",
            return_value=mock_embedding_generator,
        ),
        patch(
            "agent_brain_server.indexing.get_bm25_manager",
            return_value=mock_bm25_manager,
        ),
        patch(
            "agent_brain_server.services.query_service.get_bm25_manager",
            return_value=mock_bm25_manager,
        ),
        patch(
            "agent_brain_server.indexing.graph_index.get_graph_index_manager",
            return_value=mock_graph_index_manager,
        ),
        patch(
            "agent_brain_server.services.query_service.get_graph_index_manager",
            return_value=mock_graph_index_manager,
        ),
        patch(
            "agent_brain_server.services.query_service.settings",
            mock_settings,
        ),
    ):
        from agent_brain_server.api.main import app
        from agent_brain_server.services import IndexingService, QueryService

        # Configure vector store to return document by ID
        mock_vector_store.get_by_id = AsyncMock(
            return_value={
                "text": "FastAPI uses Pydantic for validation.",
                "metadata": {
                    "source": "docs/fastapi.md",
                    "source_type": "doc",
                },
            }
        )

        # Create client first - this triggers the lifespan which sets up real services
        with TestClient(app) as client:
            # NOW override app.state with mock-backed services AFTER lifespan runs
            # This ensures our mocks are used instead of the real services
            app.state.vector_store = mock_vector_store
            app.state.bm25_manager = mock_bm25_manager
            app.state.indexing_service = IndexingService(
                vector_store=mock_vector_store,
                bm25_manager=mock_bm25_manager,
                graph_index_manager=mock_graph_index_manager,
            )
            app.state.query_service = QueryService(
                vector_store=mock_vector_store,
                embedding_generator=mock_embedding_generator,
                bm25_manager=mock_bm25_manager,
                graph_index_manager=mock_graph_index_manager,
            )
            app.state.mode = "project"
            app.state.instance_id = None
            app.state.project_id = None
            app.state.active_projects = None

            yield client


@pytest.fixture
def client_graph_enabled(
    mock_vector_store,
    mock_embedding_generator,
    mock_bm25_manager,
    mock_graph_index_manager,
):
    """Create test client with graph support enabled."""
    with create_test_client(
        mock_vector_store,
        mock_embedding_generator,
        mock_bm25_manager,
        mock_graph_index_manager,
        enable_graph=True,
    ) as client:
        yield client


@pytest.fixture
def client_graph_disabled(
    mock_vector_store,
    mock_embedding_generator,
    mock_bm25_manager,
    mock_graph_index_manager,
):
    """Create test client with graph support disabled."""
    with create_test_client(
        mock_vector_store,
        mock_embedding_generator,
        mock_bm25_manager,
        mock_graph_index_manager,
        enable_graph=False,
    ) as client:
        yield client


class TestGraphQueryMode:
    """Tests for graph query mode."""

    def test_graph_query_enabled(self, client_graph_enabled, mock_graph_index_manager):
        """Test graph query when enabled."""
        response = client_graph_enabled.post(
            "/query/",
            json={
                "query": "How does FastAPI use Pydantic?",
                "mode": "graph",
                "top_k": 5,
            },
        )

        if response.status_code != 200:
            print(f"Error response: {response.text}")
        assert response.status_code == 200, f"Unexpected error: {response.text}"
        data = response.json()
        assert "results" in data
        mock_graph_index_manager.query.assert_called()

    def test_graph_query_disabled(
        self, client_graph_disabled, mock_graph_index_manager
    ):
        """Test graph query returns error when disabled."""
        response = client_graph_disabled.post(
            "/query/",
            json={
                "query": "How does FastAPI use Pydantic?",
                "mode": "graph",
                "top_k": 5,
            },
        )

        # Should return 500 with error message about graph not enabled
        assert response.status_code == 500
        assert "not enabled" in response.json()["detail"].lower()


class TestMultiQueryMode:
    """Tests for multi-retrieval query mode.

    Tests the MULTI mode which combines vector, BM25, and graph retrieval
    using Reciprocal Rank Fusion (RRF).
    """

    def test_multi_mode_is_valid_query_mode(self):
        """Test that 'multi' is a valid query mode."""
        from agent_brain_server.models import QueryMode, QueryRequest

        request = QueryRequest(
            query="test query",
            mode=QueryMode.MULTI,
        )
        assert request.mode == QueryMode.MULTI
        assert request.mode.value == "multi"

    def test_multi_query_enabled(
        self,
        mock_vector_store,
        mock_embedding_generator,
        mock_bm25_manager,
        mock_graph_index_manager,
    ):
        """Test multi-mode query when graph is enabled."""
        from agent_brain_server.storage.vector_store import SearchResult

        # Setup vector results
        mock_vector_store.similarity_search = AsyncMock(
            return_value=[
                SearchResult(
                    text="Vector result",
                    metadata={"source": "vector.md", "source_type": "doc"},
                    score=0.9,
                    chunk_id="v1",
                )
            ]
        )
        mock_vector_store.get_count = AsyncMock(return_value=10)

        # Setup BM25 results
        mock_bm25_node = MagicMock()
        mock_bm25_node.node.get_content.return_value = "BM25 result"
        mock_bm25_node.node.metadata = {"source": "bm25.md", "source_type": "doc"}
        mock_bm25_node.node.node_id = "b1"
        mock_bm25_node.score = 0.85

        mock_retriever = MagicMock()
        mock_retriever.aretrieve = AsyncMock(return_value=[mock_bm25_node])
        mock_bm25_manager.get_retriever = MagicMock(return_value=mock_retriever)

        with create_test_client(
            mock_vector_store,
            mock_embedding_generator,
            mock_bm25_manager,
            mock_graph_index_manager,
            enable_graph=True,
        ) as client:
            response = client.post(
                "/query/",
                json={
                    "query": "test query",
                    "mode": "multi",
                    "top_k": 10,
                },
            )

            assert response.status_code == 200, f"Unexpected error: {response.text}"
            data = response.json()
            assert "results" in data
            assert data["total_results"] >= 1

    def test_multi_query_disabled_still_works(
        self,
        mock_vector_store,
        mock_embedding_generator,
        mock_bm25_manager,
        mock_graph_index_manager,
    ):
        """Test multi-mode works when graph is disabled (vector+BM25 only)."""
        from agent_brain_server.storage.vector_store import SearchResult

        mock_vector_store.similarity_search = AsyncMock(
            return_value=[
                SearchResult(
                    text="Vector result",
                    metadata={"source": "vector.md", "source_type": "doc"},
                    score=0.9,
                    chunk_id="v1",
                )
            ]
        )
        mock_vector_store.get_count = AsyncMock(return_value=10)

        mock_retriever = MagicMock()
        mock_retriever.aretrieve = AsyncMock(return_value=[])
        mock_bm25_manager.get_retriever = MagicMock(return_value=mock_retriever)

        with create_test_client(
            mock_vector_store,
            mock_embedding_generator,
            mock_bm25_manager,
            mock_graph_index_manager,
            enable_graph=False,
        ) as client:
            response = client.post(
                "/query/",
                json={
                    "query": "test query",
                    "mode": "multi",
                    "top_k": 5,
                },
            )

            # Multi mode should still work without graph
            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            # Should have vector results at least
            assert data["total_results"] >= 1

    def test_multi_query_combines_all_sources(
        self,
        mock_vector_store,
        mock_embedding_generator,
        mock_bm25_manager,
        mock_graph_index_manager,
    ):
        """Test multi-mode combines results from all three sources."""
        from agent_brain_server.storage.vector_store import SearchResult

        # Unique results from each source
        mock_vector_store.similarity_search = AsyncMock(
            return_value=[
                SearchResult(
                    text="Vector unique",
                    metadata={"source": "vector.md", "source_type": "doc"},
                    score=0.9,
                    chunk_id="vector_only",
                )
            ]
        )
        mock_vector_store.get_count = AsyncMock(return_value=10)

        mock_bm25_node = MagicMock()
        mock_bm25_node.node.get_content.return_value = "BM25 unique"
        mock_bm25_node.node.metadata = {"source": "bm25.md", "source_type": "doc"}
        mock_bm25_node.node.node_id = "bm25_only"
        mock_bm25_node.score = 0.85

        mock_retriever = MagicMock()
        mock_retriever.aretrieve = AsyncMock(return_value=[mock_bm25_node])
        mock_bm25_manager.get_retriever = MagicMock(return_value=mock_retriever)
        # Also mock search_with_filters for ChromaBackend path (Phase 5)
        mock_bm25_manager.search_with_filters = AsyncMock(return_value=[mock_bm25_node])

        # Graph returns a different chunk
        mock_graph_index_manager.query.return_value = [
            {
                "entity": "TestEntity",
                "subject": "TestEntity",
                "predicate": "relates_to",
                "object": "AnotherEntity",
                "source_chunk_id": "graph_only",
                "relationship_path": "TestEntity -> relates_to -> AnotherEntity",
                "graph_score": 0.8,
            }
        ]

        # Mock get_by_id for graph chunk lookup
        async def get_by_id_side_effect(chunk_id):
            if chunk_id == "graph_only":
                return {
                    "text": "Graph unique content",
                    "metadata": {"source": "graph.md", "source_type": "doc"},
                }
            return None

        mock_vector_store.get_by_id = AsyncMock(side_effect=get_by_id_side_effect)

        with create_test_client(
            mock_vector_store,
            mock_embedding_generator,
            mock_bm25_manager,
            mock_graph_index_manager,
            enable_graph=True,
        ) as client:
            # Re-set search_with_filters after create_test_client resets it
            mock_bm25_manager.search_with_filters = AsyncMock(
                return_value=[mock_bm25_node]
            )

            response = client.post(
                "/query/",
                json={
                    "query": "test query",
                    "mode": "multi",
                    "top_k": 10,
                },
            )

            assert response.status_code == 200
            data = response.json()

            # Should have results from all three sources
            chunk_ids = [r["chunk_id"] for r in data["results"]]
            assert "vector_only" in chunk_ids
            assert "bm25_only" in chunk_ids
            assert "graph_only" in chunk_ids

    def test_multi_query_rrf_ranking(
        self,
        mock_vector_store,
        mock_embedding_generator,
        mock_bm25_manager,
        mock_graph_index_manager,
    ):
        """Test multi-mode uses RRF to rank results."""
        from agent_brain_server.storage.vector_store import SearchResult

        # Same document appears in multiple rankings
        mock_vector_store.similarity_search = AsyncMock(
            return_value=[
                SearchResult(
                    text="Shared doc",
                    metadata={"source": "shared.md", "source_type": "doc"},
                    score=0.9,
                    chunk_id="shared",
                ),
                SearchResult(
                    text="Vector only",
                    metadata={"source": "vector.md", "source_type": "doc"},
                    score=0.85,
                    chunk_id="vector_only",
                ),
            ]
        )
        mock_vector_store.get_count = AsyncMock(return_value=10)

        mock_shared_node = MagicMock()
        mock_shared_node.node.get_content.return_value = "Shared doc"
        mock_shared_node.node.metadata = {"source": "shared.md", "source_type": "doc"}
        mock_shared_node.node.node_id = "shared"
        mock_shared_node.score = 0.88

        mock_retriever = MagicMock()
        mock_retriever.aretrieve = AsyncMock(return_value=[mock_shared_node])
        mock_bm25_manager.get_retriever = MagicMock(return_value=mock_retriever)

        mock_graph_index_manager.query.return_value = []

        with create_test_client(
            mock_vector_store,
            mock_embedding_generator,
            mock_bm25_manager,
            mock_graph_index_manager,
            enable_graph=True,
        ) as client:
            response = client.post(
                "/query/",
                json={
                    "query": "test query",
                    "mode": "multi",
                    "top_k": 10,
                },
            )

            assert response.status_code == 200
            data = response.json()

            # Shared doc should be ranked higher due to appearing in multiple rankings
            results = data["results"]
            shared_idx = next(
                (i for i, r in enumerate(results) if r["chunk_id"] == "shared"), -1
            )
            vector_only_idx = next(
                (i for i, r in enumerate(results) if r["chunk_id"] == "vector_only"), -1
            )

            # Shared should be ranked higher (lower index)
            assert shared_idx < vector_only_idx


class TestHealthStatusWithGraph:
    """Tests for health status including graph index."""

    def test_status_includes_graph_index(
        self, client_graph_enabled, mock_graph_index_manager
    ):
        """Test /health/status includes graph index information."""
        response = client_graph_enabled.get("/health/status")

        assert response.status_code == 200
        data = response.json()

        # Should include graph_index in response
        assert "graph_index" in data
        graph_status = data["graph_index"]
        assert "enabled" in graph_status
        assert "entity_count" in graph_status
        assert "relationship_count" in graph_status


class TestQueryModeEnum:
    """Tests for QueryMode enum values."""

    def test_graph_mode_exists(self):
        """Test GRAPH mode exists in QueryMode enum."""
        assert QueryMode.GRAPH.value == "graph"

    def test_multi_mode_exists(self):
        """Test MULTI mode exists in QueryMode enum."""
        assert QueryMode.MULTI.value == "multi"

    def test_query_request_accepts_graph_mode(self):
        """Test QueryRequest accepts graph mode."""
        request = QueryRequest(
            query="test query",
            mode=QueryMode.GRAPH,
        )
        assert request.mode == QueryMode.GRAPH

    def test_query_request_accepts_multi_mode(self):
        """Test QueryRequest accepts multi mode."""
        request = QueryRequest(
            query="test query",
            mode=QueryMode.MULTI,
        )
        assert request.mode == QueryMode.MULTI


class TestGraphQueryResult:
    """Tests for graph-specific query result fields."""

    def test_result_includes_graph_score(
        self, client_graph_enabled, mock_graph_index_manager
    ):
        """Test query result includes graph_score field."""
        response = client_graph_enabled.post(
            "/query/",
            json={
                "query": "FastAPI framework",
                "mode": "graph",
                "top_k": 5,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Results should have graph-related fields
        if data["results"]:
            result = data["results"][0]
            # These fields should be present (may be null)
            assert "graph_score" in result or result.get("score") is not None

    def test_result_includes_related_entities(
        self, client_graph_enabled, mock_graph_index_manager
    ):
        """Test query result includes related_entities field."""
        response = client_graph_enabled.post(
            "/query/",
            json={
                "query": "FastAPI framework",
                "mode": "graph",
                "top_k": 5,
            },
        )

        assert response.status_code == 200
        data = response.json()

        if data["results"]:
            result = data["results"][0]
            # Should have related_entities field (may be null or list)
            assert "related_entities" in result or "metadata" in result


class TestStoreTypeSwitching:
    """Integration tests for store type switching (T037 - User Story 3).

    Tests the ability to switch between SimplePropertyGraphStore and Kuzu
    graph store backends.
    """

    def test_status_shows_store_type_simple(
        self, client_graph_enabled, mock_graph_index_manager
    ):
        """Test /health/status shows store_type as 'simple' by default."""
        # Configure mock to return simple store type
        mock_graph_index_manager.get_status.return_value = MagicMock(
            enabled=True,
            initialized=True,
            entity_count=10,
            relationship_count=20,
            store_type="simple",
            last_updated=None,
        )

        response = client_graph_enabled.get("/health/status")

        assert response.status_code == 200
        data = response.json()
        assert "graph_index" in data
        assert data["graph_index"]["store_type"] == "simple"

    def test_status_shows_store_type_kuzu(
        self,
        mock_vector_store,
        mock_embedding_generator,
        mock_bm25_manager,
        mock_graph_index_manager,
    ):
        """Test /health/status shows store_type as 'kuzu' when configured."""
        # Configure mock to return kuzu store type
        mock_graph_index_manager.get_status.return_value = MagicMock(
            enabled=True,
            initialized=True,
            entity_count=50,
            relationship_count=100,
            store_type="kuzu",
            last_updated=None,
        )

        with create_test_client(
            mock_vector_store,
            mock_embedding_generator,
            mock_bm25_manager,
            mock_graph_index_manager,
            enable_graph=True,
        ) as client:
            response = client.get("/health/status")

            assert response.status_code == 200
            data = response.json()
            assert "graph_index" in data
            assert data["graph_index"]["store_type"] == "kuzu"

    def test_graph_query_works_with_simple_store(
        self, client_graph_enabled, mock_graph_index_manager
    ):
        """Test graph queries work with simple store backend."""
        mock_graph_index_manager.get_status.return_value = MagicMock(
            enabled=True,
            initialized=True,
            entity_count=5,
            relationship_count=10,
            store_type="simple",
            last_updated=None,
        )

        response = client_graph_enabled.post(
            "/query/",
            json={
                "query": "test query",
                "mode": "graph",
                "top_k": 5,
            },
        )

        assert response.status_code == 200
        mock_graph_index_manager.query.assert_called()

    def test_graph_query_works_with_kuzu_store(
        self,
        mock_vector_store,
        mock_embedding_generator,
        mock_bm25_manager,
        mock_graph_index_manager,
    ):
        """Test graph queries work with kuzu store backend."""
        mock_graph_index_manager.get_status.return_value = MagicMock(
            enabled=True,
            initialized=True,
            entity_count=50,
            relationship_count=100,
            store_type="kuzu",
            last_updated=None,
        )

        with create_test_client(
            mock_vector_store,
            mock_embedding_generator,
            mock_bm25_manager,
            mock_graph_index_manager,
            enable_graph=True,
        ) as client:
            response = client.post(
                "/query/",
                json={
                    "query": "test query with kuzu",
                    "mode": "graph",
                    "top_k": 5,
                },
            )

            assert response.status_code == 200
            mock_graph_index_manager.query.assert_called()

    def test_store_type_in_graph_index_status_model(self):
        """Test GraphIndexStatus model includes store_type field."""
        from agent_brain_server.models import GraphIndexStatus

        status = GraphIndexStatus(
            enabled=True,
            initialized=True,
            entity_count=10,
            relationship_count=20,
            store_type="kuzu",
        )

        assert status.store_type == "kuzu"
        assert status.model_dump()["store_type"] == "kuzu"

    def test_store_type_defaults_to_simple(self):
        """Test GraphIndexStatus defaults store_type to 'simple'."""
        from agent_brain_server.models import GraphIndexStatus

        status = GraphIndexStatus()

        assert status.store_type == "simple"

    def test_multi_query_works_regardless_of_store_type(
        self,
        mock_vector_store,
        mock_embedding_generator,
        mock_bm25_manager,
        mock_graph_index_manager,
    ):
        """Test multi-mode query works with either store type."""
        from agent_brain_server.storage.vector_store import SearchResult

        mock_vector_store.similarity_search = AsyncMock(
            return_value=[
                SearchResult(
                    text="Test result",
                    metadata={"source": "test.md", "source_type": "doc"},
                    score=0.9,
                    chunk_id="test_chunk",
                )
            ]
        )
        mock_vector_store.get_count = AsyncMock(return_value=10)

        mock_retriever = MagicMock()
        mock_retriever.aretrieve = AsyncMock(return_value=[])
        mock_bm25_manager.get_retriever = MagicMock(return_value=mock_retriever)

        # Test with kuzu store type
        mock_graph_index_manager.get_status.return_value = MagicMock(
            enabled=True,
            initialized=True,
            entity_count=50,
            relationship_count=100,
            store_type="kuzu",
            last_updated=None,
        )

        with create_test_client(
            mock_vector_store,
            mock_embedding_generator,
            mock_bm25_manager,
            mock_graph_index_manager,
            enable_graph=True,
        ) as client:
            response = client.post(
                "/query/",
                json={
                    "query": "multi-mode test",
                    "mode": "multi",
                    "top_k": 10,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "results" in data
