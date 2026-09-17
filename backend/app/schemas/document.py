from enum import StrEnum


class DocumentType(StrEnum):
    SALARY_SLIP = "salary_slip"
    BANK_STATEMENT = "bank_statement"
    UNKNOWN = "unknown"