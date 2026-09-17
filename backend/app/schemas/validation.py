from enum import StrEnum

from pydantic import BaseModel, Field


class ValidationSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ValidationIssue(BaseModel):
    code: str
    message: str
    severity: ValidationSeverity
    field: str | None = None


class ValidationResult(BaseModel):
    is_valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)