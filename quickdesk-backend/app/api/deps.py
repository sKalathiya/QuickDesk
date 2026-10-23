#dependencies for the application

from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED
from app.core.database import SessionLocal
from app.models.user import User
from fastapi import Cookie, Depends
from app.core.security import get_user_id_from_access_token

async def get_db():
    async with SessionLocal() as db:
        yield db    

async def get_current_user(access_token: str = Cookie(default=None), db: AsyncSession = Depends(get_db)) -> User:
    user_id = get_user_id_from_access_token(access_token)
    result = await db.execute(select(User).where(User.id == user_id).limit(1))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED , detail="Invalid Token")
    return user