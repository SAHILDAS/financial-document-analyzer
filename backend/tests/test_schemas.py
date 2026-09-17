from app.schemas.classification import ClassificationResult
from app.schemas.document import DocumentType
from app.schemas.processing import ProcessingMetadata, ProcessingStatus
from app.schemas.validation import (
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)


def test_classification_result():
    result = ClassificationResult(
        document_type=DocumentType.SALARY_SLIP,
        confidence=0.94,
        reason="Salary-related fields detected.",
    )

    assert result.document_type == DocumentType.SALARY_SLIP
    assert result.confidence == 0.94


def test_validation_result_defaults_to_empty_issues():
    result = ValidationResult(is_valid=True)

    assert result.is_valid is True
    assert result.issues == []


def test_validation_issue():
    issue = ValidationIssue(
        code="SALARY_NET_MISMATCH",
        message="Gross salary minus deductions does not match net salary.",
        severity=ValidationSeverity.WARNING,
        field="net_salary",
    )

    assert issue.code == "SALARY_NET_MISMATCH"
    assert issue.severity == ValidationSeverity.WARNING


def test_processing_metadata():
    metadata = ProcessingMetadata(
        status=ProcessingStatus.COMPLETED,
        processing_time_ms=1250,
        pages_processed=2,
        ocr_used=True,
    )

    assert metadata.status == ProcessingStatus.COMPLETED
    assert metadata.pages_processed == 2
    assert metadata.ocr_used is True