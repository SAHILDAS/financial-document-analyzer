from enum import StrEnum

from pydantic import BaseModel, Field


class ConfidenceLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConfidenceResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    level: ConfidenceLevel
    needs_review: bool
    reasons: list[str] = Field(default_factory=list)