"""pgvector vector search and upsert operations.

This module provides the VectorOps class for performing vector similarity
search and embedding upserts using pgvector operators on PostgreSQL.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy import text

from agent_brain_server.storage.postgres.connection import PostgresConnectionManager
from agent_brain_server.storage.protocol import SearchResult, StorageError

logger = logging.getLogger(__name__)

# pgvector distance operators by metric name
_DISTANCE_OPERATORS: dict[str, str] = {
    "cosine": "<=>",
    "l2": "<->",
    "inner_product": "<#>",
}


class VectorOps:
    """pgvector vector search and upsert operations.

    Supports cosine distance, L2 (Euclidean) distance, and negative inner
    product distance metrics. All scores are normalized to 0-1 range where
    higher values indicate better matches.

    Attributes:
        connection_manager: Initialized PostgresConnectionManager.
    """

    def __init__(self, connection_manager: PostgresConnectionManager) -> None:
        """Initialize vector operations.

        Args:
            connection_manager: An initialized PostgresConnectionManager.
        """
        self.connection_manager = connection_manager

    async def upsert_embeddings(self, chunk_id: str, embedding: list[float]) -> None:
        """Update the embedding column for an existing document.

        Args:
            chunk_id: Unique chunk identifier.
            embedding: Embedding vector as list of floats.

        Raises:
            StorageError: If the upsert operation fails.
        """
        engine = self.connection_manager.engine
        try:
            embedding_str = json.dumps(embedding)
            async with engine.begin() as conn:
                await conn.execute(
                    text(
                        """
                        UPDATE documents
                        SET embedding = :embedding::vector,
                            updated_at = NOW()
                        WHERE chunk_id = :chunk_id
                        """
                    ),
                    {"chunk_id": chunk_id, "embedding": embedding_str},
                )
        except Exception as e:
            raise StorageError(
                f"Failed to upsert embedding for chunk {chunk_id}: {e}",
                backend="postgres",
            ) from e

    async def vector_search(
        self,
        query_embedding: list[float],
        top_k: int,
        similarity_threshold: float,
        distance_metric: str = "cosine",
        where: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Perform vector similarity search using pgvector.

        Supports three distance metrics:
        - ``cosine``: Cosine distance (``<=>``, score = 1 - distance).
        - ``l2``: Euclidean distance (``<->``, score = 1 / (1 + distance)).
        - ``inner_product``: Negative inner product (``<#>``,
          score = 0 - distance).

        All scores are normalized to 0-1 range where higher = better match.

        Args:
            query_embedding: Query embedding vector.
            top_k: Maximum number of results to return.
            similarity_threshold: Minimum similarity score (0-1).
            distance_metric: Distance metric to use.
            where: Optional JSONB metadata containment filter.

        Returns:
            List of SearchResult sorted by score descending.

        Raises:
            StorageError: If the search operation fails.
        """
        operator = _DISTANCE_OPERATORS.get(distance_metric)
        if operator is None:
            raise StorageError(
                f"Unsupported distance metric '{distance_metric}'. "
                f"Must be one of: {', '.join(_DISTANCE_OPERATORS.keys())}",
                backend="postgres",
            )

        engine = self.connection_manager.engine
        try:
            embedding_str = json.dumps(query_embedding)

            # Build optional metadata filter clause
            filter_clause = ""
            params: dict[str, Any] = {
                "query_embedding": embedding_str,
                "top_k": top_k,
            }

            if where:
                filter_clause = "AND metadata @> :filter::jsonb"
                params["filter"] = json.dumps(where)

            sql = f"""
                SELECT chunk_id, document_text, metadata,
                       embedding {operator} :query_embedding::vector AS distance
                FROM documents
                WHERE embedding IS NOT NULL
                {filter_clause}
                ORDER BY embedding {operator} :query_embedding::vector
                LIMIT :top_k
            """

            async with engine.connect() as conn:
                result = await conn.execute(text(sql), params)
                rows = result.fetchall()

            # Convert distance to normalized 0-1 score (higher = better)
            results: list[SearchResult] = []
            for row in rows:
                distance = float(row[3])
                score = _normalize_score(distance, distance_metric)

                if score >= similarity_threshold:
                    metadata_val = row[2]
                    if isinstance(metadata_val, str):
                        metadata_val = json.loads(metadata_val)

                    results.append(
                        SearchResult(
                            text=row[1],
                            metadata=metadata_val,
                            score=score,
                            chunk_id=row[0],
                        )
                    )

            return results

        except StorageError:
            raise
        except Exception as e:
            raise StorageError(
                f"Vector search failed: {e}",
                backend="postgres",
            ) from e


def _normalize_score(distance: float, metric: str) -> float:
    """Normalize a pgvector distance to a 0-1 similarity score.

    Args:
        distance: Raw distance from pgvector operator.
        metric: Distance metric name.

    Returns:
        Normalized score where higher = better match.
    """
    if metric == "cosine":
        # Cosine distance is in [0, 2]; similarity = 1 - distance
        return max(0.0, min(1.0, 1.0 - distance))
    elif metric == "l2":
        # L2 distance is in [0, inf); similarity = 1 / (1 + distance)
        return 1.0 / (1.0 + distance)
    elif metric == "inner_product":
        # pgvector <#> returns negative inner product; similarity = -distance
        return max(0.0, 0.0 - distance)
    else:
        return 0.0
