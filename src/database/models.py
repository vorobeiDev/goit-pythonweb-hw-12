import enum
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    func,
    Date,
    Text,
    ForeignKey,
    Boolean,
    Enum,
)

from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Contact(Base):
    """
    Represents a contact entity in the database.

    Attributes:
        id (int): The unique identifier for the contact.
        name (str): The name of the contact.
        email (str): The email address of the contact.
        phone (str): The phone number of the contact.
        birthday (date): The birth date of the contact.
        additional_data (str, optional): Any additional information related to the contact.
        user_id (int): The ID of the user who owns the contact.
        user (User): Relationship reference to the User entity.
    """

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    additional_data = Column(Text, nullable=True)

    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="users")


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    """
    Represents a user entity in the database.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        hashed_password (str): The hashed password of the user.
        created_at (datetime): The timestamp when the user was created.
        avatar (str, optional): The URL of the user's avatar.
        confirmed (bool): Indicates whether the user's email has been confirmed.
        role (UserRole): The user role of the user.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.user)
