from io import BytesIO

import fitz
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_pdf(text: str) -> bytes:
    """Create a small native-text PDF for API integration tests."""
    document = fitz.open()

    page = document.new_page()
    page.insert_text(
        (50, 80),
        text,
        fontsize=12,
    )

    buffer = BytesIO()
    document.save(buffer)
    document.close()

    return buffer.getvalue()


def test_bank_statement_api_returns_complete_analysis():
    pdf_content = create_pdf(
        """
        BANK STATEMENT

        Account Holder: Test Employee
        Bank: Example Bank

        Transaction Date
        Opening Balance
        Closing Balance

        Account Statement
        Salary Credit
        Loan EMI
        Debit
        Credit
        """
    )

    response = client.post(
        "/api/documents/analyze",
        files={
            "file": (
                "bank_statement.pdf",
                pdf_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["document_id"]
    assert body["document_type"] == "bank_statement"

    assert 0.0 <= body["confidence"] <= 1.0

    assert body["data"] is not None
    assert body["data"]["bank"] is not None

    bank = body["data"]["bank"]

    # ---------------------------------------------------------
    # Extracted statement
    # ---------------------------------------------------------

    statement = bank["statement"]

    assert statement["account"]["holder_name"] == "Test Employee"
    assert statement["account"]["bank_name"] == "Example Bank"
    assert statement["account"]["account_number"] == "XXXXXX1234"
    assert statement["account"]["ifsc"] == "EXMP0001234"

    assert statement["statement_period"]["from_date"] == "2026-08-01"
    assert statement["statement_period"]["to_date"] == "2026-08-31"

    assert statement["opening_balance"] == "100000"
    assert statement["closing_balance"] == "131000"

    transactions = statement["transactions"]

    assert len(transactions) == 5

    # ---------------------------------------------------------
    # Deterministic financial analysis
    # ---------------------------------------------------------

    analysis = bank["analysis"]

    assert analysis["total_credits"] == "84000"
    assert analysis["total_debits"] == "53000"

    assert analysis["average_monthly_credit"] == "84000.00"

    # Salary credit
    salary_candidates = analysis["salary_credit_candidates"]

    assert len(salary_candidates) == 1
    assert (
        salary_candidates[0]["transaction"]["narration"]
        == "SALARY CREDIT AUGUST 2026"
    )
    assert salary_candidates[0]["score"] >= 0.8

    # Large transaction
    large_transactions = analysis["large_transactions"]

    assert len(large_transactions) == 1
    assert large_transactions[0]["amount"] == "59000"
    assert large_transactions[0]["direction"] == "credit"

    # EMI candidate
    emi_candidates = analysis["emi_candidates"]

    assert len(emi_candidates) == 1
    assert emi_candidates[0]["transaction"]["narration"] == "HOME LOAN EMI"
    assert emi_candidates[0]["score"] >= 0.8

    # No repeated narration in the mock statement
    assert analysis["recurring_transactions"] == []

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    validation = bank["validation"]

    assert validation["is_valid"] is True
    assert validation["issues"] == []

    # Top-level validation mirrors bank validation
    assert body["validation"]["is_valid"] is True
    assert body["validation"]["issues"] == []

    # ---------------------------------------------------------
    # Processing metadata
    # ---------------------------------------------------------

    processing = body["processing"]

    assert processing is not None
    assert processing["source"] == "native_text"
    assert "pdf_text" in processing["methods"]
    assert processing["page_count"] == 1
    assert processing["text_quality_score"] > 0


def test_bank_statement_api_preserves_file_metadata():
    pdf_content = create_pdf(
        """
        BANK STATEMENT
        ACCOUNT STATEMENT
        TRANSACTION DATE
        OPENING BALANCE
        CLOSING BALANCE
        """
    )

    filename = "my_bank_statement.pdf"

    response = client.post(
        "/api/documents/analyze",
        files={
            "file": (
                filename,
                pdf_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["file"]["filename"] == filename
    assert body["data"]["file"]["extension"] == ".pdf"
    assert body["data"]["file"]["size_bytes"] == len(pdf_content)


def test_unsupported_file_returns_graceful_error():
    response = client.post(
        "/api/documents/analyze",
        files={
            "file": (
                "bank_statement.txt",
                b"this is not a supported financial document",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["document_id"]

    assert body["data"] is not None
    assert body["data"]["file"]["filename"] == "bank_statement.txt"

    assert body["errors"]

    assert body["errors"][0]["code"] == "UNSUPPORTED_FILE_TYPE"
    assert body["errors"][0]["retryable"] is False