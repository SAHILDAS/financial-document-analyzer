from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from app.schemas.analyze import (
    AnalyzeData,
    AnalyzeFileInfo,
    AnalyzeProcessingInfo,
    AnalyzeResponse,
)
from app.schemas.document import DocumentType
from app.services.analysis.document_analysis import DocumentAnalysisService
from app.services.classification.document_classifier import DocumentClassifier
from app.services.extraction.providers.factory import (
    create_bank_extractor,
    create_salary_extractor,
)
from app.services.ingestion.document_ingestion import DocumentIngestionService

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

ingestion_service = DocumentIngestionService()
classifier = DocumentClassifier()

salary_extractor = create_salary_extractor()
bank_extractor = create_bank_extractor()

document_analysis_service = DocumentAnalysisService(
    salary_extractor=salary_extractor,
    bank_extractor=bank_extractor,
)


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
async def analyze_document(
    file: UploadFile = File(...),
) -> AnalyzeResponse | JSONResponse:
    """
    Analyze an uploaded financial document.

    Processing pipeline:

        Upload
          ↓
        Ingestion
          ↓
        Text extraction / OCR
          ↓
        Document classification
          ↓
        Document-specific analysis
          ↓
        Structured response
    """

    # ---------------------------------------------------------
    # 1. Read uploaded file
    # ---------------------------------------------------------
    content = await file.read()

    # ---------------------------------------------------------
    # 2. Ingest document
    # ---------------------------------------------------------
    ingestion_result = ingestion_service.ingest(
        filename=file.filename,
        content_type=file.content_type,
        content=content,
    )

    # ---------------------------------------------------------
    # 3. Handle ingestion failure
    # ---------------------------------------------------------
    if not ingestion_result.success:
        response = AnalyzeResponse(
            success=False,
            document_id=ingestion_result.document_id,
            data=AnalyzeData(
                file=AnalyzeFileInfo(
                    filename=ingestion_result.file.filename,
                    extension=ingestion_result.file.extension,
                    size_bytes=ingestion_result.file.size_bytes,
                ),
            ),
            errors=ingestion_result.errors,
        )

        return JSONResponse(
            status_code=400,
            content=response.model_dump(mode="json"),
        )

    # ---------------------------------------------------------
    # 4. Ensure extracted text exists
    # ---------------------------------------------------------
    extracted_text = ingestion_result.extracted_text

    if extracted_text is None:
        response = AnalyzeResponse(
            success=False,
            document_id=ingestion_result.document_id,
            data=AnalyzeData(
                file=AnalyzeFileInfo(
                    filename=ingestion_result.file.filename,
                    extension=ingestion_result.file.extension,
                    size_bytes=ingestion_result.file.size_bytes,
                ),
            ),
        )

        return JSONResponse(
            status_code=422,
            content=response.model_dump(mode="json"),
        )

    # ---------------------------------------------------------
    # 5. Classify document
    # ---------------------------------------------------------
    classification = classifier.classify(
        extracted_text.text,
    )

    # ---------------------------------------------------------
    # 6. Common processing metadata
    # ---------------------------------------------------------
    processing = AnalyzeProcessingInfo(
        source=extracted_text.source,
        methods=extracted_text.methods,
        page_count=extracted_text.page_count,
        text_quality_score=extracted_text.quality.quality_score,
    )

    file_info = AnalyzeFileInfo(
        filename=ingestion_result.file.filename,
        extension=ingestion_result.file.extension,
        size_bytes=ingestion_result.file.size_bytes,
    )

    # ---------------------------------------------------------
    # 7. Handle unknown document
    # ---------------------------------------------------------
    if classification.document_type == DocumentType.UNKNOWN:
        return AnalyzeResponse(
            success=True,
            document_id=ingestion_result.document_id,
            document_type=classification.document_type,
            confidence=classification.confidence,
            data=AnalyzeData(
                classification_reason=classification.reason,
                file=file_info,
            ),
            processing=processing,
        )

    # ---------------------------------------------------------
    # 8. Handle bank statement
    # ---------------------------------------------------------
    if classification.document_type == DocumentType.BANK_STATEMENT:
        try:
            bank_analysis = document_analysis_service.analyze_bank(
                extracted_text.text,
            )

        except Exception:
            response = AnalyzeResponse(
                success=False,
                document_id=ingestion_result.document_id,
                document_type=classification.document_type,
                confidence=classification.confidence,
                data=AnalyzeData(
                    classification_reason=classification.reason,
                    file=file_info,
                ),
                processing=processing,
            )

            return JSONResponse(
                status_code=422,
                content=response.model_dump(mode="json"),
            )

        return AnalyzeResponse(
            success=True,
            document_id=ingestion_result.document_id,
            document_type=classification.document_type,
            confidence=classification.confidence,
            data=AnalyzeData(
                classification_reason=classification.reason,
                file=file_info,
                bank=bank_analysis,
            ),
            validation=bank_analysis.validation.model_dump(
                mode="json",
            ),
            processing=processing,
        )
    
    # ---------------------------------------------------------
    # 9. Handle salary slip
    # ---------------------------------------------------------
    if classification.document_type == DocumentType.SALARY_SLIP:
        try:
            salary_analysis = (
                document_analysis_service.analyze_salary(
                    extracted_text.text,
                    text_quality_score=(
                        extracted_text.quality.quality_score
                    ),
                )
            )

        except Exception:
            response = AnalyzeResponse(
                success=False,
                document_id=ingestion_result.document_id,
                document_type=classification.document_type,
                confidence=classification.confidence,
                data=AnalyzeData(
                    classification_reason=classification.reason,
                    file=file_info,
                ),
                processing=processing,
            )

            return JSONResponse(
                status_code=422,
                content=response.model_dump(mode="json"),
            )

        return AnalyzeResponse(
            success=True,
            document_id=ingestion_result.document_id,
            document_type=classification.document_type,
            confidence=salary_analysis.confidence.score,
            data=AnalyzeData(
                classification_reason=classification.reason,
                file=file_info,
                salary=salary_analysis,
            ),
            validation=salary_analysis.validation.model_dump(
                mode="json",
            ),
            processing=processing,
        )

    # ---------------------------------------------------------
    # 10. Defensive fallback
    # ---------------------------------------------------------
    response = AnalyzeResponse(
        success=False,
        document_id=ingestion_result.document_id,
        document_type=classification.document_type,
        confidence=classification.confidence,
        data=AnalyzeData(
            classification_reason=classification.reason,
            file=file_info,
        ),
        processing=processing,
    )

    return JSONResponse(
        status_code=422,
        content=response.model_dump(mode="json"),
    )