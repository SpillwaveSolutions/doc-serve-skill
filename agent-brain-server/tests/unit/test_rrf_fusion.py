"""Unit tests for Reciprocal Rank Fusion (RRF) in multi-mode queries."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent_brain_server.models.query import QueryMode, QueryRequest
from agent_brain_server.services.query_service import QueryService
from agent_brain_server.storage.vector_store import SearchResult


class TestRRFFusion:
    """Tests for RRF fusion algorithm in multi-mode queries."""

    @pytest.fixture
    def mock_graph_index_manager(self):
        """Create a mock graph index manager."""
        mock = MagicMock()
        mock.query.return_value = []
        mock.get_status.return_value = MagicMock(
            enabled=True,
            initialized=True,
            entity_count=0,
            relationship_count=0,
            store_type="simple",
            last_updated=None,
        )
        return mock

    @pytest.fixture
    def query_service_with_graph(
        self,
        mock_vector_store,
        mock_embedding_generator,
        mock_bm25_manager,
        mock_graph_index_manager,
    ):
        """Create query service with graph support."""
        return QueryService(
            vector_store=mock_vector_store,
            embedding_generator=mock_embedding_generator,
            bm25_manager=mock_bm25_manager,
            graph_index_manager=mock_graph_index_manager,
        )

    def test_rrf_formula_single_ranking(self):
        """Test RRF formula: score = 1 / (k + rank) for single ranking."""
        k = 60
        # Rank 1 (0-indexed as 0)
        score_rank_1 = 1.0 / (k + 0 + 1)  # 1 / 61 = 0.01639...
        assert abs(score_rank_1 - 1.0 / 61) < 0.0001

        # Rank 2 (0-indexed as 1)
        score_rank_2 = 1.0 / (k + 1 + 1)  # 1 / 62 = 0.01612...
        assert abs(score_rank_2 - 1.0 / 62) < 0.0001

        # Rank 10 (0-indexed as 9)
        score_rank_10 = 1.0 / (k + 9 + 1)  # 1 / 70 = 0.01428...
        assert abs(score_rank_10 - 1.0 / 70) < 0.0001

    def test_rrf_combined_score_multiple_rankings(self):
        """Test RRF combines scores from multiple rankings."""
        k = 60
        # Doc at rank 1 in vector (idx: 0), rank 3 in BM25 (idx: 2)
        vector_contribution = 1.0 / (k + 0 + 1)  # 1/61
        bm25_contribution = 1.0 / (k + 2 + 1)  # 1/63
        combined = vector_contribution + bm25_contribution

        # Combined should be greater than either individual
        assert combined > vector_contribution
        assert combined > bm25_contribution
        # Expected: 1/61 + 1/63 = 0.01639 + 0.01587 = 0.03226
        assert abs(combined - (1 / 61 + 1 / 63)) < 0.0001

    @pytest.mark.asyncio
    async def test_multi_mode_requires_graph_enabled(
        self,
        query_service_with_graph,
        mock_vector_store,
        mock_bm25_manager,
    ):
        """Test multi-mode works when graph is disabled (vector+BM25 only)."""
        mock_vector_store.is_initialized = True
        mock_bm25_manager.is_initialized = True
        mock_vector_store.get_count = AsyncMock(return_value=10)

        mock_vector_store.similarity_search = AsyncMock(
            return_value=[
                SearchResult(
                    text="Vector result",
                    metadata={"source": "v.md", "source_type": "doc"},
                    score=0.9,
                    chunk_id="v1",
                )
            ]
        )

        mock_bm25_manager.search_with_filters = AsyncMock(return_value=[])
        mock_bm25_manager.get_retriever = MagicMock(
            return_value=MagicMock(aretrieve=AsyncMock(return_value=[]))
        )

        # Patch settings to disable graph
        with patch(
            "agent_brain_server.services.query_service.settings"
        ) as mock_settings:
            mock_settings.ENABLE_GRAPH_INDEX = False
            mock_settings.GRAPH_RRF_K = 60

            request = QueryRequest(query="test", mode=QueryMode.MULTI)
            response = await query_service_with_graph.execute_query(request)

            # Should still work with vector results only
            assert response.total_results >= 1

    @pytest.mark.asyncio
    async def test_multi_mode_combines_vector_and_bm25(
        self,
        query_service_with_graph,
        mock_vector_store,
        mock_bm25_manager,
        mock_embedding_generator,
    ):
        """Test multi-mode combines vector and BM25 results using RRF."""
        mock_vector_store.is_initialized = True
        mock_bm25_manager.is_initialized = True
        mock_vector_store.get_count = AsyncMock(return_value=10)

        # Vector result
        mock_vector_store.similarity_search = AsyncMock(
            return_value=[
                SearchResult(
                    text="Vector only result",
                    metadata={"source": "vector.md", "source_type": "doc"},
                    score=0.95,
                    chunk_id="v1",
                ),
                SearchResult(
                    text="Shared result",
                    metadata={"source": "shared.md", "source_type": "doc"},
                    score=0.85,
                    chunk_id="shared",
                ),
            ]
        )

        # BM25 result - shared appears here too
        mock_bm25_node = MagicMock()
        mock_bm25_node.node.get_content.return_value = "BM25 only result"
        mock_bm25_node.node.metadata = {"source": "bm25.md", "source_type": "doc"}
        mock_bm25_node.node.node_id = "b1"
        mock_bm25_node.score = 0.9

        mock_shared_node = MagicMock()
        mock_shared_node.node.get_content.return_value = "Shared result"
        mock_shared_node.node.metadata = {"source": "shared.md", "source_type": "doc"}
        mock_shared_node.node.node_id = "shared"
        mock_shared_node.score = 0.8

        mock_retriever = MagicMock()
        mock_retriever.aretrieve = AsyncMock(
            return_value=[mock_bm25_node, mock_shared_node]
        )
        mock_bm25_manager.get_retriever = MagicMock(return_value=mock_retriever)
        # Also mock search_with_filters for ChromaBackend path (Phase 5)
        mock_bm25_manager.search_with_filters = AsyncMock(
            return_value=[mock_bm25_node, mock_shared_node]
        )

        with patch(
            "agent_brain_server.services.query_service.settings"
        ) as mock_settings:
            mock_settings.ENABLE_GRAPH_INDEX = False
            mock_settings.GRAPH_RRF_K = 60

            request = QueryRequest(query="test", mode=QueryMode.MULTI, top_k=10)
            response = await query_service_with_graph.execute_query(request)

            # Should have results from both sources
            assert response.total_results == 3  # v1, shared, b1

            # Find the shared result - it should have highest RRF score
            # because it appears in both rankings
            shared_results = [r for r in response.results if r.chunk_id == "shared"]
            assert len(shared_results) == 1

            # Shared should have highest score (appears in both rankings)
            shared_result = shared_results[0]
            # RRF score from rank 2 in vector (1/62) + rank 2 in BM25 (1/62)
            # Other results only appear in one ranking
            vector_only = [r for r in response.results if r.chunk_id == "v1"]
            if vector_only:
                # Shared should have higher score than vector_only (rank 1 only)
                # shared: 1/62 + 1/62 = 0.0323
                # v1: 1/61 = 0.0164
                assert shared_result.score > vector_only[0].score

    @pytest.mark.asyncio
    async def test_multi_mode_includes_graph_results(
        self,
        query_service_with_graph,
        mock_vector_store,
        mock_bm25_manager,
        mock_graph_index_manager,
    ):
        """Test multi-mode includes graph results when graph is enabled."""
        mock_vector_store.is_initialized = True
        mock_bm25_manager.is_initialized = True
        mock_vector_store.get_count = AsyncMock(return_value=10)

        # Setup vector results
        mock_vector_store.similarity_search = AsyncMock(
            return_value=[
                SearchResult(
                    text="Vector result",
                    metadata={"source": "v.md", "source_type": "doc"},
                    score=0.9,
                    chunk_id="v1",
                )
            ]
        )

        # Setup BM25 results
        mock_retriever = MagicMock()
        mock_retriever.aretrieve = AsyncMock(return_value=[])
        mock_bm25_manager.get_retriever = MagicMock(return_value=mock_retriever)

        # Setup graph results
        mock_graph_index_manager.query.return_value = [
            {
                "entity": "FastAPI",
                "subject": "FastAPI",
                "predicate": "uses",
                "object": "Pydantic",
                "source_chunk_id": "g1",
                "relationship_path": "FastAPI -> uses -> Pydantic",
                "graph_score": 0.85,
            }
        ]

        # Mock get_by_id for graph result lookup
        mock_vector_store.get_by_id = AsyncMock(
            return_value={
                "text": "Graph related document",
                "metadata": {"source": "graph.md", "source_type": "doc"},
            }
        )

        with patch(
            "agent_brain_server.services.query_service.settings"
        ) as mock_settings:
            mock_settings.ENABLE_GRAPH_INDEX = True
            mock_settings.GRAPH_RRF_K = 60

            request = QueryRequest(query="test", mode=QueryMode.MULTI, top_k=10)
            response = await query_service_with_graph.execute_query(request)

            # Should have results from vector and graph
            assert response.total_results >= 2
            chunk_ids = [r.chunk_id for r in response.results]
            assert "v1" in chunk_ids
            assert "g1" in chunk_ids

    @pytest.mark.asyncio
    async def test_rrf_preserves_graph_metadata(
        self,
        query_service_with_graph,
        mock_vector_store,
        mock_bm25_manager,
        mock_graph_index_manager,
    ):
        """Test RRF fusion preserves graph-specific metadata fields."""
        mock_vector_store.is_initialized = True
        mock_bm25_manager.is_initialized = True
        mock_vector_store.get_count = AsyncMock(return_value=10)

        mock_vector_store.similarity_search = AsyncMock(return_value=[])
        mock_retriever = MagicMock()
        mock_retriever.aretrieve = AsyncMock(return_value=[])
        mock_bm25_manager.get_retriever = MagicMock(return_value=mock_retriever)

        # Graph result with entities and relationships
        mock_graph_index_manager.query.return_value = [
            {
                "entity": "QueryService",
                "subject": "QueryService",
                "predicate": "imports",
                "object": "VectorStore",
                "source_chunk_id": "code1",
                "relationship_path": "QueryService -> imports -> VectorStore",
                "graph_score": 0.9,
            }
        ]

        mock_vector_store.get_by_id = AsyncMock(
            return_value={
                "text": "class QueryService:",
                "metadata": {"source": "query_service.py", "source_type": "code"},
            }
        )

        with patch(
            "agent_brain_server.services.query_service.settings"
        ) as mock_settings:
            mock_settings.ENABLE_GRAPH_INDEX = True
            mock_settings.GRAPH_RRF_K = 60

            request = QueryRequest(query="QueryService imports", mode=QueryMode.MULTI)
            response = await query_service_with_graph.execute_query(request)

            assert response.total_results >= 1
            graph_result = response.results[0]

            # Should preserve graph-specific fields
            assert graph_result.graph_score == 0.9
            assert graph_result.related_entities is not None
            assert "QueryService" in graph_result.related_entities
            assert "VectorStore" in graph_result.related_entities

    @pytest.mark.asyncio
    async def test_rrf_k_parameter_affects_scores(
        self,
        query_service_with_graph,
        mock_vector_store,
        mock_bm25_manager,
    ):
        """Test that GRAPH_RRF_K parameter affects score distribution."""
        mock_vector_store.is_initialized = True
        mock_bm25_manager.is_initialized = True
        mock_vector_store.get_count = AsyncMock(return_value=10)

        mock_vector_store.similarity_search = AsyncMock(
            return_value=[
                SearchResult(
                    text="Result",
                    metadata={"source": "test.md", "source_type": "doc"},
                    score=0.9,
                    chunk_id="r1",
                )
            ]
        )

        mock_retriever = MagicMock()
        mock_retriever.aretrieve = AsyncMock(return_value=[])
        mock_bm25_manager.get_retriever = MagicMock(return_value=mock_retriever)

        # Test with k=60 (default)
        with patch(
            "agent_brain_server.services.query_service.settings"
        ) as mock_settings:
            mock_settings.ENABLE_GRAPH_INDEX = False
            mock_settings.GRAPH_RRF_K = 60

            request = QueryRequest(query="test", mode=QueryMode.MULTI)
            response_k60 = await query_service_with_graph.execute_query(request)

        # Reset singleton for next test
        query_service_k30 = QueryService(
            vector_store=mock_vector_store,
            embedding_generator=query_service_with_graph.embedding_generator,
            bm25_manager=mock_bm25_manager,
            graph_index_manager=query_service_with_graph.graph_index_manager,
        )

        # Test with k=30 (different value)
        with patch(
            "agent_brain_server.services.query_service.settings"
        ) as mock_settings:
            mock_settings.ENABLE_GRAPH_INDEX = False
            mock_settings.GRAPH_RRF_K = 30

            request = QueryRequest(query="test", mode=QueryMode.MULTI)
            response_k30 = await query_service_k30.execute_query(request)

        # Lower k should produce higher RRF scores
        # k=60: score = 1/61 = 0.0164
        # k=30: score = 1/31 = 0.0323
        assert response_k30.results[0].score > response_k60.results[0].score

    @pytest.mark.asyncio
    async def test_multi_mode_respects_top_k(
        self,
        query_service_with_graph,
        mock_vector_store,
        mock_bm25_manager,
    ):
        """Test multi-mode respects top_k limit."""
        mock_vector_store.is_initialized = True
        mock_bm25_manager.is_initialized = True
        mock_vector_store.get_count = AsyncMock(return_value=100)

        # Return many vector results
        mock_vector_store.similarity_search = AsyncMock(
            return_value=[
                SearchResult(
                    text=f"Result {i}",
                    metadata={"source": f"doc{i}.md", "source_type": "doc"},
                    score=0.9 - i * 0.01,
                    chunk_id=f"v{i}",
                )
                for i in range(10)
            ]
        )

        mock_retriever = MagicMock()
        mock_retriever.aretrieve = AsyncMock(return_value=[])
        mock_bm25_manager.get_retriever = MagicMock(return_value=mock_retriever)

        with patch(
            "agent_brain_server.services.query_service.settings"
        ) as mock_settings:
            mock_settings.ENABLE_GRAPH_INDEX = False
            mock_settings.GRAPH_RRF_K = 60

            request = QueryRequest(query="test", mode=QueryMode.MULTI, top_k=3)
            response = await query_service_with_graph.execute_query(request)

            # Should respect top_k limit
            assert len(response.results) == 3


class TestRRFEdgeCases:
    """Edge case tests for RRF fusion."""

    @pytest.fixture
    def mock_graph_index_manager(self):
        """Create a mock graph index manager."""
        mock = MagicMock()
        mock.query.return_value = []
        return mock

    @pytest.mark.asyncio
    async def test_multi_mode_empty_results(
        self,
        mock_vector_store,
        mock_embedding_generator,
        mock_bm25_manager,
        mock_graph_index_manager,
    ):
        """Test multi-mode handles empty results gracefully."""
        service = QueryService(
            vector_store=mock_vector_store,
            embedding_generator=mock_embedding_generator,
            bm25_manager=mock_bm25_manager,
            graph_index_manager=mock_graph_index_manager,
        )

        mock_vector_store.is_initialized = True
        mock_bm25_manager.is_initialized = True
        mock_vector_store.get_count = AsyncMock(return_value=0)

        mock_vector_store.similarity_search = AsyncMock(return_value=[])
        mock_retriever = MagicMock()
        mock_retriever.aretrieve = AsyncMock(return_value=[])
        mock_bm25_manager.get_retriever = MagicMock(return_value=mock_retriever)

        with patch(
            "agent_brain_server.services.query_service.settings"
        ) as mock_settings:
            mock_settings.ENABLE_GRAPH_INDEX = False
            mock_settings.GRAPH_RRF_K = 60

            request = QueryRequest(query="test", mode=QueryMode.MULTI)
            response = await service.execute_query(request)

            assert response.total_results == 0
            assert len(response.results) == 0

    @pytest.mark.asyncio
    async def test_multi_mode_single_source(
        self,
        mock_vector_store,
        mock_embedding_generator,
        mock_bm25_manager,
        mock_graph_index_manager,
    ):
        """Test multi-mode works with results from only one source."""
        service = QueryService(
            vector_store=mock_vector_store,
            embedding_generator=mock_embedding_generator,
            bm25_manager=mock_bm25_manager,
            graph_index_manager=mock_graph_index_manager,
        )

        mock_vector_store.is_initialized = True
        mock_bm25_manager.is_initialized = True
        mock_vector_store.get_count = AsyncMock(return_value=10)

        # Only vector returns results
        mock_vector_store.similarity_search = AsyncMock(
            return_value=[
                SearchResult(
                    text="Vector result",
                    metadata={"source": "v.md", "source_type": "doc"},
                    score=0.9,
                    chunk_id="v1",
                )
            ]
        )

        mock_retriever = MagicMock()
        mock_retriever.aretrieve = AsyncMock(return_value=[])
        mock_bm25_manager.get_retriever = MagicMock(return_value=mock_retriever)

        with patch(
            "agent_brain_server.services.query_service.settings"
        ) as mock_settings:
            mock_settings.ENABLE_GRAPH_INDEX = False
            mock_settings.GRAPH_RRF_K = 60

            request = QueryRequest(query="test", mode=QueryMode.MULTI)
            response = await service.execute_query(request)

            assert response.total_results == 1
            # Score should be RRF score from single ranking
            # rank 1 (0-indexed: 0) with k=60: 1/61
            expected_score = 1.0 / 61
            assert abs(response.results[0].score - expected_score) < 0.0001

    @pytest.mark.asyncio
    async def test_multi_mode_duplicate_chunk_ids(
        self,
        mock_vector_store,
        mock_embedding_generator,
        mock_bm25_manager,
        mock_graph_index_manager,
    ):
        """Test RRF correctly handles same document appearing in multiple rankings."""
        service = QueryService(
            vector_store=mock_vector_store,
            embedding_generator=mock_embedding_generator,
            bm25_manager=mock_bm25_manager,
            graph_index_manager=mock_graph_index_manager,
        )

        mock_vector_store.is_initialized = True
        mock_bm25_manager.is_initialized = True
        mock_vector_store.get_count = AsyncMock(return_value=10)

        # Same chunk appears in both results
        mock_vector_store.similarity_search = AsyncMock(
            return_value=[
                SearchResult(
                    text="Shared result",
                    metadata={"source": "shared.md", "source_type": "doc"},
                    score=0.9,
                    chunk_id="shared_chunk",
                )
            ]
        )

        mock_bm25_node = MagicMock()
        mock_bm25_node.node.get_content.return_value = "Shared result"
        mock_bm25_node.node.metadata = {"source": "shared.md", "source_type": "doc"}
        mock_bm25_node.node.node_id = "shared_chunk"
        mock_bm25_node.score = 0.85

        mock_retriever = MagicMock()
        mock_retriever.aretrieve = AsyncMock(return_value=[mock_bm25_node])
        mock_bm25_manager.get_retriever = MagicMock(return_value=mock_retriever)

        with patch(
            "agent_brain_server.services.query_service.settings"
        ) as mock_settings:
            mock_settings.ENABLE_GRAPH_INDEX = False
            mock_settings.GRAPH_RRF_K = 60

            request = QueryRequest(query="test", mode=QueryMode.MULTI)
            response = await service.execute_query(request)

            # Should deduplicate and combine scores
            assert response.total_results == 1
            assert response.results[0].chunk_id == "shared_chunk"

            # Combined RRF score: 1/61 (vector rank 1) + 1/61 (BM25 rank 1)
            expected_score = 1.0 / 61 + 1.0 / 61
            assert abs(response.results[0].score - expected_score) < 0.0001
