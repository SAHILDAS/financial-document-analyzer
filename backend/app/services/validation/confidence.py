from app.schemas.confidence import (
    ConfidenceLevel,
    ConfidenceResult,
)
from app.schemas.salary_slip import SalarySlip
from app.schemas.validation import (
    ValidationResult,
    ValidationSeverity,
)


class SalaryConfidenceCalculator:
    """Calculate deterministic confidence for extracted salary data."""

    HIGH_THRESHOLD = 0.85
    MEDIUM_THRESHOLD = 0.65

    def calculate(
        self,
        salary: SalarySlip,
        validation: ValidationResult,
        *,
        text_quality_score: float = 1.0,
    ) -> ConfidenceResult:
        score = 1.0
        reasons: list[str] = []

        score = self._apply_text_quality(
            score,
            text_quality_score,
            reasons,
        )

        score = self._apply_field_completeness(
            score,
            salary,
            reasons,
        )

        score = self._apply_validation(
            score,
            validation,
            reasons,
        )

        score = max(0.0, min(1.0, score))

        level = self._get_level(score)

        has_errors = any(
            issue.severity == ValidationSeverity.ERROR
            for issue in validation.issues
        )

        needs_review = (
            has_errors
            or level == ConfidenceLevel.LOW
        )

        return ConfidenceResult(
            score=round(score, 4),
            level=level,
            needs_review=needs_review,
            reasons=reasons,
        )

    @staticmethod
    def _apply_text_quality(
        score: float,
        text_quality_score: float,
        reasons: list[str],
    ) -> float:
        quality = max(0.0, min(1.0, text_quality_score))

        if quality < 0.65:
            reasons.append(
                "Extracted document text quality is low."
            )
            return score - 0.20

        if quality < 0.85:
            reasons.append(
                "Extracted document text quality is moderate."
            )
            return score - 0.10

        return score

    @staticmethod
    def _apply_field_completeness(
        score: float,
        salary: SalarySlip,
        reasons: list[str],
    ) -> float:
        fields = [
            salary.employee.name,
            salary.employee.employer,
            salary.employee.salary_month,
            salary.earnings.gross,
            salary.deductions.total,
            salary.net_salary,
        ]

        present = sum(
            value is not None
            for value in fields
        )

        completeness = present / len(fields)

        if completeness < 0.50:
            reasons.append(
                "Several important salary fields are missing."
            )
            return score - 0.25

        if completeness < 0.80:
            reasons.append(
                "Some important salary fields are missing."
            )
            return score - 0.10

        return score

    @staticmethod
    def _apply_validation(
        score: float,
        validation: ValidationResult,
        reasons: list[str],
    ) -> float:
        errors = sum(
            issue.severity == ValidationSeverity.ERROR
            for issue in validation.issues
        )

        warnings = sum(
            issue.severity == ValidationSeverity.WARNING
            for issue in validation.issues
        )

        if errors:
            reasons.append(
                "Financial consistency validation found errors."
            )
            score -= min(0.40, errors * 0.20)

        if warnings:
            reasons.append(
                "Validation found warnings or unverifiable fields."
            )
            score -= min(0.20, warnings * 0.05)

        return score

    def _get_level(
        self,
        score: float,
    ) -> ConfidenceLevel:
        if score >= self.HIGH_THRESHOLD:
            return ConfidenceLevel.HIGH

        if score >= self.MEDIUM_THRESHOLD:
            return ConfidenceLevel.MEDIUM

        return ConfidenceLevel.LOW