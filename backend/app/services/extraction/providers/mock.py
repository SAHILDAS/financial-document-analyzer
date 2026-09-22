from decimal import Decimal

from app.schemas.salary_slip import (
    SalaryBankAccount,
    SalaryDeductions,
    SalaryEarnings,
    SalaryEmployee,
    SalarySlip,
)
from app.services.extraction.salary_extractor import SalaryExtractionService


class MockSalaryExtractor(SalaryExtractionService):
    """
    Deterministic salary extractor used for development and tests.

    This deliberately does not perform real NLP/LLM extraction.
    It allows the downstream validation and analysis pipeline
    to be tested independently of an external provider.
    """

    def extract(self, text: str) -> SalarySlip:
        normalized_text = text.lower()

        if "salary slip" not in normalized_text and "payslip" not in normalized_text:
            raise ValueError(
                "Mock salary extractor received text that does not "
                "appear to be a salary slip."
            )

        return SalarySlip(
            employee=SalaryEmployee(
                name="Test Employee",
                employee_id="EMP-001",
                employer="Example Technologies",
                salary_month="August 2026",
            ),
            earnings=SalaryEarnings(
                basic=Decimal("40000"),
                hra=Decimal("15000"),
                allowances=Decimal("10000"),
                gross=Decimal("65000"),
            ),
            deductions=SalaryDeductions(
                pf=Decimal("4800"),
                professional_tax=None,
                tds=Decimal("1200"),
                other=None,
                total=Decimal("6000"),
            ),
            net_salary=Decimal("59000"),
            bank_account=SalaryBankAccount(
                account_number="XXXXXX1234",
            ),
        )