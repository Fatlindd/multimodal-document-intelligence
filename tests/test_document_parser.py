import pymupdf

from app.document_parser import parse_pdf, render_pdf_pages

document = pymupdf.open()
page = document.new_page()
page.insert_text((72, 72), "Hello document intelligence")
pdf_bytes = document.tobytes()
document.close()


def test_parse_pdf():
    result = parse_pdf(pdf_bytes)
    assert result["page_count"] == 1
    assert "Hello document intelligence" in result["text"]


def test_render_pdf_pages():
    pages = render_pdf_pages(pdf_bytes)
    assert len(pages) == 1
    assert isinstance(pages[0], bytes)
    assert pages[0].startswith(b"\x89PNG\r\n\x1a\n")
