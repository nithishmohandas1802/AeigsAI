import pymupdf

from app.exceptions import InvalidDocumentError


def extract_pdf_text(file_content: bytes) -> dict:
    """
    Extract text from a PDF while preserving page boundaries.
    """

    try:
        document = pymupdf.open(
            stream=file_content,
            filetype="pdf",
        )
    except Exception as exc:
        raise InvalidDocumentError() from exc

    pages = []

    try:
        for page_number, page in enumerate(document, start=1):
            pages.append(
                {
                    "page_number": page_number,
                    "text": page.get_text(),
                }
            )

        return {
            "page_count": len(document),
            "pages": pages,
        }

    finally:
        document.close()
