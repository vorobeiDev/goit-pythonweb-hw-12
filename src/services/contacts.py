from typing import Optional, Type, Sequence
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactCreate, ContactUpdate
from src.database.models import Contact, User


class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, contact_data: ContactCreate, user: User) -> Contact:
        return await self.repository.create(body=contact_data, user=user)

    async def get_contact(self, contact_id: int, user: User) -> Optional[Contact]:
        return await self.repository.get_by_id(contact_id=contact_id, user=user)

    async def get_contacts(
        self,
        user: User,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Sequence[Contact]:
        return await self.repository.get_all(name=name, email=email, user=user)

    async def update_contact(
        self, contact_id: int, update_data: ContactUpdate, user: User
    ) -> Optional[Contact]:
        return await self.repository.update(
            contact_id=contact_id, body=update_data, user=user
        )

    async def delete_contact(self, contact_id: int, user: User) -> bool:
        await self.repository.delete(contact_id=contact_id, user=user)
        return True

    async def get_upcoming_birthdays(self, user: User) -> Sequence[Contact]:
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
