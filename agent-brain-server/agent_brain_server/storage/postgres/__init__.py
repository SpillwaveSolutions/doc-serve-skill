"""PostgreSQL storage backend with pgvector and tsvector.

This package provides the PostgreSQL implementation of the
StorageBackendProtocol using pgvector for vector search and
tsvector for full-text keyword search.
"""

from agent_brain_server.storage.postgres.config import PostgresConfig

__all__ = ["PostgresConfig"]
