from app.services.pdf_extraction_service import extract_pdf_text


def ingest_document(
    filename: str,
    file_content: bytes,
) -> dict:
    """
    Ingest a document and extract its contents.
    """

    extraction_result = extract_pdf_text(file_content)

    return {
        "filename": filename,
        "page_count": extraction_result["page_count"],
        "pages": extraction_result["pages"],
    }
