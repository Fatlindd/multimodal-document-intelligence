from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class ExtractionResponse(BaseModel):
    document_type: Literal["invoice", "receipt", "cv", "contract"]
    data: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InvoiceData(BaseModel):
    vendor: str | None = None
    invoice_number: str | None = None
    issue_date: str | None = None
    due_date: str | None = None
    currency: str | None = None
    subtotal: float | None = None
    tax: float | None = None
    total: float | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.issue_date is not None and self.due_date is not None:
            issue_date = date.fromisoformat(self.issue_date)
            due_date = date.fromisoformat(self.due_date)
            if due_date < issue_date:
                raise ValueError("due_date cannot be earlier than issue_date")
        return self


class ReceiptData(BaseModel):
    merchant: str | None = None
    purchase_date: str | None = None
    purchase_time: str | None = None
    currency: str | None = None
    subtotal: float | None = None
    tax: float | None = None
    total: float | None = None


class CVData(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    summary: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)


class ContractData(BaseModel):
    parties: list[str] = Field(default_factory=list)
    contract_type: str | None = None
    effective_date: str | None = None
    expiration_date: str | None = None
    governing_law: str | None = None
    payment_terms: str | None = None
    summary: str | None = None
