from typing import Optional, Sequence

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.services.auth import get_current_user
from src.services.contacts import ContactService
from src.schemas.contacts import ContactOut, ContactCreate, ContactUpdate

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=Sequence[ContactOut])
async def read_contacts(
    name: Optional[str] = Query(None, description="Search by contact name"),
    email: Optional[str] = Query(None, description="Search by contact email"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(name=name, email=email, user=user)
    return contacts


@router.get("/{contact_id}", response_model=Sequence[ContactOut])
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id=contact_id, user=user)
    return contact


@router.post("/", response_model=ContactOut)
async def create_contact(
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.create_contact(contact_data=contact_data, user=user)
    return contact


@router.put("/{contact_id}", response_model=ContactOut)
async def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(
        contact_id=contact_id, update_data=contact_update, user=user
    )
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    is_deleted = await contact_service.delete_contact(contact_id=contact_id, user=user)
    if not is_deleted:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"detail": "Contact deleted successfully"}


@router.get("/upcoming_birthdays", response_model=Sequence[ContactOut])
async def get_upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    return await contact_service.get_upcoming_birthdays(user=user)
