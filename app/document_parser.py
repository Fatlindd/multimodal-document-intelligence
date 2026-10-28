import pymupdf


class InvalidPDFError(Exception):
    pass


class EmptyPDFError(Exception):
    pass


def parse_pdf(content: bytes):
    try:
        document = pymupdf.open(stream=content, filetype="pdf")
    except pymupdf.FileDataError:
        raise InvalidPDFError("Invalid or corrupted PDF")
    with document:
        if document.page_count == 0:
            raise EmptyPDFError("PDF contains no pages")
        text = "".join(page.get_text() for page in document)
        return {
            "page_count": document.page_count,
            "text": text,
        }


def render_pdf_pages(content: bytes):
    try:
        document = pymupdf.open(stream=content, filetype="pdf")
    except pymupdf.FileDataError:
        raise InvalidPDFError("Invalid or corrupted PDF")
    with document:
        if document.page_count == 0:
            raise EmptyPDFError("PDF contains no pages")
        return [page.get_pixmap().tobytes("png") for page in document]
