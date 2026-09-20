import pymupdf

from app.schemas.ingestion import (
    DocumentSource,
    ExtractionMethod,
    ProcessingErrorCode,
)
from app.services.ocr.pdf_ocr import PdfOcrService


def create_scanned_style_pdf(
    pages: list[str],
) -> bytes:
    """
    Create a PDF containing rendered text-like pages.

    The text is drawn as PDF vector text here, but the PDF OCR service
    intentionally ignores the native text layer and renders each page
    before OCR.
    """

    document = pymupdf.open()

    for text in pages:
        page = document.new_page(
            width=1200,
            height=800,
        )

        page.insert_text(
            (80, 100),
            text,
            fontsize=32,
        )

    content = document.tobytes()

    document.close()

    return content


def test_extracts_text_from_pdf_pages_using_ocr():
    service = PdfOcrService()

    result = service.extract(
        create_scanned_style_pdf(
            [
                "SALARY SLIP",
                "NET SALARY 50000",
            ],
        ),
    )

    assert result.success is True
    assert result.error is None
    assert result.extracted_text is not None

    extracted = result.extracted_text

    assert extracted.source == DocumentSource.OCR
    assert extracted.methods == [ExtractionMethod.PDF_OCR]
    assert extracted.page_count == 2
    assert extracted.quality.is_empty is False
    assert extracted.quality.character_count > 0
    assert extracted.quality.word_count > 0

    normalized_text = extracted.text.upper()

    assert "SALARY" in normalized_text
    assert "50000" in normalized_text


def test_handles_pdf_without_ocr_text():
    document = pymupdf.open()

    document.new_page(
        width=800,
        height=600,
    )

    content = document.tobytes()

    document.close()

    service = PdfOcrService()

    result = service.extract(content)

    assert result.success is True
    assert result.error is None
    assert result.extracted_text is not None

    extracted = result.extracted_text

    assert extracted.source == DocumentSource.OCR
    assert extracted.methods == [ExtractionMethod.PDF_OCR]
    assert extracted.page_count == 1
    assert extracted.quality.is_empty is True


def test_rejects_empty_content():
    service = PdfOcrService()

    result = service.extract(b"")

    assert result.success is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.EMPTY_FILE


def test_rejects_malformed_pdf():
    service = PdfOcrService()

    result = service.extract(
        b"%PDF-this-is-not-a-real-pdf",
    )

    assert result.success is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.MALFORMED_PDF
