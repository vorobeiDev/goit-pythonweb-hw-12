from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Form,
    BackgroundTasks,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas.users import (
    UserCreateSchema,
    TokenSchema,
    UserSchema,
    RequestEmailSchema,
    ResetPasswordRequest,
    ResetPasswordConfirm,
)
from src.services.auth import (
    create_access_token,
    Hash,
    get_email_from_token,
)
from src.services.email import send_email, send_reset_password_email
from src.services.users import UserService
from src.database.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


class OAuth2PasswordRequestFormEmail(OAuth2PasswordRequestForm):
    """
    Custom OAuth2 password request form that requires an email instead of a username.
    """

    def __init__(
        self,
        email: str = Form(...),
        password: str = Form(...),
        scope: str = Form(""),
        client_id: str = Form(None),
        client_secret: str = Form(None),
    ):
        super().__init__(
            username=email,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )


@router.post(
    "/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreateSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Registers a new user in the system.

    Args:
        user_data (UserCreateSchema): The data required to create a user.
        background_tasks (BackgroundTasks): Tasks to be executed in the background.
        request (Request): The HTTP request instance.
        db (AsyncSession): The database session dependency.

    Returns:
        UserSchema: The newly registered user.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login_user(
    form_data: OAuth2PasswordRequestFormEmail = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticates a user and returns an access token.

    Args:
        form_data (OAuth2PasswordRequestFormEmail): Login credentials.
        db (AsyncSession): The database session dependency.

    Returns:
        TokenSchema: A dictionary containing the access token and token type.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(form_data.username)

    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email confirm failed",
        )

    access_token = await create_access_token(data={"sub": user.email}, role=user.role)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirms a user's email using a verification token.

    Args:
        token (str): The email confirmation token.
        db (AsyncSession): The database session dependency.

    Returns:
        dict: A message indicating the confirmation status.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email has been confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Email is confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmailSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Requests an email confirmation for a user.

    Args:
        body (RequestEmailSchema): The request containing the email to confirm.
        background_tasks (BackgroundTasks): Background task manager.
        request (Request): The HTTP request instance.
        db (AsyncSession): The database session dependency.

    Returns:
        dict: A message indicating whether the confirmation email was sent.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Your email has been confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for confirmation"}


@router.post("/reset-password")
async def request_password_reset(
    body: ResetPasswordRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request for password reset. User get an confirmation email.

    Args:
        body (RequestEmailSchema): The request containing the email to confirm.
        background_tasks (BackgroundTasks): Background task manager.
        request (Request): The HTTP request instance.
        db (AsyncSession): The database session dependency.

    Returns:
        dict: Message indicating the confirmation email was sent.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    background_tasks.add_task(send_reset_password_email, user.email, request.base_url)

    return {"message": "Check your email for password reset instructions"}


@router.post("/reset-password/confirm")
async def confirm_reset_password(
    body: ResetPasswordConfirm, db: AsyncSession = Depends(get_db)
):
    """
    Confirm a password reset email.

    Args:
        body (ResetPasswordConfirm): The request containing the email and password.
        db (AsyncSession): The database session dependency.

    Returns:
        dict: Повідомлення про успішне скидання пароля.
    """
    email = await get_email_from_token(body.token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token or user not found",
        )

    new_hashed_password = Hash().get_password_hash(body.new_password)
    await user_service.update_password(email, new_hashed_password)

    return {"message": "Password successfully reset"}
