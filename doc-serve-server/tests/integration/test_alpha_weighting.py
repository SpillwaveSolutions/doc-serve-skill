"""Integration tests for alpha weighting in hybrid mode."""

from unittest.mock import AsyncMock, MagicMock, patch


class TestAlphaWeighting:
    """Tests for alpha parameter validation and behavior."""

    def test_alpha_validation_bounds(self, client):
        """Test that alpha must be between 0.0 and 1.0."""
        # Valid bounds
        for alpha in [0.0, 0.5, 1.0]:
            # Use mock to avoid actual execution but check validation
            with patch(
                "doc_serve_server.api.routers.query.get_query_service"
            ) as mock_get_service:
                mock_service = MagicMock()
                mock_service.is_ready.return_value = True
                mock_service.execute_query = AsyncMock(
                    return_value=MagicMock(results=[], query_time_ms=0, total_results=0)
                )
                mock_get_service.return_value = mock_service

                response = client.post(
                    "/query/",
                    json={"query": "test", "mode": "hybrid", "alpha": alpha},
                )
                assert response.status_code == 200

        # Invalid bounds
        for alpha in [-0.1, 1.1]:
            response = client.post(
                "/query/",
                json={"query": "test", "mode": "hybrid", "alpha": alpha},
            )
            assert response.status_code == 422

    def test_alpha_passing_to_service(
        self, client, mock_vector_store, mock_bm25_manager, mock_embedding_generator
    ):
        """Test that alpha is passed correctly to the QueryFusionRetriever."""
        from doc_serve_server.services.query_service import get_query_service

        service = get_query_service()
        service.vector_store = mock_vector_store
        service.bm25_manager = mock_bm25_manager
        service.embedding_generator = mock_embedding_generator

        mock_vector_store.is_initialized = True

        mock_bm25_manager.is_initialized = True

        with patch(
            "doc_serve_server.services.query_service.QueryFusionRetriever"
        ) as mock_fusion_cls:
            mock_fusion = AsyncMock()
            mock_fusion.aretrieve = AsyncMock(return_value=[])
            mock_fusion_cls.return_value = mock_fusion

            alpha_value = 0.7
            client.post(
                "/query/",
                json={
                    "query": "alpha test",
                    "mode": "hybrid",
                    "alpha": alpha_value,
                },
            )

            # Verify retriever_weights [alpha, 1-alpha]
            args, kwargs = mock_fusion_cls.call_args
            assert kwargs["retriever_weights"] == [alpha_value, 1.0 - alpha_value]
