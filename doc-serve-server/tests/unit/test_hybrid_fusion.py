"""Unit tests for Hybrid retrieval functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from doc_serve_server.models.query import QueryMode, QueryRequest
from doc_serve_server.services.query_service import QueryService


class TestHybridRetrieval:
    """Tests for hybrid retrieval logic."""

    @pytest.mark.asyncio
    async def test_hybrid_query_logic(
        self, mock_vector_store, mock_bm25_manager, mock_embedding_generator
    ):
        """Test the hybrid query execution logic."""
        # Setup mocks
        service = QueryService(
            vector_store=mock_vector_store,
            embedding_generator=mock_embedding_generator,
            bm25_manager=mock_bm25_manager,
        )

        mock_vector_store.is_initialized = True
        mock_bm25_manager.is_initialized = True

        # Mock vector search results
        mock_vector_store.similarity_search.return_value = [
            MagicMock(
                text="Vector Result",
                chunk_id="v1",
                metadata={"source": "v.md"},
                score=0.8,
            )
        ]

        # Mock BM25 results
        bm25_retriever_mock = AsyncMock()
        node_mock = MagicMock()
        node_mock.node.get_content.return_value = "BM25 Result"
        node_mock.node.metadata = {"source": "b.md"}
        node_mock.node.node_id = "b1"
        node_mock.score = 0.9
        bm25_retriever_mock.aretrieve.return_value = [node_mock]
        mock_bm25_manager.get_retriever.return_value = bm25_retriever_mock

        request = QueryRequest(query="test query", mode=QueryMode.HYBRID, alpha=0.5)

        # We need to mock QueryFusionRetriever.aretrieve because it's hard to unit test
        # the internal fusion without heavy LlamaIndex dependencies setup
        with patch(
            "doc_serve_server.services.query_service.QueryFusionRetriever"
        ) as mock_fusion_cls:
            mock_fusion = AsyncMock()
            fusion_node = MagicMock()
            fusion_node.node.get_content.return_value = "Fused Result"
            fusion_node.node.metadata = {"source": "f.md"}
            fusion_node.node.node_id = "f1"
            fusion_node.score = 0.85
            mock_fusion.aretrieve.return_value = [fusion_node]
            mock_fusion_cls.return_value = mock_fusion

            response = await service.execute_query(request)

            assert response.total_results == 1
            assert response.results[0].text == "Fused Result"
            mock_fusion_cls.assert_called_once()

            # Verify alpha was passed correctly to retriever_weights
            args, kwargs = mock_fusion_cls.call_args
            assert kwargs["retriever_weights"] == [0.5, 0.5]
            assert kwargs["mode"].value == "relative_score"
