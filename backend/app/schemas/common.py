from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Any | None = None