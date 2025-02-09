from pydantic import BaseModel, ConfigDict, EmailStr


class UserSchema(BaseModel):
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
    role: str

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(BaseModel):
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


class TokenSchema(BaseModel):
    """
    Schema for authentication tokens.

    Attributes:
        access_token (str): The JWT access token.
        token_type (str): The type of token (e.g., "bearer").
    """

    access_token: str
    token_type: str


class RequestEmailSchema(BaseModel):
    """
    Schema for requesting email-related operations.

    Attributes:
        email (EmailStr): The email address for verification or password reset requests.
    """

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """
    Schema for requesting password reset requests.

    Attributes:
        email (EmailStr): The email address for verification or password reset requests.
    """

    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    """
    Schema for requesting password reset confirmation requests.

    Attributes:
        email (EmailStr): The email address for verification or password reset confirmation requests.
        new_password (str): The new password.
    """

    token: str
    new_password: str
