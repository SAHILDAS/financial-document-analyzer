from app.schemas.ingestion import ProcessingErrorCode
from app.services.ingestion.file_validator import FileValidator


PDF_BYTES = b"%PDF-1.7\nmock pdf content"
JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"mock jpeg content"
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"mock png content"


def test_valid_pdf():
    validator = FileValidator()

    result = validator.validate(
        filename="salary.pdf",
        content_type="application/pdf",
        content=PDF_BYTES,
    )

    assert result.valid is True
    assert result.error is None
    assert result.metadata is not None
    assert result.metadata.extension == ".pdf"
    assert result.metadata.content_type == "application/pdf"


def test_valid_jpeg():
    validator = FileValidator()

    result = validator.validate(
        filename="salary.jpg",
        content_type="image/jpeg",
        content=JPEG_BYTES,
    )

    assert result.valid is True
    assert result.metadata is not None
    assert result.metadata.extension == ".jpg"


def test_valid_png():
    validator = FileValidator()

    result = validator.validate(
        filename="statement.png",
        content_type="image/png",
        content=PNG_BYTES,
    )

    assert result.valid is True
    assert result.metadata is not None
    assert result.metadata.extension == ".png"


def test_rejects_unsupported_extension():
    validator = FileValidator()

    result = validator.validate(
        filename="statement.txt",
        content_type="text/plain",
        content=b"some text",
    )

    assert result.valid is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.UNSUPPORTED_FILE_TYPE


def test_rejects_empty_file():
    validator = FileValidator()

    result = validator.validate(
        filename="statement.pdf",
        content_type="application/pdf",
        content=b"",
    )

    assert result.valid is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.EMPTY_FILE


def test_rejects_mime_extension_mismatch():
    validator = FileValidator()

    result = validator.validate(
        filename="statement.pdf",
        content_type="image/png",
        content=PDF_BYTES,
    )

    assert result.valid is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.INVALID_FILE


def test_rejects_invalid_file_signature():
    validator = FileValidator()

    result = validator.validate(
        filename="statement.pdf",
        content_type="application/pdf",
        content=b"This is not actually a PDF",
    )

    assert result.valid is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.INVALID_FILE


def test_rejects_unsafe_filename():
    validator = FileValidator()

    result = validator.validate(
        filename="salary<script>.pdf",
        content_type="application/pdf",
        content=PDF_BYTES,
    )

    assert result.valid is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.INVALID_FILE


def test_rejects_missing_filename():
    validator = FileValidator()

    result = validator.validate(
        filename=None,
        content_type="application/pdf",
        content=PDF_BYTES,
    )

    assert result.valid is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.INVALID_FILE


def test_strips_path_from_filename():
    validator = FileValidator()

    result = validator.validate(
        filename="/tmp/salary.pdf",
        content_type="application/pdf",
        content=PDF_BYTES,
    )

    assert result.valid is True
    assert result.metadata is not None
    assert result.metadata.filename == "salary.pdf"


def test_accepts_jpeg_extension_case_insensitively():
    validator = FileValidator()

    result = validator.validate(
        filename="salary.JPEG",
        content_type="image/jpeg",
        content=JPEG_BYTES,
    )

    assert result.valid is True
    assert result.metadata is not None
    assert result.metadata.extension == ".jpeg"


def test_accepts_file_at_maximum_size(monkeypatch):
    validator = FileValidator()

    monkeypatch.setattr(
        "app.services.ingestion.file_validator.settings.max_file_size_mb",
        1,
    )

    content = PDF_BYTES + b"x" * (1024 * 1024 - len(PDF_BYTES))

    result = validator.validate(
        filename="large.pdf",
        content_type="application/pdf",
        content=content,
    )

    assert result.valid is True
    assert result.metadata is not None
    assert result.metadata.size_bytes == 1024 * 1024


def test_rejects_file_above_maximum_size(monkeypatch):
    validator = FileValidator()

    monkeypatch.setattr(
        "app.services.ingestion.file_validator.settings.max_file_size_mb",
        1,
    )

    content = PDF_BYTES + b"x" * (1024 * 1024 - len(PDF_BYTES) + 1)

    result = validator.validate(
        filename="large.pdf",
        content_type="application/pdf",
        content=content,
    )

    assert result.valid is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.FILE_TOO_LARGE