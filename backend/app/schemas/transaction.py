from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class Transaction(BaseModel):
    date: date
    narration: str = Field(min_length=1)

    debit: Decimal = Field(default=Decimal("0"), ge=0)
    credit: Decimal = Field(default=Decimal("0"), ge=0)

    balance: Decimal | None = None

    @model_validator(mode="after")
    def validate_transaction_amounts(self) -> "Transaction":
        if self.debit > 0 and self.credit > 0:
            raise ValueError(
                "A transaction cannot have both debit and credit amounts."
            )

        if self.debit == 0 and self.credit == 0:
            raise ValueError(
                "A transaction must have either a debit or credit amount."
            )

        return self