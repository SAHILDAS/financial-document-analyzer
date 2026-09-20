from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageEnhance, ImageFilter, UnidentifiedImageError
import pytesseract

from app.schemas.ingestion import (
    DocumentSource,
    ExtractedText,
    ExtractionMethod,
    ProcessingError,
    ProcessingErrorCode,
    TextQuality,
)


@dataclass(frozen=True)
class ImageOcrResult:
    success: bool
    extracted_text: ExtractedText | None = None
    error: ProcessingError | None = None


class ImageOcrService:
    """Extract text from image documents using Tesseract OCR."""

    def extract(self, content: bytes) -> ImageOcrResult:
        """Run OCR against PNG/JPEG image bytes."""

        if not content:
            return self._error(
                ProcessingErrorCode.EMPTY_FILE,
                "The image content is empty.",
            )

        try:
            image = Image.open(BytesIO(content))
            image.load()
        except (UnidentifiedImageError, OSError):
            return self._error(
                ProcessingErrorCode.INVALID_FILE,
                "The uploaded image could not be opened.",
            )

        try:
            text = self.extract_image(image)

            extracted = ExtractedText(
                text=text,
                source=DocumentSource.OCR,
                methods=[ExtractionMethod.IMAGE_OCR],
                page_count=1,
                quality=self.assess_quality(text),
            )

            return ImageOcrResult(
                success=True,
                extracted_text=extracted,
            )

        except pytesseract.TesseractNotFoundError:
            return self._error(
                ProcessingErrorCode.OCR_FAILED,
                "OCR is unavailable because the Tesseract executable "
                "could not be found.",
            )

        except Exception:
            return self._error(
                ProcessingErrorCode.OCR_FAILED,
                "The document could not be processed using OCR.",
                retryable=True,
            )

    def extract_image(self, image: Image.Image) -> str:
        """Run OCR against an already-loaded PIL image."""

        processed_image = self._preprocess(image)

        text = pytesseract.image_to_string(
            processed_image,
            config="--psm 6",
        )

        return text.strip()

    @staticmethod
    def _preprocess(image: Image.Image) -> Image.Image:
        """Prepare an image for OCR while preserving financial text."""

        grayscale = image.convert("L")

        contrast = ImageEnhance.Contrast(grayscale).enhance(1.5)

        sharpened = contrast.filter(ImageFilter.SHARPEN)

        return sharpened

    @staticmethod
    def assess_quality(text: str) -> TextQuality:
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
    ) -> ImageOcrResult:
        return ImageOcrResult(
            success=False,
            error=ProcessingError(
                code=code,
                message=message,
                retryable=retryable,
            ),
        )
