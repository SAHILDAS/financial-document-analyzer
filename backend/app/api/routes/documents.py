from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from app.schemas.analyze import (
    AnalyzeData,
    AnalyzeFileInfo,
    AnalyzeProcessingInfo,
    AnalyzeResponse,
)
from app.services.classification.document_classifier import DocumentClassifier
from app.services.ingestion.document_ingestion import DocumentIngestionService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


ingestion_service = DocumentIngestionService()
classifier = DocumentClassifier()


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
async def analyze_document(
    file: UploadFile = File(...),
) -> AnalyzeResponse | JSONResponse:
    content = await file.read()

    ingestion_result = ingestion_service.ingest(
        filename=file.filename,
        content_type=file.content_type,
        content=content,
    )

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

    classification = classifier.classify(
        extracted_text.text,
    )

    return AnalyzeResponse(
        success=True,
        document_id=ingestion_result.document_id,
        document_type=classification.document_type,
        confidence=classification.confidence,
        data=AnalyzeData(
            classification_reason=classification.reason,
            file=AnalyzeFileInfo(
                filename=ingestion_result.file.filename,
                extension=ingestion_result.file.extension,
                size_bytes=ingestion_result.file.size_bytes,
            ),
        ),
        processing=AnalyzeProcessingInfo(
            source=extracted_text.source,
            methods=extracted_text.methods,
            page_count=extracted_text.page_count,
            text_quality_score=extracted_text.quality.quality_score,
        ),
    )