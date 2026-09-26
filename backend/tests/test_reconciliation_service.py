from datetime import date
from decimal import Decimal

from app.schemas.bank_statement import (
    BankAccount,
    BankStatement,
    BankStatementPeriod,
    BankTransaction,
)
from app.schemas.reconciliation import ReconciliationStatus
from app.schemas.salary_slip import (
    SalaryDeductions,
    SalaryEarnings,
    SalaryEmployee,
    SalarySlip,
)
from app.services.reconciliation.reconciliation_service import (
    ReconciliationService,
)


def create_salary(
    *,
    net: str = "50500",
    salary_month: str = "September 2026",
    employer: str | None = "Demo Company",
) -> SalarySlip:
    return SalarySlip(
        employee=SalaryEmployee(
            name="Sanjib Das",
            employee_id="Emp101",
            employer=employer,
            salary_month=salary_month,
        ),
        earnings=SalaryEarnings(
            basic=Decimal("45000"),
            hra=Decimal("10000"),
            allowances=Decimal("1000"),
            gross=Decimal("56000"),
        ),
        deductions=SalaryDeductions(
            pf=Decimal("4500"),
            tds=Decimal("1000"),
            total=Decimal("5500"),
        ),
        net_salary=Decimal(net) if net is not None else None,
    )


def create_statement(
    transactions: list[BankTransaction],
) -> BankStatement:
    return BankStatement(
        account=BankAccount(
            holder_name="Sanjib Das",
            bank_name="Example Bank",
        ),
        statement_period=BankStatementPeriod(
            from_date=date(2026, 9, 1),
            to_date=date(2026, 9, 30),
        ),
        transactions=transactions,
    )


def test_exact_salary_credit_is_matched():
    salary = create_salary()

    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 9, 1),
                narration="SALARY CREDIT - DEMO COMPANY",
                credit=Decimal("50500"),
            ),
            BankTransaction(
                date=date(2026, 9, 5),
                narration="SWIGGY",
                debit=Decimal("850"),
            ),
        ]
    )

    result = ReconciliationService().reconcile(
        salary,
        statement,
    )

    assert result.status == ReconciliationStatus.MATCHED
    assert result.selected_candidate is not None
    assert result.selected_candidate.amount == Decimal("50500")
    assert result.selected_candidate.amount_score == 1.0
    assert result.confidence >= 0.80


def test_non_matching_amount_does_not_auto_match():
    salary = create_salary()

    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 9, 1),
                narration="SALARY CREDIT - DEMO COMPANY",
                credit=Decimal("45000"),
            ),
        ]
    )

    result = ReconciliationService().reconcile(
        salary,
        statement,
    )

    assert result.status in {
        ReconciliationStatus.NO_MATCH,
        ReconciliationStatus.NEEDS_REVIEW,
    }

    if result.selected_candidate:
        assert result.selected_candidate.amount != Decimal("50500")


def test_debits_are_not_salary_candidates():
    salary = create_salary()

    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 9, 1),
                narration="SALARY PAYMENT",
                debit=Decimal("50500"),
            ),
        ]
    )

    result = ReconciliationService().reconcile(
        salary,
        statement,
    )

    assert result.status == ReconciliationStatus.NO_MATCH
    assert result.candidates == []


def test_salary_month_is_used_for_date_scoring():
    salary = create_salary()

    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 9, 15),
                narration="SALARY CREDIT",
                credit=Decimal("50500"),
            ),
        ]
    )

    result = ReconciliationService().reconcile(
        salary,
        statement,
    )

    assert result.selected_candidate is not None
    assert result.selected_candidate.date_score == 1.0


def test_employer_and_salary_narration_strengthen_match():
    salary = create_salary(
        employer="Demo Company",
    )

    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 9, 1),
                narration="SALARY CREDIT DEMO COMPANY",
                credit=Decimal("50500"),
            ),
        ]
    )

    result = ReconciliationService().reconcile(
        salary,
        statement,
    )

    assert result.status == ReconciliationStatus.MATCHED
    assert result.selected_candidate is not None
    assert result.selected_candidate.narration_score == 1.0


def test_multiple_strong_candidates_require_review():
    salary = create_salary()

    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 9, 1),
                narration="SALARY CREDIT DEMO COMPANY",
                credit=Decimal("50500"),
            ),
            BankTransaction(
                date=date(2026, 9, 3),
                narration="SALARY CREDIT DEMO COMPANY",
                credit=Decimal("50500"),
            ),
        ]
    )

    result = ReconciliationService().reconcile(
        salary,
        statement,
    )

    assert result.status == ReconciliationStatus.MULTIPLE_CANDIDATES
    assert result.selected_candidate is None
    assert len(result.candidates) == 2


def test_missing_salary_net_requires_review():
    salary = create_salary(net=None)

    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 9, 1),
                narration="SALARY CREDIT DEMO COMPANY",
                credit=Decimal("50500"),
            ),
        ]
    )

    result = ReconciliationService().reconcile(
        salary,
        statement,
    )

    assert result.status == ReconciliationStatus.NEEDS_REVIEW
    assert result.selected_candidate is None


def test_no_bank_credits_returns_no_match():
    salary = create_salary()

    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 9, 2),
                narration="ATM WITHDRAWAL",
                debit=Decimal("5000"),
            ),
        ]
    )

    result = ReconciliationService().reconcile(
        salary,
        statement,
    )

    assert result.status == ReconciliationStatus.NO_MATCH
    assert result.candidates == []
