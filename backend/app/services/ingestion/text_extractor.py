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
        """
        Assess the quality of extracted native PDF text.

        The score measures whether the extracted text looks usable,
        rather than rewarding documents simply for being long.

        Factors:
        - character count
        - word count
        - line count
        - replacement characters
        - non-printable characters
        """

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

        if character_count == 0 or word_count == 0:
            return TextQuality(
                character_count=character_count,
                word_count=word_count,
                line_count=line_count,
                is_empty=True,
                quality_score=0.0,
            )

        # Use smaller saturation thresholds so short but clean
        # business documents can still achieve a high quality score.
        character_score = min(
            character_count / 200,
            1.0,
        )

        word_score = min(
            word_count / 40,
            1.0,
        )

        line_score = min(
            line_count / 10,
            1.0,
        )

        quality_score = (
            character_score * 0.35
            + word_score * 0.35
            + line_score * 0.30
        )

        # Penalize Unicode replacement characters because they are
        # strong evidence that the extracted text contains corrupted
        # or undecodable characters.
        replacement_character_count = stripped.count("�")

        if replacement_character_count:
            replacement_ratio = (
                replacement_character_count / character_count
            )

            quality_score -= min(
                0.30,
                replacement_ratio * 2.0,
            )

        # Penalize unexpected non-printable characters while allowing
        # normal newline and tab characters.
        non_printable_count = sum(
            not character.isprintable()
            and character not in "\n\t"
            for character in stripped
        )

        if non_printable_count:
            non_printable_ratio = (
                non_printable_count / character_count
            )

            quality_score -= min(
                0.20,
                non_printable_ratio * 2.0,
            )

        quality_score = max(
            0.0,
            min(1.0, quality_score),
        )

        return TextQuality(
            character_count=character_count,
            word_count=word_count,
            line_count=line_count,
            is_empty=False,
            quality_score=round(
                quality_score,
                3,
            ),
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