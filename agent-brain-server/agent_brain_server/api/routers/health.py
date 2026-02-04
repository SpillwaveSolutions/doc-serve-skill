"""Health check endpoints with non-blocking queue status."""

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Request

from agent_brain_server import __version__
from agent_brain_server.models import HealthStatus, IndexingStatus

router = APIRouter()


@router.get(
    "/",
    response_model=HealthStatus,
    summary="Health Check",
    description="Returns the current server health status.",
)
async def health_check(request: Request) -> HealthStatus:
    """Check server health status.

    This endpoint never blocks and always returns quickly.

    Returns:
        HealthStatus with current status:
        - healthy: Server is running and ready for queries
        - indexing: Server is currently indexing documents
        - degraded: Server is up but some services are unavailable
        - unhealthy: Server is not operational
    """
    vector_store = request.app.state.vector_store
    job_service = getattr(request.app.state, "job_service", None)

    # Determine status using queue service (non-blocking)
    status: Literal["healthy", "indexing", "degraded", "unhealthy"]
    message: str

    # Check queue status (non-blocking)
    is_indexing = False
    current_folder = None
    if job_service:
        try:
            queue_stats = await job_service.get_queue_stats()
            is_indexing = queue_stats.running > 0
            if is_indexing and queue_stats.current_job_id:
                # Get current job details for message
                current_job = await job_service.get_job(queue_stats.current_job_id)
                if current_job:
                    current_folder = current_job.folder_path
        except Exception:
            # Non-blocking: don't fail health check if queue service errors
            pass

    if is_indexing:
        status = "indexing"
        message = f"Indexing in progress: {current_folder or 'unknown'}"
    elif not vector_store.is_initialized:
        status = "degraded"
        message = "Vector store not initialized"
    else:
        status = "healthy"
        message = "Server is running and ready for queries"

    # Multi-instance metadata
    mode = getattr(request.app.state, "mode", "project")
    instance_id = getattr(request.app.state, "instance_id", None)
    project_id = getattr(request.app.state, "project_id", None)
    active_projects = getattr(request.app.state, "active_projects", None)

    return HealthStatus(
        status=status,
        message=message,
        timestamp=datetime.now(timezone.utc),
        version=__version__,
        mode=mode,
        instance_id=instance_id,
        project_id=project_id,
        active_projects=active_projects,
    )


@router.get(
    "/status",
    response_model=IndexingStatus,
    summary="Indexing Status",
    description="Returns detailed indexing status information. Never blocks.",
)
async def indexing_status(request: Request) -> IndexingStatus:
    """Get detailed indexing status.

    This endpoint never blocks and always returns quickly, even during indexing.

    Returns:
        IndexingStatus with:
        - total_documents: Number of documents indexed
        - total_chunks: Number of chunks in vector store
        - indexing_in_progress: Boolean indicating active indexing
        - queue_pending: Number of pending jobs
        - queue_running: Number of running jobs (0 or 1)
        - current_job_running_time_ms: How long current job has been running
        - last_indexed_at: Timestamp of last indexing operation
        - indexed_folders: List of folders that have been indexed
    """
    indexing_service = request.app.state.indexing_service
    vector_store = request.app.state.vector_store
    job_service = getattr(request.app.state, "job_service", None)

    # Get vector store count (non-blocking read)
    try:
        total_chunks = (
            await vector_store.get_count() if vector_store.is_initialized else 0
        )
    except Exception:
        total_chunks = 0

    # Get queue status (non-blocking)
    queue_pending = 0
    queue_running = 0
    current_job_id = None
    current_job_running_time_ms = None
    progress_percent = 0.0

    if job_service:
        try:
            queue_stats = await job_service.get_queue_stats()
            queue_pending = queue_stats.pending
            queue_running = queue_stats.running
            current_job_id = queue_stats.current_job_id
            current_job_running_time_ms = queue_stats.current_job_running_time_ms

            # Get progress from current job
            if current_job_id:
                current_job = await job_service.get_job(current_job_id)
                if current_job and current_job.progress:
                    progress_percent = current_job.progress.percent_complete
        except Exception:
            # Non-blocking: don't fail status if queue service errors
            pass

    # Get indexing service status for historical data
    # This is read-only and non-blocking
    service_status = await indexing_service.get_status()

    return IndexingStatus(
        total_documents=service_status.get("total_documents", 0),
        total_chunks=total_chunks,
        total_doc_chunks=service_status.get("total_doc_chunks", 0),
        total_code_chunks=service_status.get("total_code_chunks", 0),
        indexing_in_progress=queue_running > 0,
        current_job_id=current_job_id,
        progress_percent=progress_percent,
        last_indexed_at=(
            datetime.fromisoformat(service_status["completed_at"])
            if service_status.get("completed_at")
            else None
        ),
        indexed_folders=service_status.get("indexed_folders", []),
        supported_languages=service_status.get("supported_languages", []),
        graph_index=service_status.get("graph_index"),
        # Queue status (Feature 115)
        queue_pending=queue_pending,
        queue_running=queue_running,
        current_job_running_time_ms=current_job_running_time_ms,
    )
