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
from app.models.token_deny_list import TokenDenyList
import uuid
from app.exceptions.auth_exceptions import UnauthorizedException, InvalidUserIDException, TokenMissingException, TokenAlreadyDeniedException
from app.core.notification import NotificationManager
from app.schemas.auth import Session

async def get_db():
    async with SessionLocal() as db:
        yield db    

async def get_current_user(access_token: str = Cookie(default=None), db: AsyncSession = Depends(get_db)) -> Session:
    """Return the active user identified by the access-token cookie."""
    try:
        if not access_token:
            raise TokenMissingException("Unauthorized")
        user_id, jti = get_user_id_from_access_token(access_token)
        user_id = uuid.UUID(user_id)
        jti = uuid.UUID(jti)
        revoked_token = await db.scalar(select(TokenDenyList).where(TokenDenyList.jti == jti).limit(1))
        if revoked_token:
            raise TokenAlreadyDeniedException("Unauthorized")
        result = await db.execute(select(User).where(User.id == user_id).limit(1))
        user = result.scalar_one_or_none()
        # Inactive accounts use the same unauthorized error as an unknown id.
        if not user or not user.isActive:
            raise InvalidUserIDException("Unauthorized")
        return Session(user=user, jti=jti)
    except (UnauthorizedException, ValueError, TypeError, KeyError, OverflowError) as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED , detail=str(e)) from e


async def get_current_agent_user(session: Session = Depends(get_current_user)) -> Session:
    if session.user.role != UserRole.AGENT:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN , detail="Forbidden")
    return session

async def get_current_employee_user(session: Session = Depends(get_current_user)) -> Session:
    if session.user.role != UserRole.EMPLOYEE:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN , detail="Forbidden")
    return session


async def get_agent_notification_manager(request: Request) -> NotificationManager:
    return request.app.state.agent_notification_manager

async def get_employee_notification_manager(request: Request) -> NotificationManager:
    return request.app.state.employee_notification_manager
