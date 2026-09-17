from enum import StrEnum

from pydantic import BaseModel


class ProcessingStatus(StrEnum):
    COMPLETED = "completed"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"


class ProcessingMetadata(BaseModel):
    status: ProcessingStatus
    processing_time_ms: int | None = None
    pages_processed: int | None = None
    ocr_used: bool = False