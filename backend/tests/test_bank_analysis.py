from datetime import date
from decimal import Decimal

from app.schemas.bank_statement import (
    BankAccount,
    BankStatement,
    BankStatementPeriod,
    BankTransaction,
)
from app.services.analysis.bank_analysis import BankFinancialAnalyzer


def create_statement(
    transactions: list[BankTransaction],
) -> BankStatement:
    return BankStatement(
        account=BankAccount(
            holder_name="Test Employee",
            bank_name="Example Bank",
            account_number="XXXXXX1234",
            ifsc="EXMP0001234",
        ),
        statement_period=BankStatementPeriod(
            from_date=date(2026, 8, 1),
            to_date=date(2026, 8, 31),
        ),
        opening_balance=Decimal("100000"),
        closing_balance=Decimal("131000"),
        transactions=transactions,
    )


def test_calculates_total_credits():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 1),
                narration="SALARY CREDIT",
                credit=Decimal("59000"),
                debit=None,
                balance=Decimal("159000"),
            ),
            BankTransaction(
                date=date(2026, 8, 15),
                narration="TRANSFER FROM SAVINGS",
                credit=Decimal("25000"),
                debit=None,
                balance=Decimal("184000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert result.total_credits == Decimal("84000")


def test_calculates_total_debits():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 5),
                narration="HOME LOAN EMI",
                debit=Decimal("18000"),
                credit=None,
                balance=Decimal("141000"),
            ),
            BankTransaction(
                date=date(2026, 8, 20),
                narration="ONLINE PURCHASE",
                debit=Decimal("30000"),
                credit=None,
                balance=Decimal("111000"),
            ),
            BankTransaction(
                date=date(2026, 8, 25),
                narration="UTILITY PAYMENT",
                debit=Decimal("5000"),
                credit=None,
                balance=Decimal("106000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert result.total_debits == Decimal("53000")


def test_calculates_average_monthly_credit_for_single_month():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 1),
                narration="SALARY CREDIT",
                credit=Decimal("59000"),
                debit=None,
                balance=Decimal("159000"),
            ),
            BankTransaction(
                date=date(2026, 8, 15),
                narration="TRANSFER FROM SAVINGS",
                credit=Decimal("25000"),
                debit=None,
                balance=Decimal("184000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert result.average_monthly_credit == Decimal("84000.00")


def test_calculates_average_monthly_credit_across_multiple_months():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 7, 1),
                narration="SALARY CREDIT JULY",
                credit=Decimal("50000"),
                debit=None,
                balance=Decimal("150000"),
            ),
            BankTransaction(
                date=date(2026, 8, 1),
                narration="SALARY CREDIT AUGUST",
                credit=Decimal("60000"),
                debit=None,
                balance=Decimal("210000"),
            ),
            BankTransaction(
                date=date(2026, 8, 15),
                narration="TRANSFER",
                credit=Decimal("20000"),
                debit=None,
                balance=Decimal("230000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    # July = 50,000
    # August = 80,000
    # Average = 65,000
    assert result.average_monthly_credit == Decimal("65000.00")


def test_returns_none_when_there_are_no_credit_transactions():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 5),
                narration="HOME LOAN EMI",
                debit=Decimal("18000"),
                credit=None,
                balance=Decimal("82000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert result.total_credits == Decimal("0")
    assert result.average_monthly_credit is None


def test_empty_statement_returns_zero_totals():
    statement = create_statement([])

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert result.total_credits == Decimal("0")
    assert result.total_debits == Decimal("0")
    assert result.average_monthly_credit is None


def test_detects_large_credit_transaction():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 1),
                narration="SALARY CREDIT",
                credit=Decimal("59000"),
                debit=None,
                balance=Decimal("159000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert len(result.large_transactions) == 1

    large_transaction = result.large_transactions[0]

    assert large_transaction.amount == Decimal("59000")
    assert large_transaction.direction == "credit"
    assert "₹50,000" in large_transaction.reason


def test_detects_large_debit_transaction():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 10),
                narration="PROPERTY PAYMENT",
                debit=Decimal("75000"),
                credit=None,
                balance=Decimal("25000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert len(result.large_transactions) == 1

    large_transaction = result.large_transactions[0]

    assert large_transaction.amount == Decimal("75000")
    assert large_transaction.direction == "debit"


def test_50000_transaction_is_not_classified_as_large():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 10),
                narration="TRANSFER",
                credit=Decimal("50000"),
                debit=None,
                balance=Decimal("150000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert result.large_transactions == []


def test_detects_multiple_large_transactions():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 1),
                narration="SALARY CREDIT",
                credit=Decimal("59000"),
                debit=None,
                balance=Decimal("159000"),
            ),
            BankTransaction(
                date=date(2026, 8, 10),
                narration="PROPERTY PAYMENT",
                debit=Decimal("75000"),
                credit=None,
                balance=Decimal("84000"),
            ),
            BankTransaction(
                date=date(2026, 8, 15),
                narration="SMALL TRANSFER",
                credit=Decimal("10000"),
                debit=None,
                balance=Decimal("94000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert len(result.large_transactions) == 2

    assert result.large_transactions[0].amount == Decimal("59000")
    assert result.large_transactions[0].direction == "credit"

    assert result.large_transactions[1].amount == Decimal("75000")
    assert result.large_transactions[1].direction == "debit"



def test_detects_possible_salary_credit():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 1),
                narration="SALARY CREDIT AUGUST 2026",
                credit=Decimal("59000"),
                debit=None,
                balance=Decimal("159000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert len(result.salary_credit_candidates) == 1

    candidate = result.salary_credit_candidates[0]

    assert candidate.transaction.credit == Decimal("59000")
    assert candidate.score == 1.0
    assert any(
        "salary" in reason.lower()
        for reason in candidate.reasons
    )


def test_does_not_classify_debit_as_salary_credit():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 5),
                narration="SALARY PAYMENT",
                debit=Decimal("59000"),
                credit=None,
                balance=Decimal("41000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert result.salary_credit_candidates == []


def test_detects_payroll_credit():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 1),
                narration="PAYROLL ACME CORPORATION",
                credit=Decimal("72000"),
                debit=None,
                balance=Decimal("172000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert len(result.salary_credit_candidates) == 1

    candidate = result.salary_credit_candidates[0]

    assert candidate.transaction.credit == Decimal("72000")
    assert candidate.score == 0.8


def test_ignores_unrelated_credit():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 15),
                narration="TRANSFER FROM SAVINGS",
                credit=Decimal("25000"),
                debit=None,
                balance=Decimal("125000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert result.salary_credit_candidates == []



def test_detects_recurring_transaction():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 6, 5),
                narration="HOME LOAN EMI",
                debit=Decimal("18000"),
                credit=None,
                balance=Decimal("82000"),
            ),
            BankTransaction(
                date=date(2026, 7, 5),
                narration="HOME LOAN EMI",
                debit=Decimal("18000"),
                credit=None,
                balance=Decimal("64000"),
            ),
            BankTransaction(
                date=date(2026, 8, 5),
                narration="HOME LOAN EMI",
                debit=Decimal("18000"),
                credit=None,
                balance=Decimal("46000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert len(result.recurring_transactions) == 1

    recurring = result.recurring_transactions[0]

    assert recurring.narration == "home loan emi"
    assert recurring.occurrence_count == 3
    assert recurring.average_amount == Decimal("18000.00")
    assert recurring.approximate_interval_days == 30.5


def test_recurring_transaction_detects_similar_amounts():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 6, 5),
                narration="RENT PAYMENT",
                debit=Decimal("20000"),
                credit=None,
                balance=Decimal("80000"),
            ),
            BankTransaction(
                date=date(2026, 7, 5),
                narration="RENT PAYMENT",
                debit=Decimal("20500"),
                credit=None,
                balance=Decimal("59500"),
            ),
            BankTransaction(
                date=date(2026, 8, 5),
                narration="RENT PAYMENT",
                debit=Decimal("19800"),
                credit=None,
                balance=Decimal("39700"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert len(result.recurring_transactions) == 1

    recurring = result.recurring_transactions[0]

    assert recurring.average_amount == Decimal("20100.00")

    assert any(
        "similar" in reason.lower()
        for reason in recurring.reasons
    )


def test_different_narrations_are_not_grouped():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 5),
                narration="RENT PAYMENT",
                debit=Decimal("20000"),
                credit=None,
                balance=Decimal("80000"),
            ),
            BankTransaction(
                date=date(2026, 8, 6),
                narration="UTILITY PAYMENT",
                debit=Decimal("20000"),
                credit=None,
                balance=Decimal("60000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert result.recurring_transactions == []


def test_single_transaction_is_not_recurring():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 5),
                narration="HOME LOAN EMI",
                debit=Decimal("18000"),
                credit=None,
                balance=Decimal("82000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert result.recurring_transactions == []


def test_detects_probable_emi():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 5),
                narration="HOME LOAN EMI",
                debit=Decimal("18000"),
                credit=None,
                balance=Decimal("82000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert len(result.emi_candidates) == 1

    candidate = result.emi_candidates[0]

    assert candidate.transaction.debit == Decimal("18000")
    assert candidate.score == 0.9

    assert any(
        "emi" in reason.lower()
        for reason in candidate.reasons
    )


def test_detects_loan_debit():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 5),
                narration="PERSONAL LOAN REPAYMENT",
                debit=Decimal("12000"),
                credit=None,
                balance=Decimal("88000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert len(result.emi_candidates) == 1

    candidate = result.emi_candidates[0]

    assert candidate.transaction.debit == Decimal("12000")
    assert candidate.score == 0.8


def test_detects_nach_loan_payment():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 5),
                narration="NACH HOME LOAN",
                debit=Decimal("22000"),
                credit=None,
                balance=Decimal("78000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert len(result.emi_candidates) == 1

    candidate = result.emi_candidates[0]

    assert candidate.score == 0.9

    assert any(
        "nach" in reason.lower()
        for reason in candidate.reasons
    )


def test_credit_loan_narration_is_not_emi_candidate():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 5),
                narration="LOAN DISBURSEMENT",
                debit=None,
                credit=Decimal("500000"),
                balance=Decimal("600000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert result.emi_candidates == []


def test_unrelated_debit_is_not_emi_candidate():
    statement = create_statement(
        [
            BankTransaction(
                date=date(2026, 8, 10),
                narration="ONLINE PURCHASE",
                debit=Decimal("5000"),
                credit=None,
                balance=Decimal("95000"),
            ),
        ]
    )

    analyzer = BankFinancialAnalyzer()

    result = analyzer.analyze(statement)

    assert result.emi_candidates == []
    