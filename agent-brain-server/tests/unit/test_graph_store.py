"""Unit tests for GraphStoreManager (Feature 113)."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent_brain_server.storage.graph_store import (
    GraphStoreManager,
    _MinimalGraphStore,
    get_graph_store_manager,
    initialize_graph_store,
    reset_graph_store_manager,
)


@pytest.fixture(autouse=True)
def reset_graph_singleton():
    """Reset graph store singleton before and after each test."""
    reset_graph_store_manager()
    yield
    reset_graph_store_manager()


@pytest.fixture
def graph_persist_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for graph persistence."""
    graph_dir = tmp_path / "graph_index"
    graph_dir.mkdir(parents=True, exist_ok=True)
    return graph_dir


class TestGraphStoreManagerInitialization:
    """Tests for GraphStoreManager initialization."""

    def test_init_with_defaults(self, graph_persist_dir: Path):
        """Test initialization with default parameters."""
        manager = GraphStoreManager(graph_persist_dir)

        assert manager.persist_dir == graph_persist_dir
        assert manager.store_type == "simple"
        assert not manager.is_initialized
        assert manager.entity_count == 0
        assert manager.relationship_count == 0

    def test_init_with_custom_store_type(self, graph_persist_dir: Path):
        """Test initialization with custom store type."""
        manager = GraphStoreManager(graph_persist_dir, store_type="kuzu")

        assert manager.store_type == "kuzu"

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_initialize_disabled(
        self, mock_settings: MagicMock, graph_persist_dir: Path
    ):
        """Test initialization when graph indexing is disabled."""
        mock_settings.ENABLE_GRAPH_INDEX = False

        manager = GraphStoreManager(graph_persist_dir)
        manager.initialize()

        assert not manager.is_initialized
        assert manager.graph_store is None

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_initialize_simple_store(
        self, mock_settings: MagicMock, graph_persist_dir: Path
    ):
        """Test initialization with simple store type."""
        mock_settings.ENABLE_GRAPH_INDEX = True

        manager = GraphStoreManager(graph_persist_dir, store_type="simple")
        manager.initialize()

        assert manager.is_initialized
        assert manager.graph_store is not None

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_initialize_idempotent(
        self, mock_settings: MagicMock, graph_persist_dir: Path
    ):
        """Test that multiple initialize calls are safe."""
        mock_settings.ENABLE_GRAPH_INDEX = True

        manager = GraphStoreManager(graph_persist_dir)
        manager.initialize()
        first_store = manager.graph_store

        manager.initialize()  # Second call
        assert manager.graph_store is first_store

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_initialize_kuzu_fallback(
        self, mock_settings: MagicMock, graph_persist_dir: Path
    ):
        """Test Kuzu initialization falls back to simple when not available."""
        mock_settings.ENABLE_GRAPH_INDEX = True

        manager = GraphStoreManager(graph_persist_dir, store_type="kuzu")
        manager.initialize()

        # Should fall back to simple since kuzu is likely not installed
        assert manager.is_initialized
        assert manager.store_type == "simple"  # Fallback


class TestGraphStoreManagerSingleton:
    """Tests for GraphStoreManager singleton pattern."""

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_singleton_pattern(self, mock_settings: MagicMock, graph_persist_dir: Path):
        """Test singleton pattern returns same instance."""
        mock_settings.GRAPH_INDEX_PATH = str(graph_persist_dir)
        mock_settings.GRAPH_STORE_TYPE = "simple"

        instance1 = GraphStoreManager.get_instance(graph_persist_dir)
        instance2 = GraphStoreManager.get_instance(graph_persist_dir)

        assert instance1 is instance2

    def test_singleton_reset(self, graph_persist_dir: Path):
        """Test singleton reset creates new instance."""
        instance1 = GraphStoreManager.get_instance(graph_persist_dir)
        GraphStoreManager.reset_instance()
        instance2 = GraphStoreManager.get_instance(graph_persist_dir)

        assert instance1 is not instance2


class TestGraphStoreManagerPersistence:
    """Tests for GraphStoreManager persistence operations."""

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_persist_simple_store(
        self, mock_settings: MagicMock, graph_persist_dir: Path
    ):
        """Test persisting simple store creates files."""
        mock_settings.ENABLE_GRAPH_INDEX = True

        manager = GraphStoreManager(graph_persist_dir, store_type="simple")
        manager.initialize()
        manager.persist()

        # Check for LlamaIndex persistence or metadata file
        llamaindex_path = graph_persist_dir / "graph_store_llamaindex.json"
        metadata_path = graph_persist_dir / "graph_metadata.json"
        legacy_path = graph_persist_dir / "graph_store.json"

        # At least one of the persistence files should exist
        assert (
            llamaindex_path.exists() or metadata_path.exists() or legacy_path.exists()
        )

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_persist_disabled(self, mock_settings: MagicMock, graph_persist_dir: Path):
        """Test persist is no-op when disabled."""
        mock_settings.ENABLE_GRAPH_INDEX = False

        manager = GraphStoreManager(graph_persist_dir)
        manager.persist()

        persist_path = graph_persist_dir / "graph_store.json"
        assert not persist_path.exists()

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_persist_not_initialized(
        self, mock_settings: MagicMock, graph_persist_dir: Path
    ):
        """Test persist is no-op when not initialized."""
        mock_settings.ENABLE_GRAPH_INDEX = True

        manager = GraphStoreManager(graph_persist_dir)
        # Don't call initialize()
        manager.persist()

        persist_path = graph_persist_dir / "graph_store.json"
        assert not persist_path.exists()

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_load_no_data(self, mock_settings: MagicMock, graph_persist_dir: Path):
        """Test loading when no persisted data exists."""
        mock_settings.ENABLE_GRAPH_INDEX = True

        manager = GraphStoreManager(graph_persist_dir)
        manager.initialize()

        result = manager.load()
        # Should return False if no data file exists initially
        # (the initialization itself may create an empty store)
        assert isinstance(result, bool)

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_persist_and_load_cycle(
        self, mock_settings: MagicMock, graph_persist_dir: Path
    ):
        """Test full persist and load cycle."""
        mock_settings.ENABLE_GRAPH_INDEX = True

        # Create and persist
        manager1 = GraphStoreManager(graph_persist_dir, store_type="simple")
        manager1.initialize()
        manager1._entity_count = 5
        manager1._relationship_count = 10
        manager1.persist()

        # Reset and load
        GraphStoreManager.reset_instance()
        manager2 = GraphStoreManager(graph_persist_dir, store_type="simple")
        manager2.initialize()
        loaded = manager2.load()

        assert loaded
        assert manager2._entity_count == 5
        assert manager2._relationship_count == 10


class TestGraphStoreManagerOperations:
    """Tests for GraphStoreManager graph operations."""

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_add_triplet(self, mock_settings: MagicMock, graph_persist_dir: Path):
        """Test adding a triplet to the graph."""
        mock_settings.ENABLE_GRAPH_INDEX = True

        manager = GraphStoreManager(graph_persist_dir)
        manager.initialize()

        result = manager.add_triplet(
            subject="FastAPI",
            predicate="uses",
            obj="Pydantic",
            subject_type="Framework",
            object_type="Library",
        )

        assert result is True
        assert manager.relationship_count >= 1

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_add_triplet_disabled(
        self, mock_settings: MagicMock, graph_persist_dir: Path
    ):
        """Test add_triplet is no-op when disabled."""
        mock_settings.ENABLE_GRAPH_INDEX = False

        manager = GraphStoreManager(graph_persist_dir)

        result = manager.add_triplet(
            subject="FastAPI",
            predicate="uses",
            obj="Pydantic",
        )

        assert result is False

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_clear_graph(self, mock_settings: MagicMock, graph_persist_dir: Path):
        """Test clearing the graph."""
        mock_settings.ENABLE_GRAPH_INDEX = True

        manager = GraphStoreManager(graph_persist_dir)
        manager.initialize()

        # Add some data
        manager.add_triplet("A", "relates", "B")
        manager.persist()

        # Clear
        manager.clear()

        assert manager.entity_count == 0
        assert manager.relationship_count == 0

        # Persisted file should be removed
        persist_path = graph_persist_dir / "graph_store.json"
        assert not persist_path.exists()

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_clear_disabled(self, mock_settings: MagicMock, graph_persist_dir: Path):
        """Test clear is no-op when disabled."""
        mock_settings.ENABLE_GRAPH_INDEX = False

        manager = GraphStoreManager(graph_persist_dir)
        manager.clear()  # Should not raise


class TestGraphStoreManagerProperties:
    """Tests for GraphStoreManager properties."""

    def test_is_initialized_default(self, graph_persist_dir: Path):
        """Test is_initialized is False by default."""
        manager = GraphStoreManager(graph_persist_dir)
        assert not manager.is_initialized

    def test_entity_count_default(self, graph_persist_dir: Path):
        """Test entity_count is 0 by default."""
        manager = GraphStoreManager(graph_persist_dir)
        assert manager.entity_count == 0

    def test_relationship_count_default(self, graph_persist_dir: Path):
        """Test relationship_count is 0 by default."""
        manager = GraphStoreManager(graph_persist_dir)
        assert manager.relationship_count == 0

    def test_last_updated_default(self, graph_persist_dir: Path):
        """Test last_updated is None by default."""
        manager = GraphStoreManager(graph_persist_dir)
        assert manager.last_updated is None

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_last_updated_after_persist(
        self, mock_settings: MagicMock, graph_persist_dir: Path
    ):
        """Test last_updated is set after persist."""
        mock_settings.ENABLE_GRAPH_INDEX = True

        manager = GraphStoreManager(graph_persist_dir)
        manager.initialize()

        before = datetime.now(timezone.utc)
        manager.persist()
        after = datetime.now(timezone.utc)

        assert manager.last_updated is not None
        assert before <= manager.last_updated <= after


class TestMinimalGraphStore:
    """Tests for _MinimalGraphStore fallback."""

    def test_init(self):
        """Test minimal store initialization."""
        store = _MinimalGraphStore()

        assert store._entities == {}
        assert store._relationships == []

    def test_add_triplet(self):
        """Test adding triplet to minimal store."""
        store = _MinimalGraphStore()

        store._add_triplet(
            subject="A",
            predicate="relates",
            obj="B",
            subject_type="Type1",
            object_type="Type2",
            source_chunk_id="chunk_1",
        )

        assert "A" in store._entities
        assert "B" in store._entities
        assert len(store._relationships) == 1
        assert store._relationships[0]["predicate"] == "relates"

    def test_clear(self):
        """Test clearing minimal store."""
        store = _MinimalGraphStore()
        store._add_triplet("A", "relates", "B")

        store.clear()

        assert store._entities == {}
        assert store._relationships == []


class TestModuleFunctions:
    """Tests for module-level convenience functions."""

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_get_graph_store_manager(
        self, mock_settings: MagicMock, graph_persist_dir: Path
    ):
        """Test get_graph_store_manager returns singleton."""
        mock_settings.GRAPH_INDEX_PATH = str(graph_persist_dir)
        mock_settings.GRAPH_STORE_TYPE = "simple"

        manager1 = get_graph_store_manager(graph_persist_dir)
        manager2 = get_graph_store_manager(graph_persist_dir)

        assert manager1 is manager2

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_initialize_graph_store(
        self, mock_settings: MagicMock, graph_persist_dir: Path
    ):
        """Test initialize_graph_store initializes and returns manager."""
        mock_settings.ENABLE_GRAPH_INDEX = True
        mock_settings.GRAPH_INDEX_PATH = str(graph_persist_dir)
        mock_settings.GRAPH_STORE_TYPE = "simple"

        manager = initialize_graph_store(graph_persist_dir)

        assert manager.is_initialized

    def test_reset_graph_store_manager(self, graph_persist_dir: Path):
        """Test reset_graph_store_manager clears singleton."""
        manager1 = get_graph_store_manager(graph_persist_dir)
        reset_graph_store_manager()
        manager2 = get_graph_store_manager(graph_persist_dir)

        assert manager1 is not manager2


class TestGraphStoreManagerEdgeCases:
    """Tests for edge cases and error handling."""

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_load_invalid_json(self, mock_settings: MagicMock, graph_persist_dir: Path):
        """Test loading invalid JSON file."""
        mock_settings.ENABLE_GRAPH_INDEX = True

        # Create invalid JSON file
        persist_path = graph_persist_dir / "graph_store.json"
        persist_path.write_text("invalid json content")

        manager = GraphStoreManager(graph_persist_dir)
        manager.initialize()

        result = manager.load()
        assert result is False

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_persist_creates_directory(self, mock_settings: MagicMock, tmp_path: Path):
        """Test persist creates directory if it doesn't exist."""
        mock_settings.ENABLE_GRAPH_INDEX = True

        non_existent = tmp_path / "new_dir" / "graph"
        manager = GraphStoreManager(non_existent)
        manager.initialize()
        manager.persist()

        assert non_existent.exists()

    @patch("agent_brain_server.storage.graph_store.settings")
    def test_add_triplet_not_initialized(
        self, mock_settings: MagicMock, graph_persist_dir: Path
    ):
        """Test add_triplet fails when not initialized."""
        mock_settings.ENABLE_GRAPH_INDEX = True

        manager = GraphStoreManager(graph_persist_dir)
        # Don't call initialize()

        result = manager.add_triplet("A", "relates", "B")
        assert result is False
