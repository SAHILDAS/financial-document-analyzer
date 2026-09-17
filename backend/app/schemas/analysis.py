from pydantic import BaseModel

from app.schemas.classification import ClassificationResult
from app.schemas.processing import ProcessingMetadata
from app.schemas.validation import ValidationResult


class DocumentAnalysisResponse(BaseModel):
    success: bool
    document_id: str
    document_type: str
    confidence: float
    classification: ClassificationResult
    data: dict | None = None
    validation: ValidationResult
    processing: ProcessingMetadata