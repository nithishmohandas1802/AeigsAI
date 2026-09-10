from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.services.document_service import ingest_document


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    status_code=status.HTTP_200_OK,
)
async def upload_document(
    file: UploadFile = File(...),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are supported",
        )

    file_content = await file.read()

    result = ingest_document(
        filename=file.filename or "unknown.pdf",
        file_content=file_content,
    )

    return result
