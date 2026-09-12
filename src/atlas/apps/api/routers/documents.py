"""Document ingestion and listing."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.apps.api.deps import runtime_dep, session_dep, settings_dep
from atlas.apps.api.errors import ApiError
from atlas.apps.api.schemas import PaginatedDocuments
from atlas.config.settings import Settings
from atlas.rag.ingestion import IngestionService
from atlas.repositories.document_repository import DocumentRepository
from atlas.security.uploads import UploadRejectedError
from atlas.services.runtime import Runtime

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(session_dep),
    settings: Settings = Depends(settings_dep),
    runtime: Runtime = Depends(runtime_dep),
) -> dict[str, str]:
    data = await file.read()
    service = IngestionService(session, runtime.embeddings, settings)
    try:
        document_id = await service.ingest_bytes(
            file.filename or "upload.txt",
            data,
            content_type=file.content_type,
        )
    except UploadRejectedError as exc:
        raise ApiError(str(exc), status_code=400, code="upload_rejected") from exc
    return {"document_id": document_id}


@router.get("", response_model=PaginatedDocuments)
async def list_documents(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(session_dep),
) -> PaginatedDocuments:
    rows = await DocumentRepository(session).list_documents(limit=limit, offset=offset)
    return PaginatedDocuments(
        items=[
            {
                "id": row.id,
                "filename": row.filename,
                "source": row.source,
                "content_type": row.content_type,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ],
        limit=limit,
        offset=offset,
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    session: AsyncSession = Depends(session_dep),
) -> dict[str, bool]:
    deleted = await DocumentRepository(session).delete(document_id)
    if not deleted:
        raise ApiError("document not found", status_code=404, code="not_found")
    await session.commit()
    return {"deleted": True}
