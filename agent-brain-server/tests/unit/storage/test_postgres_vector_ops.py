"""Unit tests for pgvector VectorOps."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from agent_brain_server.storage.postgres.config import PostgresConfig
from agent_brain_server.storage.postgres.connection import (
    PostgresConnectionManager,
)
from agent_brain_server.storage.postgres.vector_ops import (
    VectorOps,
    _normalize_score,
)
from agent_brain_server.storage.protocol import StorageError


def _make_mock_manager() -> PostgresConnectionManager:
    """Create a connection manager with a fully mocked engine."""
    config = PostgresConfig()
    manager = PostgresConnectionManager(config)

    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock()

    mock_engine = MagicMock()
    mock_engine.begin = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_conn),
            __aexit__=AsyncMock(return_value=False),
        )
    )
    mock_engine.connect = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_conn),
            __aexit__=AsyncMock(return_value=False),
        )
    )
    manager._engine = mock_engine
    return manager


@pytest.fixture
def manager() -> PostgresConnectionManager:
    """Create mocked connection manager."""
    return _make_mock_manager()


@pytest.fixture
def vector_ops(manager: PostgresConnectionManager) -> VectorOps:
    """Create VectorOps with mocked connection manager."""
    return VectorOps(manager)


def _get_conn(manager: PostgresConnectionManager) -> AsyncMock:
    """Get the mock connection from the manager's engine."""
    engine = manager._engine
    assert engine is not None
    # Use begin for write, connect for read
    connect_cm = engine.connect.return_value  # type: ignore[union-attr]
    return connect_cm.__aenter__.return_value  # type: ignore[return-value]


def _get_begin_conn(manager: PostgresConnectionManager) -> AsyncMock:
    """Get the mock connection from begin() context manager."""
    engine = manager._engine
    assert engine is not None
    begin_cm = engine.begin.return_value  # type: ignore[union-attr]
    return begin_cm.__aenter__.return_value  # type: ignore[return-value]


class TestUpsertEmbeddings:
    """Tests for upsert_embeddings() method."""

    async def test_executes_update_sql(
        self,
        vector_ops: VectorOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """upsert_embeddings() executes UPDATE SQL."""
        await vector_ops.upsert_embeddings(
            chunk_id="chunk-1",
            embedding=[0.1, 0.2, 0.3],
        )

        conn = _get_begin_conn(manager)
        conn.execute.assert_awaited_once()
        call_args = conn.execute.call_args
        sql_text = str(call_args[0][0].text)
        assert "UPDATE documents" in sql_text
        assert "embedding" in sql_text


class TestVectorSearch:
    """Tests for vector_search() method."""

    async def test_cosine_uses_correct_operator(
        self,
        vector_ops: VectorOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """vector_search() with cosine uses <=> operator."""
        conn = _get_conn(manager)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        conn.execute = AsyncMock(return_value=mock_result)

        await vector_ops.vector_search(
            query_embedding=[0.1, 0.2],
            top_k=5,
            similarity_threshold=0.0,
            distance_metric="cosine",
        )

        call_args = conn.execute.call_args
        sql_text = str(call_args[0][0].text)
        assert "<=>" in sql_text

    async def test_l2_uses_correct_operator(
        self,
        vector_ops: VectorOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """vector_search() with l2 uses <-> operator."""
        conn = _get_conn(manager)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        conn.execute = AsyncMock(return_value=mock_result)

        await vector_ops.vector_search(
            query_embedding=[0.1, 0.2],
            top_k=5,
            similarity_threshold=0.0,
            distance_metric="l2",
        )

        call_args = conn.execute.call_args
        sql_text = str(call_args[0][0].text)
        assert "<->" in sql_text

    async def test_inner_product_uses_correct_operator(
        self,
        vector_ops: VectorOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """vector_search() with inner_product uses <#> operator."""
        conn = _get_conn(manager)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        conn.execute = AsyncMock(return_value=mock_result)

        await vector_ops.vector_search(
            query_embedding=[0.1, 0.2],
            top_k=5,
            similarity_threshold=0.0,
            distance_metric="inner_product",
        )

        call_args = conn.execute.call_args
        sql_text = str(call_args[0][0].text)
        assert "<#>" in sql_text

    async def test_returns_empty_when_no_results(
        self,
        vector_ops: VectorOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """vector_search() returns empty list when no results."""
        conn = _get_conn(manager)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        conn.execute = AsyncMock(return_value=mock_result)

        results = await vector_ops.vector_search(
            query_embedding=[0.1, 0.2],
            top_k=5,
            similarity_threshold=0.0,
        )

        assert results == []

    async def test_filters_by_similarity_threshold(
        self,
        vector_ops: VectorOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """vector_search() filters by similarity_threshold."""
        conn = _get_conn(manager)
        mock_result = MagicMock()
        # Cosine distance 0.1 -> score 0.9, distance 0.8 -> score 0.2
        mock_result.fetchall.return_value = [
            ("chunk-1", "text1", {"key": "val"}, 0.1),
            ("chunk-2", "text2", {"key": "val"}, 0.8),
        ]
        conn.execute = AsyncMock(return_value=mock_result)

        results = await vector_ops.vector_search(
            query_embedding=[0.1, 0.2],
            top_k=5,
            similarity_threshold=0.5,
            distance_metric="cosine",
        )

        # Only chunk-1 should pass threshold (score 0.9 >= 0.5)
        assert len(results) == 1
        assert results[0].chunk_id == "chunk-1"

    async def test_applies_metadata_filter(
        self,
        vector_ops: VectorOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """vector_search() applies metadata where filter."""
        conn = _get_conn(manager)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        conn.execute = AsyncMock(return_value=mock_result)

        await vector_ops.vector_search(
            query_embedding=[0.1, 0.2],
            top_k=5,
            similarity_threshold=0.0,
            where={"source_type": "code"},
        )

        call_args = conn.execute.call_args
        sql_text = str(call_args[0][0].text)
        assert "@>" in sql_text
        assert "filter" in sql_text

    async def test_wraps_exceptions_in_storage_error(
        self,
        vector_ops: VectorOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """vector_search() wraps exceptions in StorageError."""
        conn = _get_conn(manager)
        conn.execute = AsyncMock(side_effect=RuntimeError("DB connection lost"))

        with pytest.raises(StorageError, match="Vector search failed"):
            await vector_ops.vector_search(
                query_embedding=[0.1, 0.2],
                top_k=5,
                similarity_threshold=0.0,
            )


class TestNormalizeScore:
    """Tests for _normalize_score() helper."""

    def test_cosine_normalization(self) -> None:
        """Cosine: score = 1 - distance."""
        assert _normalize_score(0.0, "cosine") == 1.0
        assert _normalize_score(0.5, "cosine") == 0.5
        assert _normalize_score(1.0, "cosine") == 0.0

    def test_l2_normalization(self) -> None:
        """L2: score = 1/(1+distance)."""
        assert _normalize_score(0.0, "l2") == 1.0
        assert _normalize_score(1.0, "l2") == 0.5

    def test_inner_product_normalization(self) -> None:
        """Inner product: score = -distance."""
        assert _normalize_score(-0.5, "inner_product") == 0.5
        assert _normalize_score(-1.0, "inner_product") == 1.0
