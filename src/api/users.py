from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.schemas.users import UserSchema
from src.services.auth import get_current_user, is_admin
from src.services.upload_file import UploadFileService
from src.services.users import UserService
from src.utils.limiter import limiter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSchema)
@limiter.limit("5/minute")
async def me(request: Request, user: UserSchema = Depends(get_current_user)):
    """
    Retrieve the details of the currently authenticated user.

    Args:
        request (Request): The request instance.
        user (UserSchema): The currently authenticated user.

    Returns:
        UserSchema: The authenticated user's details.
    """
    return user


@router.patch("/avatar", response_model=UserSchema)
async def update_avatar_user(
    file: UploadFile = File(),
    user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the avatar of the authenticated user.

    Args:
        file (UploadFile): The uploaded avatar file.
        user (UserSchema): The currently authenticated user.
        db (AsyncSession): The database session dependency.

    Returns:
        UserSchema: The user with the updated avatar.
    """
    print(user.username)
    print(user.email)
    print(user.role)
    print(is_admin(user))
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Only admins can update avatars")

    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
