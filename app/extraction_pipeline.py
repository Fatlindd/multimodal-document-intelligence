import time

from app.ai_extractor import classify_document, extract_structured_document
from app.document_parser import parse_pdf, render_pdf_pages
from app.extraction_warnings import build_extraction_warnings
from app.logging_config import get_logger
from app.request_context import get_request_id
from app.schemas import ExtractionResponse

logger = get_logger(__name__)


def _log_duration(operation: str, started: float) -> None:
    duration_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "operation completed request_id=%s operation=%s duration_ms=%.2f",
        get_request_id(),
        operation,
        duration_ms,
    )


def extract_pdf_document(content: bytes):
    started = time.perf_counter()
    try:
        parsed = parse_pdf(content)
    finally:
        _log_duration("parse_pdf", started)

    started = time.perf_counter()
    try:
        pages = render_pdf_pages(content)
    finally:
        _log_duration("render_pdf_pages", started)

    first_page_image = pages[0]
    started = time.perf_counter()
    try:
        document_type = classify_document(parsed["text"], first_page_image)
    finally:
        _log_duration("classify_document", started)
    logger.info(
        "document classified request_id=%s document_type=%s",
        get_request_id(),
        document_type,
    )

    started = time.perf_counter()
    try:
        structured_model = extract_structured_document(
            parsed["text"],
            first_page_image,
            document_type,
        )
    finally:
        _log_duration("extract_structured_document", started)
    data = structured_model.model_dump()
    return ExtractionResponse(
        document_type=document_type,
        data=data,
        warnings=build_extraction_warnings(document_type, data),
        metadata={
            "page_count": parsed["page_count"],
            "request_id": get_request_id(),
        },
    )
