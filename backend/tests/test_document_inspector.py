import pymupdf

from app.schemas.ingestion import ProcessingErrorCode
from app.services.ingestion.document_inspector import DocumentInspector


def create_pdf(text: str = "Financial Document") -> bytes:
    document = pymupdf.open()

    page = document.new_page()
    page.insert_text(
        (72, 72),
        text,
    )

    content = document.tobytes()
    document.close()

    return content


def test_inspects_valid_pdf():
    inspector = DocumentInspector()

    result = inspector.inspect_pdf(
        create_pdf("Salary Slip\nNet Salary: 50000"),
    )

    assert result.success is True
    assert result.error is None
    assert result.inspection is not None

    assert result.inspection.is_pdf is True
    assert result.inspection.page_count == 1
    assert result.inspection.has_native_text is True
    assert result.inspection.is_encrypted is False


def test_rejects_empty_content():
    inspector = DocumentInspector()

    result = inspector.inspect_pdf(b"")

    assert result.success is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.EMPTY_FILE


def test_rejects_malformed_pdf():
    inspector = DocumentInspector()

    result = inspector.inspect_pdf(
        b"%PDF-this-is-not-a-real-pdf",
    )

    assert result.success is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.MALFORMED_PDF


def test_detects_pdf_without_native_text():
    document = pymupdf.open()
    document.new_page()

    content = document.tobytes()
    document.close()

    inspector = DocumentInspector()

    result = inspector.inspect_pdf(content)

    assert result.success is True
    assert result.inspection is not None
    assert result.inspection.page_count == 1
    assert result.inspection.has_native_text is False