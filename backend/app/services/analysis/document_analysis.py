from app.schemas.salary_analysis import SalaryAnalysisResult
from app.services.analysis.salary_analysis import SalaryAnalysisService
from app.services.extraction.llm_salary_extractor import LlmSalaryExtractor


class DocumentAnalysisService:
    """Coordinate document-specific financial analysis."""

    def __init__(
        self,
        salary_extractor: LlmSalaryExtractor,
        salary_analysis: SalaryAnalysisService | None = None,
    ):
        self.salary_extractor = salary_extractor
        self.salary_analysis = (
            salary_analysis or SalaryAnalysisService()
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