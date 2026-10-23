from fastapi.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from app.schemas.auth import Token
from app.schemas.auth import UserLogin
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import verify_password
from app.schemas.auth import UserCreate
from app.schemas.user import UserResponse
from app.core.security import hash_password
from fastapi import status

#Create a new user and return the user details with status code 201
async def create_user(user: UserCreate, db: AsyncSession) -> UserResponse:
    existing_user = await db.execute(select(User).where(User.email == user.email).limit(1))
    if existing_user.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    hashed_password = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserResponse(id=new_user.id, name=new_user.name, email=new_user.email, role=new_user.role)


async def login_user(user: UserLogin, db: AsyncSession) -> Token:
    result = await db.execute(select(User).where(User.email == user.email).limit(1))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED , detail="Invalid email or password!")
    db_password = verify_password(user.password , db_user.hashed_password)
    if not db_password:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED , detail="Invalid email or password!")
    
    #JWT code

    return Token(access_token="sdsd" , expires_in=20)
