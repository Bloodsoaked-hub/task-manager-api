from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.services.embedding_service import EmbeddingService
from app.services.s3_service import S3service

router = APIRouter(prefix="/projects/{project_id}/documents", tags=["documents"])


@router.post("/upload")
async def upload_document_for_rag(
    project_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    s3_service: S3service = Depends(),
    embedding_service: EmbeddingService = Depends(),
):
    s3_key = s3_service.upload_rag_document(file)
    raw_text = s3_service.read_rag_document(s3_key)
    chunks = embedding_service.chunk_text(raw_text)


    chunk_objects = [
        DocumentChunk(
            project_id=project_id,
            s3_key=s3_key,
            content=chunk_text,
            embedding=embedding_service.generate_embedding(chunk_text),
        )
        for chunk_text in chunks
    ]

    db.add_all(chunk_objects)
    db.commit()

    return {
        "status": "success",
        "message": f"Stored {len(chunk_objects)} chunks for project {project_id}.",
        "s3_key": s3_key,
        "chunks_count": len(chunk_objects),
    }