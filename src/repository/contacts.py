from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas.contacts import ContactCreate, ContactUpdate


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_all(
        self,
        user: User,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Sequence[Contact]:
        query = select(Contact).filter_by(user=user)

        if name:
            query = query.filter(Contact.name.ilike(f"%{name}%"))
        if email:
            query = query.filter(Contact.email.ilike(f"%{email}%"))

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, contact_id: int, user: User) -> Optional[Contact]:
        query = select(Contact).filter_by(id=contact_id, user=user)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, body: ContactCreate, user: User) -> Contact:
        contact = Contact(**body.model_dump())
        contact.user = user

        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)

        return contact

    async def update(self, contact_id: int, body: ContactUpdate, user: User) -> Contact:
        contact = await self.get_by_id(contact_id=contact_id, user=user)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def delete(self, contact_id: int, user: User) -> None:
        contact = await self.get_by_id(contact_id=contact_id, user=user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()

        return contact
