#user service

from app.schemas.user import UserCreate, UserCreateResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from fastapi import status
from fastapi.exceptions import HTTPException
from app.core.security import hash_password
from sqlalchemy import select

#Create a new user and return the user details with status code 201
async def create_user(user: UserCreate, db: AsyncSession) -> UserCreateResponse:
    existing_user = await db.execute(select(User).where(User.email == user.email).limit(1))
    existing = existing_user.scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    hashed_password = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserCreateResponse(id=new_user.id, name=new_user.name, email=new_user.email, role=new_user.role)
