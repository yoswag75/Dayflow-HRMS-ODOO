import os

class Settings:
    SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "user")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "password")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@dayflow.hr")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "test")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

settings = Settings()
