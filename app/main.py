from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.api_errors import api_error
from app.exception_handlers import register_exception_handlers
from app.extraction_pipeline import extract_pdf_document
from app.request_context import register_request_id_middleware

app = FastAPI()
register_exception_handlers(app)
register_request_id_middleware(app)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents/upload")
async def upload_document(file: Annotated[UploadFile, File()]):
    if file.content_type not in {"application/pdf", "image/png", "image/jpeg"}:
        raise HTTPException(
            status_code=415,
            detail=api_error("unsupported_file_type", "Unsupported file type"),
        )
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=api_error("file_too_large", "File too large"),
        )
    if file.content_type == "application/pdf":
        return await run_in_threadpool(
            extract_pdf_document,
            contents,
        )
    return {
        "filename": file.filename,
        "content_type": file.content_type,
    }
