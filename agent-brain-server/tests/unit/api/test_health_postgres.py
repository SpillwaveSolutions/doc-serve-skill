"""Unit tests for /health/postgres endpoint."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from agent_brain_server.api.routers.health import router


def _create_app(
    backend_type: str = "postgres",
    pool_metrics: dict[str, Any] | None = None,
    db_version: str = "PostgreSQL 16.0",
    raise_error: bool = False,
) -> FastAPI:
    """Create a test FastAPI app with mocked state."""
    app = FastAPI()
    app.include_router(router, prefix="/health")

    mock_backend = MagicMock()
    mock_backend.config = MagicMock()
    mock_backend.config.host = "localhost"
    mock_backend.config.port = 5432
    mock_backend.config.database = "test_db"

    # Mock connection manager
    mock_cm = MagicMock()

    if pool_metrics is None:
        pool_metrics = {
            "status": "active",
            "pool_size": 10,
            "checked_in": 8,
            "checked_out": 2,
            "overflow": 0,
            "total": 10,
        }

    mock_cm.get_pool_status = AsyncMock(return_value=pool_metrics)

    # Mock engine for version query
    mock_conn = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (db_version,)
    mock_conn.execute = AsyncMock(return_value=mock_result)
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)

    mock_engine = MagicMock()
    mock_engine.connect = MagicMock(return_value=mock_conn)
    mock_cm.engine = mock_engine

    if raise_error:
        mock_cm.get_pool_status = AsyncMock(side_effect=RuntimeError("Connection lost"))

    mock_backend.connection_manager = mock_cm
    app.state.storage_backend = mock_backend

    return app


class TestPostgresHealthEndpoint:
    """Tests for /health/postgres endpoint."""

    @patch(
        "agent_brain_server.api.routers.health.get_effective_backend_type",
        return_value="postgres",
    )
    def test_returns_200_with_pool_metrics(self, mock_backend_type: MagicMock) -> None:
        """Returns 200 with pool metrics when backend is postgres."""
        app = _create_app(backend_type="postgres")
        client = TestClient(app)

        response = client.get("/health/postgres")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["backend"] == "postgres"

    @patch(
        "agent_brain_server.api.routers.health.get_effective_backend_type",
        return_value="postgres",
    )
    def test_includes_pool_metrics(self, mock_backend_type: MagicMock) -> None:
        """Returns pool_size, checked_in, checked_out, overflow."""
        app = _create_app()
        client = TestClient(app)

        response = client.get("/health/postgres")

        data = response.json()
        pool = data["pool"]
        assert pool["pool_size"] == 10
        assert pool["checked_in"] == 8
        assert pool["checked_out"] == 2
        assert pool["overflow"] == 0
        assert pool["total"] == 10

    @patch(
        "agent_brain_server.api.routers.health.get_effective_backend_type",
        return_value="postgres",
    )
    def test_includes_database_info(self, mock_backend_type: MagicMock) -> None:
        """Returns database version and connection info."""
        app = _create_app(db_version="PostgreSQL 16.0")
        client = TestClient(app)

        response = client.get("/health/postgres")

        data = response.json()
        db_info = data["database"]
        assert db_info["version"] == "PostgreSQL 16.0"
        assert db_info["host"] == "localhost"
        assert db_info["port"] == 5432
        assert db_info["database"] == "test_db"

    @patch(
        "agent_brain_server.api.routers.health.get_effective_backend_type",
        return_value="chroma",
    )
    def test_returns_400_when_not_postgres(self, mock_backend_type: MagicMock) -> None:
        """Returns 400 when backend is not postgres."""
        app = _create_app(backend_type="chroma")
        client = TestClient(app)

        response = client.get("/health/postgres")

        assert response.status_code == 400
        data = response.json()
        assert "only available" in data["detail"]

    @patch(
        "agent_brain_server.api.routers.health.get_effective_backend_type",
        return_value="postgres",
    )
    def test_returns_unhealthy_on_connection_error(
        self, mock_backend_type: MagicMock
    ) -> None:
        """Returns unhealthy status on connection error."""
        app = _create_app(raise_error=True)
        client = TestClient(app)

        response = client.get("/health/postgres")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "error" in data
