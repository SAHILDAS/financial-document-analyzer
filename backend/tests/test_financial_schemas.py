from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.bank_analysis import BankFinancialAnalysis
from app.schemas.bank_statement import (
    BankAccount,
    BankStatement,
    BankStatementPeriod,
    BankTransaction,
)
from app.schemas.bank_validation import (
    BankValidationResult,
)
from app.schemas.reconciliation import (
    ReconciliationResult,
    ReconciliationStatus,
)
from app.schemas.salary_slip import (
    SalaryDeductions,
    SalaryEarnings,
    SalaryEmployee,
    SalarySlip,
)


def test_bank_transaction_accepts_credit():
    transaction = BankTransaction(
        date=date(2026, 9, 1),
        narration="SALARY CREDIT",
        credit=Decimal("75000.00"),
        balance=Decimal("120000.00"),
    )

    assert transaction.credit == Decimal("75000.00")
    assert transaction.debit is None


def test_bank_transaction_accepts_debit():
    transaction = BankTransaction(
        date=date(2026, 9, 1),
        narration="UTILITY PAYMENT",
        debit=Decimal("1000.00"),
        balance=Decimal("119000.00"),
    )

    assert transaction.debit == Decimal("1000.00")
    assert transaction.credit is None


def test_bank_transaction_accepts_missing_amounts_at_schema_level():
    """
    Amount completeness is enforced by BankTransactionValidator,
    not by the Pydantic domain schema itself.
    """

    transaction = BankTransaction(
        date=date(2026, 9, 1),
        narration="MISSING AMOUNT",
    )

    assert transaction.debit is None
    assert transaction.credit is None


def test_bank_transaction_rejects_negative_amount():
    with pytest.raises(ValidationError):
        BankTransaction(
            date=date(2026, 9, 1),
            narration="INVALID",
            debit=Decimal("-1000"),
        )


def test_bank_statement():
    statement = BankStatement(
        account=BankAccount(
            holder_name="Test User",
            bank_name="Example Bank",
        ),
        statement_period=BankStatementPeriod(
            from_date=date(2026, 9, 1),
            to_date=date(2026, 9, 30),
        ),
        opening_balance=Decimal("50000"),
        closing_balance=Decimal("90000"),
        transactions=[],
    )

    assert statement.account.bank_name == "Example Bank"
    assert statement.statement_period.from_date == date(2026, 9, 1)
    assert statement.statement_period.to_date == date(2026, 9, 30)
    assert statement.opening_balance == Decimal("50000")
    assert statement.closing_balance == Decimal("90000")
    assert statement.transactions == []


def test_bank_statement_period():
    period = BankStatementPeriod(
        from_date=date(2026, 9, 1),
        to_date=date(2026, 9, 30),
    )

    assert period.from_date == date(2026, 9, 1)
    assert period.to_date == date(2026, 9, 30)


def test_bank_financial_analysis_defaults():
    analysis = BankFinancialAnalysis(
        total_credits=Decimal("150000"),
        total_debits=Decimal("60000"),
    )

    assert analysis.total_credits == Decimal("150000")
    assert analysis.total_debits == Decimal("60000")
    assert analysis.large_transactions == []
    assert analysis.salary_credit_candidates == []
    assert analysis.recurring_transactions == []
    assert analysis.emi_candidates == []


def test_bank_validation_result_defaults():
    validation = BankValidationResult(
        is_valid=True,
    )

    assert validation.is_valid is True
    assert validation.issues == []


def test_salary_slip():
    salary = SalarySlip(
        employee=SalaryEmployee(
            name="Test Employee",
            employer="Example Technologies",
            salary_month="August 2026",
        ),
        earnings=SalaryEarnings(
            basic=Decimal("40000"),
            hra=Decimal("15000"),
            allowances=Decimal("10000"),
            gross=Decimal("65000"),
        ),
        deductions=SalaryDeductions(
            pf=Decimal("4800"),
            tds=Decimal("1200"),
            total=Decimal("6000"),
        ),
        net_salary=Decimal("59000"),
    )

    assert salary.earnings.gross == Decimal("65000")
    assert salary.net_salary == Decimal("59000")


def test_reconciliation_result():
    result = ReconciliationResult(
        status=ReconciliationStatus.MATCHED,
        salary_net_amount=Decimal("59000"),
        confidence=0.92,
        explanation="A bank credit closely matches the salary net amount.",
    )

    assert result.status == ReconciliationStatus.MATCHED
    assert result.confidence == 0.92