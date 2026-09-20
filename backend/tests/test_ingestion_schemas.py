from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.ingestion import (
    DocumentInspection,
    DocumentSource,
    ExtractedText,
    ExtractionMethod,
    FileMetadata,
    IngestionResult,
    ProcessingError,
    ProcessingErrorCode,
    TextQuality,
)


def test_file_metadata_accepts_valid_file():
    metadata = FileMetadata(
        filename="salary.pdf",
        content_type="application/pdf",
        extension=".pdf",
        size_bytes=1024,
    )

    assert metadata.filename == "salary.pdf"
    assert metadata.extension == ".pdf"
    assert metadata.size_bytes == 1024


def test_file_metadata_rejects_negative_size():
    with pytest.raises(ValidationError):
        FileMetadata(
            filename="salary.pdf",
            content_type="application/pdf",
            extension=".pdf",
            size_bytes=-1,
        )


def test_document_inspection_defaults():
    inspection = DocumentInspection(
        is_pdf=True,
    )

    assert inspection.is_pdf is True
    assert inspection.page_count is None
    assert inspection.has_native_text is False
    assert inspection.is_encrypted is False


def test_text_quality_defaults():
    quality = TextQuality()

    assert quality.character_count == 0
    assert quality.word_count == 0
    assert quality.line_count == 0
    assert quality.is_empty is True
    assert quality.quality_score == 0.0


def test_extracted_text_accepts_native_pdf_text():
    extracted = ExtractedText(
        text="Employee Name: John Doe\nNet Salary: 50000",
        source=DocumentSource.NATIVE_TEXT,
        methods=[ExtractionMethod.PDF_TEXT],
        page_count=1,
        quality=TextQuality(
            character_count=43,
            word_count=8,
            line_count=2,
            is_empty=False,
            quality_score=0.95,
        ),
    )

    assert extracted.source == DocumentSource.NATIVE_TEXT
    assert ExtractionMethod.PDF_TEXT in extracted.methods
    assert extracted.page_count == 1
    assert extracted.quality.quality_score == 0.95


def test_processing_error():
    error = ProcessingError(
        code=ProcessingErrorCode.UNSUPPORTED_FILE_TYPE,
        message="The uploaded file type is not supported.",
    )

    assert error.code == ProcessingErrorCode.UNSUPPORTED_FILE_TYPE
    assert error.retryable is False


def test_ingestion_result_success():
    now = datetime.now(timezone.utc)

    result = IngestionResult(
        document_id="doc-123",
        file=FileMetadata(
            filename="statement.pdf",
            content_type="application/pdf",
            extension=".pdf",
            size_bytes=2048,
        ),
        inspection=DocumentInspection(
            is_pdf=True,
            page_count=2,
            has_native_text=True,
        ),
        extracted_text=ExtractedText(
            text="Account Statement",
            source=DocumentSource.NATIVE_TEXT,
            methods=[ExtractionMethod.PDF_TEXT],
            page_count=2,
            quality=TextQuality(
                character_count=17,
                word_count=2,
                line_count=1,
                is_empty=False,
                quality_score=1.0,
            ),
        ),
        started_at=now,
        completed_at=now,
        success=True,
    )

    assert result.success is True
    assert result.document_id == "doc-123"
    assert result.extracted_text is not None
    assert result.extracted_text.source == DocumentSource.NATIVE_TEXT


def test_ingestion_result_defaults_to_failure():
    result = IngestionResult(
        document_id="doc-456",
        file=FileMetadata(
            filename="document.jpg",
            content_type="image/jpeg",
            extension=".jpg",
            size_bytes=500,
        ),
        started_at=datetime.now(timezone.utc),
    )

    assert result.success is False
    assert result.extracted_text is None
    assert result.errors == []