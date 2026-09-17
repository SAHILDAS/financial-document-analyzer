from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.bank_statement import (
    BankAccount,
    BankStatement,
    StatementBalances,
    StatementPeriod,
)
from app.schemas.financial_analysis import FinancialAnalysis
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
from app.schemas.transaction import Transaction


def test_transaction_accepts_credit():
    transaction = Transaction(
        date=date(2026, 9, 1),
        narration="SALARY CREDIT",
        credit=Decimal("75000.00"),
        balance=Decimal("120000.00"),
    )

    assert transaction.credit == Decimal("75000.00")
    assert transaction.debit == Decimal("0")


def test_transaction_rejects_debit_and_credit_together():
    with pytest.raises(ValidationError):
        Transaction(
            date=date(2026, 9, 1),
            narration="INVALID",
            debit=Decimal("1000"),
            credit=Decimal("1000"),
        )


def test_transaction_rejects_zero_amount():
    with pytest.raises(ValidationError):
        Transaction(
            date=date(2026, 9, 1),
            narration="INVALID",
        )


def test_bank_statement():
    statement = BankStatement(
        account=BankAccount(
            holder_name="Test User",
            bank_name="Example Bank",
        ),
        period=StatementPeriod(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        ),
        balances=StatementBalances(
            opening=Decimal("50000"),
            closing=Decimal("90000"),
        ),
        transactions=[],
    )

    assert statement.account.bank_name == "Example Bank"
    assert statement.balances.opening == Decimal("50000")


def test_bank_statement_rejects_invalid_period():
    with pytest.raises(ValidationError):
        StatementPeriod(
            start_date=date(2026, 9, 30),
            end_date=date(2026, 9, 1),
        )


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


def test_financial_analysis_defaults():
    analysis = FinancialAnalysis(
        total_credits=Decimal("150000"),
        total_debits=Decimal("60000"),
    )

    assert analysis.total_credits == Decimal("150000")
    assert analysis.total_debits == Decimal("60000")
    assert analysis.large_transactions == []
    assert analysis.salary_credit_candidates == []


def test_reconciliation_result():
    result = ReconciliationResult(
        status=ReconciliationStatus.MATCHED,
        salary_net_amount=Decimal("59000"),
        confidence=0.92,
        explanation="A bank credit closely matches the salary net amount.",
    )

    assert result.status == ReconciliationStatus.MATCHED
    assert result.confidence == 0.92