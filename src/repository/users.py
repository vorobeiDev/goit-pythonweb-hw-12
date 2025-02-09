from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User
from src.schemas.users import UserCreateSchema
from pydantic import EmailStr


class UserRepository:
    """
    Repository for interacting with user data in the database.

    This class provides methods to create, retrieve, update, and delete user records.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the UserRepository with a database session.

        Args:
            session (AsyncSession): The SQLAlchemy async session.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieves a user by their unique ID.

        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            User | None: The user object if found, else None.
        """
        stmt = select(User).where(User.id == user_id).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieves a user by their username.

        Args:
            username (str): The username of the user.

        Returns:
            User | None: The user object if found, else None.
        """
        stmt = select(User).where(User.username == username).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: EmailStr) -> User | None:
        """
        Retrieves a user by their email address.

        Args:
            email (EmailStr): The email of the user.

        Returns:
            User | None: The user object if found, else None.
        """
        stmt = select(User).where(User.email == email).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, body: UserCreateSchema, avatar: str = None) -> User:
        """
        Creates a new user and stores their information in the database.

        Args:
            body (UserCreateSchema): The data required to create a new user.
            avatar (str, optional): URL to the user's avatar image.

        Returns:
            User: The created user object.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_avatar_url(self, email: EmailStr, url: str) -> User:
        """
        Updates the avatar URL of a user.

        Args:
            email (EmailStr): The email of the user whose avatar is being updated.
            url (str): The new avatar URL.

        Returns:
            User: The updated user object.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: EmailStr) -> None:
        """
        Marks a user's email as confirmed in the database.

        Args:
            email (EmailStr): The email of the user whose email is being confirmed.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_password(self, email: EmailStr, new_hashed_password: str) -> User:
        """
        Updates the password of a user.

        Args:
            email (EmailStr): The user's email.
            new_hashed_password (str): The new password.

        Returns:
            User: The updated user object.
        """
        user = await self.get_user_by_email(email)
        user.hashed_password = new_hashed_password
        await self.db.commit()
        await self.db.refresh(user)
        return user
