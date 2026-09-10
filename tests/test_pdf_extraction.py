import pymupdf
import pytest

from app.exceptions import InvalidDocumentError
from app.services.pdf_extraction_service import extract_pdf_text


def create_test_pdf() -> bytes:
    document = pymupdf.open()

    page = document.new_page()
    page.insert_text(
        (72, 72),
        "AegisAI PDF extraction test.",
    )

    pdf_bytes = document.tobytes()

    document.close()

    return pdf_bytes


def test_extract_pdf_text():
    pdf_bytes = create_test_pdf()

    result = extract_pdf_text(pdf_bytes)

    assert result["page_count"] == 1
    assert len(result["pages"]) == 1
    assert result["pages"][0]["page_number"] == 1
    assert "AegisAI PDF extraction test." in result["pages"][0]["text"]


def test_extract_invalid_pdf():
    with pytest.raises(
        InvalidDocumentError,
        match="Invalid PDF document",
    ):
        extract_pdf_text(b"not a real pdf")
