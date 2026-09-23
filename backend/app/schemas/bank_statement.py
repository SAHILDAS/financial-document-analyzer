from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class BankAccount(BaseModel):
    holder_name: str | None = None
    bank_name: str | None = None
    account_number: str | None = None
    ifsc: str | None = None


class BankStatementPeriod(BaseModel):
    from_date: date | None = None
    to_date: date | None = None


class BankTransaction(BaseModel):
    date: date
    narration: str
    debit: Decimal | None = Field(default=None, ge=0)
    credit: Decimal | None = Field(default=None, ge=0)
    balance: Decimal | None = Field(default=None, ge=0)


class BankStatement(BaseModel):
    account: BankAccount
    statement_period: BankStatementPeriod
    opening_balance: Decimal | None = Field(default=None, ge=0)
    closing_balance: Decimal | None = Field(default=None, ge=0)
    transactions: list[BankTransaction] = Field(default_factory=list)