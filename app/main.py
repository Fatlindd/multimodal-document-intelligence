from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.document_parser import parse_pdf

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents/upload")
async def upload_document(file: Annotated[UploadFile, File()]):
    if file.content_type not in {"application/pdf", "image/png", "image/jpeg"}:
        raise HTTPException(status_code=415, detail="Unsupported file type")
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")
    if file.content_type == "application/pdf":
        parsed = parse_pdf(contents)
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "page_count": parsed["page_count"],
            "text": parsed["text"],
        }
    return {
        "filename": file.filename,
        "content_type": file.content_type,
    }
