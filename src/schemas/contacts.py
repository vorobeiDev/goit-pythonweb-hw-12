from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    birthday: date
    user_id: int
    additional_data: Optional[str] = Field(None)


class ContactUpdate(BaseModel):
    name: Optional[str] = Field(None)
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None)
    birthday: Optional[date] = Field(None)
    additional_data: Optional[str] = Field(None)


class ContactOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_data: Optional[str]

    class Config:
        orm_mode = True
