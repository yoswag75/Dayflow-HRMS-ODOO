from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Dayflow HRMS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./hrms.db"
    SECRET_KEY: str = "dayflow-hrms-development-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_TIMEOUT: int = 30
    EMAIL_PROVIDER: str = "null"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="allow"
    )


settings = Settings()
