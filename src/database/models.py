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
)

from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Contact(Base):
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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
