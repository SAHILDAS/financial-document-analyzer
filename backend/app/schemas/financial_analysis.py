from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class LargeTransaction(BaseModel):
    date: date
    narration: str
    amount: Decimal
    transaction_type: str
    balance: Decimal | None = None


class RecurringTransaction(BaseModel):
    narration_pattern: str
    average_amount: Decimal
    occurrence_count: int = Field(ge=2)
    likely_frequency: str | None = None


class SalaryCreditCandidate(BaseModel):
    date: date
    narration: str
    amount: Decimal
    score: float = Field(ge=0, le=1)
    reasons: list[str] = Field(default_factory=list)


class EmiCandidate(BaseModel):
    date: date
    narration: str
    amount: Decimal
    score: float = Field(ge=0, le=1)
    reasons: list[str] = Field(default_factory=list)


class FinancialAnalysis(BaseModel):
    total_credits: Decimal
    total_debits: Decimal

    average_monthly_credit: Decimal | None = None

    large_transactions: list[LargeTransaction] = Field(
        default_factory=list
    )

    recurring_transactions: list[RecurringTransaction] = Field(
        default_factory=list
    )

    salary_credit_candidates: list[SalaryCreditCandidate] = Field(
        default_factory=list
    )

    emi_candidates: list[EmiCandidate] = Field(
        default_factory=list
    )