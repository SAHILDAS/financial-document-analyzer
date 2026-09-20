from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from app.schemas.ingestion import (
    DocumentSource,
    ExtractionMethod,
    ProcessingErrorCode,
)
from app.services.ocr.image_ocr import ImageOcrService


def create_test_image(
    text: str = "SALARY SLIP\nNET SALARY 50000",
    image_format: str = "PNG",
) -> bytes:
    image = Image.new(
        "RGB",
        (1200, 400),
        "white",
    )

    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default(size=32)

    draw.text(
        (50, 50),
        text,
        fill="black",
        font=font,
        spacing=20,
    )

    output = BytesIO()
    image.save(output, format=image_format)

    return output.getvalue()


def test_extracts_text_from_png():
    service = ImageOcrService()

    result = service.extract(
        create_test_image(),
    )

    assert result.success is True
    assert result.error is None
    assert result.extracted_text is not None

    extracted = result.extracted_text

    assert extracted.source == DocumentSource.OCR
    assert extracted.methods == [ExtractionMethod.IMAGE_OCR]
    assert extracted.page_count == 1
    assert extracted.quality.is_empty is False
    assert extracted.quality.character_count > 0
    assert extracted.quality.word_count > 0


def test_extracts_text_from_jpeg():
    service = ImageOcrService()

    result = service.extract(
        create_test_image(
            "BANK STATEMENT\nACCOUNT NUMBER 123456789",
            image_format="JPEG",
        ),
    )

    assert result.success is True
    assert result.error is None
    assert result.extracted_text is not None

    extracted = result.extracted_text

    assert extracted.source == DocumentSource.OCR
    assert extracted.methods == [ExtractionMethod.IMAGE_OCR]
    assert extracted.page_count == 1
    assert extracted.quality.is_empty is False


def test_handles_empty_ocr_result():
    image = Image.new(
        "RGB",
        (800, 400),
        "white",
    )

    output = BytesIO()
    image.save(output, format="PNG")

    service = ImageOcrService()

    result = service.extract(output.getvalue())

    assert result.success is True
    assert result.error is None
    assert result.extracted_text is not None

    extracted = result.extracted_text

    assert extracted.text == ""
    assert extracted.source == DocumentSource.OCR
    assert extracted.quality.is_empty is True
    assert extracted.quality.quality_score == 0.0


def test_rejects_empty_content():
    service = ImageOcrService()

    result = service.extract(b"")

    assert result.success is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.EMPTY_FILE


def test_rejects_invalid_image():
    service = ImageOcrService()

    result = service.extract(
        b"this-is-not-an-image",
    )

    assert result.success is False
    assert result.error is not None
    assert result.error.code == ProcessingErrorCode.INVALID_FILE
