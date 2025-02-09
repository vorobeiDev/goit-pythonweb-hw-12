from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.schemas.users import User
from src.services.auth import get_current_user
from src.services.upload_file import UploadFileService
from src.services.users import UserService
from src.utils.limiter import limiter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
@limiter.limit("5/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Retrieve the details of the currently authenticated user.

    Args:
        request (Request): The request instance.
        user (User): The currently authenticated user.

    Returns:
        User: The authenticated user's details.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the avatar of the authenticated user.

    Args:
        file (UploadFile): The uploaded avatar file.
        user (User): The currently authenticated user.
        db (AsyncSession): The database session dependency.

    Returns:
        User: The user with the updated avatar.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
