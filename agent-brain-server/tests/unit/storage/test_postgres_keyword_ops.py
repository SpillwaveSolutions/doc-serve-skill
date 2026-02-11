"""Unit tests for tsvector KeywordOps."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from agent_brain_server.storage.postgres.config import PostgresConfig
from agent_brain_server.storage.postgres.connection import (
    PostgresConnectionManager,
)
from agent_brain_server.storage.postgres.keyword_ops import KeywordOps
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
def keyword_ops(manager: PostgresConnectionManager) -> KeywordOps:
    """Create KeywordOps with mocked connection manager."""
    return KeywordOps(manager, language="english")


def _get_conn(manager: PostgresConnectionManager) -> AsyncMock:
    """Get the mock connection from connect() context manager."""
    engine = manager._engine
    assert engine is not None
    connect_cm = engine.connect.return_value  # type: ignore[union-attr]
    return connect_cm.__aenter__.return_value  # type: ignore[return-value]


def _get_begin_conn(manager: PostgresConnectionManager) -> AsyncMock:
    """Get the mock connection from begin() context manager."""
    engine = manager._engine
    assert engine is not None
    begin_cm = engine.begin.return_value  # type: ignore[union-attr]
    return begin_cm.__aenter__.return_value  # type: ignore[return-value]


class TestUpsertWithTsvector:
    """Tests for upsert_with_tsvector() method."""

    async def test_executes_insert_with_setweight(
        self,
        keyword_ops: KeywordOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """upsert_with_tsvector() executes INSERT with setweight SQL."""
        await keyword_ops.upsert_with_tsvector(
            chunk_id="chunk-1",
            document_text="Hello world",
            metadata={"filename": "test.py", "summary": "A test file"},
        )

        conn = _get_begin_conn(manager)
        conn.execute.assert_awaited_once()
        call_args = conn.execute.call_args
        sql_text = str(call_args[0][0].text)
        assert "INSERT INTO documents" in sql_text
        assert "setweight" in sql_text

    async def test_extracts_title_from_filename(
        self,
        keyword_ops: KeywordOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """upsert_with_tsvector() extracts title from metadata.filename."""
        await keyword_ops.upsert_with_tsvector(
            chunk_id="chunk-1",
            document_text="content",
            metadata={"filename": "myfile.py"},
        )

        conn = _get_begin_conn(manager)
        call_args = conn.execute.call_args
        params = call_args[0][1]
        assert params["title"] == "myfile.py"

    async def test_extracts_title_from_title_field(
        self,
        keyword_ops: KeywordOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """upsert_with_tsvector() falls back to title field."""
        await keyword_ops.upsert_with_tsvector(
            chunk_id="chunk-1",
            document_text="content",
            metadata={"title": "My Document"},
        )

        conn = _get_begin_conn(manager)
        call_args = conn.execute.call_args
        params = call_args[0][1]
        assert params["title"] == "My Document"

    async def test_extracts_summary_from_metadata(
        self,
        keyword_ops: KeywordOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """upsert_with_tsvector() extracts summary from metadata."""
        await keyword_ops.upsert_with_tsvector(
            chunk_id="chunk-1",
            document_text="content",
            metadata={"summary": "Brief summary"},
        )

        conn = _get_begin_conn(manager)
        call_args = conn.execute.call_args
        params = call_args[0][1]
        assert params["summary"] == "Brief summary"


class TestKeywordSearch:
    """Tests for keyword_search() method."""

    async def test_uses_websearch_to_tsquery(
        self,
        keyword_ops: KeywordOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """keyword_search() uses websearch_to_tsquery."""
        conn = _get_conn(manager)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        conn.execute = AsyncMock(return_value=mock_result)

        await keyword_ops.keyword_search(query="test query", top_k=5)

        call_args = conn.execute.call_args
        sql_text = str(call_args[0][0].text)
        assert "websearch_to_tsquery" in sql_text

    async def test_normalizes_scores_to_0_1(
        self,
        keyword_ops: KeywordOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """keyword_search() normalizes scores via per-query max."""
        conn = _get_conn(manager)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("chunk-1", "text1", {"key": "val"}, 0.8),
            ("chunk-2", "text2", {"key": "val"}, 0.4),
        ]
        conn.execute = AsyncMock(return_value=mock_result)

        results = await keyword_ops.keyword_search(query="test", top_k=5)

        # Max score is 0.8, so chunk-1 = 1.0, chunk-2 = 0.5
        assert len(results) == 2
        assert results[0].score == 1.0
        assert results[1].score == 0.5

    async def test_returns_empty_when_no_matches(
        self,
        keyword_ops: KeywordOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """keyword_search() returns empty list when no matches."""
        conn = _get_conn(manager)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        conn.execute = AsyncMock(return_value=mock_result)

        results = await keyword_ops.keyword_search(query="nonexistent", top_k=5)

        assert results == []

    async def test_handles_zero_scores(
        self,
        keyword_ops: KeywordOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """keyword_search() handles zero scores correctly."""
        conn = _get_conn(manager)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("chunk-1", "text1", {"key": "val"}, 0.0),
        ]
        conn.execute = AsyncMock(return_value=mock_result)

        results = await keyword_ops.keyword_search(query="test", top_k=5)

        # When max_score <= 0, it becomes 1.0, so score = 0.0/1.0 = 0.0
        assert len(results) == 1
        assert results[0].score == 0.0

    async def test_filters_by_source_types(
        self,
        keyword_ops: KeywordOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """keyword_search() filters by source_types."""
        conn = _get_conn(manager)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        conn.execute = AsyncMock(return_value=mock_result)

        await keyword_ops.keyword_search(
            query="test",
            top_k=5,
            source_types=["code"],
        )

        call_args = conn.execute.call_args
        sql_text = str(call_args[0][0].text)
        assert "source_type" in sql_text

    async def test_filters_by_languages(
        self,
        keyword_ops: KeywordOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """keyword_search() filters by languages."""
        conn = _get_conn(manager)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        conn.execute = AsyncMock(return_value=mock_result)

        await keyword_ops.keyword_search(
            query="test",
            top_k=5,
            languages=["python"],
        )

        call_args = conn.execute.call_args
        sql_text = str(call_args[0][0].text)
        assert "language" in sql_text

    async def test_wraps_exceptions_in_storage_error(
        self,
        keyword_ops: KeywordOps,
        manager: PostgresConnectionManager,
    ) -> None:
        """keyword_search() wraps exceptions in StorageError."""
        conn = _get_conn(manager)
        conn.execute = AsyncMock(side_effect=RuntimeError("DB connection lost"))

        with pytest.raises(StorageError, match="Keyword search failed"):
            await keyword_ops.keyword_search(query="test", top_k=5)
