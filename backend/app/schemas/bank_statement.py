from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.schemas.transaction import Transaction


class BankAccount(BaseModel):
    holder_name: str | None = None
    bank_name: str | None = None
    account_number: str | None = None
    ifsc: str | None = None


class StatementPeriod(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_period(self) -> "StatementPeriod":
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValueError("Statement start date cannot be after end date.")

        return self


class StatementBalances(BaseModel):
    opening: Decimal | None = None
    closing: Decimal | None = None


class BankStatement(BaseModel):
    account: BankAccount
    period: StatementPeriod
    balances: StatementBalances

    transactions: list[Transaction] = Field(default_factory=list)