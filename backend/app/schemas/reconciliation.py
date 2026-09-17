from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class ReconciliationStatus(StrEnum):
    MATCHED = "matched"
    MULTIPLE_CANDIDATES = "multiple_candidates"
    NO_MATCH = "no_match"
    NEEDS_REVIEW = "needs_review"


class ReconciliationCandidate(BaseModel):
    transaction_date: date
    amount: Decimal
    narration: str

    amount_score: float = Field(ge=0, le=1)
    date_score: float = Field(ge=0, le=1)
    narration_score: float = Field(ge=0, le=1)
    periodicity_score: float = Field(ge=0, le=1)

    overall_score: float = Field(ge=0, le=1)

    reasons: list[str] = Field(default_factory=list)


class ReconciliationResult(BaseModel):
    status: ReconciliationStatus

    salary_net_amount: Decimal

    candidates: list[ReconciliationCandidate] = Field(
        default_factory=list
    )

    selected_candidate: ReconciliationCandidate | None = None

    confidence: float = Field(ge=0, le=1)

    explanation: str