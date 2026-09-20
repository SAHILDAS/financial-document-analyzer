from dataclasses import dataclass

import pymupdf

from app.schemas.ingestion import (
    DocumentInspection,
    ProcessingError,
    ProcessingErrorCode,
)


@dataclass(frozen=True)
class DocumentInspectionResult:
    success: bool
    inspection: DocumentInspection | None = None
    error: ProcessingError | None = None


class DocumentInspector:
    """Inspect document structure before text extraction."""

    def inspect_pdf(self, content: bytes) -> DocumentInspectionResult:
        """Inspect a PDF and return structural metadata."""

        if not content:
            return self._error(
                ProcessingErrorCode.EMPTY_FILE,
                "The PDF content is empty.",
            )

        try:
            document = pymupdf.open(stream=content, filetype="pdf")
        except Exception:
            return self._error(
                ProcessingErrorCode.MALFORMED_PDF,
                "The uploaded PDF could not be opened.",
            )

        try:
            if document.needs_pass:
                return self._error(
                    ProcessingErrorCode.PASSWORD_PROTECTED_PDF,
                    "The PDF is password protected and cannot be processed.",
                )

            page_count = len(document)

            if page_count == 0:
                return self._error(
                    ProcessingErrorCode.INVALID_FILE,
                    "The PDF does not contain any pages.",
                )

            has_native_text = self._has_native_text(document)

            inspection = DocumentInspection(
                is_pdf=True,
                page_count=page_count,
                has_native_text=has_native_text,
                is_encrypted=document.is_encrypted,
            )

            return DocumentInspectionResult(
                success=True,
                inspection=inspection,
            )

        finally:
            document.close()

    @staticmethod
    def _has_native_text(document: pymupdf.Document) -> bool:
        """Return True when at least one page contains meaningful text."""

        for page in document:
            text = page.get_text("text")

            if text and text.strip():
                return True

        return False

    @staticmethod
    def _error(
        code: ProcessingErrorCode,
        message: str,
        retryable: bool = False,
    ) -> DocumentInspectionResult:
        return DocumentInspectionResult(
            success=False,
            error=ProcessingError(
                code=code,
                message=message,
                retryable=retryable,
            ),
        )