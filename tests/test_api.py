import pymupdf
from fastapi.testclient import TestClient

from app.ai_extractor import AIOutputValidationError, AIServiceError
from app.main import app
from app.request_context import get_request_id
from app.schemas import ExtractionResponse

client = TestClient(app)

document = pymupdf.open()
document.new_page()
pdf_bytes = document.tobytes()
document.close()

empty_pdf = b"""%PDF-1.1
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Count 0 /Kids [] >>
endobj
trailer
<< /Root 1 0 R >>
%%EOF
"""


def upload(filename, content, content_type):
    return client.post(
        "/documents/upload",
        files={"file": (filename, content, content_type)},
    )


def assert_api_error(response, status_code, code, message):
    assert response.status_code == status_code
    assert response.headers["X-Request-ID"]
    assert response.json() == {
        "error": {
            "code": code,
            "message": message,
        }
    }


def test_successful_pdf_upload(monkeypatch):
    def extract_pdf_document(content):
        return ExtractionResponse(
            document_type="invoice",
            data={"vendor": "Acme", "total": 42.0},
            warnings=[],
            metadata={"page_count": 1, "request_id": get_request_id()},
        )

    monkeypatch.setattr("app.main.extract_pdf_document", extract_pdf_document)

    response = upload("invoice.pdf", pdf_bytes, "application/pdf")
    body = response.json()

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    assert body["document_type"] == "invoice"
    assert body["data"] == {"vendor": "Acme", "total": 42.0}
    assert body["warnings"] == []
    assert body["metadata"]["page_count"] == 1
    assert body["metadata"]["request_id"] == response.headers["X-Request-ID"]


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["X-Request-ID"]


def test_unsupported_file_type():
    response = upload("notes.txt", b"hello", "text/plain")
    assert_api_error(response, 415, "unsupported_file_type", "Unsupported file type")


def test_file_too_large():
    content = b"x" * (10 * 1024 * 1024 + 1)
    response = upload("large.pdf", content, "application/pdf")
    assert_api_error(response, 413, "file_too_large", "File too large")


def test_invalid_pdf():
    response = upload("bad.pdf", b"not a pdf", "application/pdf")
    assert_api_error(response, 400, "invalid_pdf", "Invalid or corrupted PDF")


def test_empty_pdf():
    response = upload("empty.pdf", empty_pdf, "application/pdf")
    assert_api_error(response, 400, "empty_pdf", "PDF contains no pages")


def test_unsupported_document_type(monkeypatch):
    monkeypatch.setattr(
        "app.extraction_pipeline.classify_document",
        lambda text, image_bytes: "purchase_order",
    )

    response = upload("doc.pdf", pdf_bytes, "application/pdf")
    assert_api_error(
        response,
        422,
        "unsupported_document_type",
        "Unsupported document type",
    )


def test_ai_output_validation_failure(monkeypatch):
    monkeypatch.setattr(
        "app.extraction_pipeline.classify_document",
        lambda text, image_bytes: "invoice",
    )

    def fail(text, image_bytes, document_type):
        raise AIOutputValidationError("AI output failed validation")

    monkeypatch.setattr(
        "app.extraction_pipeline.extract_structured_document",
        fail,
    )

    response = upload("doc.pdf", pdf_bytes, "application/pdf")
    assert_api_error(
        response,
        422,
        "ai_output_validation_failed",
        "AI output failed validation",
    )


def test_ai_service_failure(monkeypatch):
    def fail(text, image_bytes):
        raise AIServiceError("AI service unavailable")

    monkeypatch.setattr("app.extraction_pipeline.classify_document", fail)

    response = upload("doc.pdf", pdf_bytes, "application/pdf")
    assert_api_error(
        response,
        503,
        "ai_service_unavailable",
        "AI service unavailable",
    )
