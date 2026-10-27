import pytest

from app.schema_registry import get_schema_for_document_type
from app.schemas import ContractData, CVData, InvoiceData, ReceiptData


def test_supported_document_types():
    assert get_schema_for_document_type("invoice") is InvoiceData
    assert get_schema_for_document_type("receipt") is ReceiptData
    assert get_schema_for_document_type("cv") is CVData
    assert get_schema_for_document_type("contract") is ContractData


def test_unsupported_document_type():
    with pytest.raises(ValueError) as exc_info:
        get_schema_for_document_type("other")
    assert str(exc_info.value) == "Unsupported document type"
