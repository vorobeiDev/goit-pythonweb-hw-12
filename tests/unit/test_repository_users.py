import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User
from src.repository.users import UserRepository
from src.schemas.users import UserCreateSchema
from pydantic import EmailStr


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def test_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword123",
        avatar="https://example.com/avatar.png",
        confirmed=False,
    )


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session, test_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_id(1)

    assert user is not None
    assert user.id == 1
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session, test_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_username("testuser")

    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session, test_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_email("test@example.com")

    assert user is not None
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):
    user_data = UserCreateSchema(
        username="newuser",
        email="new@example.com",
        password="newpassword123",
    )

    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    result = await user_repository.create_user(user_data)

    assert isinstance(result, User)
    assert result.username == "newuser"
    assert result.email == "new@example.com"

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session, test_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    updated_user = await user_repository.update_avatar_url(
        "test@example.com", "https://newavatar.com/image.png"
    )

    assert updated_user is not None
    assert updated_user.avatar == "https://newavatar.com/image.png"

    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(test_user)


@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session, test_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()

    await user_repository.confirmed_email("test@example.com")

    assert test_user.confirmed is True

    mock_session.commit.assert_awaited_once()
