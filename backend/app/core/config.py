import os

class Settings:
    SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "user")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "password")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@dayflow.hr")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "test")

settings = Settings()
