"""Unit tests for StorageConfig and integration with ProviderSettings."""

import pytest
from pydantic import ValidationError as PydanticValidationError

from agent_brain_server.config.provider_config import (
    ProviderSettings,
    StorageConfig,
    ValidationSeverity,
    validate_provider_config,
)


def test_storage_config_defaults() -> None:
    """Test StorageConfig defaults to chroma backend."""
    config = StorageConfig()

    assert config.backend == "chroma"
    assert config.postgres == {}


def test_storage_config_postgres_backend() -> None:
    """Test StorageConfig with postgres backend."""
    config = StorageConfig(backend="postgres")

    assert config.backend == "postgres"
    assert config.postgres == {}


def test_storage_config_postgres_with_params() -> None:
    """Test StorageConfig with postgres connection parameters."""
    postgres_params = {
        "host": "localhost",
        "port": 5432,
        "database": "agent_brain",
        "user": "postgres",
        "password": "secret",
    }

    config = StorageConfig(backend="postgres", postgres=postgres_params)

    assert config.backend == "postgres"
    assert config.postgres == postgres_params


def test_storage_config_case_insensitive() -> None:
    """Test StorageConfig normalizes backend to lowercase."""
    config1 = StorageConfig(backend="CHROMA")
    config2 = StorageConfig(backend="Postgres")
    config3 = StorageConfig(backend="ChRoMa")

    assert config1.backend == "chroma"
    assert config2.backend == "postgres"
    assert config3.backend == "chroma"


def test_storage_config_invalid_backend() -> None:
    """Test StorageConfig raises ValidationError for invalid backend."""
    with pytest.raises(PydanticValidationError) as exc_info:
        StorageConfig(backend="invalid")

    error_msg = str(exc_info.value)
    assert "Invalid storage backend" in error_msg
    # Check for both backends in error (set order is non-deterministic)
    assert "chroma" in error_msg
    assert "postgres" in error_msg


def test_storage_config_invalid_backend_rejects_common_typos() -> None:
    """Test StorageConfig rejects common typos."""
    invalid_backends = ["chrome", "postgress", "postgresql", "chromadb", "pg"]

    for backend in invalid_backends:
        with pytest.raises(PydanticValidationError):
            StorageConfig(backend=backend)


def test_provider_settings_includes_storage() -> None:
    """Test ProviderSettings includes storage field with default."""
    settings = ProviderSettings()

    assert hasattr(settings, "storage")
    assert isinstance(settings.storage, StorageConfig)
    assert settings.storage.backend == "chroma"


def test_provider_settings_storage_override() -> None:
    """Test ProviderSettings with custom storage config."""
    settings = ProviderSettings(
        storage=StorageConfig(backend="postgres"),
    )

    assert settings.storage.backend == "postgres"


def test_provider_settings_yaml_roundtrip_chroma() -> None:
    """Test parsing YAML-like dict with chroma storage."""
    config_dict = {
        "embedding": {
            "provider": "openai",
            "model": "text-embedding-3-large",
        },
        "summarization": {
            "provider": "anthropic",
            "model": "claude-haiku-4-5-20251001",
        },
        "storage": {
            "backend": "chroma",
        },
    }

    settings = ProviderSettings(**config_dict)

    assert settings.storage.backend == "chroma"
    assert settings.embedding.provider == "openai"


def test_provider_settings_yaml_roundtrip_postgres() -> None:
    """Test parsing YAML-like dict with postgres storage."""
    config_dict = {
        "storage": {
            "backend": "postgres",
            "postgres": {
                "host": "localhost",
                "port": 5432,
                "database": "agent_brain",
            },
        },
    }

    settings = ProviderSettings(**config_dict)

    assert settings.storage.backend == "postgres"
    assert settings.storage.postgres["host"] == "localhost"
    assert settings.storage.postgres["port"] == 5432


def test_validate_provider_config_postgres_no_config_warning() -> None:
    """Test validate_provider_config warns when postgres backend has no config."""
    settings = ProviderSettings(
        storage=StorageConfig(backend="postgres", postgres={}),
    )

    errors = validate_provider_config(settings, reranking_enabled=False)

    # Should have at least one warning about missing postgres config
    storage_errors = [e for e in errors if e.provider_type == "storage"]
    assert len(storage_errors) >= 1

    error = storage_errors[0]
    assert error.severity == ValidationSeverity.WARNING
    assert "postgres configuration" in error.message.lower()
    assert error.field == "postgres"


def test_validate_provider_config_postgres_with_config_no_warning() -> None:
    """Test validate_provider_config passes when postgres has config."""
    settings = ProviderSettings(
        storage=StorageConfig(
            backend="postgres",
            postgres={"host": "localhost", "port": 5432},
        ),
    )

    errors = validate_provider_config(settings, reranking_enabled=False)

    # Should have no storage-related errors
    storage_errors = [e for e in errors if e.provider_type == "storage"]
    assert len(storage_errors) == 0


def test_validate_provider_config_chroma_no_warning() -> None:
    """Test validate_provider_config does not warn for chroma backend."""
    settings = ProviderSettings(
        storage=StorageConfig(backend="chroma"),
    )

    errors = validate_provider_config(settings, reranking_enabled=False)

    # Should have no storage-related errors
    storage_errors = [e for e in errors if e.provider_type == "storage"]
    assert len(storage_errors) == 0


def test_storage_config_json_serialization() -> None:
    """Test StorageConfig can be serialized to JSON."""
    config = StorageConfig(
        backend="postgres",
        postgres={"host": "localhost", "port": 5432},
    )

    # Pydantic v2 uses model_dump
    data = config.model_dump()

    assert data["backend"] == "postgres"
    assert data["postgres"]["host"] == "localhost"
    assert data["postgres"]["port"] == 5432


def test_storage_config_partial_postgres_params() -> None:
    """Test StorageConfig accepts partial postgres parameters."""
    config = StorageConfig(
        backend="postgres",
        postgres={"host": "localhost"},  # Only host specified
    )

    assert config.backend == "postgres"
    assert config.postgres == {"host": "localhost"}
    assert "port" not in config.postgres
