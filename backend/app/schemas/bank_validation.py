from enum import StrEnum

from pydantic import BaseModel, Field


class BankValidationSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class BankValidationIssue(BaseModel):
    code: str
    message: str
    severity: BankValidationSeverity
    transaction_index: int | None = None


class BankValidationResult(BaseModel):
    is_valid: bool
    issues: list[BankValidationIssue] = Field(default_factory=list)