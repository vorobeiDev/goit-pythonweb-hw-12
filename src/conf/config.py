import os

from dotenv import load_dotenv
from pydantic import EmailStr
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    """
    Configuration settings for the application.

    This class loads environment variables and provides configurations
    such as database connection settings, JWT settings, cloud storage,
    and email server settings.
    """

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://admin:admin@localhost:5432/hw8"
    )
    """The database connection URL."""

    JWT_SECRET: str = os.getenv("JWT_SECRET", "YOUR_SECRET_KEY")
    """The secret key used for JWT authentication."""

    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    """The algorithm used for signing JWT tokens."""

    JWT_EXPIRATION_SECONDS: str = os.getenv("JWT_EXPIRATION_SECONDS", 3600)
    """The expiration time for JWT tokens in seconds."""

    CLD_NAME: str = os.getenv("CLD_NAME", "asdasdasd")
    """Cloud storage provider name."""

    CLD_API_KEY: int = os.getenv("CLD_API_KEY", 156282568713174)
    """Cloud storage API key."""

    CLD_API_SECRET: str = os.getenv("CLD_API_SECRET", "GREGFDGSDSFWEF")
    """Cloud storage API secret key."""

    MAIL_USERNAME: EmailStr = "example@meta.ua"
    """The username for the email server authentication."""

    MAIL_PASSWORD: str = "secretPassword"
    """The password for the email server authentication."""

    MAIL_FROM: EmailStr = "example@meta.ua"
    """The default sender email address."""

    MAIL_PORT: int = 465
    """The port number for the email server."""

    MAIL_SERVER: str = "smtp.meta.ua"
    """The email SMTP server address."""

    MAIL_FROM_NAME: str = "Rest API Service"
    """The display name of the email sender."""

    MAIL_STARTTLS: bool = False
    """Boolean flag indicating whether to use STARTTLS."""

    MAIL_SSL_TLS: bool = True
    """Boolean flag indicating whether to use SSL/TLS encryption."""

    USE_CREDENTIALS: bool = True
    """Boolean flag indicating whether authentication credentials are required."""

    VALIDATE_CERTS: bool = True
    """Boolean flag indicating whether to validate SSL certificates."""

settings = Settings()
"""
Global instance of the Settings class, automatically loading configurations from environment variables.
"""
