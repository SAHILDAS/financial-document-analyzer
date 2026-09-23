from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.bank_statement import BankTransaction


class LargeTransaction(BaseModel):
    transaction: BankTransaction
    amount: Decimal = Field(ge=0)
    direction: str
    reason: str


class SalaryCreditCandidate(BaseModel):
    transaction: BankTransaction
    score: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)


class RecurringTransaction(BaseModel):
    narration: str
    occurrence_count: int = Field(ge=1)
    amounts: list[Decimal] = Field(default_factory=list)
    average_amount: Decimal | None = None
    approximate_interval_days: float | None = None
    reasons: list[str] = Field(default_factory=list)


class EmiCandidate(BaseModel):
    transaction: BankTransaction
    score: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)


class BankFinancialAnalysis(BaseModel):
    total_credits: Decimal = Field(default=Decimal("0"), ge=0)
    total_debits: Decimal = Field(default=Decimal("0"), ge=0)
    average_monthly_credit: Decimal | None = Field(default=None, ge=0)

    large_transactions: list[LargeTransaction] = Field(default_factory=list)
    salary_credit_candidates: list[SalaryCreditCandidate] = Field(
        default_factory=list
    )
    recurring_transactions: list[RecurringTransaction] = Field(
        default_factory=list
    )
    emi_candidates: list[EmiCandidate] = Field(default_factory=list)