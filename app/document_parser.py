import pymupdf


def parse_pdf(content: bytes):
    with pymupdf.open(stream=content, filetype="pdf") as document:
        text = "".join(page.get_text() for page in document)
        return {
            "page_count": document.page_count,
            "text": text,
        }


def render_pdf_pages(content: bytes):
    with pymupdf.open(stream=content, filetype="pdf") as document:
        return [page.get_pixmap().tobytes("png") for page in document]
