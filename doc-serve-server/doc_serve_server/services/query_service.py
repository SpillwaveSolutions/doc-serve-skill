"""Query service for executing semantic search queries."""

import logging
import time
from typing import Optional

from llama_index.core.retrievers import BaseRetriever, QueryFusionRetriever
from llama_index.core.retrievers.fusion_retriever import FUSION_MODES
from llama_index.core.schema import NodeWithScore, QueryBundle, TextNode

from doc_serve_server.indexing import EmbeddingGenerator, get_embedding_generator
from doc_serve_server.indexing.bm25_index import BM25IndexManager, get_bm25_manager
from doc_serve_server.models import QueryMode, QueryRequest, QueryResponse, QueryResult
from doc_serve_server.storage import VectorStoreManager, get_vector_store

logger = logging.getLogger(__name__)


class VectorManagerRetriever(BaseRetriever):
    """LlamaIndex retriever wrapper for VectorStoreManager."""

    def __init__(
        self,
        service: "QueryService",
        top_k: int,
        threshold: float,
    ):
        super().__init__()
        self.service = service
        self.top_k = top_k
        self.threshold = threshold

    def _retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        # Synchronous retrieve not supported, use aretrieve
        return []

    async def _aretrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        query_embedding = await self.service.embedding_generator.embed_query(
            query_bundle.query_str
        )
        results = await self.service.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=self.top_k,
            similarity_threshold=self.threshold,
        )
        return [
            NodeWithScore(
                node=TextNode(text=res.text, id_=res.chunk_id, metadata=res.metadata),
                score=res.score,
            )
            for res in results
        ]


class QueryService:
    """
    Executes semantic, keyword, and hybrid search queries.

    Coordinates embedding generation, vector similarity search,
    and BM25 retrieval with result fusion.
    """

    def __init__(
        self,
        vector_store: Optional[VectorStoreManager] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        bm25_manager: Optional[BM25IndexManager] = None,
    ):
        """
        Initialize the query service.

        Args:
            vector_store: Vector store manager instance.
            embedding_generator: Embedding generator instance.
            bm25_manager: BM25 index manager instance.
        """
        self.vector_store = vector_store or get_vector_store()
        self.embedding_generator = embedding_generator or get_embedding_generator()
        self.bm25_manager = bm25_manager or get_bm25_manager()

    def is_ready(self) -> bool:
        """
        Check if the service is ready to process queries.

        Returns:
            True if the vector store is initialized and has documents.
        """
        return self.vector_store.is_initialized

    async def execute_query(self, request: QueryRequest) -> QueryResponse:
        """
        Execute a search query based on the requested mode.

        Args:
            request: QueryRequest with query text and parameters.

        Returns:
            QueryResponse with ranked results.

        Raises:
            RuntimeError: If the service is not ready.
        """
        if not self.is_ready():
            raise RuntimeError(
                "Query service not ready. Please wait for indexing to complete."
            )

        start_time = time.time()

        if request.mode == QueryMode.BM25:
            results = await self._execute_bm25_query(request)
        elif request.mode == QueryMode.VECTOR:
            results = await self._execute_vector_query(request)
        else:  # HYBRID
            results = await self._execute_hybrid_query(request)

        query_time_ms = (time.time() - start_time) * 1000

        logger.debug(
            f"Query ({request.mode}) '{request.query[:50]}...' returned "
            f"{len(results)} results in {query_time_ms:.2f}ms"
        )

        return QueryResponse(
            results=results,
            query_time_ms=query_time_ms,
            total_results=len(results),
        )

    async def _execute_vector_query(self, request: QueryRequest) -> list[QueryResult]:
        """Execute pure semantic search."""
        query_embedding = await self.embedding_generator.embed_query(request.query)
        search_results = await self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
        )

        return [
            QueryResult(
                text=res.text,
                source=res.metadata.get(
                    "source", res.metadata.get("file_path", "unknown")
                ),
                score=res.score,
                vector_score=res.score,
                chunk_id=res.chunk_id,
                metadata={
                    k: v
                    for k, v in res.metadata.items()
                    if k not in ("source", "file_path")
                },
            )
            for res in search_results
        ]

    async def _execute_bm25_query(self, request: QueryRequest) -> list[QueryResult]:
        """Execute pure keyword search."""
        if not self.bm25_manager.is_initialized:
            raise RuntimeError("BM25 index not initialized")

        retriever = self.bm25_manager.get_retriever(top_k=request.top_k)
        nodes = await retriever.aretrieve(request.query)

        return [
            QueryResult(
                text=node.node.get_content(),
                source=node.node.metadata.get(
                    "source", node.node.metadata.get("file_path", "unknown")
                ),
                score=node.score or 0.0,
                bm25_score=node.score,
                chunk_id=node.node.node_id,
                metadata={
                    k: v
                    for k, v in node.node.metadata.items()
                    if k not in ("source", "file_path")
                },
            )
            for node in nodes
        ]

    async def _execute_hybrid_query(self, request: QueryRequest) -> list[QueryResult]:
        """Execute hybrid search using Relative Score Fusion."""
        # For US5, we want to provide individual scores.
        # We'll perform the individual searches first to get the scores.

        # 1. Vector Search
        query_embedding = await self.embedding_generator.embed_query(request.query)
        vector_results = await self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=request.top_k * 2,  # Get more to ensure overlap
            similarity_threshold=request.similarity_threshold,
        )
        vector_scores = {res.chunk_id: res.score for res in vector_results}

        # 2. BM25 Search
        bm25_results = []
        if self.bm25_manager.is_initialized:
            bm25_retriever = self.bm25_manager.get_retriever(top_k=request.top_k * 2)
            bm25_nodes = await bm25_retriever.aretrieve(request.query)
            bm25_results = bm25_nodes
        bm25_scores = {node.node.node_id: node.score for node in bm25_results}

        # 3. Perform fusion using QueryFusionRetriever (still best for logic)
        # But we'll use our pre-fetched results if possible, or just let it run.
        # Given we need the fused ranking, we'll let it run but then enrich.

        vector_retriever = VectorManagerRetriever(
            self, top_k=request.top_k, threshold=request.similarity_threshold
        )

        bm25_retriever = self.bm25_manager.get_retriever(top_k=request.top_k)

        fusion_retriever = QueryFusionRetriever(
            [vector_retriever, bm25_retriever],
            similarity_top_k=request.top_k,
            num_queries=1,
            mode=FUSION_MODES.RELATIVE_SCORE,
            retriever_weights=[request.alpha, 1.0 - request.alpha],
            use_async=True,
        )

        fused_nodes = await fusion_retriever.aretrieve(request.query)

        return [
            QueryResult(
                text=node.node.get_content(),
                source=node.node.metadata.get(
                    "source", node.node.metadata.get("file_path", "unknown")
                ),
                score=node.score or 0.0,
                vector_score=vector_scores.get(node.node.node_id),
                bm25_score=bm25_scores.get(node.node.node_id),
                chunk_id=node.node.node_id,
                metadata={
                    k: v
                    for k, v in node.node.metadata.items()
                    if k not in ("source", "file_path")
                },
            )
            for node in fused_nodes
        ]

    async def get_document_count(self) -> int:
        """
        Get the total number of indexed documents.

        Returns:
            Number of documents in the vector store.
        """
        if not self.is_ready():
            return 0
        return await self.vector_store.get_count()


# Singleton instance
_query_service: Optional[QueryService] = None


def get_query_service() -> QueryService:
    """Get the global query service instance."""
    global _query_service
    if _query_service is None:
        _query_service = QueryService()
    return _query_service
