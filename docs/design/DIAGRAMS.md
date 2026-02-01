# Agent Brain Design Diagrams Index

This document provides an index of all design diagrams in the Agent Brain documentation.

## Summary

| Category | PlantUML | Mermaid | Total |
|----------|----------|---------|-------|
| Architecture Overview | 0 | 4 | 4 |
| Query Architecture | 0 | 8 | 8 |
| Indexing Pipeline | 0 | 11 | 11 |
| Storage Architecture | 0 | 11 | 11 |
| Class Diagrams | 0 | 14 | 14 |
| Deployment Architecture | 0 | 9 | 9 |
| Component Diagrams | 7 | 0 | 7 |
| Package Diagrams | 6 | 0 | 6 |
| Query Sequences | 5 | 0 | 5 |
| Indexing Sequences | 4 | 0 | 4 |
| CLI Sequences | 5 | 0 | 5 |
| Server States | 4 | 0 | 4 |
| Deployment Diagrams | 5 | 0 | 5 |
| **Total** | **36** | **57** | **93** |

## Architecture Overview (Mermaid)

| Diagram | Source | Image | Description |
|---------|--------|-------|-------------|
| C4 Context Diagram | [architecture-overview.md](architecture-overview.md) | [PNG](images/architecture-overview_c4_context_diagram.png) | System context showing Agent Brain's position in the ecosystem |
| Component Architecture | [architecture-overview.md](architecture-overview.md) | [PNG](images/architecture-overview_component_architecture.png) | Internal structure of each package |
| Multi-Instance Architecture | [architecture-overview.md](architecture-overview.md) | [PNG](images/architecture-overview_multi-instance_architecture.png) | Per-project server isolation |
| Lock File Protocol | [architecture-overview.md](architecture-overview.md) | [PNG](images/architecture-overview_lock_file_protocol.png) | Server lock acquisition sequence |

## Query Architecture (Mermaid)

| Diagram | Source | Image | Description |
|---------|--------|-------|-------------|
| Query Modes Overview | [query-architecture.md](query-architecture.md) | [PNG](images/query-architecture_query_modes_overview.png) | Five query mode routing |
| Vector Search Flow | [query-architecture.md](query-architecture.md) | [PNG](images/query-architecture_vector_search_flow.png) | Semantic search sequence |
| BM25 Keyword Search | [query-architecture.md](query-architecture.md) | [PNG](images/query-architecture_bm25_keyword_search_flow.png) | BM25 retrieval sequence |
| Hybrid Search Flow | [query-architecture.md](query-architecture.md) | [PNG](images/query-architecture_hybrid_search_flow.png) | Combined vector + BM25 |
| Graph Search Flow | [query-architecture.md](query-architecture.md) | [PNG](images/query-architecture_graph_search_flow_graphrag.png) | GraphRAG traversal |
| Multi-Retrieval RRF | [query-architecture.md](query-architecture.md) | [PNG](images/query-architecture_multi-retrieval_with_rrf.png) | Reciprocal Rank Fusion |
| Content Filtering | [query-architecture.md](query-architecture.md) | [PNG](images/query-architecture_content_filtering.png) | Post-retrieval filters |
| Mode Selection Guide | [query-architecture.md](query-architecture.md) | [PNG](images/query-architecture_choosing_the_right_mode.png) | Query mode decision tree |

## Indexing Pipeline (Mermaid)

| Diagram | Source | Image | Description |
|---------|--------|-------|-------------|
| Pipeline Overview | [indexing-pipeline.md](indexing-pipeline.md) | [PNG](images/indexing-pipeline_pipeline_overview.png) | End-to-end indexing flow |
| Service Orchestration | [indexing-pipeline.md](indexing-pipeline.md) | [PNG](images/indexing-pipeline_indexing_service_orchestration.png) | IndexingService coordination |
| Document Loading | [indexing-pipeline.md](indexing-pipeline.md) | [PNG](images/indexing-pipeline_document_loading.png) | File discovery and classification |
| Document Chunking | [indexing-pipeline.md](indexing-pipeline.md) | [PNG](images/indexing-pipeline_document_chunking.png) | Text splitting strategy |
| Code Chunking | [indexing-pipeline.md](indexing-pipeline.md) | [PNG](images/indexing-pipeline_code_chunking_ast-aware.png) | AST-aware code splitting |
| AST Query Patterns | [indexing-pipeline.md](indexing-pipeline.md) | [PNG](images/indexing-pipeline_ast_query_patterns_by_language.png) | Language-specific AST queries |
| Embedding Generation | [indexing-pipeline.md](indexing-pipeline.md) | [PNG](images/indexing-pipeline_embedding_generation.png) | Batch embedding process |
| Graph Extraction | [indexing-pipeline.md](indexing-pipeline.md) | [PNG](images/indexing-pipeline_graph_extraction_pipeline.png) | Knowledge graph building |
| Storage Operations | [indexing-pipeline.md](indexing-pipeline.md) | [PNG](images/indexing-pipeline_storage_operations.png) | Vector/BM25/Graph storage |
| Pipeline Timing | [indexing-pipeline.md](indexing-pipeline.md) | [PNG](images/indexing-pipeline_complete_pipeline_timing.png) | Gantt chart of timing |
| Error Handling | [indexing-pipeline.md](indexing-pipeline.md) | [PNG](images/indexing-pipeline_error_handling.png) | Failure recovery flow |

## Storage Architecture (Mermaid)

| Diagram | Source | Image | Description |
|---------|--------|-------|-------------|
| Storage Overview | [storage-architecture.md](storage-architecture.md) | [PNG](images/storage-architecture_storage_overview.png) | Three-tier storage architecture |
| VectorStore Architecture | [storage-architecture.md](storage-architecture.md) | [PNG](images/storage-architecture_architecture.png) | VectorStoreManager internals |
| Similarity Calculation | [storage-architecture.md](storage-architecture.md) | [PNG](images/storage-architecture_similarity_score_calculation.png) | Distance to similarity conversion |
| BM25 Architecture | [storage-architecture.md](storage-architecture.md) | [PNG](images/storage-architecture_architecture_2.png) | BM25IndexManager internals |
| BM25 Filtering | [storage-architecture.md](storage-architecture.md) | [PNG](images/storage-architecture_bm25_filtering_strategy.png) | Over-fetch and post-filter |
| Graph Architecture | [storage-architecture.md](storage-architecture.md) | [PNG](images/storage-architecture_architecture_3.png) | GraphStoreManager internals |
| Backend Comparison | [storage-architecture.md](storage-architecture.md) | [PNG](images/storage-architecture_backend_comparison.png) | Simple vs Kuzu vs Minimal |
| Directory Structure | [storage-architecture.md](storage-architecture.md) | [PNG](images/storage-architecture_directory_structure.png) | Per-project state files |
| Lock Protocol | [storage-architecture.md](storage-architecture.md) | [PNG](images/storage-architecture_lock_protocol.png) | Instance lock management |
| Path Resolution | [storage-architecture.md](storage-architecture.md) | [PNG](images/storage-architecture_storage_path_resolution.png) | Storage path configuration |
| Reset Sequence | [storage-architecture.md](storage-architecture.md) | [PNG](images/storage-architecture_reset_sequence.png) | Index reset procedure |

## Class Diagrams (Mermaid)

| Diagram | Source | Image | Description |
|---------|--------|-------|-------------|
| QueryService | [class-diagrams.md](class-diagrams.md) | [PNG](images/class-diagrams_queryservice.png) | Query service class structure |
| IndexingService | [class-diagrams.md](class-diagrams.md) | [PNG](images/class-diagrams_indexingservice.png) | Indexing service class structure |
| VectorStoreManager | [class-diagrams.md](class-diagrams.md) | [PNG](images/class-diagrams_vectorstoremanager.png) | Vector store class structure |
| BM25IndexManager | [class-diagrams.md](class-diagrams.md) | [PNG](images/class-diagrams_bm25indexmanager.png) | BM25 index class structure |
| GraphStoreManager | [class-diagrams.md](class-diagrams.md) | [PNG](images/class-diagrams_graphstoremanager.png) | Graph store class structure |
| Document Loading | [class-diagrams.md](class-diagrams.md) | [PNG](images/class-diagrams_document_loading.png) | DocumentLoader classes |
| Chunking | [class-diagrams.md](class-diagrams.md) | [PNG](images/class-diagrams_chunking.png) | Chunker class hierarchy |
| Embedding Generation | [class-diagrams.md](class-diagrams.md) | [PNG](images/class-diagrams_embedding_generation.png) | EmbeddingGenerator class |
| Graph Indexing | [class-diagrams.md](class-diagrams.md) | [PNG](images/class-diagrams_graph_indexing.png) | GraphIndexManager classes |
| Graph Models | [class-diagrams.md](class-diagrams.md) | [PNG](images/class-diagrams_graph_models.png) | GraphTriple, GraphEntity models |
| FastAPI Application | [class-diagrams.md](class-diagrams.md) | [PNG](images/class-diagrams_fastapi_application.png) | API layer structure |
| CLI Classes | [class-diagrams.md](class-diagrams.md) | [PNG](images/class-diagrams_cli_classes.png) | CLI command structure |
| Configuration Classes | [class-diagrams.md](class-diagrams.md) | [PNG](images/class-diagrams_configuration_classes.png) | Settings and RuntimeState |
| Class Relationships | [class-diagrams.md](class-diagrams.md) | [PNG](images/class-diagrams_class_relationships_overview.png) | Overall class relationships |

## Deployment Architecture (Mermaid)

| Diagram | Source | Image | Description |
|---------|--------|-------|-------------|
| Deployment Overview | [deployment-architecture.md](deployment-architecture.md) | [PNG](images/deployment-architecture_deployment_overview.png) | Three deployment modes |
| Local Development | [deployment-architecture.md](deployment-architecture.md) | [PNG](images/deployment-architecture_architecture.png) | Local dev setup |
| Multi-Instance | [deployment-architecture.md](deployment-architecture.md) | [PNG](images/deployment-architecture_architecture_2.png) | Per-project instances |
| Port Allocation | [deployment-architecture.md](deployment-architecture.md) | [PNG](images/deployment-architecture_port_allocation.png) | Dynamic port assignment |
| Single Server | [deployment-architecture.md](deployment-architecture.md) | [PNG](images/deployment-architecture_option_1_single_server_with_persistence.png) | Basic production setup |
| Docker Deployment | [deployment-architecture.md](deployment-architecture.md) | [PNG](images/deployment-architecture_option_2_docker_deployment.png) | Containerized deployment |
| Kubernetes | [deployment-architecture.md](deployment-architecture.md) | [PNG](images/deployment-architecture_option_3_kubernetes_deployment.png) | K8s enterprise setup |
| Production Checklist | [deployment-architecture.md](deployment-architecture.md) | [PNG](images/deployment-architecture_production_checklist.png) | Deployment checklist |
| Monitoring | [deployment-architecture.md](deployment-architecture.md) | [PNG](images/deployment-architecture_monitoring_integration.png) | Prometheus/Grafana stack |

## Component Diagrams (PlantUML)

| Diagram | Source | Image | Description |
|---------|--------|-------|-------------|
| System Overview | [component-diagrams.md](component-diagrams.md) | [PNG](images/System%20Component%20Overview.png) | Top-level system components |
| Server Components | [component-diagrams.md](component-diagrams.md) | [PNG](images/Server%20Components.png) | FastAPI server internals |
| Query Service | [component-diagrams.md](component-diagrams.md) | [PNG](images/Query%20Service%20Components.png) | QueryService components |
| Indexing Pipeline | [component-diagrams.md](component-diagrams.md) | [PNG](images/Indexing%20Pipeline.png) | Indexing pipeline components |
| Storage Components | [component-diagrams.md](component-diagrams.md) | [PNG](images/Storage%20Components.png) | Storage layer components |
| Integration | [component-diagrams.md](component-diagrams.md) | [PNG](images/Integration%20Components.png) | Plugin/CLI/Server integration |
| Interface Summary | [component-diagrams.md](component-diagrams.md) | [PNG](images/Interface%20Summary.png) | API interface overview |

## Package Diagrams (PlantUML)

| Diagram | Source | Image | Description |
|---------|--------|-------|-------------|
| Monorepo Structure | [package-diagrams.md](package-diagrams.md) | [PNG](images/Monorepo%20Package%20Structure.png) | Top-level package organization |
| Server Package | [package-diagrams.md](package-diagrams.md) | [PNG](images/Server%20Package%20Structure.png) | agent-brain-server internals |
| CLI Package | [package-diagrams.md](package-diagrams.md) | [PNG](images/CLI%20Package%20Structure.png) | agent-brain-cli internals |
| Plugin Package | [package-diagrams.md](package-diagrams.md) | [PNG](images/Plugin%20Package%20Structure.png) | agent-brain-plugin structure |
| External Dependencies | [package-diagrams.md](package-diagrams.md) | [PNG](images/External%20Dependencies.png) | Third-party dependencies |
| Package Interaction | [package-diagrams.md](package-diagrams.md) | [PNG](images/Package%20Interaction%20Flow.png) | Inter-package communication |

## Query Sequences (PlantUML)

| Diagram | Source | Image | Description |
|---------|--------|-------|-------------|
| Vector Query | [query-sequences.md](query-sequences.md) | [PNG](images/Vector%20Query%20Sequence.png) | Vector search sequence |
| BM25 Query | [query-sequences.md](query-sequences.md) | [PNG](images/BM25%20Query%20Sequence.png) | BM25 search sequence |
| Hybrid Query | [query-sequences.md](query-sequences.md) | [PNG](images/Hybrid%20Query%20Sequence.png) | Hybrid search sequence |
| Graph Query | [query-sequences.md](query-sequences.md) | [PNG](images/Graph%20Query%20Sequence.png) | Graph traversal sequence |
| Multi-Mode Query | [query-sequences.md](query-sequences.md) | [PNG](images/Multi-Mode%20Query%20Sequence.png) | RRF fusion sequence |

## Indexing Sequences (PlantUML)

| Diagram | Source | Image | Description |
|---------|--------|-------|-------------|
| Document Indexing | [indexing-sequences.md](indexing-sequences.md) | [PNG](images/Document%20Indexing%20Sequence.png) | Document processing sequence |
| Code Indexing | [indexing-sequences.md](indexing-sequences.md) | [PNG](images/Code%20Indexing%20Sequence.png) | Code processing with AST |
| Graph Building | [indexing-sequences.md](indexing-sequences.md) | [PNG](images/Graph%20Building%20Sequence.png) | Knowledge graph construction |
| Indexing Overview | [indexing-sequences.md](indexing-sequences.md) | [PNG](images/Indexing%20Overview.png) | High-level indexing flow |

## CLI Sequences (PlantUML)

| Diagram | Source | Image | Description |
|---------|--------|-------|-------------|
| Server Start | [cli-sequences.md](cli-sequences.md) | [PNG](images/Server%20Start%20Sequence.png) | `agent-brain start` flow |
| Server Stop | [cli-sequences.md](cli-sequences.md) | [PNG](images/Server%20Stop%20Sequence.png) | `agent-brain stop` flow |
| Query Command | [cli-sequences.md](cli-sequences.md) | [PNG](images/Query%20Sequence.png) | `agent-brain query` flow |
| Status Check | [cli-sequences.md](cli-sequences.md) | [PNG](images/Status%20Check%20Sequence.png) | `agent-brain status` flow |
| Index Command | [cli-sequences.md](cli-sequences.md) | [PNG](images/Index%20Command%20Sequence.png) | `agent-brain index` flow |

## Server States (PlantUML)

| Diagram | Source | Image | Description |
|---------|--------|-------|-------------|
| Lifecycle States | [server-states.md](server-states.md) | [PNG](images/Server%20Lifecycle%20States.png) | Server state machine |
| Index States | [server-states.md](server-states.md) | [PNG](images/Index%20States.png) | Indexing state machine |
| Health States | [server-states.md](server-states.md) | [PNG](images/Health%20States.png) | Health check states |
| State Summary | [server-states.md](server-states.md) | [PNG](images/State%20Machine%20Summary.png) | Combined state overview |

## Deployment Diagrams (PlantUML)

| Diagram | Source | Image | Description |
|---------|--------|-------|-------------|
| Deployment Overview | [deployment-diagram.md](deployment-diagram.md) | [PNG](images/Agent%20Brain%20Deployment%20Overview.png) | Top-level deployment view |
| Local Development | [deployment-diagram.md](deployment-diagram.md) | [PNG](images/Local%20Development%20Deployment.png) | Developer machine setup |
| Multi-Instance | [deployment-diagram.md](deployment-diagram.md) | [PNG](images/Multi-Instance%20Deployment.png) | Per-project instances |
| Docker | [deployment-diagram.md](deployment-diagram.md) | [PNG](images/Docker%20Deployment.png) | Container deployment |
| Environment Config | [deployment-diagram.md](deployment-diagram.md) | [PNG](images/Environment%20Configuration.png) | Environment variables |

## Directory Structure

```
docs/design/
├── DIAGRAMS.md              # This index file
├── src/                     # Source diagram files
│   ├── *.puml              # PlantUML source files (36)
│   └── *.mmd               # Mermaid source files (57)
├── images/                  # Generated PNG images (93)
│   └── *.png               # Generated diagram images
├── architecture-overview.md # Architecture documentation
├── query-architecture.md    # Query flow documentation
├── indexing-pipeline.md     # Indexing documentation
├── storage-architecture.md  # Storage documentation
├── class-diagrams.md        # Class model documentation
├── deployment-architecture.md # Deployment documentation
├── component-diagrams.md    # Component documentation
├── package-diagrams.md      # Package documentation
├── query-sequences.md       # Query sequence diagrams
├── indexing-sequences.md    # Indexing sequence diagrams
├── cli-sequences.md         # CLI sequence diagrams
├── server-states.md         # State machine diagrams
└── deployment-diagram.md    # Deployment diagrams
```

## Regenerating Images

To regenerate all diagram images:

```bash
# Generate PlantUML images
cd docs/design
plantuml -tpng -o images src/*.puml

# Generate Mermaid images
for f in src/*.mmd; do
    name=$(basename "$f" .mmd)
    mmdc -i "$f" -o "images/${name}.png" -w 1200 -b transparent
done
```

### Prerequisites

- **PlantUML**: `brew install plantuml` (macOS) or download from [plantuml.com](https://plantuml.com/)
- **Mermaid CLI**: `npm install -g @mermaid-js/mermaid-cli`
- **Java**: Required for PlantUML (`brew install openjdk`)

## Viewing Diagrams

- **GitHub**: Mermaid diagrams render natively in markdown files
- **VS Code**: Use "Markdown Preview Mermaid Support" extension
- **Images**: All PNG images are in the `images/` directory
- **PlantUML**: Use PlantUML VS Code extension or online viewer
