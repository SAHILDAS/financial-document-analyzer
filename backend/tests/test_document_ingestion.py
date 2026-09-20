from io import BytesIO

import pymupdf
from PIL import Image, ImageDraw, ImageFont

from app.schemas.ingestion import (
    DocumentSource,
    ProcessingErrorCode,
)
from app.services.ingestion.document_ingestion import DocumentIngestionService


def create_text_pdf(text: str) -> bytes:
    document = pymupdf.open()

    page = document.new_page()
    page.insert_text((72, 72), text)

    content = document.tobytes()
    document.close()

    return content


def create_scanned_pdf(text: str) -> bytes:
    image = Image.new("RGB", (1200, 600), "white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            48,
        )
    except OSError:
        font = ImageFont.load_default()

    draw.text(
        (60, 60),
        text,
        fill="black",
        font=font,
    )

    image_buffer = BytesIO()
    image.save(image_buffer, format="PNG")

    document = pymupdf.open()
    page = document.new_page(width=1200, height=600)

    image_buffer.seek(0)
    page.insert_image(
        page.rect,
        stream=image_buffer.read(),
    )

    content = document.tobytes()
    document.close()

    return content


def create_png(text: str) -> bytes:
    image = Image.new("RGB", (1200, 600), "white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            48,
        )
    except OSError:
        font = ImageFont.load_default()

    draw.text(
        (60, 60),
        text,
        fill="black",
        font=font,
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return buffer.getvalue()


def test_ingestion_service_extracts_native_pdf_text():
    service = DocumentIngestionService()

    content = create_text_pdf(
        "SALARY SLIP\nNET SALARY 50000"
    )

    result = service.ingest(
        filename="salary.pdf",
        content_type="application/pdf",
        content=content,
    )

    assert result.success is True
    assert result.document_id
    assert result.file.filename == "salary.pdf"
    assert result.file.extension == ".pdf"

    assert result.inspection is not None
    assert result.inspection.is_pdf is True
    assert result.inspection.has_native_text is True

    assert result.extracted_text is not None
    assert result.extracted_text.source == DocumentSource.NATIVE_TEXT
    assert "NET SALARY 50000" in result.extracted_text.text

    assert result.errors == []
    assert result.completed_at is not None


def test_ingestion_service_uses_ocr_for_scanned_pdf():
    service = DocumentIngestionService()

    content = create_scanned_pdf(
        "SALARY SLIP NET SALARY 50000"
    )

    result = service.ingest(
        filename="salary-scan.pdf",
        content_type="application/pdf",
        content=content,
    )

    assert result.success is True

    assert result.inspection is not None
    assert result.inspection.is_pdf is True
    assert result.inspection.has_native_text is False

    assert result.extracted_text is not None
    assert result.extracted_text.source == DocumentSource.OCR
    assert "SALARY" in result.extracted_text.text.upper()
    assert "50000" in result.extracted_text.text


def test_ingestion_service_uses_ocr_for_png():
    service = DocumentIngestionService()

    content = create_png(
        "BANK STATEMENT ACCOUNT BALANCE 50000"
    )

    result = service.ingest(
        filename="statement.png",
        content_type="image/png",
        content=content,
    )

    assert result.success is True
    assert result.inspection is None

    assert result.extracted_text is not None
    assert result.extracted_text.source == DocumentSource.OCR
    assert "BANK" in result.extracted_text.text.upper()

    assert result.errors == []


def test_ingestion_service_rejects_unsupported_file_type():
    service = DocumentIngestionService()

    result = service.ingest(
        filename="document.txt",
        content_type="text/plain",
        content=b"some document content",
    )

    assert result.success is False
    assert result.extracted_text is None

    assert result.errors
    assert result.errors[0].code == ProcessingErrorCode.UNSUPPORTED_FILE_TYPE


def test_ingestion_service_rejects_empty_file():
    service = DocumentIngestionService()

    result = service.ingest(
        filename="empty.pdf",
        content_type="application/pdf",
        content=b"",
    )

    assert result.success is False
    assert result.extracted_text is None

    assert result.errors
    assert result.errors[0].code == ProcessingErrorCode.EMPTY_FILE


def test_ingestion_service_rejects_malformed_pdf():
    service = DocumentIngestionService()

    result = service.ingest(
        filename="broken.pdf",
        content_type="application/pdf",
        content=b"%PDF-this-is-not-a-valid-pdf",
    )

    assert result.success is False
    assert result.extracted_text is None

    assert result.errors
    assert result.errors[0].code == ProcessingErrorCode.MALFORMED_PDF


def test_ingestion_service_rejects_mismatched_content_type():
    service = DocumentIngestionService()

    content = create_text_pdf("TEST DOCUMENT")

    result = service.ingest(
        filename="document.pdf",
        content_type="image/png",
        content=content,
    )

    assert result.success is False
    assert result.extracted_text is None

    assert result.errors
    assert result.errors[0].code == ProcessingErrorCode.INVALID_FILE


def test_ingestion_service_generates_unique_document_ids():
    service = DocumentIngestionService()

    content = create_text_pdf("TEST DOCUMENT")

    result_one = service.ingest(
        filename="document-one.pdf",
        content_type="application/pdf",
        content=content,
    )

    result_two = service.ingest(
        filename="document-two.pdf",
        content_type="application/pdf",
        content=content,
    )

    assert result_one.success is True
    assert result_two.success is True
    assert result_one.document_id != result_two.document_id
