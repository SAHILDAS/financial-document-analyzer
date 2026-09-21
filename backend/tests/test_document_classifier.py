from app.schemas.document import DocumentType
from app.services.classification.document_classifier import DocumentClassifier


classifier = DocumentClassifier()


def test_classifies_salary_slip():
    text = """
    SALARY SLIP
    Employee Name: Rahul Kumar
    Employee ID: EMP-1024
    Pay Period: August 2026

    Earnings
    Basic Salary 50000
    HRA 20000
    Gross Salary 70000

    Deductions
    Provident Fund 6000
    Professional Tax 200
    TDS 4000

    Net Salary 59800
    """

    result = classifier.classify(text)

    assert result.document_type == DocumentType.SALARY_SLIP
    assert result.confidence >= 0.5
    assert result.reason is not None


def test_classifies_bank_statement():
    text = """
    BANK STATEMENT

    Account Holder: Rahul Kumar
    Account Number: 1234567890
    IFSC: ABCD0001234

    Opening Balance: 25000

    Transaction Date
    Narration
    Debit
    Credit
    Balance

    01/08/2026 Salary Credit 0 59800 84800
    05/08/2026 Rent Payment 18000 0 66800
    10/08/2026 Grocery 5000 0 61800

    Closing Balance: 61800
    """

    result = classifier.classify(text)

    assert result.document_type == DocumentType.BANK_STATEMENT
    assert result.confidence >= 0.5
    assert result.reason is not None


def test_unknown_document():
    text = """
    Restaurant Menu

    Pizza
    Burger
    Pasta
    Coffee
    """

    result = classifier.classify(text)

    assert result.document_type == DocumentType.UNKNOWN
    assert result.confidence == 0.0


def test_empty_text_is_unknown():
    result = classifier.classify("")

    assert result.document_type == DocumentType.UNKNOWN
    assert result.confidence == 0.0
    assert "No readable text" in (result.reason or "")


def test_ambiguous_document_is_not_forced_into_a_type():
    text = """
    Salary credit
    Account balance
    Credit
    Debit
    Employee name
    """

    result = classifier.classify(text)

    assert result.document_type == DocumentType.UNKNOWN
    assert result.reason is not None


def test_classification_is_case_insensitive():
    text = """
    salary slip
    BASIC SALARY
    GROSS SALARY
    NET SALARY
    """

    result = classifier.classify(text)

    assert result.document_type == DocumentType.SALARY_SLIP


def test_signal_boundaries_prevent_accidental_substring_matches():
    text = """
    Threat analysis completed.
    Creditworthy customer profile.
    """

    result = classifier.classify(text)

    assert result.document_type == DocumentType.UNKNOWN