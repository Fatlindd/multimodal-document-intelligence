from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.ai_extractor import AIOutputValidationError, AIServiceError
from app.document_parser import EmptyPDFError, InvalidPDFError
from app.extraction_pipeline import extract_pdf_document
from app.schema_registry import UnsupportedDocumentTypeError

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
        try:
            return extract_pdf_document(contents)
        except InvalidPDFError:
            raise HTTPException(status_code=400, detail="Invalid or corrupted PDF")
        except EmptyPDFError:
            raise HTTPException(status_code=400, detail="PDF contains no pages")
        except UnsupportedDocumentTypeError:
            raise HTTPException(status_code=422, detail="Unsupported document type")
        except AIOutputValidationError:
            raise HTTPException(status_code=422, detail="AI output failed validation")
        except AIServiceError:
            raise HTTPException(status_code=503, detail="AI service unavailable")
    return {
        "filename": file.filename,
        "content_type": file.content_type,
    }
