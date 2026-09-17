from pydantic import BaseModel, Field

from app.schemas.document import DocumentType


class ClassificationResult(BaseModel):
    document_type: DocumentType
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str | None = None