import pymupdf

from app.schemas.ingestion import (
    DocumentSource,
    ExtractionMethod,
    ProcessingErrorCode,
)
from app.services.ingestion.text_extractor import PdfTextExtractor


def create_pdf(texts: list[str]) -> bytes:
    document = pymupdf.open()

    for text in texts:
        page = document.new_page()
        page.insert_text(
            (72, 72),
            text,
        )

    content = document.tobytes()
    document.close()

    return content


def test_extracts_native_text():
    extractor = PdfTextExtractor()

    result = extractor.extract(
        create_pdf(
            [
                "Salary Slip",
                "Employee Name: John Doe\nNet Salary: 50000",
            ]
        )
    )

    assert result.success is True
    assert result.error is None
    assert result.extracted_text is not None

    extracted = result.extracted_text

    assert extracted.source == DocumentSource.NATIVE_TEXT
    assert extracted.methods == [ExtractionMethod.PDF_TEXT]
    assert extracted.page_count == 2

    assert "Salary Slip" in extracted.text
    assert "John Doe" in extracted.text
    assert "50000" in extracted.text

    assert extracted.quality.is_empty is False
    assert extracted.quality.character_count > 0
    assert extracted.quality.word_count > 0
    assert extracted.quality.line_count > 0
    assert extracted.quality.quality_score > 0


def test_extracts_empty_text_from_scanned_style_pdf():
    document = pymupdf.open()
    document.new_page()

    content = document.tobytes()
    document.close()

    extractor = PdfTextExtractor()

    result = extractor.extract(content)

    assert result.success is True
    assert result.extracted_text is not None

    extracted = result.extracted_text

    assert extracted.text == ""
    assert extracted.source == DocumentSource.NATIVE_TEXT
    assert extracted.quality.is_empty is True
    assert extracted.quality.quality_score == 0.0


def test_rejects_empty_content():
    extractor = PdfTextExtractor()

    result = extractor.extract(b"")

    assert result.success is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.EMPTY_FILE


def test_rejects_malformed_pdf():
    extractor = PdfTextExtractor()

    result = extractor.extract(
        b"%PDF-not-a-real-document",
    )

    assert result.success is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.MALFORMED_PDF