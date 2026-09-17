from decimal import Decimal

from pydantic import BaseModel, Field


class SalaryEmployee(BaseModel):
    name: str | None = None
    employee_id: str | None = None
    employer: str | None = None
    salary_month: str | None = None
    pan: str | None = None


class SalaryEarnings(BaseModel):
    basic: Decimal | None = Field(default=None, ge=0)
    hra: Decimal | None = Field(default=None, ge=0)
    allowances: Decimal | None = Field(default=None, ge=0)
    bonus: Decimal | None = Field(default=None, ge=0)
    other: Decimal | None = Field(default=None, ge=0)
    gross: Decimal | None = Field(default=None, ge=0)


class SalaryDeductions(BaseModel):
    pf: Decimal | None = Field(default=None, ge=0)
    professional_tax: Decimal | None = Field(default=None, ge=0)
    tds: Decimal | None = Field(default=None, ge=0)
    other: Decimal | None = Field(default=None, ge=0)
    total: Decimal | None = Field(default=None, ge=0)


class SalaryBankAccount(BaseModel):
    account_number: str | None = None


class SalaryFieldConfidence(BaseModel):
    employee_name: float | None = Field(default=None, ge=0, le=1)
    employee_id: float | None = Field(default=None, ge=0, le=1)
    employer: float | None = Field(default=None, ge=0, le=1)
    salary_month: float | None = Field(default=None, ge=0, le=1)
    gross: float | None = Field(default=None, ge=0, le=1)
    total_deductions: float | None = Field(default=None, ge=0, le=1)
    net_salary: float | None = Field(default=None, ge=0, le=1)


class SalarySlip(BaseModel):
    employee: SalaryEmployee
    earnings: SalaryEarnings
    deductions: SalaryDeductions

    net_salary: Decimal | None = Field(default=None, ge=0)

    bank_account: SalaryBankAccount | None = None

    field_confidence: SalaryFieldConfidence | None = None