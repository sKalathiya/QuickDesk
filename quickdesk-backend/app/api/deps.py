#dependencies for the application

from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from fastapi import Cookie, Depends
from app.core.security import get_user_id_from_access_token
import uuid

async def get_db():
    async with SessionLocal() as db:
        yield db    

async def get_current_user(access_token: str = Cookie(default=None), db: AsyncSession = Depends(get_db)) -> User:
    if not access_token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED , detail="Unauthorized")
    try:
        user_id = uuid.UUID(get_user_id_from_access_token(access_token))
    except (ValueError, AttributeError) as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED , detail="Unauthorized") from e
    result = await db.execute(select(User).where(User.id == user_id).limit(1))
    user = result.scalar_one_or_none()
    if not user or not user.isActive:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED , detail="Unauthorized")
    return user


async def get_current_agent_user(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.AGENT:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN , detail="Forbidden")
    return user

async def get_current_employee_user(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.EMPLOYEE:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN , detail="Forbidden")
    return user