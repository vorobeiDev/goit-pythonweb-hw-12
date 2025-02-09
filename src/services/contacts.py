from typing import Optional, Type, Sequence
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactCreate, ContactUpdate
from src.database.models import Contact, User


class ContactService:
    """
    Service class for handling contact-related business logic.
    """

    def __init__(self, db: AsyncSession):
        """
        Initializes the ContactService with a database session.

        Args:
            db (AsyncSession): The SQLAlchemy async session.
        """
        self.repository = ContactRepository(db)

    async def create_contact(self, contact_data: ContactCreate, user: User) -> Contact:
        """
        Creates a new contact for the user.

        Args:
            contact_data (ContactCreate): The data required to create a contact.
            user (User): The owner of the contact.

        Returns:
            Contact: The newly created contact.
        """
        return await self.repository.create(body=contact_data, user=user)

    async def get_contact(self, contact_id: int, user: User) -> Optional[Contact]:
        """
        Retrieves a specific contact by ID.

        Args:
            contact_id (int): The unique identifier of the contact.
            user (User): The owner of the contact.

        Returns:
            Optional[Contact]: The contact if found, otherwise None.
        """
        return await self.repository.get_by_id(contact_id=contact_id, user=user)

    async def get_contacts(
        self,
        user: User,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Sequence[Contact]:
        """
        Retrieves a list of contacts for a user with optional filters.

        Args:
            user (User): The owner of the contacts.
            name (Optional[str]): Filter contacts by name.
            email (Optional[str]): Filter contacts by email.

        Returns:
            Sequence[Contact]: A list of matching contacts.
        """
        return await self.repository.get_all(name=name, email=email, user=user)

    async def update_contact(
        self, contact_id: int, update_data: ContactUpdate, user: User
    ) -> Optional[Contact]:
        """
        Updates an existing contact's details.

        Args:
            contact_id (int): The unique identifier of the contact.
            update_data (ContactUpdate): The updated contact details.
            user (User): The owner of the contact.

        Returns:
            Optional[Contact]: The updated contact if successful, otherwise None.
        """
        return await self.repository.update(
            contact_id=contact_id, body=update_data, user=user
        )

    async def delete_contact(self, contact_id: int, user: User) -> bool:
        """
        Deletes a contact by ID.

        Args:
            contact_id (int): The unique identifier of the contact to delete.
            user (User): The owner of the contact.

        Returns:
            bool: True if deletion was successful.
        """
        await self.repository.delete(contact_id=contact_id, user=user)
        return True

    async def get_upcoming_birthdays(self, user: User) -> Sequence[Contact]:
        """
        Retrieves contacts with upcoming birthdays within the next 7 days.

        Args:
            user (User): The owner of the contacts.

        Returns:
            Sequence[Contact]: A list of contacts with upcoming birthdays.
        """
        contacts = await self.repository.get_all(user=user)
        today = date.today()
        upcoming_contacts = []
        for contact in contacts:
            try:
                birthday_this_year = contact.birthday.replace(year=today.year)
            except ValueError:
                birthday_this_year = contact.birthday.replace(year=today.year, day=28)
            if birthday_this_year < today:
                try:
                    birthday_this_year = contact.birthday.replace(year=today.year + 1)
                except ValueError:
                    birthday_this_year = contact.birthday.replace(
                        year=today.year + 1, day=28
                    )
            if today <= birthday_this_year <= today + timedelta(days=7):
                upcoming_contacts.append(contact)
        return upcoming_contacts
