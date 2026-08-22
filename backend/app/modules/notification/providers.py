from abc import ABC, abstractmethod
from app.core.config import settings

class EmailProvider(ABC):
    @abstractmethod
    async def send(self, to: str, subject: str, body: str) -> None: ...

class SMTPProvider(EmailProvider):
    async def send(self, to: str, subject: str, body: str) -> None:
        # aiosmtplib implementation here
        pass

class SendGridProvider(EmailProvider):
    async def send(self, to: str, subject: str, body: str) -> None:
        # POST to SendGrid API here
        pass

class NullProvider(EmailProvider):
    """Used in tests and local dev. Silently discards all emails."""
    async def send(self, to: str, subject: str, body: str) -> None:
        pass

def get_email_provider() -> EmailProvider:
    provider = getattr(settings, "EMAIL_PROVIDER", "null")  # "smtp" | "sendgrid" | "null"
    if provider == "sendgrid":
        return SendGridProvider()
    elif provider == "smtp":
        return SMTPProvider()
    return NullProvider()
