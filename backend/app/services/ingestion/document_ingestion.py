from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.ingestion import (
    DocumentSource,
    ExtractedText,
    FileMetadata,
    IngestionResult,
    ProcessingError,
    ProcessingErrorCode,
)
from app.services.ingestion.document_inspector import DocumentInspector
from app.services.ingestion.file_validator import FileValidator
from app.services.ingestion.text_extractor import PdfTextExtractor
from app.services.ocr.image_ocr import ImageOcrService
from app.services.ocr.pdf_ocr import PdfOcrService


class DocumentIngestionService:
    """Orchestrate validation, inspection, text extraction, and OCR."""

    PDF_EXTENSION = ".pdf"
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

    def __init__(
        self,
        file_validator: FileValidator | None = None,
        document_inspector: DocumentInspector | None = None,
        text_extractor: PdfTextExtractor | None = None,
        image_ocr_service: ImageOcrService | None = None,
        pdf_ocr_service: PdfOcrService | None = None,
    ):
        self.file_validator = file_validator or FileValidator()
        self.document_inspector = document_inspector or DocumentInspector()
        self.text_extractor = text_extractor or PdfTextExtractor()
        self.image_ocr_service = image_ocr_service or ImageOcrService()
        self.pdf_ocr_service = pdf_ocr_service or PdfOcrService(
            image_ocr_service=self.image_ocr_service
        )

    def ingest(
        self,
        filename: str | None,
        content_type: str | None,
        content: bytes,
    ) -> IngestionResult:
        """Validate and extract text from a supported financial document."""

        started_at = datetime.now(timezone.utc)
        document_id = str(uuid4())

        validation = self.file_validator.validate(
            filename=filename,
            content_type=content_type,
            content=content,
        )

        if not validation.valid:
            return self._failure(
                document_id=document_id,
                file=validation.metadata
                or self._build_failure_metadata(
                    filename=filename,
                    content_type=content_type,
                    content=content,
                ),
                error=validation.error,
                started_at=started_at,
            )

        metadata = validation.metadata
        assert metadata is not None

        if metadata.extension == self.PDF_EXTENSION:
            return self._ingest_pdf(
                document_id=document_id,
                metadata=metadata,
                content=content,
                started_at=started_at,
            )

        if metadata.extension in self.IMAGE_EXTENSIONS:
            return self._ingest_image(
                document_id=document_id,
                metadata=metadata,
                content=content,
                started_at=started_at,
            )

        return self._failure(
            document_id=document_id,
            file=metadata,
            error=ProcessingError(
                code=ProcessingErrorCode.UNSUPPORTED_FILE_TYPE,
                message="The uploaded file type is not supported.",
            ),
            started_at=started_at,
        )

    def _ingest_pdf(
        self,
        document_id: str,
        metadata,
        content: bytes,
        started_at: datetime,
    ) -> IngestionResult:
        inspection_result = self.document_inspector.inspect_pdf(content)

        if not inspection_result.success:
            return self._failure(
                document_id=document_id,
                file=metadata,
                error=inspection_result.error,
                started_at=started_at,
            )

        inspection = inspection_result.inspection
        assert inspection is not None

        if inspection.has_native_text:
            extraction_result = self.text_extractor.extract(content)

            if extraction_result.success and extraction_result.extracted_text:
                extracted_text = extraction_result.extracted_text

                if not extracted_text.quality.is_empty:
                    return self._success(
                        document_id=document_id,
                        metadata=metadata,
                        inspection=inspection,
                        extracted_text=extracted_text,
                        started_at=started_at,
                    )

            # Native text was detected but extraction produced no usable text.
            # Fall back to OCR rather than failing immediately.

        ocr_result = self.pdf_ocr_service.extract(content)

        if not ocr_result.success:
            return self._failure(
                document_id=document_id,
                file=metadata,
                inspection=inspection,
                error=ocr_result.error,
                started_at=started_at,
            )

        extracted_text = ocr_result.extracted_text
        assert extracted_text is not None

        if extracted_text.quality.is_empty:
            return self._failure(
                document_id=document_id,
                file=metadata,
                inspection=inspection,
                error=ProcessingError(
                    code=ProcessingErrorCode.DOCUMENT_UNREADABLE,
                    message="No readable text could be extracted from the PDF.",
                ),
                started_at=started_at,
            )

        return self._success(
            document_id=document_id,
            metadata=metadata,
            inspection=inspection,
            extracted_text=extracted_text,
            started_at=started_at,
        )

    def _ingest_image(
        self,
        document_id: str,
        metadata,
        content: bytes,
        started_at: datetime,
    ) -> IngestionResult:
        ocr_result = self.image_ocr_service.extract(content)

        if not ocr_result.success:
            return self._failure(
                document_id=document_id,
                file=metadata,
                error=ocr_result.error,
                started_at=started_at,
            )

        extracted_text = ocr_result.extracted_text
        assert extracted_text is not None

        if extracted_text.quality.is_empty:
            return self._failure(
                document_id=document_id,
                file=metadata,
                error=ProcessingError(
                    code=ProcessingErrorCode.DOCUMENT_UNREADABLE,
                    message="No readable text could be extracted from the image.",
                ),
                started_at=started_at,
            )

        return self._success(
            document_id=document_id,
            metadata=metadata,
            extracted_text=extracted_text,
            started_at=started_at,
        )

    @staticmethod
    def _build_failure_metadata(
        filename: str | None,
        content_type: str | None,
        content: bytes,
    ) -> FileMetadata:
        from pathlib import Path

        normalized_filename = Path(filename or "unknown").name
        extension = Path(normalized_filename).suffix.lower()

        return FileMetadata(
            filename=normalized_filename,
            content_type=content_type,
            extension=extension,
            size_bytes=len(content),
        )

    @staticmethod
    def _success(
        document_id: str,
        metadata,
        extracted_text: ExtractedText,
        started_at: datetime,
        inspection=None,
    ) -> IngestionResult:
        completed_at = datetime.now(timezone.utc)

        return IngestionResult(
            document_id=document_id,
            file=metadata,
            inspection=inspection,
            extracted_text=extracted_text,
            errors=[],
            started_at=started_at,
            completed_at=completed_at,
            success=True,
        )

    @staticmethod
    def _failure(
        document_id: str,
        file,
        error: ProcessingError | None,
        started_at: datetime,
        inspection=None,
    ) -> IngestionResult:
        completed_at = datetime.now(timezone.utc)

        errors = [error] if error else []

        return IngestionResult(
            document_id=document_id,
            file=file,
            inspection=inspection,
            extracted_text=None,
            errors=errors,
            started_at=started_at,
            completed_at=completed_at,
            success=False,
        )
