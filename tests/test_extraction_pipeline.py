import pymupdf
import pytest

from app.extraction_pipeline import extract_pdf_document
from app.schema_registry import UnsupportedDocumentTypeError
from app.schemas import ExtractionResponse, InvoiceData


def test_extract_pdf_document(monkeypatch):
    invoice = InvoiceData(vendor="Acme", invoice_number="INV-1", total=42.0)
    monkeypatch.setattr(
        "app.extraction_pipeline.classify_document",
        lambda text, image_bytes: "invoice",
    )
    monkeypatch.setattr(
        "app.extraction_pipeline.extract_structured_document",
        lambda text, image_bytes, document_type: invoice,
    )

    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Invoice from Acme")
    pdf_bytes = document.tobytes()
    document.close()

    result = extract_pdf_document(pdf_bytes)

    assert isinstance(result, ExtractionResponse)
    assert result.document_type == "invoice"
    assert result.data == invoice.model_dump()
    assert result.warnings == []
    assert result.metadata["page_count"] == 1


def test_extract_pdf_document_unsupported_type(monkeypatch):
    monkeypatch.setattr(
        "app.extraction_pipeline.classify_document",
        lambda text, image_bytes: "purchase_order",
    )

    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Purchase order")
    pdf_bytes = document.tobytes()
    document.close()

    with pytest.raises(UnsupportedDocumentTypeError):
        extract_pdf_document(pdf_bytes)
