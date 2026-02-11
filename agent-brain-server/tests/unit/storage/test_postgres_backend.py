"""Unit tests for PostgresBackend."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent_brain_server.providers.exceptions import ProviderMismatchError
from agent_brain_server.storage.postgres.backend import PostgresBackend
from agent_brain_server.storage.postgres.config import PostgresConfig
from agent_brain_server.storage.protocol import (
    EmbeddingMetadata,
    SearchResult,
    StorageError,
)


@pytest.fixture
def config() -> PostgresConfig:
    """Create a test PostgresConfig."""
    return PostgresConfig()


@pytest.fixture
def backend(config: PostgresConfig) -> PostgresBackend:
    """Create a PostgresBackend with mocked internals."""
    b = PostgresBackend(config)

    # Mock all internal components
    b.connection_manager = MagicMock()
    b.connection_manager.initialize_with_retry = AsyncMock()
    b.connection_manager.close = AsyncMock()
    b.connection_manager.engine = MagicMock()

    b.vector_ops = MagicMock()
    b.vector_ops.vector_search = AsyncMock(return_value=[])
    b.vector_ops.upsert_embeddings = AsyncMock()

    b.keyword_ops = MagicMock()
    b.keyword_ops.keyword_search = AsyncMock(return_value=[])
    b.keyword_ops.upsert_with_tsvector = AsyncMock()

    return b


class TestConstructor:
    """Tests for PostgresBackend construction."""

    def test_creates_all_components(self, config: PostgresConfig) -> None:
        """Constructor creates all internal components."""
        b = PostgresBackend(config)
        assert b.connection_manager is not None
        assert b.vector_ops is not None
        assert b.keyword_ops is not None
        assert b.config is config


class TestIsInitialized:
    """Tests for is_initialized property."""

    def test_false_before_initialize(self, backend: PostgresBackend) -> None:
        """is_initialized returns False before initialize."""
        assert backend.is_initialized is False

    def test_true_after_initialize(self, backend: PostgresBackend) -> None:
        """is_initialized returns True after _initialized set."""
        backend._initialized = True
        assert backend.is_initialized is True


class TestInitialize:
    """Tests for initialize() method."""

    @patch("agent_brain_server.storage.postgres.backend.ProviderRegistry")
    @patch("agent_brain_server.storage.postgres.backend.load_provider_settings")
    async def test_calls_connection_manager(
        self,
        mock_settings: MagicMock,
        mock_registry: MagicMock,
        backend: PostgresBackend,
    ) -> None:
        """initialize() calls connection_manager.initialize_with_retry()."""
        mock_provider = MagicMock()
        mock_provider.get_dimensions.return_value = 3072
        mock_registry.get_embedding_provider.return_value = mock_provider

        # Mock schema manager to be created
        with patch(
            "agent_brain_server.storage.postgres.backend." "PostgresSchemaManager"
        ) as mock_schema_cls:
            mock_sm = MagicMock()
            mock_sm.create_schema = AsyncMock()
            mock_sm.validate_dimensions = AsyncMock()
            mock_schema_cls.return_value = mock_sm

            await backend.initialize()

        backend.connection_manager.initialize_with_retry.assert_awaited_once()

    @patch("agent_brain_server.storage.postgres.backend.ProviderRegistry")
    @patch("agent_brain_server.storage.postgres.backend.load_provider_settings")
    async def test_creates_schema(
        self,
        mock_settings: MagicMock,
        mock_registry: MagicMock,
        backend: PostgresBackend,
    ) -> None:
        """initialize() calls schema_manager.create_schema()."""
        mock_provider = MagicMock()
        mock_provider.get_dimensions.return_value = 3072
        mock_registry.get_embedding_provider.return_value = mock_provider

        with patch(
            "agent_brain_server.storage.postgres.backend." "PostgresSchemaManager"
        ) as mock_schema_cls:
            mock_sm = MagicMock()
            mock_sm.create_schema = AsyncMock()
            mock_sm.validate_dimensions = AsyncMock()
            mock_schema_cls.return_value = mock_sm

            await backend.initialize()

            mock_sm.create_schema.assert_awaited_once()

    @patch("agent_brain_server.storage.postgres.backend.ProviderRegistry")
    @patch("agent_brain_server.storage.postgres.backend.load_provider_settings")
    async def test_validates_dimensions(
        self,
        mock_settings: MagicMock,
        mock_registry: MagicMock,
        backend: PostgresBackend,
    ) -> None:
        """initialize() calls schema_manager.validate_dimensions()."""
        mock_provider = MagicMock()
        mock_provider.get_dimensions.return_value = 3072
        mock_registry.get_embedding_provider.return_value = mock_provider

        with patch(
            "agent_brain_server.storage.postgres.backend." "PostgresSchemaManager"
        ) as mock_schema_cls:
            mock_sm = MagicMock()
            mock_sm.create_schema = AsyncMock()
            mock_sm.validate_dimensions = AsyncMock()
            mock_schema_cls.return_value = mock_sm

            await backend.initialize()

            mock_sm.validate_dimensions.assert_awaited_once()

    async def test_raises_storage_error_on_failure(
        self,
        backend: PostgresBackend,
    ) -> None:
        """initialize() raises StorageError on connection failure."""
        backend.connection_manager.initialize_with_retry = AsyncMock(
            side_effect=StorageError("Connection failed", backend="postgres")
        )

        with pytest.raises(StorageError, match="Connection failed"):
            await backend.initialize()


class TestUpsertDocuments:
    """Tests for upsert_documents() method."""

    async def test_calls_keyword_and_vector_ops(self, backend: PostgresBackend) -> None:
        """upsert_documents() calls keyword_ops and vector_ops."""
        count = await backend.upsert_documents(
            ids=["c1", "c2"],
            embeddings=[[0.1, 0.2], [0.3, 0.4]],
            documents=["text1", "text2"],
            metadatas=[{"k": "v1"}, {"k": "v2"}],
        )

        assert count == 2
        assert backend.keyword_ops.upsert_with_tsvector.await_count == 2
        assert backend.vector_ops.upsert_embeddings.await_count == 2

    async def test_validates_list_lengths(self, backend: PostgresBackend) -> None:
        """upsert_documents() validates list lengths match."""
        with pytest.raises(ValueError, match="lengths must match"):
            await backend.upsert_documents(
                ids=["c1"],
                embeddings=[[0.1, 0.2], [0.3, 0.4]],
                documents=["text1"],
                metadatas=[{"k": "v1"}],
            )

    async def test_returns_correct_count(self, backend: PostgresBackend) -> None:
        """upsert_documents() returns correct count."""
        count = await backend.upsert_documents(
            ids=["c1", "c2", "c3"],
            embeddings=[[0.1], [0.2], [0.3]],
            documents=["t1", "t2", "t3"],
            metadatas=[{}, {}, {}],
        )
        assert count == 3


class TestVectorSearch:
    """Tests for vector_search() method."""

    async def test_delegates_to_vector_ops(self, backend: PostgresBackend) -> None:
        """vector_search() delegates to vector_ops."""
        expected = [
            SearchResult(
                text="t",
                metadata={},
                score=0.9,
                chunk_id="c1",
            )
        ]
        backend.vector_ops.vector_search = AsyncMock(return_value=expected)

        results = await backend.vector_search(
            query_embedding=[0.1, 0.2],
            top_k=5,
            similarity_threshold=0.0,
        )

        assert results == expected


class TestKeywordSearch:
    """Tests for keyword_search() method."""

    async def test_delegates_to_keyword_ops(self, backend: PostgresBackend) -> None:
        """keyword_search() delegates to keyword_ops."""
        expected = [
            SearchResult(
                text="t",
                metadata={},
                score=0.8,
                chunk_id="c1",
            )
        ]
        backend.keyword_ops.keyword_search = AsyncMock(return_value=expected)

        results = await backend.keyword_search(query="test", top_k=5)

        assert results == expected


class TestHybridSearchWithRrf:
    """Tests for hybrid_search_with_rrf() method."""

    async def test_combines_vector_and_keyword_results(
        self, backend: PostgresBackend
    ) -> None:
        """hybrid_search_with_rrf() combines both result sets."""
        vec_results = [
            SearchResult(text="t1", metadata={}, score=0.9, chunk_id="c1"),
            SearchResult(text="t2", metadata={}, score=0.8, chunk_id="c2"),
            SearchResult(text="t3", metadata={}, score=0.7, chunk_id="c3"),
        ]
        kw_results = [
            SearchResult(text="t2", metadata={}, score=1.0, chunk_id="c2"),
            SearchResult(text="t4", metadata={}, score=0.8, chunk_id="c4"),
            SearchResult(text="t5", metadata={}, score=0.6, chunk_id="c5"),
        ]
        backend.vector_ops.vector_search = AsyncMock(return_value=vec_results)
        backend.keyword_ops.keyword_search = AsyncMock(return_value=kw_results)

        results = await backend.hybrid_search_with_rrf(
            query="test",
            query_embedding=[0.1, 0.2],
            top_k=3,
        )

        # c2 should score highest (appears in both)
        assert len(results) <= 3
        assert results[0].chunk_id == "c2"

    async def test_rrf_scores_normalized_to_0_1(self, backend: PostgresBackend) -> None:
        """hybrid_search_with_rrf() normalizes RRF scores to 0-1."""
        vec_results = [
            SearchResult(text="t1", metadata={}, score=0.9, chunk_id="c1"),
        ]
        kw_results = [
            SearchResult(text="t2", metadata={}, score=1.0, chunk_id="c2"),
        ]
        backend.vector_ops.vector_search = AsyncMock(return_value=vec_results)
        backend.keyword_ops.keyword_search = AsyncMock(return_value=kw_results)

        results = await backend.hybrid_search_with_rrf(
            query="test",
            query_embedding=[0.1, 0.2],
            top_k=5,
        )

        # Top score should be normalized to 1.0
        assert results[0].score == 1.0
        for r in results:
            assert 0.0 <= r.score <= 1.0


class TestGetCount:
    """Tests for get_count() method."""

    async def test_executes_count_query(self, backend: PostgresBackend) -> None:
        """get_count() executes COUNT query."""
        # Set up mock engine
        mock_conn = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (42,)
        mock_conn.execute = AsyncMock(return_value=mock_result)
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        backend.connection_manager.engine = MagicMock()
        backend.connection_manager.engine.connect = MagicMock(return_value=mock_conn)

        count = await backend.get_count()
        assert count == 42


class TestGetById:
    """Tests for get_by_id() method."""

    async def test_returns_document_dict(self, backend: PostgresBackend) -> None:
        """get_by_id() returns document dict."""
        mock_conn = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = ("doc text", {"key": "val"})
        mock_conn.execute = AsyncMock(return_value=mock_result)
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        backend.connection_manager.engine = MagicMock()
        backend.connection_manager.engine.connect = MagicMock(return_value=mock_conn)

        result = await backend.get_by_id("chunk-1")
        assert result is not None
        assert result["text"] == "doc text"
        assert result["metadata"] == {"key": "val"}

    async def test_returns_none_when_not_found(self, backend: PostgresBackend) -> None:
        """get_by_id() returns None when not found."""
        mock_conn = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_conn.execute = AsyncMock(return_value=mock_result)
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        backend.connection_manager.engine = MagicMock()
        backend.connection_manager.engine.connect = MagicMock(return_value=mock_conn)

        result = await backend.get_by_id("nonexistent")
        assert result is None


class TestReset:
    """Tests for reset() method."""

    async def test_drops_and_recreates_tables(self, backend: PostgresBackend) -> None:
        """reset() drops and recreates tables."""
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        backend.connection_manager.engine = MagicMock()
        backend.connection_manager.engine.begin = MagicMock(return_value=mock_conn)

        mock_sm = MagicMock()
        mock_sm.create_schema = AsyncMock()
        backend.schema_manager = mock_sm

        await backend.reset()

        # Should have executed DROP TABLE statements
        assert mock_conn.execute.await_count == 2
        mock_sm.create_schema.assert_awaited_once()


class TestEmbeddingMetadata:
    """Tests for get/set embedding metadata."""

    async def test_get_delegates_to_schema_manager(
        self, backend: PostgresBackend
    ) -> None:
        """get_embedding_metadata() delegates to schema_manager."""
        mock_sm = MagicMock()
        mock_sm.get_embedding_metadata = AsyncMock(
            return_value={"provider": "openai", "model": "m", "dimensions": 3072}
        )
        backend.schema_manager = mock_sm

        result = await backend.get_embedding_metadata()

        assert result is not None
        assert result.provider == "openai"
        assert result.dimensions == 3072

    async def test_set_delegates_to_schema_manager(
        self, backend: PostgresBackend
    ) -> None:
        """set_embedding_metadata() delegates to schema_manager."""
        mock_sm = MagicMock()
        mock_sm.store_embedding_metadata = AsyncMock()
        backend.schema_manager = mock_sm

        await backend.set_embedding_metadata("openai", "model", 3072)

        mock_sm.store_embedding_metadata.assert_awaited_once_with(
            provider="openai",
            model="model",
            dimensions=3072,
        )


class TestValidateEmbeddingCompatibility:
    """Tests for validate_embedding_compatibility()."""

    def test_passes_with_no_stored_metadata(self, backend: PostgresBackend) -> None:
        """Passes when no stored metadata."""
        backend.validate_embedding_compatibility(
            provider="openai",
            model="m",
            dimensions=3072,
            stored_metadata=None,
        )

    def test_raises_on_dimension_mismatch(self, backend: PostgresBackend) -> None:
        """Raises ProviderMismatchError on dimension mismatch."""
        stored = EmbeddingMetadata(provider="openai", model="m1", dimensions=1536)

        with pytest.raises(ProviderMismatchError):
            backend.validate_embedding_compatibility(
                provider="openai",
                model="m2",
                dimensions=3072,
                stored_metadata=stored,
            )


class TestClose:
    """Tests for close() method."""

    async def test_calls_connection_manager_close(
        self, backend: PostgresBackend
    ) -> None:
        """close() calls connection_manager.close()."""
        await backend.close()

        backend.connection_manager.close.assert_awaited_once()
        assert backend.is_initialized is False
