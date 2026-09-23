from app.schemas.bank_statement import (
    BankStatement,
    BankTransaction,
)
from app.schemas.bank_validation import (
    BankValidationIssue,
    BankValidationResult,
    BankValidationSeverity,
)


class BankTransactionValidator:
    """Validates bank statement transactions."""

    def validate_transaction(
        self,
        transaction: BankTransaction,
        index: int,
    ) -> list[BankValidationIssue]:
        issues: list[BankValidationIssue] = []

        # Narration should normally be present.
        if not transaction.narration.strip():
            issues.append(
                BankValidationIssue(
                    code="EMPTY_NARRATION",
                    message="Transaction narration is empty.",
                    severity=BankValidationSeverity.WARNING,
                    transaction_index=index,
                )
            )

        # A transaction should not contain both debit and credit.
        if (
            transaction.debit is not None
            and transaction.credit is not None
        ):
            issues.append(
                BankValidationIssue(
                    code="BOTH_DEBIT_AND_CREDIT",
                    message=(
                        "Transaction contains both debit and credit "
                        "amounts."
                    ),
                    severity=BankValidationSeverity.ERROR,
                    transaction_index=index,
                )
            )

        # A transaction should contain at least one amount.
        if (
            transaction.debit is None
            and transaction.credit is None
        ):
            issues.append(
                BankValidationIssue(
                    code="MISSING_TRANSACTION_AMOUNT",
                    message=(
                        "Transaction contains neither debit "
                        "nor credit amount."
                    ),
                    severity=BankValidationSeverity.ERROR,
                    transaction_index=index,
                )
            )

        return issues

    @staticmethod
    def _transaction_signature(
        transaction: BankTransaction,
    ) -> tuple:
        """
        Build a deterministic signature used to identify
        exact duplicate transactions.
        """
        return (
            transaction.date,
            transaction.narration.strip().lower(),
            transaction.debit,
            transaction.credit,
            transaction.balance,
        )

    def validate(
        self,
        statement: BankStatement,
    ) -> BankValidationResult:
        issues: list[BankValidationIssue] = []
        seen: dict[tuple, int] = {}

        for index, transaction in enumerate(statement.transactions):
            # Validate the individual transaction.
            issues.extend(
                self.validate_transaction(
                    transaction,
                    index,
                )
            )

            # Build a signature for duplicate detection.
            signature = self._transaction_signature(transaction)

            if signature in seen:
                issues.append(
                    BankValidationIssue(
                        code="DUPLICATE_TRANSACTION",
                        message=(
                            "Transaction appears to be duplicated "
                            f"from transaction {seen[signature] + 1}."
                        ),
                        severity=BankValidationSeverity.WARNING,
                        transaction_index=index,
                    )
                )
            else:
                seen[signature] = index

        # Only ERROR-level issues make the statement invalid.
        has_errors = any(
            issue.severity == BankValidationSeverity.ERROR
            for issue in issues
        )

        return BankValidationResult(
            is_valid=not has_errors,
            issues=issues,
        )