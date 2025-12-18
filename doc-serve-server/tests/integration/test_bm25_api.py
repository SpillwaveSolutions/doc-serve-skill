"""Integration tests for BM25 retrieval mode."""

from unittest.mock import AsyncMock, MagicMock


class TestBM25QueryEndpoint:
    """Tests for BM25 query mode via API."""

    def test_query_bm25_mode(self, client, mock_vector_store, mock_bm25_manager):
        """Test querying with mode=bm25."""
        # Use a more direct patch on the service instance used by the router
        from doc_serve_server.services.query_service import get_query_service

        service = get_query_service()

        # Manually set the mocks on the singleton service
        service.vector_store = mock_vector_store
        service.bm25_manager = mock_bm25_manager

        mock_vector_store.is_initialized = True
        mock_bm25_manager.is_initialized = True

        # Setup mock retriever results
        retriever_mock = AsyncMock()
        node_mock = MagicMock()
        node_mock.node.get_content.return_value = "Exact keyword match"
        node_mock.node.metadata = {"source": "docs/keyword.md"}
        node_mock.node.node_id = "chunk_bm25"
        node_mock.score = 1.0
        retriever_mock.aretrieve = AsyncMock(return_value=[node_mock])
        mock_bm25_manager.get_retriever.return_value = retriever_mock

        response = client.post(
            "/query/",
            json={
                "query": "specific_keyword",
                "mode": "bm25",
                "top_k": 5,
            },
        )

        assert response.status_code == 200, f"Error: {response.json()}"
        data = response.json()
        assert data["total_results"] == 1
        assert data["results"][0]["bm25_score"] == 1.0
        assert data["results"][0]["text"] == "Exact keyword match"

    def test_query_invalid_mode(self, client):
        """Test querying with an invalid mode."""
        response = client.post(
            "/query/",
            json={
                "query": "test",
                "mode": "invalid_mode",
            },
        )
        assert response.status_code == 422  # Pydantic validation error
