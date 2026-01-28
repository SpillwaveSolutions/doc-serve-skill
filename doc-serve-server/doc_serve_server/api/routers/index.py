"""Indexing endpoints for document processing."""

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status

from doc_serve_server.models import IndexRequest, IndexResponse

router = APIRouter()


@router.post(
    "/",
    response_model=IndexResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Index Documents",
    description="Start indexing documents from a folder.",
)
async def index_documents(
    request_body: IndexRequest, request: Request
) -> IndexResponse:
    """Start indexing documents from the specified folder.

    This endpoint initiates a background indexing job and returns immediately.
    Use the /health/status endpoint to monitor progress.

    Args:
        request_body: IndexRequest with folder_path and optional configuration.
        request: FastAPI request for accessing app state.

    Returns:
        IndexResponse with job_id and status.

    Raises:
        400: Invalid folder path
        409: Indexing already in progress
    """
    # Validate folder path
    folder_path = Path(request_body.folder_path).expanduser().resolve()

    if not folder_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Folder not found: {request_body.folder_path}",
        )

    if not folder_path.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Path is not a directory: {request_body.folder_path}",
        )

    if not os.access(folder_path, os.R_OK):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot read folder: {request_body.folder_path}",
        )

    # Get indexing service from app state
    indexing_service = request.app.state.indexing_service

    # Check if already indexing
    if indexing_service.is_indexing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Indexing already in progress. Please wait for completion.",
        )

    # Start indexing
    try:
        # Update request with resolved path
        resolved_request = IndexRequest(
            folder_path=str(folder_path),
            chunk_size=request_body.chunk_size,
            chunk_overlap=request_body.chunk_overlap,
            recursive=request_body.recursive,
            include_code=request_body.include_code,
            supported_languages=request_body.supported_languages,
            code_chunk_strategy=request_body.code_chunk_strategy,
            include_patterns=request_body.include_patterns,
            exclude_patterns=request_body.exclude_patterns,
            generate_summaries=request_body.generate_summaries,
        )
        job_id = await indexing_service.start_indexing(resolved_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start indexing: {str(e)}",
        ) from e

    return IndexResponse(
        job_id=job_id,
        status="started",
        message=f"Indexing started for {request_body.folder_path}",
    )


@router.post(
    "/add",
    response_model=IndexResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Add Documents",
    description="Add documents from another folder to the existing index.",
)
async def add_documents(request_body: IndexRequest, request: Request) -> IndexResponse:
    """Add documents from a new folder to the existing index.

    This is similar to the index endpoint but adds to the existing
    vector store instead of replacing it.

    Args:
        request_body: IndexRequest with folder_path and optional configuration.
        request: FastAPI request for accessing app state.

    Returns:
        IndexResponse with job_id and status.
    """
    # Same validation as index_documents
    folder_path = Path(request_body.folder_path).expanduser().resolve()

    if not folder_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Folder not found: {request_body.folder_path}",
        )

    if not folder_path.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Path is not a directory: {request_body.folder_path}",
        )

    indexing_service = request.app.state.indexing_service

    if indexing_service.is_indexing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Indexing already in progress. Please wait for completion.",
        )

    try:
        resolved_request = IndexRequest(
            folder_path=str(folder_path),
            chunk_size=request_body.chunk_size,
            chunk_overlap=request_body.chunk_overlap,
            recursive=request_body.recursive,
            include_code=request_body.include_code,
            supported_languages=request_body.supported_languages,
            code_chunk_strategy=request_body.code_chunk_strategy,
            include_patterns=request_body.include_patterns,
            exclude_patterns=request_body.exclude_patterns,
        )
        job_id = await indexing_service.start_indexing(resolved_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add documents: {str(e)}",
        ) from e

    return IndexResponse(
        job_id=job_id,
        status="started",
        message=f"Adding documents from {request_body.folder_path}",
    )


@router.delete(
    "/",
    response_model=IndexResponse,
    summary="Reset Index",
    description="Delete all indexed documents and reset the vector store.",
)
async def reset_index(request: Request) -> IndexResponse:
    """Reset the index by deleting all stored documents.

    Warning: This permanently removes all indexed content.

    Args:
        request: FastAPI request for accessing app state.

    Returns:
        IndexResponse confirming the reset.

    Raises:
        409: Indexing in progress
    """
    indexing_service = request.app.state.indexing_service

    if indexing_service.is_indexing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot reset while indexing is in progress.",
        )

    try:
        await indexing_service.reset()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset index: {str(e)}",
        ) from e

    return IndexResponse(
        job_id="reset",
        status="completed",
        message="Index has been reset successfully",
    )
