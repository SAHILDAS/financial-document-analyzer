from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.bank_statement import (
    BankAccount,
    BankStatement,
    BankStatementPeriod,
    BankTransaction,
)


def test_bank_transaction_accepts_credit():
    transaction = BankTransaction(
        date=date(2026, 9, 1),
        narration="SALARY CREDIT",
        credit=Decimal("59000"),
        balance=Decimal("120000"),
    )

    assert transaction.credit == Decimal("59000")
    assert transaction.debit is None


def test_bank_transaction_accepts_debit():
    transaction = BankTransaction(
        date=date(2026, 9, 2),
        narration="EMI PAYMENT",
        debit=Decimal("18000"),
        balance=Decimal("102000"),
    )

    assert transaction.debit == Decimal("18000")
    assert transaction.credit is None


def test_bank_transaction_rejects_negative_credit():
    with pytest.raises(ValidationError):
        BankTransaction(
            date=date(2026, 9, 1),
            narration="INVALID",
            credit=Decimal("-100"),
        )


def test_bank_statement_contains_account_period_and_transactions():
    statement = BankStatement(
        account=BankAccount(
            holder_name="Test Employee",
            bank_name="Example Bank",
            account_number="XXXX1234",
            ifsc="EXMP0001234",
        ),
        statement_period=BankStatementPeriod(
            from_date=date(2026, 8, 1),
            to_date=date(2026, 8, 31),
        ),
        opening_balance=Decimal("100000"),
        closing_balance=Decimal("131000"),
        transactions=[
            BankTransaction(
                date=date(2026, 8, 1),
                narration="SALARY CREDIT",
                credit=Decimal("59000"),
                balance=Decimal("159000"),
            ),
            BankTransaction(
                date=date(2026, 8, 5),
                narration="EMI PAYMENT",
                debit=Decimal("18000"),
                balance=Decimal("141000"),
            ),
        ],
    )

    assert statement.account.bank_name == "Example Bank"
    assert statement.statement_period.from_date == date(2026, 8, 1)
    assert len(statement.transactions) == 2