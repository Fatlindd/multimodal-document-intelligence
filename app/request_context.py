import time
import uuid
from contextvars import ContextVar

from fastapi import FastAPI, Request

from app.logging_config import get_logger

logger = get_logger(__name__)
_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    return _request_id.get()


def register_request_id_middleware(app: FastAPI):
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        started = time.perf_counter()
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        token = _request_id.set(request_id)
        logger.info(
            "request started request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            duration_ms = (time.perf_counter() - started) * 1000
            logger.info(
                "request completed request_id=%s operation=%s status_code=%s duration_ms=%.2f",
                request_id,
                "request",
                response.status_code,
                duration_ms,
            )
            return response
        finally:
            _request_id.reset(token)
