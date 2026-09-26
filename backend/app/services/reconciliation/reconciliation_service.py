from __future__ import annotations

import re
from calendar import monthrange
from datetime import date, datetime, timedelta
from decimal import Decimal
from difflib import SequenceMatcher

from app.schemas.bank_statement import BankStatement, BankTransaction
from app.schemas.reconciliation import (
    ReconciliationCandidate,
    ReconciliationResult,
    ReconciliationStatus,
)
from app.schemas.salary_slip import SalarySlip


class ReconciliationService:
    """
    Deterministically reconcile salary net pay against bank credits.

    The service deliberately does not use an LLM. It compares the
    extracted salary amount and salary month against credit transactions
    in the bank statement and produces explainable candidate scores.
    """

    AMOUNT_WEIGHT = 0.50
    DATE_WEIGHT = 0.25
    NARRATION_WEIGHT = 0.15
    PERIODICITY_WEIGHT = 0.10

    DATE_TOLERANCE_DAYS = 7
    STRONG_DATE_TOLERANCE_DAYS = 3

    MATCH_THRESHOLD = 0.80
    REVIEW_THRESHOLD = 0.65
    CANDIDATE_THRESHOLD = 0.50

    AMOUNT_EXACT_TOLERANCE = Decimal("1.00")
    AMOUNT_PERCENT_TOLERANCE = Decimal("0.02")

    SALARY_KEYWORDS = (
        "salary",
        "payroll",
        "wages",
        "pay credit",
        "salary credit",
        "salary neft",
        "salary transfer",
    )

    def reconcile(
        self,
        salary: SalarySlip,
        statement: BankStatement,
    ) -> ReconciliationResult:
        """
        Reconcile salary net salary against bank credit transactions.
        """

        salary_amount = salary.net_salary

        if salary_amount is None:
            return ReconciliationResult(
                status=ReconciliationStatus.NEEDS_REVIEW,
                salary_net_amount=Decimal("0"),
                candidates=[],
                selected_candidate=None,
                confidence=0.0,
                explanation=(
                    "Salary net amount is missing, so bank reconciliation "
                    "cannot be performed."
                ),
            )

        credit_transactions = [
            transaction
            for transaction in statement.transactions
            if transaction.credit is not None
            and transaction.credit > Decimal("0")
        ]

        if not credit_transactions:
            return ReconciliationResult(
                status=ReconciliationStatus.NO_MATCH,
                salary_net_amount=salary_amount,
                candidates=[],
                selected_candidate=None,
                confidence=0.0,
                explanation=(
                    "No positive credit transactions were found in the "
                    "bank statement."
                ),
            )

        salary_month_start, salary_month_end = self._salary_month_range(
            salary.employee.salary_month
        )

        candidate_transactions = self._filter_candidate_transactions(
            credit_transactions,
            salary_month_start,
            salary_month_end,
        )

        # If salary month cannot be parsed or no transactions fall inside
        # the month, evaluate all credits rather than silently failing.
        if not candidate_transactions:
            candidate_transactions = credit_transactions

        candidates = [
            self._build_candidate(
                salary=salary,
                transaction=transaction,
                statement=statement,
            )
            for transaction in candidate_transactions
        ]

        candidates.sort(
            key=lambda candidate: candidate.overall_score,
            reverse=True,
        )

        if not candidates:
            return ReconciliationResult(
                status=ReconciliationStatus.NO_MATCH,
                salary_net_amount=salary_amount,
                candidates=[],
                selected_candidate=None,
                confidence=0.0,
                explanation="No suitable bank credit candidates were found.",
            )

        best = candidates[0]

        # A meaningful salary-amount mismatch must not be promoted to an
        # automatic match solely because date/narration evidence is strong.
        if (
            best.amount_score < 0.90
            and best.overall_score >= self.REVIEW_THRESHOLD
        ):
            return ReconciliationResult(
                status=ReconciliationStatus.NEEDS_REVIEW,
                salary_net_amount=salary_amount,
                candidates=candidates[:5],
                selected_candidate=best,
                confidence=round(best.overall_score, 4),
                explanation=(
                    "A possible salary credit was found, but the credited "
                    "amount differs materially from the salary net amount. "
                    "Human review is required."
                ),
            )

        if best.overall_score < self.CANDIDATE_THRESHOLD:
            return ReconciliationResult(
                status=ReconciliationStatus.NO_MATCH,
                salary_net_amount=salary_amount,
                candidates=candidates[:5],
                selected_candidate=None,
                confidence=round(best.overall_score, 4),
                explanation=(
                    "No bank credit reached the minimum reconciliation "
                    "candidate threshold."
                ),
            )

        if best.overall_score >= self.MATCH_THRESHOLD:
            close_candidates = [
                candidate
                for candidate in candidates[1:]
                if (
                    candidate.overall_score >= self.MATCH_THRESHOLD
                    and best.overall_score - candidate.overall_score <= 0.05
                )
            ]

            if close_candidates:
                return ReconciliationResult(
                    status=ReconciliationStatus.MULTIPLE_CANDIDATES,
                    salary_net_amount=salary_amount,
                    candidates=candidates[:5],
                    selected_candidate=None,
                    confidence=round(best.overall_score, 4),
                    explanation=(
                        "Multiple bank credits have similarly strong "
                        "reconciliation scores. Human review is required "
                        "to select the correct salary credit."
                    ),
                )

            return ReconciliationResult(
                status=ReconciliationStatus.MATCHED,
                salary_net_amount=salary_amount,
                candidates=candidates[:5],
                selected_candidate=best,
                confidence=round(best.overall_score, 4),
                explanation=self._build_match_explanation(
                    salary_amount,
                    best,
                ),
            )

        if best.overall_score >= self.REVIEW_THRESHOLD:
            return ReconciliationResult(
                status=ReconciliationStatus.NEEDS_REVIEW,
                salary_net_amount=salary_amount,
                candidates=candidates[:5],
                selected_candidate=best,
                confidence=round(best.overall_score, 4),
                explanation=(
                    "A possible salary credit was found, but its "
                    "reconciliation score is not high enough for an "
                    "automatic match."
                ),
            )

        return ReconciliationResult(
            status=ReconciliationStatus.NO_MATCH,
            salary_net_amount=salary_amount,
            candidates=candidates[:5],
            selected_candidate=None,
            confidence=round(best.overall_score, 4),
            explanation=(
                "Bank credit candidates were found, but none provided "
                "sufficient evidence for a salary match."
            ),
        )

    def _build_candidate(
        self,
        salary: SalarySlip,
        transaction: BankTransaction,
        statement: BankStatement,
    ) -> ReconciliationCandidate:
        assert salary.net_salary is not None
        assert transaction.credit is not None

        amount_score, amount_reason = self._amount_score(
            salary.net_salary,
            transaction.credit,
        )

        date_score, date_reason = self._date_score(
            salary.employee.salary_month,
            transaction.date,
        )

        narration_score, narration_reason = self._narration_score(
            salary.employee.employer,
            transaction.narration,
        )

        periodicity_score, periodicity_reason = self._periodicity_score(
            transaction,
            statement,
        )

        overall_score = (
            amount_score * self.AMOUNT_WEIGHT
            + date_score * self.DATE_WEIGHT
            + narration_score * self.NARRATION_WEIGHT
            + periodicity_score * self.PERIODICITY_WEIGHT
        )

        reasons = [
            amount_reason,
            date_reason,
            narration_reason,
            periodicity_reason,
        ]

        return ReconciliationCandidate(
            transaction_date=transaction.date,
            amount=transaction.credit,
            narration=transaction.narration,
            amount_score=round(amount_score, 4),
            date_score=round(date_score, 4),
            narration_score=round(narration_score, 4),
            periodicity_score=round(periodicity_score, 4),
            overall_score=round(overall_score, 4),
            reasons=reasons,
        )

    def _amount_score(
        self,
        salary_amount: Decimal,
        credit_amount: Decimal,
    ) -> tuple[float, str]:
        difference = abs(salary_amount - credit_amount)

        if difference <= self.AMOUNT_EXACT_TOLERANCE:
            return 1.0, "Credit amount exactly matches the salary net amount."

        if salary_amount == 0:
            return 0.0, "Salary net amount is zero."

        percentage_difference = (
            difference / abs(salary_amount)
        )

        if percentage_difference <= self.AMOUNT_PERCENT_TOLERANCE:
            return (
                0.90,
                "Credit amount is within 2% of the salary net amount.",
            )

        if percentage_difference <= Decimal("0.05"):
            return (
                0.70,
                "Credit amount is within 5% of the salary net amount.",
            )

        if percentage_difference <= Decimal("0.10"):
            return (
                0.40,
                "Credit amount is within 10% of the salary net amount.",
            )

        return (
            0.0,
            "Credit amount differs materially from the salary net amount.",
        )

    def _date_score(
        self,
        salary_month: str | None,
        transaction_date: date,
    ) -> tuple[float, str]:
        month_range = self._salary_month_range(salary_month)

        if month_range is None:
            return (
                0.50,
                "Salary month could not be parsed; date evidence is neutral.",
            )

        month_start, month_end = month_range

        if month_start <= transaction_date <= month_end:
            return (
                1.0,
                "Credit transaction falls within the salary month.",
            )

        nearest_date = (
            month_start
            if transaction_date < month_start
            else month_end
        )

        distance = abs((transaction_date - nearest_date).days)

        if distance <= self.STRONG_DATE_TOLERANCE_DAYS:
            return (
                0.80,
                f"Credit transaction is {distance} day(s) outside the salary month.",
            )

        if distance <= self.DATE_TOLERANCE_DAYS:
            return (
                0.50,
                f"Credit transaction is {distance} day(s) outside the salary month.",
            )

        return (
            0.0,
            "Credit transaction is outside the allowed salary-date tolerance.",
        )

    def _narration_score(
        self,
        employer: str | None,
        narration: str,
    ) -> tuple[float, str]:
        normalized_narration = self._normalize_text(narration)

        keyword_matches = [
            keyword
            for keyword in self.SALARY_KEYWORDS
            if keyword in normalized_narration
        ]

        normalized_employer = self._normalize_text(employer)

        if normalized_employer:
            employer_tokens = [
                token
                for token in normalized_employer.split()
                if len(token) >= 3
            ]

            employer_matches = [
                token
                for token in employer_tokens
                if token in normalized_narration
            ]
        else:
            employer_matches = []

        if keyword_matches and employer_matches:
            return (
                1.0,
                "Narration contains salary-related and employer-related signals.",
            )

        if keyword_matches:
            return (
                0.80,
                "Narration contains salary-related keyword(s): "
                + ", ".join(keyword_matches)
                + ".",
            )

        if employer_matches:
            return (
                0.70,
                "Narration contains employer-related text.",
            )

        if normalized_narration:
            return (
                0.20,
                "Narration is present but does not contain strong salary signals.",
            )

        return (
            0.0,
            "Bank transaction narration is empty.",
        )

    def _periodicity_score(
        self,
        transaction: BankTransaction,
        statement: BankStatement,
    ) -> tuple[float, str]:
        """
        Reward a transaction when other similar salary-like credits occur
        at approximately monthly intervals.

        For a single-month statement this remains neutral rather than
        inventing periodicity evidence.
        """

        if not transaction.credit:
            return 0.0, "Transaction is not a positive credit."

        similar_salary_credits = []

        for candidate in statement.transactions:
            if candidate.credit is None:
                continue

            if candidate.date == transaction.date:
                continue

            if not self._amounts_are_similar(
                transaction.credit,
                candidate.credit,
            ):
                continue

            if self._contains_salary_keyword(candidate.narration):
                similar_salary_credits.append(candidate)

        if not similar_salary_credits:
            return (
                0.50,
                "No recurring salary-credit evidence is available in the statement.",
            )

        for candidate in similar_salary_credits:
            days = abs((transaction.date - candidate.date).days)

            if 25 <= days <= 35:
                return (
                    1.0,
                    "Similar salary-like credits occur at approximately monthly intervals.",
                )

        return (
            0.60,
            "Similar salary-like credit evidence exists, but periodicity is not clearly monthly.",
        )

    def _filter_candidate_transactions(
        self,
        transactions: list[BankTransaction],
        month_start: date | None,
        month_end: date | None,
    ) -> list[BankTransaction]:
        if month_start is None or month_end is None:
            return transactions

        extended_start = month_start - timedelta(
            days=self.DATE_TOLERANCE_DAYS
        )
        extended_end = month_end + timedelta(
            days=self.DATE_TOLERANCE_DAYS
        )

        return [
            transaction
            for transaction in transactions
            if extended_start <= transaction.date <= extended_end
        ]

    @staticmethod
    def _salary_month_range(
        salary_month: str | None,
    ) -> tuple[date, date] | None:
        if not salary_month:
            return None

        normalized = salary_month.strip()

        formats = (
            "%B %Y",
            "%b %Y",
            "%Y-%m",
            "%m/%Y",
            "%m-%Y",
        )

        parsed: datetime | None = None

        for fmt in formats:
            try:
                parsed = datetime.strptime(normalized, fmt)
                break
            except ValueError:
                continue

        if parsed is None:
            return None

        year = parsed.year
        month = parsed.month
        last_day = monthrange(year, month)[1]

        return (
            date(year, month, 1),
            date(year, month, last_day),
        )

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        if not value:
            return ""

        value = value.lower()
        value = re.sub(r"[^a-z0-9]+", " ", value)

        return " ".join(value.split())

    @classmethod
    def _contains_salary_keyword(cls, narration: str) -> bool:
        normalized = cls._normalize_text(narration)

        return any(
            keyword in normalized
            for keyword in cls.SALARY_KEYWORDS
        )

    @staticmethod
    def _amounts_are_similar(
        first: Decimal,
        second: Decimal,
    ) -> bool:
        difference = abs(first - second)

        if difference <= Decimal("1.00"):
            return True

        if first == 0:
            return False

        return (
            difference / abs(first)
            <= Decimal("0.02")
        )

    @staticmethod
    def _build_match_explanation(
        salary_amount: Decimal,
        candidate: ReconciliationCandidate,
    ) -> str:
        return (
            f"Bank credit of ₹{candidate.amount} matches the salary net "
            f"amount of ₹{salary_amount}. "
            f"Overall reconciliation score is "
            f"{candidate.overall_score:.2f}."
        )
