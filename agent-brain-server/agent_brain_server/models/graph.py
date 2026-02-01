"""Models for GraphRAG feature (Feature 113).

Defines Pydantic models for graph entities, relationships, and status.
All models are configured with frozen=True for immutability.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GraphTriple(BaseModel):
    """Represents a subject-predicate-object triple in the knowledge graph.

    Triples are the fundamental unit of knowledge representation in GraphRAG.
    They capture relationships between entities extracted from documents.

    Attributes:
        subject: The subject entity (e.g., "FastAPI").
        subject_type: Optional type classification (e.g., "Framework").
        predicate: The relationship type (e.g., "uses").
        object: The object entity (e.g., "Pydantic").
        object_type: Optional type classification (e.g., "Library").
        source_chunk_id: Optional ID of the source document chunk.
    """

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "subject": "FastAPI",
                    "subject_type": "Framework",
                    "predicate": "uses",
                    "object": "Pydantic",
                    "object_type": "Library",
                    "source_chunk_id": "chunk_abc123",
                },
                {
                    "subject": "UserController",
                    "subject_type": "Class",
                    "predicate": "calls",
                    "object": "authenticate_user",
                    "object_type": "Function",
                    "source_chunk_id": "chunk_def456",
                },
            ]
        },
    )

    subject: str = Field(
        ...,
        min_length=1,
        description="Subject entity in the triple",
    )
    subject_type: Optional[str] = Field(
        default=None,
        description="Type classification for subject entity",
    )
    predicate: str = Field(
        ...,
        min_length=1,
        description="Relationship type connecting subject to object",
    )
    object: str = Field(
        ...,
        min_length=1,
        description="Object entity in the triple",
    )
    object_type: Optional[str] = Field(
        default=None,
        description="Type classification for object entity",
    )
    source_chunk_id: Optional[str] = Field(
        default=None,
        description="ID of the source document chunk",
    )


class GraphEntity(BaseModel):
    """Represents an entity node in the knowledge graph.

    Entities are the nodes in the graph, representing concepts,
    code elements, or other named items extracted from documents.

    Attributes:
        name: Unique name/identifier of the entity.
        entity_type: Classification type (e.g., "Class", "Function", "Concept").
        description: Optional description of the entity.
        source_chunk_ids: List of source chunk IDs where entity appears.
        properties: Additional metadata properties.
    """

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "VectorStoreManager",
                    "entity_type": "Class",
                    "description": "Manages Chroma vector store operations",
                    "source_chunk_ids": ["chunk_001", "chunk_002"],
                    "properties": {"module": "storage.vector_store"},
                },
            ]
        },
    )

    name: str = Field(
        ...,
        min_length=1,
        description="Unique name/identifier of the entity",
    )
    entity_type: Optional[str] = Field(
        default=None,
        description="Classification type for the entity",
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of the entity",
    )
    source_chunk_ids: list[str] = Field(
        default_factory=list,
        description="List of source chunk IDs where entity appears",
    )
    properties: dict[str, str] = Field(
        default_factory=dict,
        description="Additional metadata properties",
    )


class GraphIndexStatus(BaseModel):
    """Status of the graph index.

    Provides information about the graph index state,
    including whether it's enabled, initialized, and statistics.

    Attributes:
        enabled: Whether graph indexing is enabled.
        initialized: Whether the graph store is initialized.
        entity_count: Number of entities in the graph.
        relationship_count: Number of relationships in the graph.
        last_updated: Timestamp of last graph update.
        store_type: Type of graph store backend.
    """

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "enabled": True,
                    "initialized": True,
                    "entity_count": 150,
                    "relationship_count": 320,
                    "last_updated": "2024-12-15T10:30:00Z",
                    "store_type": "simple",
                },
                {
                    "enabled": False,
                    "initialized": False,
                    "entity_count": 0,
                    "relationship_count": 0,
                    "last_updated": None,
                    "store_type": "simple",
                },
            ]
        },
    )

    enabled: bool = Field(
        default=False,
        description="Whether graph indexing is enabled",
    )
    initialized: bool = Field(
        default=False,
        description="Whether the graph store is initialized",
    )
    entity_count: int = Field(
        default=0,
        ge=0,
        description="Number of entities in the graph",
    )
    relationship_count: int = Field(
        default=0,
        ge=0,
        description="Number of relationships in the graph",
    )
    last_updated: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last graph update",
    )
    store_type: str = Field(
        default="simple",
        description="Type of graph store backend (simple or kuzu)",
    )


class GraphQueryContext(BaseModel):
    """Context information from graph-based retrieval.

    Contains additional context extracted from the knowledge graph
    during query processing.

    Attributes:
        related_entities: List of related entity names.
        relationship_paths: List of relationship paths as strings.
        subgraph_triplets: Relevant triplets from the graph.
        graph_score: Score from graph-based retrieval.
    """

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "related_entities": ["FastAPI", "Pydantic", "Uvicorn"],
                    "relationship_paths": [
                        "FastAPI -> uses -> Pydantic",
                        "FastAPI -> runs_on -> Uvicorn",
                    ],
                    "subgraph_triplets": [
                        {
                            "subject": "FastAPI",
                            "predicate": "uses",
                            "object": "Pydantic",
                        },
                    ],
                    "graph_score": 0.85,
                },
            ]
        },
    )

    related_entities: list[str] = Field(
        default_factory=list,
        description="List of related entity names",
    )
    relationship_paths: list[str] = Field(
        default_factory=list,
        description="Relationship paths as formatted strings",
    )
    subgraph_triplets: list[GraphTriple] = Field(
        default_factory=list,
        description="Relevant triplets from the graph",
    )
    graph_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Score from graph-based retrieval",
    )
