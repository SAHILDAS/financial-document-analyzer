from dataclasses import dataclass

import pymupdf

from app.schemas.ingestion import (
    DocumentSource,
    ExtractedText,
    ExtractionMethod,
    ProcessingError,
    ProcessingErrorCode,
)
from app.services.ocr.image_ocr import ImageOcrService


@dataclass(frozen=True)
class PdfOcrResult:
    success: bool
    extracted_text: ExtractedText | None = None
    error: ProcessingError | None = None


class PdfOcrService:
    """Render scanned PDF pages and extract text using OCR."""

    # 150 DPI is a reasonable prototype balance between OCR quality
    # and memory/processing cost.
    RENDER_DPI = 150

    def __init__(
        self,
        image_ocr_service: ImageOcrService | None = None,
    ) -> None:
        self.image_ocr_service = image_ocr_service or ImageOcrService()

    def extract(self, content: bytes) -> PdfOcrResult:
        """Render every PDF page and run OCR."""

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

            page_count = len(document)

            if page_count == 0:
                return self._error(
                    ProcessingErrorCode.INVALID_FILE,
                    "The PDF does not contain any pages.",
                )

            page_texts: list[str] = []

            for page in document:
                text = self._extract_page(page)
                page_texts.append(text)

            combined_text = "\n".join(
                text
                for text in page_texts
                if text.strip()
            ).strip()

            extracted = ExtractedText(
                text=combined_text,
                source=DocumentSource.OCR,
                methods=[ExtractionMethod.PDF_OCR],
                page_count=page_count,
                quality=self.image_ocr_service.assess_quality(
                    combined_text,
                ),
            )

            return PdfOcrResult(
                success=True,
                extracted_text=extracted,
            )

        except Exception:
            return self._error(
                ProcessingErrorCode.OCR_FAILED,
                "The PDF could not be processed using OCR.",
                retryable=True,
            )

        finally:
            document.close()

    def _extract_page(
        self,
        page: pymupdf.Page,
    ) -> str:
        """Render one PDF page and run the shared image OCR engine."""

        scale = self.RENDER_DPI / 72

        matrix = pymupdf.Matrix(
            scale,
            scale,
        )

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False,
        )

        image_bytes = pixmap.tobytes("png")

        image = self._load_image(image_bytes)

        return self.image_ocr_service.extract_image(image)

    @staticmethod
    def _load_image(image_bytes: bytes):
        from io import BytesIO

        from PIL import Image

        image = Image.open(BytesIO(image_bytes))
        image.load()

        return image

    @staticmethod
    def _error(
        code: ProcessingErrorCode,
        message: str,
        retryable: bool = False,
    ) -> PdfOcrResult:
        return PdfOcrResult(
            success=False,
            error=ProcessingError(
                code=code,
                message=message,
                retryable=retryable,
            ),
        )
