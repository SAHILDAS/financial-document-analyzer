from io import BytesIO

import pymupdf
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_text_pdf(text: str) -> bytes:
    document = pymupdf.open()

    page = document.new_page()
    page.insert_text((72, 72), text)

    content = document.tobytes()
    document.close()

    return content


def test_analyze_salary_document() -> None:
    pdf_content = create_text_pdf(
        """
        Salary Slip
        Employee Name: John Doe
        Employee ID: EMP001
        Basic Salary: 50000
        HRA: 20000
        Gross Salary: 70000
        Provident Fund: 6000
        TDS: 4000
        Net Salary: 60000
        """
    )

    response = client.post(
        "/api/documents/analyze",
        files={
            "file": (
                "salary.pdf",
                BytesIO(pdf_content),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["document_type"] == "salary_slip"
    assert body["document_id"]
    assert body["confidence"] > 0
    assert body["data"]["classification_reason"]
    assert body["processing"]["source"] == "native_text"
    assert "text" not in body


def test_analyze_bank_document() -> None:
    pdf_content = create_text_pdf(
        """
        Bank Statement
        Account Number: 1234567890
        IFSC: ABCD0001234
        Transaction Date
        Opening Balance: 50000
        Closing Balance: 75000
        Narration
        Credit
        Debit
        Available Balance
        """
    )

    response = client.post(
        "/api/documents/analyze",
        files={
            "file": (
                "bank.pdf",
                BytesIO(pdf_content),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["document_type"] == "bank_statement"
    assert body["document_id"]
    assert body["confidence"] > 0
    assert body["processing"]["source"] == "native_text"
    assert "text" not in body


def test_analyze_unsupported_file() -> None:
    response = client.post(
        "/api/documents/analyze",
        files={
            "file": (
                "document.txt",
                BytesIO(b"unsupported content"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["errors"]
    assert body["errors"][0]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_analyze_unknown_document() -> None:
    pdf_content = create_text_pdf(
        """
        General Company Information
        Project Overview
        Meeting Notes
        """
    )

    response = client.post(
        "/api/documents/analyze",
        files={
            "file": (
                "unknown.pdf",
                BytesIO(pdf_content),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["document_type"] == "unknown"
    assert body["confidence"] == 0.0
    assert body["data"]["classification_reason"]