from app.schemas import ContractData, CVData, InvoiceData, ReceiptData


class UnsupportedDocumentTypeError(Exception):
    pass


SCHEMA_BY_TYPE = {
    "invoice": InvoiceData,
    "receipt": ReceiptData,
    "cv": CVData,
    "contract": ContractData,
}


def get_schema_for_document_type(document_type: str):
    if document_type not in SCHEMA_BY_TYPE:
        raise UnsupportedDocumentTypeError(
            f"Unsupported document type: {document_type}"
        )
    return SCHEMA_BY_TYPE[document_type]
