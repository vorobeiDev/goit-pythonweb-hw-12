import json
from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.database.redis import get_redis
from src.database.models import User
from src.schemas.users import UserSchema
from src.services.users import UserService


class Hash:
    """
    A utility class for hashing and verifying passwords.

    This class utilizes bcrypt hashing algorithm to securely store passwords.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify if the provided password matches the stored hashed password.

        Args:
            plain_password (str): The raw password provided by the user.
            hashed_password (str): The stored hashed password.

        Returns:
            bool: True if passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def create_access_token(
    data: dict, role: str, expires_delta: Optional[int] = None
) -> str:
    """
    Generate a JWT access token with an expiration time.

    Args:
        data (dict): The payload data to include in the token.
        role (str): The role of the token.
        expires_delta (Optional[int]): The expiration time in seconds.

    Returns:
        str: Encoded JWT access token.
    """
    to_encode = data.copy()
    to_encode.update({"role": role})

    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(
            seconds=int(settings.JWT_EXPIRATION_SECONDS)
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
) -> User:
    """
    Retrieve the currently authenticated user from a JWT token.

    Args:
        token (str): The JWT access token provided by the user.
        db (AsyncSession): The database session.
        redis: Redis connection instance.

    Returns:
        User: The authenticated user instance.

    Raises:
        HTTPException: If token validation fails or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    cached_user = await redis.get(f"user:{token}")
    if cached_user:
        return User(**json.loads(cached_user))

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload.get("sub")
        role = payload.get("role")
        if email is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    user_schema = UserSchema.model_validate(user)
    await redis.setex(f"user:{token}", 600, json.dumps(user_schema.model_dump()))

    return user


def create_email_token(data: dict) -> str:
    """
    Generate an email confirmation token.

    Args:
        data (dict): The payload data to encode in the token.

    Returns:
        str: Encoded JWT token with a 7-day expiration time.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str) -> str:
    """
    Extract the email address from an email confirmation token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        str: The extracted email address.

    Raises:
        HTTPException: If the token is invalid or cannot be processed.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload.get("sub")
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Incorrect token",
        )


async def generate_reset_token(
    email: EmailStr, expires_delta: Optional[int] = None
) -> str:
    """
    Generate JWT-token with an expiration time for a given email.

    Args:
        email (EmailStr): The email to generate a token for.
        expires_delta (Optional[int]): The expiration time in seconds.

    Return:
        str: Encoded JWT access token.
    """
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(
            seconds=int(settings.JWT_EXPIRATION_SECONDS)
        )
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def is_admin(user: UserSchema) -> bool:
    """
    Check if the user is an administrator.

    Returns:
        bool: True if the user is an administrator.
    """
    return user.role == "admin"
