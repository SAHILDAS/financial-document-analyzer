from datetime import date
from decimal import Decimal

from app.schemas.bank_statement import (
    BankAccount,
    BankStatement,
    BankStatementPeriod,
    BankTransaction,
)
from app.schemas.bank_validation import BankValidationSeverity
from app.services.validation.bank_transaction_normalizer import (
    BankTransactionNormalizer,
)
from app.services.validation.bank_transaction_validator import (
    BankTransactionValidator,
)


def make_statement(transactions):
    return BankStatement(
        account=BankAccount(
            holder_name="Test Employee",
            bank_name="Example Bank",
        ),
        statement_period=BankStatementPeriod(
            from_date=date(2026, 8, 1),
            to_date=date(2026, 8, 31),
        ),
        transactions=transactions,
    )


def test_normalizer_cleans_narration():
    transaction = BankTransaction(
        date=date(2026, 8, 1),
        narration="  SALARY    CREDIT   AUGUST 2026  ",
        credit=Decimal("59000"),
    )

    normalized = BankTransactionNormalizer.normalize(transaction)

    assert normalized.narration == "SALARY CREDIT AUGUST 2026"


def test_normalizer_preserves_decimal_amounts():
    transaction = BankTransaction(
        date=date(2026, 8, 1),
        narration="SALARY",
        credit=Decimal("59,000".replace(",", "")),
    )

    normalized = BankTransactionNormalizer.normalize(transaction)

    assert normalized.credit == Decimal("59000")


def test_validator_accepts_valid_credit_transaction():
    statement = make_statement(
        [
            BankTransaction(
                date=date(2026, 8, 1),
                narration="SALARY CREDIT",
                credit=Decimal("59000"),
            )
        ]
    )

    result = BankTransactionValidator().validate(statement)

    assert result.is_valid is True
    assert result.issues == []


def test_validator_rejects_transaction_with_both_debit_and_credit():
    statement = make_statement(
        [
            BankTransaction(
                date=date(2026, 8, 1),
                narration="INVALID",
                debit=Decimal("1000"),
                credit=Decimal("2000"),
            )
        ]
    )

    result = BankTransactionValidator().validate(statement)

    assert result.is_valid is False

    assert any(
        issue.code == "BOTH_DEBIT_AND_CREDIT"
        and issue.severity == BankValidationSeverity.ERROR
        for issue in result.issues
    )


def test_validator_rejects_transaction_with_no_amount():
    statement = make_statement(
        [
            BankTransaction(
                date=date(2026, 8, 1),
                narration="MISSING AMOUNT",
            )
        ]
    )

    result = BankTransactionValidator().validate(statement)

    assert result.is_valid is False

    assert any(
        issue.code == "MISSING_TRANSACTION_AMOUNT"
        for issue in result.issues
    )


def test_validator_warns_about_duplicate_transaction():
    transaction = BankTransaction(
        date=date(2026, 8, 1),
        narration="SALARY CREDIT",
        credit=Decimal("59000"),
        balance=Decimal("159000"),
    )

    statement = make_statement(
        [
            transaction,
            transaction.model_copy(),
        ]
    )

    result = BankTransactionValidator().validate(statement)

    assert result.is_valid is True

    assert any(
        issue.code == "DUPLICATE_TRANSACTION"
        and issue.severity == BankValidationSeverity.WARNING
        for issue in result.issues
    )