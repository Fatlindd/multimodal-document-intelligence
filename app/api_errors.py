def api_error(code: str, message: str) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
        }
    }
