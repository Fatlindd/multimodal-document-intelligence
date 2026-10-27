import pytest
from pydantic import ValidationError

from app.schemas import InvoiceData


def test_valid_dates():
    invoice = InvoiceData(issue_date="2026-10-20", due_date="2026-10-30")
    assert invoice.issue_date == "2026-10-20"
    assert invoice.due_date == "2026-10-30"


def test_invalid_date_order():
    with pytest.raises(ValidationError) as exc_info:
        InvoiceData(issue_date="2026-10-20", due_date="2026-10-10")
    assert "due_date cannot be earlier than issue_date" in str(exc_info.value)


def test_missing_due_date():
    invoice = InvoiceData(issue_date="2026-10-20")
    assert invoice.due_date is None
