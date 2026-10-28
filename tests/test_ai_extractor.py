import httpx2
import pytest
from openai import APIConnectionError, APIError
from pydantic import BaseModel

from app.ai_extractor import (
    AIOutputValidationError,
    AIServiceError,
    _call_with_retry,
    classify_document,
    extract_structured_document,
)


def raise_api_error(*args, **kwargs):
    request = httpx2.Request("POST", "https://api.openai.com/v1/responses")
    raise APIError("service down", request, body=None)


def test_classify_document_api_error(monkeypatch):
    monkeypatch.setattr("app.ai_extractor.client.responses.create", raise_api_error)

    with pytest.raises(AIServiceError) as exc_info:
        classify_document("invoice text", b"image")

    assert "AI service unavailable" in str(exc_info.value)


def test_extract_structured_document_api_error(monkeypatch):
    monkeypatch.setattr("app.ai_extractor.client.responses.parse", raise_api_error)

    with pytest.raises(AIServiceError):
        extract_structured_document("invoice text", b"image", "invoice")


def test_extract_structured_document_validation_error(monkeypatch):
    class RequiredValue(BaseModel):
        value: int

    def raise_validation_error(*args, **kwargs):
        RequiredValue.model_validate({})

    monkeypatch.setattr(
        "app.ai_extractor.client.responses.parse",
        raise_validation_error,
    )

    with pytest.raises(AIOutputValidationError) as exc_info:
        extract_structured_document("invoice text", b"image", "invoice")

    assert "AI output failed validation" in str(exc_info.value)


def connection_error():
    request = httpx2.Request("POST", "https://api.openai.com/v1/responses")
    return APIConnectionError(message="Connection error.", request=request)


def test_call_with_retry_succeeds_on_second_attempt():
    calls = 0

    def operation():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise connection_error()
        return "ok"

    result = _call_with_retry(operation, max_attempts=2)

    assert result == "ok"
    assert calls == 2


def test_call_with_retry_exhausts_attempts():
    calls = 0

    def operation():
        nonlocal calls
        calls += 1
        raise connection_error()

    with pytest.raises(AIServiceError) as exc_info:
        _call_with_retry(operation, max_attempts=2)

    assert calls == 2
    assert "AI service unavailable" in str(exc_info.value)
