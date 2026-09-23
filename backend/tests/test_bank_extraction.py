from app.services.extraction.bank_extractor import BankExtractionError
from app.services.extraction.providers.factory import create_bank_extractor


def test_bank_extractor_returns_structured_statement():
    extractor = create_bank_extractor()

    result = extractor.extract(
        """
        Example Bank
        Account Holder: Test Employee
        Statement Period: 2026-08-01 to 2026-08-31
        """
    )

    assert result.account.holder_name == "Test Employee"
    assert result.account.bank_name == "Example Bank"
    assert result.statement_period.from_date is not None
    assert result.statement_period.to_date is not None
    assert len(result.transactions) == 5


def test_bank_extractor_returns_transaction_data():
    extractor = create_bank_extractor()

    result = extractor.extract("bank statement text")

    salary = result.transactions[0]

    assert salary.narration == "SALARY CREDIT AUGUST 2026"
    assert salary.credit == 59000
    assert salary.debit is None


def test_bank_extractor_handles_empty_text():
    extractor = create_bank_extractor()

    try:
        extractor.extract("")
        assert False, "Expected BankExtractionError"
    except BankExtractionError as exc:
        assert "empty text" in str(exc).lower()