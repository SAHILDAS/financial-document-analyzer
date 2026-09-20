from dataclasses import dataclass

import pymupdf

from app.schemas.ingestion import (
    DocumentSource,
    ExtractedText,
    ExtractionMethod,
    ProcessingError,
    ProcessingErrorCode,
    TextQuality,
)


@dataclass(frozen=True)
class TextExtractionResult:
    success: bool
    extracted_text: ExtractedText | None = None
    error: ProcessingError | None = None


class PdfTextExtractor:
    """Extract native text from PDF documents."""

    def extract(self, content: bytes) -> TextExtractionResult:
        """Extract text from every PDF page."""

        if not content:
            return self._error(
                ProcessingErrorCode.EMPTY_FILE,
                "The PDF content is empty.",
            )

        try:
            document = pymupdf.open(
                stream=content,
                filetype="pdf",
            )
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

            if len(document) == 0:
                return self._error(
                    ProcessingErrorCode.INVALID_FILE,
                    "The PDF does not contain any pages.",
                )

            page_texts: list[str] = []

            for page in document:
                text = page.get_text("text")
                page_texts.append(text or "")

            combined_text = "\n".join(page_texts).strip()
            quality = self._assess_quality(combined_text)

            extracted = ExtractedText(
                text=combined_text,
                source=DocumentSource.NATIVE_TEXT,
                methods=[ExtractionMethod.PDF_TEXT],
                page_count=len(document),
                quality=quality,
            )

            return TextExtractionResult(
                success=True,
                extracted_text=extracted,
            )

        finally:
            document.close()

    @staticmethod
    def _assess_quality(text: str) -> TextQuality:
        stripped = text.strip()

        if not stripped:
            return TextQuality()

        lines = [
            line.strip()
            for line in stripped.splitlines()
            if line.strip()
        ]

        words = stripped.split()

        character_count = len(stripped)
        word_count = len(words)
        line_count = len(lines)

        quality_score = min(
            1.0,
            (
                min(character_count / 1000, 1.0) * 0.4
                + min(word_count / 150, 1.0) * 0.3
                + min(line_count / 30, 1.0) * 0.3
            ),
        )

        return TextQuality(
            character_count=character_count,
            word_count=word_count,
            line_count=line_count,
            is_empty=False,
            quality_score=round(quality_score, 3),
        )

    @staticmethod
    def _error(
        code: ProcessingErrorCode,
        message: str,
        retryable: bool = False,
    ) -> TextExtractionResult:
        return TextExtractionResult(
            success=False,
            error=ProcessingError(
                code=code,
                message=message,
                retryable=retryable,
            ),
        )