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
    """
    Retrieve a list of contacts with optional filtering by name and email.

    Args:
        name (Optional[str]): Contact name to filter results.
        email (Optional[str]): Contact email to filter results.
        db (AsyncSession): Database session dependency.
        user (User): Current authenticated user.

    Returns:
        Sequence[ContactOut]: A list of contacts matching the filter criteria.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(name=name, email=email, user=user)
    return contacts


@router.get("/{contact_id}", response_model=ContactOut)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a single contact by its ID.

    Args:
        contact_id (int): Unique identifier of the contact.
        db (AsyncSession): Database session dependency.
        user (User): Current authenticated user.

    Returns:
        ContactOut: The requested contact if found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id=contact_id, user=user)
    return contact


@router.post("/", response_model=ContactOut)
async def create_contact(
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new contact for the authenticated user.

    Args:
        contact_data (ContactCreate): The contact details to create.
        db (AsyncSession): Database session dependency.
        user (User): Current authenticated user.

    Returns:
        ContactOut: The created contact.
    """
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
    """
    Update an existing contact.

    Args:
        contact_id (int): Unique identifier of the contact to update.
        contact_update (ContactUpdate): Updated contact details.
        db (AsyncSession): Database session dependency.
        user (User): Current authenticated user.

    Returns:
        ContactOut: The updated contact.
    """
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
    """
    Delete a contact by its ID.

    Args:
        contact_id (int): Unique identifier of the contact to delete.
        db (AsyncSession): Database session dependency.
        user (User): Current authenticated user.

    Returns:
        dict: A confirmation message if the contact was successfully deleted.
    """
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
    """
    Retrieve contacts with upcoming birthdays within the next 7 days.

    Args:
        db (AsyncSession): Database session dependency.
        user (User): Current authenticated user.

    Returns:
        Sequence[ContactOut]: A list of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    return await contact_service.get_upcoming_birthdays(user=user)
