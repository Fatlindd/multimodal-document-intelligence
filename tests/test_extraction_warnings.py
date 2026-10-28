from app.extraction_warnings import build_extraction_warnings


def test_invoice_missing_invoice_number():
    warnings = build_extraction_warnings(
        "invoice",
        {"vendor": "Acme", "invoice_number": None, "total": 42.0},
    )
    assert warnings == ["Missing extracted field: invoice_number"]


def test_invoice_complete():
    warnings = build_extraction_warnings(
        "invoice",
        {"vendor": "Acme", "invoice_number": "INV-1", "total": 42.0},
    )
    assert warnings == []


def test_non_invoice_document():
    warnings = build_extraction_warnings(
        "cv",
        {"full_name": None},
    )
    assert warnings == []
