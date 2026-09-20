from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DocumentSource(str, Enum):
    NATIVE_TEXT = "native_text"
    OCR = "ocr"
    MIXED = "mixed"


class ExtractionMethod(str, Enum):
    PDF_TEXT = "pdf_text"
    IMAGE_OCR = "image_ocr"
    PDF_OCR = "pdf_ocr"


class ProcessingErrorCode(str, Enum):
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    EMPTY_FILE = "EMPTY_FILE"
    INVALID_FILE = "INVALID_FILE"
    MALFORMED_PDF = "MALFORMED_PDF"
    PASSWORD_PROTECTED_PDF = "PASSWORD_PROTECTED_PDF"
    TEXT_EXTRACTION_FAILED = "TEXT_EXTRACTION_FAILED"
    OCR_FAILED = "OCR_FAILED"
    DOCUMENT_UNREADABLE = "DOCUMENT_UNREADABLE"
    PROCESSING_FAILED = "PROCESSING_FAILED"


class ProcessingError(BaseModel):
    code: ProcessingErrorCode
    message: str
    retryable: bool = False


class FileMetadata(BaseModel):
    filename: str
    content_type: str | None = None
    extension: str
    size_bytes: int = Field(ge=0)


class DocumentInspection(BaseModel):
    is_pdf: bool
    page_count: int | None = Field(default=None, ge=0)
    has_native_text: bool = False
    is_encrypted: bool = False


class TextQuality(BaseModel):
    character_count: int = Field(default=0, ge=0)
    word_count: int = Field(default=0, ge=0)
    line_count: int = Field(default=0, ge=0)
    is_empty: bool = True
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)


class ExtractedText(BaseModel):
    text: str
    source: DocumentSource
    methods: list[ExtractionMethod] = Field(default_factory=list)
    page_count: int = Field(default=0, ge=0)
    quality: TextQuality


class IngestionResult(BaseModel):
    document_id: str
    file: FileMetadata
    inspection: DocumentInspection | None = None
    extracted_text: ExtractedText | None = None
    errors: list[ProcessingError] = Field(default_factory=list)
    started_at: datetime
    completed_at: datetime | None = None
    success: bool = False