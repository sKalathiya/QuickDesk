#dependencies for the application

from fastapi.exceptions import HTTPException
from fastapi import Depends, Request
from fastapi import Cookie
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_user_id_from_access_token
import uuid
from app.exceptions.auth_exceptions import UnauthorizedException, InvalidUserIDException, TokenMissingException
from app.core.notification import NotificationManager

async def get_db():
    async with SessionLocal() as db:
        yield db    

async def get_current_user(access_token: str = Cookie(default=None), db: AsyncSession = Depends(get_db)) -> User:
    """Return the active user identified by the access-token cookie."""
    try:
        if not access_token:
            raise TokenMissingException("Unauthorized")
        user_id = uuid.UUID(get_user_id_from_access_token(access_token))
        result = await db.execute(select(User).where(User.id == user_id).limit(1))
        user = result.scalar_one_or_none()
        # Inactive accounts use the same unauthorized error as an unknown id.
        if not user or not user.isActive:
            raise InvalidUserIDException("Unauthorized")
        return user
    except UnauthorizedException as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED , detail=str(e)) from e


async def get_current_agent_user(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.AGENT:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN , detail="Forbidden")
    return user

async def get_current_employee_user(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.EMPLOYEE:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN , detail="Forbidden")
    return user


async def get_agent_notification_manager(request: Request) -> NotificationManager:
    return request.app.state.agent_notification_manager

async def get_employee_notification_manager(request: Request) -> NotificationManager:
    return request.app.state.employee_notification_manager
