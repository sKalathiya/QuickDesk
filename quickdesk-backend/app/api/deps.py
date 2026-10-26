#dependencies for the application

from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_422_UNPROCESSABLE_CONTENT
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from fastapi import Cookie, Depends
from app.core.security import get_user_id_from_access_token
import uuid
from app.exceptions.auth_exceptions import UnauthorizedException, InvalidUserIDException, TokenMissingException

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


class Pagination:
    def __init__(self, skip: int = 0, limit: int = 10):
        if skip < 0:
            raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_CONTENT, detail="Invalid skip parameter")
        if limit < 1:
            raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_CONTENT, detail="Invalid limit parameter")
        if limit > 100:
            raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_CONTENT, detail="Limit parameter must be less than 100")

        self.skip = skip
        self.limit = limit

    def get_skip(self):
        return self.skip

    def get_limit(self):
        return self.limit