from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class ContactCreate(BaseModel):
    """
    Schema for creating a new contact.

    Attributes:
        name (str): The name of the contact.
        email (EmailStr): The email address of the contact.
        phone (str): The phone number of the contact.
        birthday (date): The birthday of the contact.
        user_id (int): The ID of the user to whom the contact belongs.
        additional_data (Optional[str]): Any additional information about the contact.
    """

    name: str
    email: EmailStr
    phone: str
    birthday: date
    user_id: int
    additional_data: Optional[str] = Field(None)


class ContactUpdate(BaseModel):
    """
    Schema for updating an existing contact.

    Attributes:
        name (Optional[str]): The updated name of the contact.
        email (Optional[EmailStr]): The updated email address.
        phone (Optional[str]): The updated phone number.
        birthday (Optional[date]): The updated birthday.
        additional_data (Optional[str]): Additional updated information.
    """

    name: Optional[str] = Field(None)
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None)
    birthday: Optional[date] = Field(None)
    additional_data: Optional[str] = Field(None)


class ContactOut(BaseModel):
    """
    Schema for representing a contact in responses.

    Attributes:
        id (int): The unique identifier of the contact.
        name (str): The name of the contact.
        email (EmailStr): The email address.
        phone (str): The phone number.
        birthday (date): The birthday.
        additional_data (Optional[str]): Additional information about the contact.
    """

    id: int
    name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_data: Optional[str]

    class Config:
        orm_mode = True
