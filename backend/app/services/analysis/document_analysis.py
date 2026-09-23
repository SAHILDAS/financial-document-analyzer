from app.schemas.bank_analysis_response import BankAnalysisResult
from app.schemas.bank_statement import BankStatement
from app.schemas.bank_validation import BankValidationResult
from app.schemas.salary_analysis import SalaryAnalysisResult
from app.services.analysis.bank_analysis import BankFinancialAnalyzer
from app.services.analysis.salary_analysis import SalaryAnalysisService
from app.services.extraction.bank_extractor import BankExtractionService
from app.services.extraction.llm_salary_extractor import LlmSalaryExtractor
from app.services.validation.bank_transaction_validator import (
    BankTransactionValidator,
)


class DocumentAnalysisService:
    """Coordinate document-specific financial analysis."""

    def __init__(
        self,
        salary_extractor: LlmSalaryExtractor,
        salary_analysis: SalaryAnalysisService | None = None,
        bank_extractor: BankExtractionService | None = None,
        bank_analyzer: BankFinancialAnalyzer | None = None,
        bank_validator: BankTransactionValidator | None = None,
    ):
        self.salary_extractor = salary_extractor
        self.salary_analysis = (
            salary_analysis or SalaryAnalysisService()
        )

        self.bank_extractor = bank_extractor
        self.bank_analyzer = (
            bank_analyzer or BankFinancialAnalyzer()
        )
        self.bank_validator = (
            bank_validator or BankTransactionValidator()
        )

    def analyze_salary(
        self,
        text: str,
        *,
        text_quality_score: float = 1.0,
    ) -> SalaryAnalysisResult:
        salary = self.salary_extractor.extract(text)

        return self.salary_analysis.analyze(
            salary,
            text_quality_score=text_quality_score,
        )

    def analyze_bank(
        self,
        text: str,
    ) -> BankAnalysisResult:
        if self.bank_extractor is None:
            raise RuntimeError(
                "Bank extraction service is not configured."
            )

        statement = self.bank_extractor.extract(text)

        validation: BankValidationResult = (
            self.bank_validator.validate(statement)
        )

        analysis = self.bank_analyzer.analyze(statement)

        return BankAnalysisResult(
            statement=statement,
            analysis=analysis,
            validation=validation,
        )