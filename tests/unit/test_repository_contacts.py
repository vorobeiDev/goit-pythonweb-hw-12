import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactCreate, ContactUpdate, ContactOut


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(
            id=1,
            name="test name",
            email="test@mail.com",
            phone="+380998887766",
            birthday=datetime.strptime("2007-01-01", "%Y-%m-%d").date(),
            user_id=user.id,
        )
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_all(user)

    assert len(contacts) == 1
    assert contacts[0].name == "test name"
    assert contacts[0].email == "test@mail.com"
    assert contacts[0].phone == "+380998887766"
    assert contacts[0].birthday == datetime.strptime("2007-01-01", "%Y-%m-%d").date()
    assert contacts[0].user_id == user.id


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1,
        name="test name",
        email="test@mail.com",
        phone="+380998887766",
        birthday=datetime.strptime("2007-01-01", "%Y-%m-%d").date(),
        user_id=user.id,
    )

    mock_session.execute = AsyncMock(return_value=mock_result)

    contact = await contact_repository.get_by_id(contact_id=1, user=user)
    assert contact is not None
    assert contact.id == 1
    assert contact.name == "test name"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    contact_data = ContactCreate(
        name="new name",
        email="new@mail.com",
        phone="+380998887766",
        birthday=datetime.strptime("2007-01-01", "%Y-%m-%d").date(),
        user_id=user.id,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1,
        name=contact_data.name,
        email=contact_data.email,
        phone=contact_data.phone,
        birthday=contact_data.birthday,
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.create(body=contact_data, user=user)

    assert isinstance(result, Contact)
    assert result.name == "new name"
    assert result.email == "new@mail.com"

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    contact_data = ContactUpdate(
        name="new name",
        email="new@mail.com",
    )

    existing_contact = Contact(
        id=1,
        name="test name",
        email="test@mail.com",
        phone="+380998887766",
        birthday=datetime.strptime("2007-01-01", "%Y-%m-%d").date(),
        user_id=user.id,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.update(contact_id=1, body=contact_data, user=user)

    assert result is not None
    assert result.name == "new name"
    assert result.email == "new@mail.com"

    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_delete_contact(contact_repository, mock_session, user):
    existing_contact = Contact(
        id=1,
        name="test name",
        email="test@mail.com",
        phone="+380998887766",
        birthday=datetime.strptime("2007-01-01", "%Y-%m-%d").date(),
        user_id=user.id,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.delete(contact_id=1, user=user)

    assert result is not None
    assert result.name == "test name"
    assert result.email == "test@mail.com"

    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_contacts_empty(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_all(user)

    assert contacts == []


@pytest.mark.asyncio
async def test_get_contact_by_id_not_found(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    contact = await contact_repository.get_by_id(contact_id=99, user=user)

    assert contact is None


@pytest.mark.asyncio
async def test_update_contact_not_found(contact_repository, mock_session, user):
    contact_data = ContactUpdate(name="updated name")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.update(
        contact_id=99, body=contact_data, user=user
    )

    assert result is None


@pytest.mark.asyncio
async def test_delete_contact_not_found(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.delete(contact_id=99, user=user)

    assert result is None
