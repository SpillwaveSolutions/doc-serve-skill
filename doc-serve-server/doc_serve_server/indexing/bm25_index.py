"""BM25 index manager for persistence and retrieval."""

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Optional

from llama_index.core.schema import BaseNode
from llama_index.retrievers.bm25 import BM25Retriever

from doc_serve_server.config import settings

logger = logging.getLogger(__name__)


class BM25IndexManager:
    """
    Manages the lifecycle of the BM25 index.

    Handles building the index from nodes, persisting it to disk,
    and loading it for retrieval.
    """

    def __init__(self, persist_dir: Optional[str] = None):
        """
        Initialize the BM25 index manager.

        Args:
            persist_dir: Directory for index persistence.
        """
        self.persist_dir = persist_dir or settings.BM25_INDEX_PATH
        self._retriever: Optional[BM25Retriever] = None

    @property
    def is_initialized(self) -> bool:
        """Check if the index is initialized."""
        return self._retriever is not None

    def initialize(self) -> None:
        """
        Load the index from disk if it exists.
        """
        persist_path = Path(self.persist_dir)
        if (persist_path / "retriever.json").exists():
            try:
                self._retriever = BM25Retriever.from_persist_dir(str(persist_path))
                logger.info(f"BM25 index loaded from {self.persist_dir}")
            except Exception as e:
                logger.error(f"Failed to load BM25 index: {e}")
                self._retriever = None
        else:
            logger.info("No existing BM25 index found")

    def build_index(self, nodes: Sequence[BaseNode]) -> None:
        """
        Build a new BM25 index from nodes and persist it.

        Args:
            nodes: List of LlamaIndex nodes.
        """
        logger.info(f"Building BM25 index with {len(nodes)} nodes")
        self._retriever = BM25Retriever.from_defaults(nodes=nodes)
        self.persist()

    def persist(self) -> None:
        """Persist the current index to disk."""
        if not self._retriever:
            logger.warning("No BM25 index to persist")
            return

        persist_path = Path(self.persist_dir)
        persist_path.mkdir(parents=True, exist_ok=True)
        self._retriever.persist(str(persist_path))
        logger.info(f"BM25 index persisted to {self.persist_dir}")

    def get_retriever(self, top_k: int = 5) -> BM25Retriever:
        """
        Get the BM25 retriever instance.

        Args:
            top_k: Number of results to return.

        Returns:
            The BM25Retriever instance.

        Raises:
            RuntimeError: If the index is not initialized.
        """
        if not self._retriever:
            raise RuntimeError("BM25 index not initialized")

        # BM25Retriever similarity_top_k is usually set during initialization.
        self._retriever.similarity_top_k = top_k
        return self._retriever

    def reset(self) -> None:
        """Reset the BM25 index by deleting persistent files."""
        self._retriever = None
        persist_path = Path(self.persist_dir)
        if persist_path.exists():
            for file in persist_path.glob("*"):
                file.unlink()
            persist_path.rmdir()
        logger.info("BM25 index reset")


# Global singleton instance
_bm25_manager: Optional[BM25IndexManager] = None


def get_bm25_manager() -> BM25IndexManager:
    """Get the global BM25 manager instance."""
    global _bm25_manager
    if _bm25_manager is None:
        _bm25_manager = BM25IndexManager()
    return _bm25_manager
