from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas.users import UserCreate


class UserService:
    """
    Service class for handling user-related business logic.
    """

    def __init__(self, db: AsyncSession):
        """
        Initializes the UserService with a database session.

        Args:
            db (AsyncSession): The SQLAlchemy async session.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Creates a new user and assigns an avatar if available.

        Args:
            body (UserCreate): The user creation data.

        Returns:
            User: The newly created user.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieves a user by their unique ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User: The user if found.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieves a user by their username.

        Args:
            username (str): The username to search for.

        Returns:
            User: The user if found.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: EmailStr):
        """
        Retrieves a user by their email.

        Args:
            email (EmailStr): The email address to search for.

        Returns:
            User: The user if found.
        """
        return await self.repository.get_user_by_email(email)

    async def update_avatar_url(self, email: EmailStr, url: str):
        """
        Updates the avatar URL of a user.

        Args:
            email (EmailStr): The user's email.
            url (str): The new avatar URL.

        Returns:
            User: The updated user.
        """
        return await self.repository.update_avatar_url(email, url)

    async def confirmed_email(self, email: EmailStr):
        """
        Confirms the user's email address.

        Args:
            email (EmailStr): The email address to confirm.
        """
        return await self.repository.confirmed_email(email)
