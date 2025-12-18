"""Unit tests for BM25 retrieval functionality."""

from llama_index.core.schema import TextNode

from doc_serve_server.indexing.bm25_index import BM25IndexManager


class TestBM25IndexManager:
    """Tests for BM25IndexManager."""

    def test_initialize_empty(self, tmp_path):
        """Test initialization with no existing index."""
        manager = BM25IndexManager(persist_dir=str(tmp_path))
        manager.initialize()
        assert manager.is_initialized is False

    def test_build_and_persist(self, tmp_path):
        """Test building and persisting the index."""
        manager = BM25IndexManager(persist_dir=str(tmp_path))
        nodes = [
            TextNode(text="Python is a programming language", id_="node1"),
            TextNode(text="FastAPI is a web framework", id_="node2"),
        ]
        manager.build_index(nodes)
        assert manager.is_initialized is True
        assert (tmp_path / "retriever.json").exists()

    def test_load_existing(self, tmp_path):
        """Test loading an existing index from disk."""
        # First build it
        manager1 = BM25IndexManager(persist_dir=str(tmp_path))
        nodes = [TextNode(text="Sample text", id_="node1")]
        manager1.build_index(nodes)

        # Then load it with a new manager
        manager2 = BM25IndexManager(persist_dir=str(tmp_path))
        manager2.initialize()
        assert manager2.is_initialized is True
        retriever = manager2.get_retriever()
        assert retriever is not None

    def test_reset(self, tmp_path):
        """Test resetting the index."""
        manager = BM25IndexManager(persist_dir=str(tmp_path))
        nodes = [TextNode(text="Sample text", id_="node1")]
        manager.build_index(nodes)
        assert (tmp_path / "retriever.json").exists()

        manager.reset()
        assert manager.is_initialized is False
        assert not (tmp_path / "retriever.json").exists()
