from decimal import Decimal

from app.services.extraction.llm_bank_extractor import LlmBankExtractor


def test_normalize_iso_date():
    assert (
        LlmBankExtractor._normalize_date("2025-07-01")
        == "2025-07-01"
    )


def test_normalize_human_readable_date():
    assert (
        LlmBankExtractor._normalize_date("01 Jul 2025")
        == "2025-07-01"
    )


def test_normalize_full_month_date():
    assert (
        LlmBankExtractor._normalize_date("31 August 2025")
        == "2025-08-31"
    )


def test_normalize_indian_number_format():
    assert (
        LlmBankExtractor._normalize_decimal("1,20,000.00")
        == "120000.00"
    )


def test_normalize_indian_lakh_format():
    assert (
        LlmBankExtractor._normalize_decimal("1,04,995.75")
        == "104995.75"
    )


def test_normalize_currency_value():
    assert (
        LlmBankExtractor._normalize_decimal("₹50,000")
        == "50000"
    )


def test_normalize_decimal_value():
    assert (
        LlmBankExtractor._normalize_decimal(" 12,500.00 ")
        == "12500.00"
    )


def test_normalize_none():
    assert LlmBankExtractor._normalize_decimal(None) is None
    assert LlmBankExtractor._normalize_date(None) is None


def test_normalize_complete_bank_response():
    response = {
        "account": {
            "holder_name": "Priya Menon",
            "bank_name": "HDFC Bank",
            "account_number": "XXXX6789",
            "ifsc": "HDFC0001234",
        },
        "statement_period": {
            "from_date": "01 Jul 2025",
            "to_date": "31 Jul 2025",
        },
        "opening_balance": "52,340.75",
        "closing_balance": "1,04,995.75",
        "transactions": [
            {
                "date": "01 Jul 2025",
                "narration": "Salary Credit - TechFusion Pvt Ltd",
                "debit": None,
                "credit": "1,20,000.00",
                "balance": "1,72,340.75",
            }
        ],
    }

    normalized = LlmBankExtractor._normalize_response(response)

    assert normalized["statement_period"]["from_date"] == "2025-07-01"
    assert normalized["statement_period"]["to_date"] == "2025-07-31"

    assert normalized["opening_balance"] == "52340.75"
    assert normalized["closing_balance"] == "104995.75"

    transaction = normalized["transactions"][0]

    assert transaction["date"] == "2025-07-01"
    assert transaction["credit"] == "120000.00"
    assert transaction["balance"] == "172340.75"