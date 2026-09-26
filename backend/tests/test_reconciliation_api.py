from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.bank_analysis import BankFinancialAnalysis
from app.schemas.bank_analysis_response import BankAnalysisResult
from app.schemas.bank_statement import (
    BankAccount,
    BankStatement,
    BankStatementPeriod,
    BankTransaction,
)
from app.schemas.bank_validation import BankValidationResult
from app.schemas.salary_analysis import SalaryAnalysisResult
from app.schemas.salary_slip import (
    SalaryDeductions,
    SalaryEarnings,
    SalaryEmployee,
    SalarySlip,
)
from app.schemas.validation import ValidationResult


client = TestClient(app)


def create_salary_analysis(
    *,
    net: str = "50500",
) -> SalaryAnalysisResult:
    salary = SalarySlip(
        employee=SalaryEmployee(
            name="Sanjib Das",
            employee_id="Emp101",
            employer="Demo Company",
            salary_month="September 2026",
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
        net_salary=Decimal(net),
    )

    return SalaryAnalysisResult(
    salary=salary,
    calculation={
        "calculated_earnings": "56000",
        "reported_gross": "56000",
        "earnings_difference": "0",
        "calculated_net": "50500",
        "reported_net": net,
        "net_difference": "0",
        "can_calculate_earnings": True,
        "can_calculate_net": True,
    },
    validation=ValidationResult(
        is_valid=True,
        issues=[],
    ),
    confidence={
        "score": 1.0,
        "level": "high",
        "needs_review": False,
        "reasons": [],
    },
)


def create_bank_analysis(
    transactions: list[BankTransaction],
) -> BankAnalysisResult:
    statement = BankStatement(
        account=BankAccount(
            holder_name="Sanjib Das",
            bank_name="Demo Bank",
            account_number="501234567890",
            ifsc="DEMO0001234",
        ),
        statement_period=BankStatementPeriod(
            from_date=date(2026, 9, 1),
            to_date=date(2026, 9, 30),
        ),
        opening_balance=Decimal("80000"),
        closing_balance=Decimal("125500"),
        transactions=transactions,
    )

    return BankAnalysisResult(
        statement=statement,
        analysis=BankFinancialAnalysis(
            total_credits=Decimal("50500"),
            total_debits=Decimal("0"),
            average_monthly_credit=Decimal("50500"),
            large_transactions=[],
            salary_credit_candidates=[],
            recurring_transactions=[],
            emi_candidates=[],
        ),
        validation=BankValidationResult(
            is_valid=True,
            issues=[],
        ),
    )


def make_request_payload(
    *,
    salary_net: str = "50500",
    transactions: list[BankTransaction],
) -> dict:
    salary = create_salary_analysis(net=salary_net)
    bank = create_bank_analysis(transactions)

    return {
        "salary": salary.model_dump(mode="json"),
        "bank": bank.model_dump(mode="json"),
    }


def test_reconciliation_api_matches_exact_salary_credit():
    payload = make_request_payload(
        transactions=[
            BankTransaction(
                date=date(2026, 9, 10),
                narration="NEFT CREDIT DEMO COMPANY SALARY",
                credit=Decimal("50500"),
            )
        ],
    )

    response = client.post(
        "/api/documents/reconcile",
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["result"]["status"] == "matched"
    assert body["result"]["salary_net_amount"] == "50500"
    assert body["result"]["selected_candidate"]["amount"] == "50500"


def test_reconciliation_api_handles_amount_mismatch():
    payload = make_request_payload(
        transactions=[
            BankTransaction(
                date=date(2026, 9, 10),
                narration="NEFT CREDIT DEMO COMPANY SALARY",
                credit=Decimal("48500"),
            )
        ],
    )

    response = client.post(
        "/api/documents/reconcile",
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["result"]["status"] in {
        "no_match",
        "needs_review",
    }


def test_reconciliation_api_handles_no_salary_credit():
    payload = make_request_payload(
        transactions=[
            BankTransaction(
                date=date(2026, 9, 10),
                narration="NEFT CREDIT FREELANCE PAYMENT",
                credit=Decimal("25000"),
            ),
        ],
    )

    response = client.post(
        "/api/documents/reconcile",
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["result"]["status"] in {
        "no_match",
        "needs_review",
    }


def test_reconciliation_api_handles_multiple_candidates():
    payload = make_request_payload(
        transactions=[
            BankTransaction(
                date=date(2026, 9, 8),
                narration="SALARY CREDIT DEMO COMPANY",
                credit=Decimal("50500"),
            ),
            BankTransaction(
                date=date(2026, 9, 10),
                narration="SALARY CREDIT DEMO COMPANY",
                credit=Decimal("50500"),
            ),
        ],
    )

    response = client.post(
        "/api/documents/reconcile",
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["result"]["status"] == "multiple_candidates"
    assert body["result"]["selected_candidate"] is None


def test_reconciliation_api_rejects_missing_salary():
    payload = {
        "bank": create_bank_analysis(
            [
                BankTransaction(
                    date=date(2026, 9, 10),
                    narration="SALARY CREDIT",
                    credit=Decimal("50500"),
                )
            ]
        ).model_dump(mode="json")
    }

    response = client.post(
        "/api/documents/reconcile",
        json=payload,
    )

    assert response.status_code == 422
