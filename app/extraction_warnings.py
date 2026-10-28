INVOICE_FIELDS = ("vendor", "invoice_number", "total")


def build_extraction_warnings(document_type: str, data: dict) -> list[str]:
    if document_type != "invoice":
        return []
    return [
        f"Missing extracted field: {field}"
        for field in INVOICE_FIELDS
        if data.get(field) is None
    ]
