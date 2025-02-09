import os

from dotenv import load_dotenv
from pydantic import EmailStr
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://admin:admin@localhost:5432/hw8"
    )
    JWT_SECRET: str = os.getenv("JWT_SECRET", "YOUR_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_SECONDS: str = os.getenv("JWT_EXPIRATION_SECONDS", 3600)

    CLD_NAME: str = os.getenv("CLD_NAME", "asdasdasd")
    CLD_API_KEY: int = os.getenv("CLD_API_KEY", 156282568713174)
    CLD_API_SECRET: str = os.getenv("CLD_API_SECRET", "GREGFDGSDSFWEF")

    MAIL_USERNAME: EmailStr = "example@meta.ua"
    MAIL_PASSWORD: str = "secretPassword"
    MAIL_FROM: EmailStr = "example@meta.ua"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"
    MAIL_FROM_NAME: str = "Rest API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True


settings = Settings()
