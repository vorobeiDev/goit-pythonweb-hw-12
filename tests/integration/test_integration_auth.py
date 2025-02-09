from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.database.models import User
from src.services.auth import create_access_token
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "admin",
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "User with this email already exists"


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "email": user_data.get("email"),
            "password": user_data.get("password"),
        },
    )

    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email confirm failed"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "email": user_data.get("email"),
            "password": user_data.get("password"),
            "role": user_data.get("role"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"email": user_data.get("email"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Incorrect login or password"


def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"email": "email", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Incorrect login or password"


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


reset_password_data = {"email": "testuser@mail.com"}

new_password_data = {
    "token": "fake_token",
    "new_password": "newpassword123",
}


def test_request_password_reset_user_not_found(client):
    response = client.post(
        "api/auth/reset-password", json={"email": "notfound@mail.com"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "User not found"
