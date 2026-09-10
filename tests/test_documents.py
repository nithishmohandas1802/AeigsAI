import pymupdf

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_test_pdf() -> bytes:
    document = pymupdf.open()

    page = document.new_page()
    page.insert_text(
        (72, 72),
        "AegisAI document upload test.",
    )

    pdf_bytes = document.tobytes()

    document.close()

    return pdf_bytes


def test_upload_pdf():
    pdf_bytes = create_test_pdf()

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.pdf",
                pdf_bytes,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "test.pdf"
    assert data["page_count"] == 1
    assert data["pages"][0]["page_number"] == 1
    assert "AegisAI document upload test." in data["pages"][0]["text"]


def test_upload_non_pdf():
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.txt",
                b"This is not a PDF.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 415


def test_upload_invalid_pdf():
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "invalid.pdf",
                b"not a real pdf",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_DOCUMENT"
    assert data["error"]["message"] == "Invalid PDF document"
    assert data["error"]["status"] == 400
