import base64

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
)
from pydantic import ValidationError

from app.ai_client import client
from app.schema_registry import get_schema_for_document_type


class AIServiceError(Exception):
    pass


class AIOutputValidationError(Exception):
    pass


def _call_with_retry(operation, max_attempts: int = 2):
    for attempt in range(max_attempts):
        try:
            return operation()
        except (
            APITimeoutError,
            APIConnectionError,
            RateLimitError,
            InternalServerError,
        ) as exc:
            if attempt == max_attempts - 1:
                raise AIServiceError("AI service unavailable") from exc


def test_openai_connection():
    response = client.responses.create(
        model="gpt-6-astra",
        input="Reply with exactly: connection ok",
    )
    return response.output_text


def extract_document_text(text: str):
    response = client.responses.create(
        model="gpt-6-astra",
        input=(
            "Identify the document type, extract the most important fields you can find, "
            "and return the answer as concise plain text.\n\n"
            f"{text}"
        ),
    )
    return response.output_text


def extract_document_multimodal(text: str, image_bytes: bytes):
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:image/png;base64,{encoded_image}"
    response = client.responses.create(
        model="gpt-6-astra",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Identify the document type, extract the most important fields, "
                            "use both the provided text and the page image, "
                            "and return concise plain text."
                        ),
                    },
                    {"type": "input_text", "text": text},
                    {"type": "input_image", "image_url": data_url},
                ],
            }
        ],
    )
    return response.output_text


def classify_document(text: str, image_bytes: bytes):
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:image/png;base64,{encoded_image}"
    try:
        response = _call_with_retry(
            lambda: client.responses.create(
                model="gpt-6-astra",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    "Classify the document into exactly one of: "
                                    "invoice, receipt, cv, contract. "
                                    "Use both the provided text and the page image. "
                                    "Return only the lowercase label and nothing else."
                                ),
                            },
                            {"type": "input_text", "text": text},
                            {"type": "input_image", "image_url": data_url},
                        ],
                    }
                ],
            )
        )
    except APIError as exc:
        raise AIServiceError("AI service unavailable") from exc
    return response.output_text.strip().lower()


def extract_structured_document(text: str, image_bytes: bytes, document_type: str):
    schema = get_schema_for_document_type(document_type)
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:image/png;base64,{encoded_image}"
    try:
        response = _call_with_retry(
            lambda: client.responses.parse(
                model="gpt-6-astra",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    "Extract the document fields according to the provided schema. "
                                    "Use both the provided text and the page image."
                                ),
                            },
                            {"type": "input_text", "text": text},
                            {"type": "input_image", "image_url": data_url},
                        ],
                    }
                ],
                text_format=schema,
            )
        )
    except APIError as exc:
        raise AIServiceError("AI service unavailable") from exc
    except ValidationError as exc:
        raise AIOutputValidationError("AI output failed validation") from exc
    return response.output_parsed
