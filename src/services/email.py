from asyncio.log import logger
from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Sends an email verification message to a user.

    Args:
        email (EmailStr): The recipient's email address.
        username (str): The username of the recipient.
        host (str): The application's base URL.

    Raises:
        ConnectionErrors: If there is an issue sending the email.
    """
    try:
        from src.services.auth import create_email_token

        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")

    except ConnectionErrors as err:
        logger.error(f"Failed to send email: {err}")
        print(f"Failed to send email: {err}")
    except Exception as e:
        logger.error(f"Unexpected error in send_email: {e}")
        print(f"Unexpected error: {e}")


async def send_reset_password_email(email: EmailStr, host: str):
    """
    Send reset password verification email.

    Args:
        email (EmailStr): The user's email address.
        host (str): The application's base URL.

    Raises:
        ConnectionErrors: If there is an issue sending the email.
    """

    try:
        from src.services.auth import create_email_token

        reset_token = create_email_token({"sub": email})
        reset_url = f"{host}/auth/reset-password/confirm?token={reset_token}"

        message = MessageSchema(
            subject="Reset Your Password",
            recipients=[email],
            template_body={"reset_url": reset_url},
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")

    except ConnectionErrors as err:
        logger.error(f"Failed to send reset password email: {err}")
        print(f"Failed to send reset password email: {err}")
    except Exception as e:
        logger.error(f"Unexpected error in send_reset_password_email: {e}")
        print(f"Unexpected error: {e}")
