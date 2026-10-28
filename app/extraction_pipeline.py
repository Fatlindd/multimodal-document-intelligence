from app.ai_extractor import classify_document, extract_structured_document
from app.document_parser import parse_pdf, render_pdf_pages
from app.extraction_warnings import build_extraction_warnings
from app.schemas import ExtractionResponse


def extract_pdf_document(content: bytes):
    parsed = parse_pdf(content)
    pages = render_pdf_pages(content)
    first_page_image = pages[0]
    document_type = classify_document(parsed["text"], first_page_image)
    structured_model = extract_structured_document(
        parsed["text"],
        first_page_image,
        document_type,
    )
    data = structured_model.model_dump()
    return ExtractionResponse(
        document_type=document_type,
        data=data,
        warnings=build_extraction_warnings(document_type, data),
        metadata={"page_count": parsed["page_count"]},
    )
