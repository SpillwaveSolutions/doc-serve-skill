"""Contract test fixtures for storage backend validation."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest

from agent_brain_server.config.provider_config import clear_settings_cache
from agent_brain_server.indexing.bm25_index import BM25IndexManager
from agent_brain_server.storage.chroma.backend import ChromaBackend
from agent_brain_server.storage.postgres import PostgresBackend, PostgresConfig
from agent_brain_server.storage.protocol import StorageBackendProtocol
from agent_brain_server.storage.vector_store import VectorStoreManager


def _postgres_available() -> bool:
    try:
        import asyncpg  # noqa: F401
    except ImportError:
        return False
    return bool(os.environ.get("DATABASE_URL"))


def _write_provider_config(path: Path) -> None:
    path.write_text("embedding:\n  params:\n    dimensions: 8\n")


async def _create_chroma_backend(tmp_path: Path) -> ChromaBackend:
    vector_store = VectorStoreManager()
    vector_store.persist_dir = str(tmp_path / "chroma")

    bm25_manager = BM25IndexManager()
    bm25_manager.persist_dir = str(tmp_path / "bm25")

    backend = ChromaBackend(vector_store=vector_store, bm25_manager=bm25_manager)
    await backend.initialize()
    return backend


async def _create_postgres_backend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> PostgresBackend:
    _write_provider_config(tmp_path / "provider-config.yaml")
    monkeypatch.setenv("AGENT_BRAIN_CONFIG", str(tmp_path / "provider-config.yaml"))
    clear_settings_cache()

    import agent_brain_server.providers  # noqa: F401

    config = PostgresConfig.from_database_url(os.environ["DATABASE_URL"])
    backend = PostgresBackend(config=config)
    await backend.initialize()
    return backend


@pytest.fixture
async def chroma_backend(tmp_path: Path) -> AsyncGenerator[ChromaBackend, None]:
    backend = await _create_chroma_backend(tmp_path)
    try:
        yield backend
    finally:
        await backend.reset()


@pytest.fixture
async def postgres_backend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> AsyncGenerator[PostgresBackend, None]:
    pytest.importorskip("asyncpg")
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set")

    backend = await _create_postgres_backend(tmp_path, monkeypatch)
    try:
        yield backend
    finally:
        await backend.reset()
        await backend.close()
        clear_settings_cache()


@pytest.fixture(params=["chroma", "postgres"])
async def storage_backend(
    request: pytest.FixtureRequest,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[StorageBackendProtocol, None]:
    backend_type = request.param

    if backend_type == "chroma":
        backend = await _create_chroma_backend(tmp_path)
        try:
            yield backend
        finally:
            await backend.reset()
        return

    pytest.importorskip("asyncpg")
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set")

    backend = await _create_postgres_backend(tmp_path, monkeypatch)
    try:
        yield backend
    finally:
        await backend.reset()
        await backend.close()
        clear_settings_cache()
