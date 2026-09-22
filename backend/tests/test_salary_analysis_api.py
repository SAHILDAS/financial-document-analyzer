from io import BytesIO

import pymupdf
from fastapi.testclient import TestClient

from app.main import app


def create_salary_pdf() -> bytes:
    document = pymupdf.open()

    page = document.new_page()

    page.insert_text(
        (72, 72),
        "Salary Slip\n"
        "Employee Name: Test Employee\n"
        "Employer: Example Technologies\n"
        "Gross Salary: 65000\n"
        "Total Deductions: 6000\n"
        "Net Salary: 59000\n",
    )

    content = document.tobytes()

    document.close()

    return content


def create_complete_salary_pdf() -> bytes:
    document = pymupdf.open()

    page = document.new_page()

    page.insert_text(
        (72, 72),
        "Salary Slip\n"
        "Employee Name: Test Employee\n"
        "Employer: Example Technologies\n"
        "Basic Salary: 40000\n"
        "HRA: 15000\n"
        "Allowances: 10000\n"
        "Gross Salary: 65000\n"
        "PF: 4800\n"
        "TDS: 1200\n"
        "Total Deductions: 6000\n"
        "Net Salary: 59000\n",
    )

    content = document.tobytes()

    document.close()

    return content


def test_analyze_salary_document_runs_salary_pipeline():
    client = TestClient(app)

    response = client.post(
        "/api/documents/analyze",
        files={
            "file": (
                "salary.pdf",
                BytesIO(create_salary_pdf()),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["document_type"] == "salary_slip"

    assert body["confidence"] >= 0.0
    assert body["confidence"] <= 1.0

    assert body["validation"] is not None


def test_analyze_non_salary_document_keeps_existing_behavior():
    document = pymupdf.open()

    page = document.new_page()

    page.insert_text(
        (72, 72),
        "Bank Statement\n"
        "Account Statement\n"
        "Opening Balance: 10000\n"
        "Closing Balance: 15000\n"
        "Transaction Date\n",
    )

    content = document.tobytes()

    document.close()

    client = TestClient(app)

    response = client.post(
        "/api/documents/analyze",
        files={
            "file": (
                "bank.pdf",
                BytesIO(content),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["document_type"] == "bank_statement"


def test_salary_document_returns_complete_analysis():
    client = TestClient(app)

    content = create_complete_salary_pdf()

    response = client.post(
        "/api/documents/analyze",
        files={
            "file": (
                "salary.pdf",
                BytesIO(content),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["document_type"] == "salary_slip"

    salary = body["data"]["salary"]

    assert salary["salary"]["employee"]["name"] == "Test Employee"

    assert salary["salary"]["employee"]["employer"] == (
        "Example Technologies"
    )

    assert salary["salary"]["earnings"]["basic"] == "40000"
    assert salary["salary"]["earnings"]["hra"] == "15000"
    assert salary["salary"]["earnings"]["allowances"] == "10000"
    assert salary["salary"]["earnings"]["gross"] == "65000"

    assert salary["salary"]["deductions"]["pf"] == "4800"
    assert salary["salary"]["deductions"]["tds"] == "1200"
    assert salary["salary"]["deductions"]["total"] == "6000"

    assert salary["salary"]["net_salary"] == "59000"

    assert salary["calculation"]["calculated_net"] == "59000"
    assert salary["calculation"]["reported_net"] == "59000"
    assert salary["calculation"]["net_difference"] == "0"

    assert salary["validation"]["is_valid"] is True

    assert salary["confidence"]["needs_review"] is False

    assert salary["confidence"]["level"] == "high"