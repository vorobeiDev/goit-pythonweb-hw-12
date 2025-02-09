from pydantic import BaseModel, ConfigDict, EmailStr


class User(BaseModel):
    """
    Schema for representing a user in responses.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        avatar (str): The URL of the user's avatar image.
    """

    id: int
    username: str
    email: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Attributes:
        username (str): The username of the new user.
        email (str): The email address of the user.
        password (str): The password for the user.
    """

    username: str
    email: str
    password: str


class Token(BaseModel):
    """
    Schema for authentication tokens.

    Attributes:
        access_token (str): The JWT access token.
        token_type (str): The type of token (e.g., "bearer").
    """

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Schema for requesting email-related operations.

    Attributes:
        email (EmailStr): The email address for verification or password reset requests.
    """

    email: EmailStr
