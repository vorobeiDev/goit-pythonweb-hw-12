from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas.contacts import ContactCreate, ContactUpdate


class ContactRepository:
    """
    Repository for managing contacts in the database.

    This class provides methods to create, retrieve, update, and delete contact records.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the ContactRepository with a database session.

        Args:
            session (AsyncSession): The SQLAlchemy async session.
        """
        self.db = session

    async def get_all(
        self,
        user: User,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Sequence[Contact]:
        """
        Retrieves a list of contacts for a user with optional filtering.

        Args:
            user (User): The owner of the contacts.
            name (Optional[str]): A name filter for searching contacts.
            email (Optional[str]): An email filter for searching contacts.

        Returns:
            Sequence[Contact]: A list of contacts that match the criteria.
        """
        query = select(Contact).filter_by(user=user)

        if name:
            query = query.filter(Contact.name.ilike(f"%{name}%"))
        if email:
            query = query.filter(Contact.email.ilike(f"%{email}%"))

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, contact_id: int, user: User) -> Optional[Contact]:
        """
        Retrieves a contact by its ID.

        Args:
            contact_id (int): The unique identifier of the contact.
            user (User): The owner of the contact.

        Returns:
            Optional[Contact]: The contact if found, otherwise None.
        """
        query = select(Contact).filter_by(id=contact_id, user=user)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, body: ContactCreate, user: User) -> Contact:
        """
        Creates a new contact for the user.

        Args:
            body (ContactCreate): The contact details to be created.
            user (User): The owner of the contact.

        Returns:
            Contact: The newly created contact.
        """
        contact = Contact(**body.model_dump())
        contact.user = user

        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)

        return contact

    async def update(self, contact_id: int, body: ContactUpdate, user: User) -> Contact:
        """
        Updates an existing contact.

        Args:
            contact_id (int): The unique identifier of the contact.
            body (ContactUpdate): The updated contact details.
            user (User): The owner of the contact.

        Returns:
            Contact: The updated contact, or None if not found.
        """
        contact = await self.get_by_id(contact_id=contact_id, user=user)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def delete(self, contact_id: int, user: User) -> None:
        """
        Deletes a contact by its ID.

        Args:
            contact_id (int): The unique identifier of the contact.
            user (User): The owner of the contact.

        Returns:
            None: If the contact is deleted successfully.
        """
        contact = await self.get_by_id(contact_id=contact_id, user=user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()

        return contact
