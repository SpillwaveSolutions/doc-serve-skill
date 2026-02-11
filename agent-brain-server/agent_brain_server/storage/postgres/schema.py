"""PostgreSQL schema management with pgvector and tsvector.

This module provides the PostgresSchemaManager class for creating and
validating the database schema, including the documents table with
dynamic vector dimensions, HNSW and GIN indexes, and embedding metadata.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import text

from agent_brain_server.storage.postgres.config import PostgresConfig
from agent_brain_server.storage.postgres.connection import PostgresConnectionManager
from agent_brain_server.storage.protocol import StorageError

logger = logging.getLogger(__name__)


class PostgresSchemaManager:
    """Manages PostgreSQL schema for the storage backend.

    Creates tables, indexes, and extensions on initialization.
    Validates embedding dimension consistency on subsequent startups.

    Attributes:
        connection_manager: Initialized PostgresConnectionManager.
        embedding_dimensions: Vector embedding dimension size.
        config: Optional PostgresConfig for HNSW and language params.
    """

    def __init__(
        self,
        connection_manager: PostgresConnectionManager,
        embedding_dimensions: int,
        config: PostgresConfig | None = None,
    ) -> None:
        """Initialize schema manager.

        Args:
            connection_manager: An initialized PostgresConnectionManager.
            embedding_dimensions: Number of embedding dimensions for the
                vector column (e.g. 3072 for text-embedding-3-large).
            config: Optional PostgresConfig for HNSW params and language.
                Falls back to sensible defaults if not provided.
        """
        self.connection_manager = connection_manager
        self.embedding_dimensions = embedding_dimensions
        self.config = config or PostgresConfig()

    async def create_schema(self) -> None:
        """Create database schema with tables and indexes.

        Creates the pgvector extension, documents table with dynamic
        vector dimensions, HNSW/GIN indexes, and embedding_metadata
        table. All operations are idempotent (IF NOT EXISTS).

        Raises:
            StorageError: If schema creation fails.
        """
        engine = self.connection_manager.engine
        hnsw_m = self.config.hnsw_m
        hnsw_ef = self.config.hnsw_ef_construction
        dims = self.embedding_dimensions

        try:
            async with engine.begin() as conn:
                # 1. Enable pgvector extension
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

                # 2. Create documents table
                await conn.execute(
                    text(
                        f"""
                        CREATE TABLE IF NOT EXISTS documents (
                            chunk_id TEXT PRIMARY KEY,
                            document_text TEXT NOT NULL,
                            metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                            embedding vector({dims}),
                            tsv tsvector,
                            created_at TIMESTAMPTZ DEFAULT NOW(),
                            updated_at TIMESTAMPTZ DEFAULT NOW()
                        );
                        """
                    )
                )

                # 3. Create HNSW index for vector similarity search
                await conn.execute(
                    text(
                        f"""
                        CREATE INDEX IF NOT EXISTS documents_embedding_idx
                        ON documents
                        USING hnsw (embedding vector_cosine_ops)
                        WITH (m = {hnsw_m}, ef_construction = {hnsw_ef});
                        """
                    )
                )

                # 4. Create GIN index for tsvector full-text search
                await conn.execute(
                    text(
                        """
                        CREATE INDEX IF NOT EXISTS documents_tsv_idx
                        ON documents USING gin(tsv);
                        """
                    )
                )

                # 5. Create GIN index for metadata JSONB queries
                await conn.execute(
                    text(
                        """
                        CREATE INDEX IF NOT EXISTS documents_metadata_idx
                        ON documents USING gin(metadata);
                        """
                    )
                )

                # 6. Create embedding_metadata table (single-row)
                await conn.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS embedding_metadata (
                            id INTEGER PRIMARY KEY DEFAULT 1,
                            provider TEXT NOT NULL,
                            model TEXT NOT NULL,
                            dimensions INTEGER NOT NULL,
                            created_at TIMESTAMPTZ DEFAULT NOW(),
                            CONSTRAINT single_row CHECK (id = 1)
                        );
                        """
                    )
                )

            logger.info(
                "PostgreSQL schema created: documents(vector(%d)), "
                "HNSW(m=%d, ef=%d), GIN(tsv, metadata), embedding_metadata",
                dims,
                hnsw_m,
                hnsw_ef,
            )
        except Exception as e:
            raise StorageError(
                f"Failed to create PostgreSQL schema: {e}",
                backend="postgres",
            ) from e

    async def validate_dimensions(self) -> None:
        """Validate embedding dimensions match stored metadata.

        Checks if previously stored dimensions differ from current
        configuration. A mismatch means the HNSW index is incompatible
        and requires a full reset.

        Raises:
            StorageError: If stored dimensions don't match current config.
        """
        metadata = await self.get_embedding_metadata()
        if metadata is None:
            return  # No metadata stored yet, nothing to validate

        stored_dims = metadata.get("dimensions")
        if stored_dims is not None and stored_dims != self.embedding_dimensions:
            raise StorageError(
                f"Embedding dimension mismatch: stored={stored_dims}, "
                f"current={self.embedding_dimensions}. Cannot use index "
                f"created with different dimensions. Run "
                f"'agent-brain reset --yes' to recreate index.",
                backend="postgres",
            )

    async def store_embedding_metadata(
        self, provider: str, model: str, dimensions: int
    ) -> None:
        """Store or update embedding metadata (upsert).

        Uses INSERT ... ON CONFLICT to ensure only one metadata row
        exists (id=1 constraint).

        Args:
            provider: Embedding provider name (e.g. "openai").
            model: Embedding model name (e.g. "text-embedding-3-large").
            dimensions: Vector dimension count.

        Raises:
            StorageError: If the upsert operation fails.
        """
        engine = self.connection_manager.engine
        try:
            async with engine.begin() as conn:
                await conn.execute(
                    text(
                        """
                        INSERT INTO embedding_metadata (id, provider, model, dimensions)
                        VALUES (1, :provider, :model, :dimensions)
                        ON CONFLICT (id) DO UPDATE SET
                            provider = EXCLUDED.provider,
                            model = EXCLUDED.model,
                            dimensions = EXCLUDED.dimensions;
                        """
                    ),
                    {
                        "provider": provider,
                        "model": model,
                        "dimensions": dimensions,
                    },
                )
            logger.info(
                "Stored embedding metadata: provider=%s, model=%s, dimensions=%d",
                provider,
                model,
                dimensions,
            )
        except Exception as e:
            raise StorageError(
                f"Failed to store embedding metadata: {e}",
                backend="postgres",
            ) from e

    async def get_embedding_metadata(self) -> dict[str, Any] | None:
        """Retrieve stored embedding metadata.

        Returns:
            Dictionary with provider, model, and dimensions keys,
            or None if no metadata has been stored.

        Raises:
            StorageError: If the query fails.
        """
        engine = self.connection_manager.engine
        try:
            async with engine.connect() as conn:
                result = await conn.execute(
                    text(
                        """
                        SELECT provider, model, dimensions
                        FROM embedding_metadata
                        WHERE id = 1;
                        """
                    )
                )
                row = result.fetchone()
                if row is None:
                    return None
                return {
                    "provider": row[0],
                    "model": row[1],
                    "dimensions": row[2],
                }
        except Exception as e:
            # Table might not exist yet on first startup
            error_msg = str(e).lower()
            if "does not exist" in error_msg or "no such table" in error_msg:
                return None
            raise StorageError(
                f"Failed to retrieve embedding metadata: {e}",
                backend="postgres",
            ) from e
