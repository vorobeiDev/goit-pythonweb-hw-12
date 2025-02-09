from unittest.mock import AsyncMock, patch
import pytest
from src.services.email import send_email, send_reset_password_email
from src.services.auth import create_email_token
from fastapi_mail import FastMail


@pytest.mark.asyncio
async def test_send_email_success():
    email = "testuser@example.com"
    username = "testuser"
    host = "http://localhost:8000"

    token = create_email_token({"sub": email})

    with patch.object(FastMail, "send_message", new_callable=AsyncMock) as mock_send:
        await send_email(email, username, host)

        mock_send.assert_called_once()

        args, kwargs = mock_send.call_args
        message = args[0]

        assert message.subject == "Confirm your email"
        assert message.recipients == [email]
        assert message.template_body["host"] == host
        assert message.template_body["username"] == username
        assert message.template_body["token"] == token
        assert kwargs["template_name"] == "verify_email.html"


@pytest.mark.asyncio
async def test_send_reset_password_email_success():
    email = "testuser@example.com"
    host = "http://localhost:8000"

    token = create_email_token({"sub": email})
    expected_url = f"{host}/auth/reset-password/confirm?token={token}"

    with patch.object(FastMail, "send_message", new_callable=AsyncMock) as mock_send:
        await send_reset_password_email(email, host)

        mock_send.assert_called_once()

        args, kwargs = mock_send.call_args
        message = args[0]

        assert message.subject == "Reset Your Password"
        assert message.recipients == [email]
        assert message.template_body["reset_url"] == expected_url
        assert kwargs["template_name"] == "reset_password.html"


@pytest.mark.asyncio
async def test_send_email_connection_error():
    email = "testuser@example.com"
    username = "testuser"
    host = "http://localhost:8000"

    with patch.object(FastMail, "send_message", new_callable=AsyncMock) as mock_send:
        mock_send.side_effect = Exception("SMTP Connection Failed")

        await send_email(email, username, host)

        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_send_reset_password_email_connection_error():
    email = "testuser@example.com"
    host = "http://localhost:8000"

    with patch.object(FastMail, "send_message", new_callable=AsyncMock) as mock_send:
        mock_send.side_effect = Exception("SMTP Connection Failed")

        await send_reset_password_email(email, host)

        mock_send.assert_called_once()
