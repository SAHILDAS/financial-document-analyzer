from pydantic import BaseModel, Field

from app.schemas.document import DocumentType
from app.schemas.ingestion import (
    DocumentSource,
    ExtractionMethod,
    ProcessingError,
)


class AnalyzeFileInfo(BaseModel):
    filename: str
    extension: str
    size_bytes: int = Field(ge=0)


class AnalyzeProcessingInfo(BaseModel):
    source: DocumentSource
    methods: list[ExtractionMethod] = Field(default_factory=list)
    page_count: int = Field(ge=0)
    text_quality_score: float = Field(ge=0.0, le=1.0)


class AnalyzeData(BaseModel):
    classification_reason: str | None = None
    file: AnalyzeFileInfo


class AnalyzeResponse(BaseModel):
    success: bool
    document_id: str | None = None
    document_type: DocumentType | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    data: AnalyzeData | None = None
    validation: dict | None = None
    processing: AnalyzeProcessingInfo | None = None
    errors: list[ProcessingError] = Field(default_factory=list)