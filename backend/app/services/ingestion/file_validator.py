from dataclasses import dataclass
from pathlib import Path
import re

from app.core.config import settings
from app.schemas.ingestion import (
    FileMetadata,
    ProcessingError,
    ProcessingErrorCode,
)


@dataclass(frozen=True)
class FileValidationResult:
    valid: bool
    metadata: FileMetadata | None = None
    error: ProcessingError | None = None


class FileValidator:
    """Validate uploaded financial-document files before processing."""

    ALLOWED_EXTENSIONS = {
        ".pdf": "application/pdf",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }

    FILE_SIGNATURES = {
        ".pdf": (b"%PDF-",),
        ".jpg": (b"\xff\xd8\xff",),
        ".jpeg": (b"\xff\xd8\xff",),
        ".png": (b"\x89PNG\r\n\x1a\n",),
    }

    SAFE_FILENAME_PATTERN = re.compile(r"^[a-zA-Z0-9._ -]+$")

    def validate(
        self,
        filename: str | None,
        content_type: str | None,
        content: bytes,
    ) -> FileValidationResult:
        """Validate a file and return normalized metadata or a structured error."""

        if not filename or not filename.strip():
            return self._error(
                ProcessingErrorCode.INVALID_FILE,
                "A valid filename is required.",
            )

        filename = Path(filename).name

        if not self.SAFE_FILENAME_PATTERN.fullmatch(filename):
            return self._error(
                ProcessingErrorCode.INVALID_FILE,
                "The filename contains unsupported characters.",
            )

        extension = Path(filename).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            return self._error(
                ProcessingErrorCode.UNSUPPORTED_FILE_TYPE,
                f"Unsupported file type: {extension or 'unknown'}. "
                "Supported formats are PDF, JPG, JPEG, and PNG.",
            )

        if not content:
            return self._error(
                ProcessingErrorCode.EMPTY_FILE,
                "The uploaded file is empty.",
            )

        max_size_bytes = settings.max_file_size_mb * 1024 * 1024

        if len(content) > max_size_bytes:
            return self._error(
                ProcessingErrorCode.FILE_TOO_LARGE,
                f"The uploaded file exceeds the maximum allowed size "
                f"of {settings.max_file_size_mb} MB.",
            )

        expected_mime = self.ALLOWED_EXTENSIONS[extension]

        if content_type:
            normalized_content_type = content_type.split(";")[0].strip().lower()

            if normalized_content_type != expected_mime:
                return self._error(
                    ProcessingErrorCode.INVALID_FILE,
                    "The declared content type does not match the file extension.",
                )

        if not self._matches_signature(extension, content):
            return self._error(
                ProcessingErrorCode.INVALID_FILE,
                "The file content does not match its declared file type.",
            )

        metadata = FileMetadata(
            filename=filename,
            content_type=content_type or expected_mime,
            extension=extension,
            size_bytes=len(content),
        )

        return FileValidationResult(
            valid=True,
            metadata=metadata,
        )

    def _matches_signature(
        self,
        extension: str,
        content: bytes,
    ) -> bool:
        signatures = self.FILE_SIGNATURES[extension]

        return any(
            content.startswith(signature)
            for signature in signatures
        )

    @staticmethod
    def _error(
        code: ProcessingErrorCode,
        message: str,
        retryable: bool = False,
    ) -> FileValidationResult:
        return FileValidationResult(
            valid=False,
            error=ProcessingError(
                code=code,
                message=message,
                retryable=retryable,
            ),
        )