from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Financial Document Analyzer"
    app_env: str = "development"
    app_debug: bool = True

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    frontend_url: str = "http://localhost:4200"

    llm_provider: str | None = None
    llm_api_key: str | None = None
    llm_model: str = "gpt-5.6-luna"

    ocr_provider: str = "tesseract"

    max_file_size_mb: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()