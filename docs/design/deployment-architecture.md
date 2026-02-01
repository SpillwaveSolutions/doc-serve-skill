# Deployment Architecture

This document details Agent Brain's deployment options, from local development to production configurations.

## Deployment Overview

Agent Brain supports multiple deployment modes optimized for different use cases.

```mermaid
flowchart TB
    subgraph DevLocal["Local Development"]
        direction TB
        LocalServer[Single Server<br/>127.0.0.1:8000]
        LocalCLI[CLI + Plugin]
        LocalStorage[(Local Files)]
        LocalServer --> LocalStorage
        LocalCLI --> LocalServer
    end

    subgraph MultiInstance["Multi-Instance (Per-Project)"]
        direction TB
        ProjectA[Project A Server<br/>:8001]
        ProjectB[Project B Server<br/>:8002]
        ProjectC[Project C Server<br/>:8003]
        StateA[".claude/agent-brain/"]
        StateB[".claude/agent-brain/"]
        StateC[".claude/agent-brain/"]
        ProjectA --> StateA
        ProjectB --> StateB
        ProjectC --> StateC
    end

    subgraph Production["Production Deployment"]
        direction TB
        LB[Load Balancer]
        Server1[Server Instance 1]
        Server2[Server Instance 2]
        SharedStorage[(Shared Storage<br/>NFS/S3)]
        LB --> Server1
        LB --> Server2
        Server1 --> SharedStorage
        Server2 --> SharedStorage
    end

    OpenAI[OpenAI API]
    DevLocal --> OpenAI
    MultiInstance --> OpenAI
    Production --> OpenAI

    classDef local fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef multi fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef prod fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black
    classDef external fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue

    class LocalServer,LocalCLI,LocalStorage local
    class ProjectA,ProjectB,ProjectC,StateA,StateB,StateC multi
    class LB,Server1,Server2,SharedStorage prod
    class OpenAI external
```

## Local Development Setup

The simplest deployment for individual developer use.

### Architecture

```mermaid
flowchart LR
    subgraph Developer["Developer Machine"]
        direction TB
        Terminal[Terminal]
        ClaudeCode[Claude Code]

        subgraph CLI["agent-brain CLI"]
            Commands[Commands]
            APIClient[API Client]
        end

        subgraph Server["agent-brain-serve"]
            FastAPI[FastAPI]
            Services[Services]
            Storage[(Local Storage)]
        end

        Terminal --> Commands
        ClaudeCode --> Commands
        Commands --> APIClient
        APIClient -->|"HTTP :8000"| FastAPI
        FastAPI --> Services
        Services --> Storage
    end

    External[OpenAI API]
    Services --> External

    classDef local fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef process fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef storage fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue
    classDef external fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black

    class Terminal,ClaudeCode local
    class Commands,APIClient,FastAPI,Services process
    class Storage storage
    class External external
```

### Quick Start

```bash
# 1. Install packages
pip install agent-brain-rag agent-brain-cli

# 2. Configure API key
export OPENAI_API_KEY="sk-proj-..."

# 3. Start server
agent-brain-serve

# 4. Index documents (in another terminal)
agent-brain index /path/to/docs

# 5. Query
agent-brain query "how does authentication work"
```

### Directory Structure

```
./                           # Working directory
├── chroma_db/              # Vector database
├── bm25_index/             # Keyword index
├── graph_index/            # Graph store (if enabled)
└── .env                    # Environment variables
```

### Configuration

```bash
# .env file
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...  # Optional, for summaries
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=false
```

## Multi-Instance Architecture

Recommended deployment for developers working on multiple projects.

### Architecture

```mermaid
flowchart TB
    subgraph ClaudeCode["Claude Code"]
        Plugin[Agent Brain Plugin]
    end

    subgraph System["Developer System"]
        direction TB
        CLI[agent-brain CLI]

        subgraph ProjectA["~/projects/project-a/"]
            ServerA["Server :8001<br/>PID: 12345"]
            StateA[".claude/agent-brain/"]
            DocsA["/docs/"]
        end

        subgraph ProjectB["~/projects/project-b/"]
            ServerB["Server :8002<br/>PID: 12346"]
            StateB[".claude/agent-brain/"]
            DocsB["/src/"]
        end
    end

    Plugin --> CLI
    CLI -->|"Detect project"| ServerA
    CLI -->|"Detect project"| ServerB
    ServerA --> StateA
    ServerB --> StateB
    ServerA -.->|"Index"| DocsA
    ServerB -.->|"Index"| DocsB

    classDef plugin fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef server fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef state fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black
    classDef docs fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue

    class Plugin plugin
    class ServerA,ServerB,CLI server
    class StateA,StateB state
    class DocsA,DocsB docs
```

### Per-Project State

Each project maintains isolated state:

```
~/projects/project-a/
├── .claude/
│   └── agent-brain/
│       ├── lock.json           # Instance lock
│       ├── runtime.json        # Server info
│       ├── config.json         # Project config
│       ├── chroma_db/          # Vector store
│       ├── bm25_index/         # Keyword index
│       └── graph_index/        # Graph store
├── src/
└── docs/
```

### Initialization

```bash
# Navigate to project
cd ~/projects/project-a

# Initialize Agent Brain for this project
agent-brain init

# Start server (auto-assigns port)
agent-brain start

# Check status
agent-brain status
```

### Port Allocation

```mermaid
sequenceDiagram
    participant CLI
    participant Server
    participant OS
    participant Runtime as runtime.json

    CLI->>Server: Start with --port 0
    Server->>OS: Bind to port 0
    OS-->>Server: Assigned port 8001
    Server->>Runtime: Write {port: 8001}
    Server-->>CLI: Started

    Note over CLI: Later commands
    CLI->>Runtime: Read port
    Runtime-->>CLI: port: 8001
    CLI->>Server: Connect to :8001
```

### List All Instances

```bash
$ agent-brain list
Instance                     Port   PID    Status
~/projects/project-a         8001   12345  Running
~/projects/project-b         8002   12346  Running
~/projects/project-c         -      -      Stopped
```

## Production Deployment Options

### Option 1: Single Server with Persistence

Basic production setup for small teams.

```mermaid
flowchart TB
    subgraph Cloud["Cloud VM"]
        direction TB
        Nginx[Nginx Reverse Proxy]
        Supervisor[Supervisor]
        Server[agent-brain-serve]

        subgraph Storage["Persistent Volume"]
            ChromaDB[(ChromaDB)]
            BM25[(BM25 Index)]
        end
    end

    Users[Users/Clients]
    OpenAI[OpenAI API]

    Users -->|"HTTPS :443"| Nginx
    Nginx -->|":8000"| Server
    Supervisor -.->|"Manages"| Server
    Server --> Storage
    Server --> OpenAI

    classDef proxy fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef server fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef storage fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue
    classDef external fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black

    class Nginx proxy
    class Supervisor,Server server
    class ChromaDB,BM25 storage
    class Users,OpenAI external
```

#### Supervisor Configuration

```ini
# /etc/supervisor/conf.d/agent-brain.conf
[program:agent-brain]
command=/path/to/venv/bin/agent-brain-serve --host 0.0.0.0 --port 8000
directory=/opt/agent-brain
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/agent-brain/error.log
stdout_logfile=/var/log/agent-brain/output.log
environment=OPENAI_API_KEY="sk-...",CHROMA_PERSIST_DIR="/data/chroma_db"
```

#### Nginx Configuration

```nginx
# /etc/nginx/sites-available/agent-brain
server {
    listen 443 ssl;
    server_name agent-brain.example.com;

    ssl_certificate /etc/letsencrypt/live/agent-brain.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/agent-brain.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Option 2: Docker Deployment

Containerized deployment for portability.

```mermaid
flowchart TB
    subgraph Docker["Docker Host"]
        direction TB
        Compose[Docker Compose]

        subgraph Network["agent-brain-network"]
            Traefik[Traefik Proxy]
            Server1[agent-brain:8000]
            Server2[agent-brain:8000]
        end

        subgraph Volumes["Docker Volumes"]
            ChromaVol[chroma-data]
            BM25Vol[bm25-data]
        end
    end

    Users[Users]
    OpenAI[OpenAI API]

    Users -->|"HTTPS"| Traefik
    Traefik --> Server1
    Traefik --> Server2
    Server1 --> ChromaVol
    Server1 --> BM25Vol
    Server2 --> ChromaVol
    Server2 --> BM25Vol
    Server1 --> OpenAI
    Server2 --> OpenAI

    classDef compose fill:#2496ED,stroke:#333,stroke-width:2px,color:white
    classDef container fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef volume fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue
    classDef external fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black

    class Compose compose
    class Traefik,Server1,Server2 container
    class ChromaVol,BM25Vol volume
    class Users,OpenAI external
```

#### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY agent-brain-server ./agent-brain-server

# Create non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

# Run server
CMD ["agent-brain-serve", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  agent-brain:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - CHROMA_PERSIST_DIR=/data/chroma_db
      - BM25_INDEX_PATH=/data/bm25_index
    volumes:
      - chroma-data:/data/chroma_db
      - bm25-data:/data/bm25_index
      - ./docs:/docs:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
    restart: unless-stopped

volumes:
  chroma-data:
  bm25-data:
```

### Option 3: Kubernetes Deployment

Enterprise-grade deployment with auto-scaling.

```mermaid
flowchart TB
    subgraph K8s["Kubernetes Cluster"]
        direction TB
        Ingress[Ingress Controller]

        subgraph Namespace["agent-brain namespace"]
            Service[Service :8000]
            Deploy[Deployment]
            HPA[HPA]

            subgraph Pods["Pods"]
                Pod1[Pod 1]
                Pod2[Pod 2]
                Pod3[Pod 3]
            end

            PVC[PersistentVolumeClaim]
            Secret[Secret]
            ConfigMap[ConfigMap]
        end

        subgraph Storage["Storage Class"]
            PV[PersistentVolume]
        end
    end

    Users[Users]
    OpenAI[OpenAI API]

    Users --> Ingress
    Ingress --> Service
    Service --> Pods
    Deploy --> Pods
    HPA --> Deploy
    Pods --> PVC
    Pods --> Secret
    Pods --> ConfigMap
    PVC --> PV
    Pods --> OpenAI

    classDef ingress fill:#326CE5,stroke:#333,stroke-width:2px,color:white
    classDef workload fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef storage fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue
    classDef config fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black
    classDef external fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen

    class Ingress ingress
    class Service,Deploy,HPA,Pod1,Pod2,Pod3 workload
    class PVC,PV storage
    class Secret,ConfigMap config
    class Users,OpenAI external
```

#### Kubernetes Manifests

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-brain
  namespace: agent-brain
spec:
  replicas: 2
  selector:
    matchLabels:
      app: agent-brain
  template:
    metadata:
      labels:
        app: agent-brain
    spec:
      containers:
        - name: agent-brain
          image: agent-brain:latest
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: agent-brain-secrets
            - configMapRef:
                name: agent-brain-config
          volumeMounts:
            - name: data
              mountPath: /data
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/status
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: agent-brain-pvc
---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: agent-brain
  namespace: agent-brain
spec:
  selector:
    app: agent-brain
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP
---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: agent-brain
  namespace: agent-brain
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - agent-brain.example.com
      secretName: agent-brain-tls
  rules:
    - host: agent-brain.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: agent-brain
                port:
                  number: 8000
```

## Environment Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for embeddings |
| `ANTHROPIC_API_KEY` | No | - | Anthropic key for summaries |
| `API_HOST` | No | 127.0.0.1 | Server bind address |
| `API_PORT` | No | 8000 | Server port |
| `DEBUG` | No | false | Enable debug logging |
| `CHROMA_PERSIST_DIR` | No | ./chroma_db | Vector DB path |
| `BM25_INDEX_PATH` | No | ./bm25_index | BM25 index path |
| `DOC_SERVE_STATE_DIR` | No | - | Override state directory |
| `DOC_SERVE_MODE` | No | project | project or shared |
| `ENABLE_GRAPH_INDEX` | No | false | Enable GraphRAG |
| `GRAPH_STORE_TYPE` | No | simple | simple or kuzu |

### Production Checklist

```mermaid
flowchart TB
    Start([Production Checklist])

    Start --> Security
    subgraph Security["Security"]
        S1[Set OPENAI_API_KEY securely]
        S2[Use HTTPS/TLS]
        S3[Configure CORS appropriately]
        S4[Run as non-root user]
    end

    Security --> Persistence
    subgraph Persistence["Persistence"]
        P1[Configure persistent storage]
        P2[Set up backup strategy]
        P3[Plan for data migration]
    end

    Persistence --> Monitoring
    subgraph Monitoring["Monitoring"]
        M1[Configure health checks]
        M2[Set up logging]
        M3[Add metrics endpoint]
        M4[Configure alerts]
    end

    Monitoring --> Scaling
    subgraph Scaling["Scaling"]
        SC1[Set resource limits]
        SC2[Configure HPA if K8s]
        SC3[Consider read replicas]
    end

    Scaling --> Complete([Ready for Production])

    classDef check fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef section fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue

    class Start,Complete check
    class S1,S2,S3,S4,P1,P2,P3,M1,M2,M3,M4,SC1,SC2,SC3 section
```

## Resource Requirements

### Minimum Requirements

| Resource | Development | Production |
|----------|-------------|------------|
| **CPU** | 1 core | 2 cores |
| **Memory** | 512 MB | 2 GB |
| **Disk** | 1 GB | 10 GB+ |
| **Network** | Local | Low latency to OpenAI |

### Sizing Guidelines

| Document Count | ChromaDB | BM25 | Memory | Recommended |
|----------------|----------|------|--------|-------------|
| < 1,000 | 50 MB | 5 MB | 512 MB | Single instance |
| 1,000 - 10,000 | 500 MB | 50 MB | 2 GB | Single instance |
| 10,000 - 100,000 | 5 GB | 500 MB | 8 GB | Consider scaling |
| > 100,000 | 50 GB+ | 5 GB+ | 32 GB+ | Distributed storage |

## Monitoring and Health Checks

### Health Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Basic liveness check |
| `/health/status` | GET | Detailed status with indexing info |

### Health Check Response

```json
{
  "status": "healthy",
  "version": "1.2.0",
  "mode": "project",
  "instance_id": "abc123",
  "indexing": {
    "status": "completed",
    "total_chunks": 1500,
    "folder_path": "/docs"
  }
}
```

### Monitoring Integration

```mermaid
flowchart LR
    Server[Agent Brain Server]

    subgraph Monitoring["Monitoring Stack"]
        Prometheus[Prometheus]
        Grafana[Grafana]
        AlertManager[AlertManager]
    end

    subgraph Logging["Logging Stack"]
        Fluentd[Fluentd]
        Elasticsearch[Elasticsearch]
        Kibana[Kibana]
    end

    Server -->|"/metrics"| Prometheus
    Prometheus --> Grafana
    Prometheus --> AlertManager

    Server -->|"stdout/stderr"| Fluentd
    Fluentd --> Elasticsearch
    Elasticsearch --> Kibana

    classDef server fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef monitor fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef logging fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black

    class Server server
    class Prometheus,Grafana,AlertManager monitor
    class Fluentd,Elasticsearch,Kibana logging
```

## Backup and Recovery

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/agent-brain/$(date +%Y%m%d)"
STATE_DIR="/data/agent-brain"

mkdir -p "$BACKUP_DIR"

# Stop writes (optional, for consistency)
# curl -X POST http://localhost:8000/admin/pause

# Backup ChromaDB
tar -czf "$BACKUP_DIR/chroma_db.tar.gz" -C "$STATE_DIR" chroma_db

# Backup BM25 index
tar -czf "$BACKUP_DIR/bm25_index.tar.gz" -C "$STATE_DIR" bm25_index

# Backup graph index (if enabled)
if [ -d "$STATE_DIR/graph_index" ]; then
    tar -czf "$BACKUP_DIR/graph_index.tar.gz" -C "$STATE_DIR" graph_index
fi

# Resume writes
# curl -X POST http://localhost:8000/admin/resume

echo "Backup completed: $BACKUP_DIR"
```

### Recovery Procedure

```bash
#!/bin/bash
# restore.sh

BACKUP_DIR="/backups/agent-brain/20240115"
STATE_DIR="/data/agent-brain"

# Stop server
systemctl stop agent-brain

# Clear existing data
rm -rf "$STATE_DIR/chroma_db" "$STATE_DIR/bm25_index" "$STATE_DIR/graph_index"

# Restore from backup
tar -xzf "$BACKUP_DIR/chroma_db.tar.gz" -C "$STATE_DIR"
tar -xzf "$BACKUP_DIR/bm25_index.tar.gz" -C "$STATE_DIR"
[ -f "$BACKUP_DIR/graph_index.tar.gz" ] && tar -xzf "$BACKUP_DIR/graph_index.tar.gz" -C "$STATE_DIR"

# Start server
systemctl start agent-brain

echo "Recovery completed from: $BACKUP_DIR"
```
