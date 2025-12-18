"""Integration tests for Hybrid retrieval mode."""

from unittest.mock import AsyncMock, MagicMock, patch


class TestHybridQueryEndpoint:
    """Tests for hybrid query mode via API."""

    def test_query_hybrid_mode(
        self, client, mock_vector_store, mock_bm25_manager, mock_embedding_generator
    ):
        """Test querying with mode=hybrid."""
        from doc_serve_server.services.query_service import get_query_service

        service = get_query_service()
        service.vector_store = mock_vector_store
        service.bm25_manager = mock_bm25_manager
        service.embedding_generator = mock_embedding_generator

        mock_vector_store.is_initialized = True
        mock_bm25_manager.is_initialized = True

        # Mock QueryFusionRetriever
        with patch(
            "doc_serve_server.services.query_service.QueryFusionRetriever"
        ) as mock_fusion_cls:
            mock_fusion = AsyncMock()
            node_mock = MagicMock()
            node_mock.node.get_content.return_value = "Hybrid result"
            node_mock.node.metadata = {"source": "docs/hybrid.md"}
            node_mock.node.node_id = "chunk_hybrid"
            node_mock.score = 0.9
            mock_fusion.aretrieve = AsyncMock(return_value=[node_mock])
            mock_fusion_cls.return_value = mock_fusion

            response = client.post(
                "/query/",
                json={
                    "query": "hybrid query",
                    "mode": "hybrid",
                    "alpha": 0.3,
                },
            )

        assert response.status_code == 200, f"Error: {response.json()}"
        data = response.json()
        assert data["total_results"] == 1
        assert data["results"][0]["text"] == "Hybrid result"
        # Check that alpha was passed to QueryFusionRetriever via retriever_weights
        args, kwargs = mock_fusion_cls.call_args
        assert kwargs["retriever_weights"] == [0.3, 0.7]
