from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import (
    http_exception_handler as default_http_exception_handler,
)
from fastapi.responses import JSONResponse

from app.ai_extractor import AIOutputValidationError, AIServiceError
from app.api_errors import api_error
from app.document_parser import EmptyPDFError, InvalidPDFError
from app.logging_config import get_logger
from app.schema_registry import UnsupportedDocumentTypeError

logger = get_logger(__name__)


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=api_error(code, message))


def _log_failure(request: Request, exc: Exception, status_code: int) -> None:
    request_id = getattr(request.state, "request_id", None)
    log = logger.error if status_code >= 500 else logger.warning
    log(
        "application failure request_id=%s exception_type=%s",
        request_id,
        type(exc).__name__,
    )


async def invalid_pdf_handler(request: Request, exc: InvalidPDFError):
    _log_failure(request, exc, 400)
    return _error_response(400, "invalid_pdf", "Invalid or corrupted PDF")


async def empty_pdf_handler(request: Request, exc: EmptyPDFError):
    _log_failure(request, exc, 400)
    return _error_response(400, "empty_pdf", "PDF contains no pages")


async def unsupported_document_type_handler(
    request: Request,
    exc: UnsupportedDocumentTypeError,
):
    _log_failure(request, exc, 422)
    return _error_response(422, "unsupported_document_type", "Unsupported document type")


async def ai_output_validation_handler(request: Request, exc: AIOutputValidationError):
    _log_failure(request, exc, 422)
    return _error_response(422, "ai_output_validation_failed", "AI output failed validation")


async def ai_service_error_handler(request: Request, exc: AIServiceError):
    _log_failure(request, exc, 503)
    return _error_response(503, "ai_service_unavailable", "AI service unavailable")


async def http_exception_handler(request: Request, exc: HTTPException):
    _log_failure(request, exc, exc.status_code)
    detail = exc.detail
    error = detail.get("error") if isinstance(detail, dict) else None
    if isinstance(error, dict) and "code" in error and "message" in error:
        return JSONResponse(status_code=exc.status_code, content=detail)
    return await default_http_exception_handler(request, exc)


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(InvalidPDFError, invalid_pdf_handler)
    app.add_exception_handler(EmptyPDFError, empty_pdf_handler)
    app.add_exception_handler(
        UnsupportedDocumentTypeError,
        unsupported_document_type_handler,
    )
    app.add_exception_handler(AIOutputValidationError, ai_output_validation_handler)
    app.add_exception_handler(AIServiceError, ai_service_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
