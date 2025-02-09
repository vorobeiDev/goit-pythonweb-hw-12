import pytest
from datetime import datetime, timedelta
from sqlalchemy import select

from src.database.models import Contact, User
from tests.conftest import TestingSessionLocal

contact_data = {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+380998887766",
    "birthday": "2000-05-20",
    "user_id": 1,
}


@pytest.mark.asyncio
async def test_create_contact(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/contacts", json=contact_data, headers=headers)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == contact_data["name"]
    assert data["email"] == contact_data["email"]
    assert data["phone"] == contact_data["phone"]


@pytest.mark.asyncio
async def test_get_contacts(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/contacts/", headers=headers)

    assert response.status_code == 200, response.text
    contacts = response.json()
    assert isinstance(contacts, list)
    assert len(contacts) > 0


@pytest.mark.asyncio
async def test_get_contact_by_id(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/contacts/1", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "name" in data
    assert "email" in data
    assert "phone" in data


@pytest.mark.asyncio
async def test_update_contact(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    update_data = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "+380991112233",
    }

    response = client.put("/api/contacts/1", json=update_data, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]
    assert data["phone"] == update_data["phone"]


@pytest.mark.asyncio()
async def test_delete_contact(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    contact_id = 1

    delete_response = client.delete(f"/api/contacts/{contact_id}", headers=headers)
    assert delete_response.status_code == 200, delete_response.text
    data = delete_response.json()
    assert data["detail"] == "Contact deleted successfully"

    get_response = client.get(f"/api/contacts/{contact_id}", headers=headers)

    assert get_response.status_code == 404


from datetime import date, timedelta


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    async with TestingSessionLocal() as session:
        user = await session.execute(select(User).limit(1))
        user = user.scalar_one_or_none()
        assert user is not None

        today = date.today()

        contacts = [
            Contact(
                name="Upcoming 1",
                email="upcoming1@mail.com",
                phone="+380991234567",
                birthday=today + timedelta(days=3),
                user_id=user.id,
            ),
            Contact(
                name="Upcoming 2",
                email="upcoming2@mail.com",
                phone="+380992345678",
                birthday=today + timedelta(days=6),
                user_id=user.id,
            ),
            Contact(
                name="Past",
                email="past@mail.com",
                phone="+380993456789",
                birthday=today - timedelta(days=3),
                user_id=user.id,
            ),
            Contact(
                name="Far Future",
                email="future@mail.com",
                phone="+380994567890",
                birthday=today + timedelta(days=10),
                user_id=user.id,
            ),
        ]

        session.add_all(contacts)
        await session.commit()

    response = client.get("/api/contacts/upcoming_birthdays", headers=headers)
    assert response.status_code == 200, response.text

    birthdays = response.json()
    assert isinstance(birthdays, list)

    assert len(birthdays) == 2
    returned_names = {contact["name"] for contact in birthdays}
    assert "Upcoming 1" in returned_names
    assert "Upcoming 2" in returned_names
    assert "Past" not in returned_names
    assert "Far Future" not in returned_names
