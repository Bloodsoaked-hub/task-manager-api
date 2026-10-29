from fastapi import APIRouter, Depends, File, UploadFile

from app.services.s3_service import S3service

router = APIRouter(prefix="/documents", tags=["RAG Documents"])

@router.post("/upload")
async def upload_document_for_rag(
    file: UploadFile = File(...), s3_service: S3service = Depends()
):
    s3_key = s3_service.upload_rag_document(file)
    document_text = s3_service.read_rag_document(s3_key)

    return {
        "status": "success",
        "message": "Document successfully stored in AWS S3 and prepared for RAG",
        "s3_key": s3_key,
        "character_count": len(document_text),
    }