import re

from app.schemas.classification import ClassificationResult
from app.schemas.document import DocumentType


class DocumentClassifier:
    """Classify supported financial documents using deterministic text signals."""

    MINIMUM_SCORE = 3.0
    MINIMUM_CONFIDENCE = 0.50
    MINIMUM_SCORE_GAP = 1.0

    # Strong document-level signals.
    #
    # Generic financial words such as "credit", "debit", or "balance"
    # should not be sufficient on their own to classify a document.
    STRONG_SALARY_SIGNALS = {
        "salary slip",
        "salary statement",
        "pay slip",
        "payslip",
        "pay period",
        "basic salary",
        "basic pay",
        "gross salary",
        "gross pay",
        "net salary",
        "net pay",
    }

    STRONG_BANK_SIGNALS = {
        "bank statement",
        "account statement",
        "transaction date",
        "opening balance",
        "closing balance",
    }

    # Salary-slip classification signals.
    SALARY_SIGNALS: dict[str, float] = {
        "salary slip": 5.0,
        "salary statement": 4.5,
        "pay slip": 5.0,
        "payslip": 5.0,
        "pay period": 3.0,
        "employee id": 2.5,
        "employee name": 1.5,
        "basic salary": 4.0,
        "basic pay": 4.0,
        "gross salary": 4.0,
        "gross pay": 4.0,
        "net salary": 4.0,
        "net pay": 4.0,
        "earnings": 2.0,
        "deductions": 2.0,
        "house rent allowance": 3.0,
        "hra": 2.0,
        "provident fund": 2.5,
        "professional tax": 2.5,
        "tds": 2.0,
    }

    # Bank-statement classification signals.
    BANK_SIGNALS: dict[str, float] = {
        "bank statement": 5.0,
        "account statement": 4.5,
        "transaction date": 3.0,
        "opening balance": 4.0,
        "closing balance": 4.0,
        "account number": 2.0,
        "ifsc": 2.0,
        "transaction": 1.5,
        "narration": 2.5,
        "withdrawal": 2.0,
        "deposit": 2.0,
        "debit": 1.5,
        "credit": 1.5,
        "available balance": 2.5,
    }

    def classify(self, text: str) -> ClassificationResult:
        """
        Classify a document based on normalized textual evidence.

        The classifier intentionally requires document-level evidence before
        returning SALARY_SLIP or BANK_STATEMENT. This prevents generic
        financial terms such as "credit", "debit", or "balance" from causing
        an unsupported classification.
        """

        normalized_text = self._normalize_text(text)

        if not normalized_text:
            return ClassificationResult(
                document_type=DocumentType.UNKNOWN,
                confidence=0.0,
                reason="No readable text was available for classification.",
            )

        salary_score, salary_matches = self._calculate_score(
            normalized_text,
            self.SALARY_SIGNALS,
        )

        bank_score, bank_matches = self._calculate_score(
            normalized_text,
            self.BANK_SIGNALS,
        )

        document_type, confidence = self._determine_type(
            salary_score=salary_score,
            bank_score=bank_score,
            salary_matches=salary_matches,
            bank_matches=bank_matches,
        )

        reason = self._build_reason(
            document_type=document_type,
            salary_score=salary_score,
            bank_score=bank_score,
            salary_matches=salary_matches,
            bank_matches=bank_matches,
        )

        return ClassificationResult(
            document_type=document_type,
            confidence=confidence,
            reason=reason,
        )

    def _determine_type(
        self,
        salary_score: float,
        bank_score: float,
        salary_matches: list[str] | None = None,
        bank_matches: list[str] | None = None,
    ) -> tuple[DocumentType, float]:
        """
        Determine the document type from weighted evidence.

        A strong document-level signal is required before returning a
        supported document type. Ambiguous evidence results in UNKNOWN.
        """

        salary_matches = salary_matches or []
        bank_matches = bank_matches or []

        has_strong_salary_signal = any(
            signal in self.STRONG_SALARY_SIGNALS
            for signal in salary_matches
        )

        has_strong_bank_signal = any(
            signal in self.STRONG_BANK_SIGNALS
            for signal in bank_matches
        )

        # Not enough evidence for either supported document type.
        if (
            salary_score < self.MINIMUM_SCORE
            and bank_score < self.MINIMUM_SCORE
        ):
            return DocumentType.UNKNOWN, 0.0

        # Generic financial terminology without document-level evidence
        # must not force a classification.
        if not has_strong_salary_signal and not has_strong_bank_signal:
            return DocumentType.UNKNOWN, 0.0

        # If both document types have similar evidence, classification is
        # ambiguous and should be reviewed rather than forced.
        if abs(salary_score - bank_score) < self.MINIMUM_SCORE_GAP:
            return DocumentType.UNKNOWN, self._calculate_confidence(
                salary_score,
                bank_score,
            )

        confidence = self._calculate_confidence(
            salary_score,
            bank_score,
        )

        if confidence < self.MINIMUM_CONFIDENCE:
            return DocumentType.UNKNOWN, confidence

        if has_strong_salary_signal and salary_score > bank_score:
            return DocumentType.SALARY_SLIP, confidence

        if has_strong_bank_signal and bank_score > salary_score:
            return DocumentType.BANK_STATEMENT, confidence

        return DocumentType.UNKNOWN, confidence

    @staticmethod
    def _calculate_confidence(
        salary_score: float,
        bank_score: float,
    ) -> float:
        """Calculate confidence from the relative winning score."""

        total_score = salary_score + bank_score

        if total_score <= 0:
            return 0.0

        winning_score = max(salary_score, bank_score)

        return round(winning_score / total_score, 3)

    @staticmethod
    def _calculate_score(
        text: str,
        signals: dict[str, float],
    ) -> tuple[float, list[str]]:
        """Calculate a weighted score and return the matched signals."""

        score = 0.0
        matches: list[str] = []

        for signal, weight in signals.items():
            if DocumentClassifier._contains_signal(text, signal):
                score += weight
                matches.append(signal)

        return score, matches

    @staticmethod
    def _contains_signal(text: str, signal: str) -> bool:
        """
        Check for a whole-word/phrase match.

        Word boundaries prevent accidental substring matches such as
        matching "hra" inside an unrelated word.
        """

        escaped_signal = re.escape(signal)

        pattern = rf"(?<!\w){escaped_signal}(?!\w)"

        return re.search(pattern, text) is not None

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize whitespace and casing before classification."""

        return " ".join(text.lower().split())

    @staticmethod
    def _build_reason(
        document_type: DocumentType,
        salary_score: float,
        bank_score: float,
        salary_matches: list[str],
        bank_matches: list[str],
    ) -> str:
        """Build a human-readable explanation for the classification."""

        if document_type == DocumentType.SALARY_SLIP:
            matches = ", ".join(salary_matches[:5])

            return (
                f"Salary-slip signals scored {salary_score:.1f} "
                f"versus bank-statement signals {bank_score:.1f}. "
                f"Matched signals: {matches}."
            )

        if document_type == DocumentType.BANK_STATEMENT:
            matches = ", ".join(bank_matches[:5])

            return (
                f"Bank-statement signals scored {bank_score:.1f} "
                f"versus salary-slip signals {salary_score:.1f}. "
                f"Matched signals: {matches}."
            )

        matched_signals = salary_matches[:3] + bank_matches[:3]

        if matched_signals:
            matches = ", ".join(matched_signals)

            return (
                "The document contains insufficient or ambiguous "
                f"classification signals. Matched signals: {matches}."
            )

        return (
            "No recognized salary-slip or bank-statement "
            "signals were found."
        )