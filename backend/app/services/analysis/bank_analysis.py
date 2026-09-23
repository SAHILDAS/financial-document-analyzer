from collections import defaultdict
from decimal import Decimal

from app.schemas.bank_analysis import (
    BankFinancialAnalysis,
    EmiCandidate,
    LargeTransaction,
    RecurringTransaction,
    SalaryCreditCandidate,
)
from app.schemas.bank_statement import BankStatement, BankTransaction


class BankFinancialAnalyzer:
    """Performs deterministic financial analysis on bank statements."""

    LARGE_TRANSACTION_THRESHOLD = Decimal("50000")

    SALARY_KEYWORDS = (
        "salary",
        "payroll",
        "wages",
        "employer",
        "stipend",
        "salary credit",
        "pay credit",
    )

    EMI_KEYWORDS = (
        "emi",
        "loan",
        "home loan",
        "personal loan",
        "mortgage",
        "nach",
        "ecs",
        "loan repayment",
        "loan installment",
        "loan instalment",
    )

    RECURRING_MIN_OCCURRENCES = 2

    def analyze(
        self,
        statement: BankStatement,
    ) -> BankFinancialAnalysis:
        total_credits = self._calculate_total_credits(statement)
        total_debits = self._calculate_total_debits(statement)
        average_monthly_credit = self._calculate_average_monthly_credit(
            statement
        )
        large_transactions = self._find_large_transactions(statement)
        salary_credit_candidates = self._find_salary_credit_candidates(
            statement
        )
        recurring_transactions = self._find_recurring_transactions(
            statement
        )
        emi_candidates = self._find_emi_candidates(statement)

        return BankFinancialAnalysis(
            total_credits=total_credits,
            total_debits=total_debits,
            average_monthly_credit=average_monthly_credit,
            large_transactions=large_transactions,
            salary_credit_candidates=salary_credit_candidates,
            recurring_transactions=recurring_transactions,
            emi_candidates=emi_candidates,
        )

    @staticmethod
    def _calculate_total_credits(
        statement: BankStatement,
    ) -> Decimal:
        return sum(
            (
                transaction.credit
                for transaction in statement.transactions
                if transaction.credit is not None
            ),
            Decimal("0"),
        )

    @staticmethod
    def _calculate_total_debits(
        statement: BankStatement,
    ) -> Decimal:
        return sum(
            (
                transaction.debit
                for transaction in statement.transactions
                if transaction.debit is not None
            ),
            Decimal("0"),
        )

    @staticmethod
    def _calculate_average_monthly_credit(
        statement: BankStatement,
    ) -> Decimal | None:
        """
        Calculate average monthly credits based on calendar months
        represented by the statement transactions.

        Months with no credit transactions are not included.
        """

        monthly_credits: dict[tuple[int, int], Decimal] = defaultdict(
            lambda: Decimal("0")
        )

        for transaction in statement.transactions:
            if transaction.credit is None:
                continue

            month_key = (
                transaction.date.year,
                transaction.date.month,
            )

            monthly_credits[month_key] += transaction.credit

        if not monthly_credits:
            return None

        total = sum(
            monthly_credits.values(),
            Decimal("0"),
        )

        average = total / Decimal(len(monthly_credits))

        return average.quantize(Decimal("0.01"))

    def _find_large_transactions(
        self,
        statement: BankStatement,
    ) -> list[LargeTransaction]:
        large_transactions: list[LargeTransaction] = []

        for transaction in statement.transactions:
            if transaction.credit is not None:
                if transaction.credit > self.LARGE_TRANSACTION_THRESHOLD:
                    large_transactions.append(
                        LargeTransaction(
                            transaction=transaction,
                            amount=transaction.credit,
                            direction="credit",
                            reason=(
                                "Credit transaction exceeds the "
                                "₹50,000 large-transaction threshold."
                            ),
                        )
                    )

            if transaction.debit is not None:
                if transaction.debit > self.LARGE_TRANSACTION_THRESHOLD:
                    large_transactions.append(
                        LargeTransaction(
                            transaction=transaction,
                            amount=transaction.debit,
                            direction="debit",
                            reason=(
                                "Debit transaction exceeds the "
                                "₹50,000 large-transaction threshold."
                            ),
                        )
                    )

        return large_transactions

    def _find_salary_credit_candidates(
        self,
        statement: BankStatement,
    ) -> list[SalaryCreditCandidate]:
        candidates: list[SalaryCreditCandidate] = []

        for transaction in statement.transactions:
            if transaction.credit is None:
                continue

            narration = transaction.narration.lower()

            matched_keywords = [
                keyword
                for keyword in self.SALARY_KEYWORDS
                if keyword in narration
            ]

            if not matched_keywords:
                continue

            reasons = [
                "Transaction is a credit.",
                (
                    "Narration contains salary-related keyword(s): "
                    + ", ".join(matched_keywords)
                    + "."
                ),
            ]

            score = Decimal("0.50")

            score += Decimal("0.30")

            if "credit" in narration:
                reasons.append(
                    "Narration explicitly indicates a credit."
                )
                score += Decimal("0.20")

            score = min(score, Decimal("1.00"))

            candidates.append(
                SalaryCreditCandidate(
                    transaction=transaction,
                    score=float(score),
                    reasons=reasons,
                )
            )

        candidates.sort(
            key=lambda candidate: candidate.score,
            reverse=True,
        )

        return candidates

    @staticmethod
    def _normalize_recurring_narration(
        narration: str,
    ) -> str:
        """Normalize narration for recurring-transaction grouping."""
        return " ".join(narration.lower().split()).strip()

    @staticmethod
    def _calculate_average_amount(
        transactions: list[BankTransaction],
    ) -> Decimal | None:
        amounts = [
            transaction.credit
            if transaction.credit is not None
            else transaction.debit
            for transaction in transactions
        ]

        amounts = [
            amount
            for amount in amounts
            if amount is not None
        ]

        if not amounts:
            return None

        total = sum(amounts, Decimal("0"))

        return (total / Decimal(len(amounts))).quantize(
            Decimal("0.01")
        )

    @staticmethod
    def _calculate_average_interval_days(
        transactions: list[BankTransaction],
    ) -> float | None:
        if len(transactions) < 2:
            return None

        sorted_transactions = sorted(
            transactions,
            key=lambda transaction: transaction.date,
        )

        intervals = []

        for previous, current in zip(
            sorted_transactions,
            sorted_transactions[1:],
        ):
            interval = (
                current.date - previous.date
            ).days

            if interval > 0:
                intervals.append(interval)

        if not intervals:
            return None

        return round(
            sum(intervals) / len(intervals),
            2,
        )

    @staticmethod
    def _amounts_are_similar(
        transactions: list[BankTransaction],
    ) -> bool:
        amounts = [
            transaction.credit
            if transaction.credit is not None
            else transaction.debit
            for transaction in transactions
        ]

        amounts = [
            amount
            for amount in amounts
            if amount is not None
        ]

        if len(amounts) < 2:
            return False

        average = sum(amounts, Decimal("0")) / Decimal(len(amounts))

        if average == 0:
            return all(amount == 0 for amount in amounts)

        tolerance = average * Decimal("0.10")

        return all(
            abs(amount - average) <= tolerance
            for amount in amounts
        )

    def _find_recurring_transactions(
        self,
        statement: BankStatement,
    ) -> list[RecurringTransaction]:
        grouped: dict[
            str,
            list[BankTransaction],
        ] = defaultdict(list)

        for transaction in statement.transactions:
            narration = self._normalize_recurring_narration(
                transaction.narration
            )

            if not narration:
                continue

            grouped[narration].append(transaction)

        recurring_transactions: list[RecurringTransaction] = []

        for narration, transactions in grouped.items():
            if len(transactions) < self.RECURRING_MIN_OCCURRENCES:
                continue

            average_amount = self._calculate_average_amount(
                transactions
            )

            average_interval_days = (
                self._calculate_average_interval_days(
                    transactions
                )
            )

            reasons: list[str] = [
                (
                    f"Transaction narration occurs "
                    f"{len(transactions)} times."
                )
            ]

            if self._amounts_are_similar(transactions):
                reasons.append(
                    "Transaction amounts are similar."
                )

            if average_interval_days is not None:
                if 25 <= average_interval_days <= 35:
                    reasons.append(
                        "Transactions occur at approximately "
                        "monthly intervals."
                    )
                elif 6 <= average_interval_days <= 8:
                    reasons.append(
                        "Transactions occur at approximately "
                        "weekly intervals."
                    )
                elif 12 <= average_interval_days <= 16:
                    reasons.append(
                        "Transactions occur at approximately "
                        "bi-weekly intervals."
                    )

            recurring_transactions.append(
                RecurringTransaction(
                    narration=narration,
                    occurrence_count=len(transactions),
                    amounts=[
                        (
                            transaction.credit
                            if transaction.credit is not None
                            else transaction.debit
                        )
                        for transaction in transactions
                        if (
                            transaction.credit is not None
                            or transaction.debit is not None
                        )
                    ],
                    average_amount=average_amount,
                    approximate_interval_days=average_interval_days,
                    reasons=reasons,
                )
            )

        recurring_transactions.sort(
            key=lambda item: item.occurrence_count,
            reverse=True,
        )

        return recurring_transactions

    def _find_emi_candidates(
        self,
        statement: BankStatement,
    ) -> list[EmiCandidate]:
        candidates: list[EmiCandidate] = []

        for transaction in statement.transactions:
            # EMI / loan payments should be debits.
            if transaction.debit is None:
                continue

            narration = transaction.narration.lower()

            matched_keywords = [
                keyword
                for keyword in self.EMI_KEYWORDS
                if keyword in narration
            ]

            if not matched_keywords:
                continue

            reasons = [
                "Transaction is a debit.",
                (
                    "Narration contains loan/EMI-related keyword(s): "
                    + ", ".join(matched_keywords)
                    + "."
                ),
            ]

            score = Decimal("0.50")

            # Strong evidence from explicit loan/EMI terminology.
            score += Decimal("0.30")

            if "emi" in narration:
                reasons.append(
                    "Narration explicitly mentions EMI."
                )
                score += Decimal("0.10")

            if (
                "nach" in narration
                or "ecs" in narration
            ):
                reasons.append(
                    "Narration contains an automated-payment "
                    "indicator (NACH/ECS)."
                )
                score += Decimal("0.10")

            score = min(score, Decimal("1.00"))

            candidates.append(
                EmiCandidate(
                    transaction=transaction,
                    score=float(score),
                    reasons=reasons,
                )
            )

        candidates.sort(
            key=lambda candidate: candidate.score,
            reverse=True,
        )

        return candidates