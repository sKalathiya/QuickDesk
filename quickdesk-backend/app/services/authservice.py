from fastapi.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from app.schemas.auth import Token
from app.schemas.auth import UserLogin
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.schemas.auth import UserCreate
from app.schemas.user import UserResponse
from app.core.security import hash_password
from fastapi import status
import time
from app.core.config import settings
from app.exceptions.auth_exceptions import UserAlreadyExistsException, InvalidCredentialsException

async def create_user(user: UserCreate, db: AsyncSession) -> UserResponse:
    """Register a new user and commit the account."""

    try:
        existing_user = await db.scalar(select(User).where(User.email == user.email).limit(1))
        if existing_user is not None:
            raise UserAlreadyExistsException("User already exists")
        hashed_password = hash_password(user.password)
        new_user = User(name=user.name, email=user.email, hashed_password=hashed_password)
        db.add(new_user)
        # Assign the new row an id before the response is built; the commit is later.
        await db.flush()
        await db.refresh(new_user)
        userResponse = UserResponse.model_validate(new_user)
        await db.commit()
        return userResponse
    except Exception:
        # Undo the uncommitted user if any step fails.
        await db.rollback()
        raise


async def login_user(user: UserLogin, db: AsyncSession) -> Token:
    db_user = await db.scalar(select(User).where(User.email == user.email).limit(1))
    # Reject a missing or inactive account with the same error as a bad password.
    if not db_user or not db_user.isActive:
        raise InvalidCredentialsException("Invalid email or password!")
    db_password = verify_password(user.password , db_user.hashed_password)
    if not db_password:
        raise InvalidCredentialsException("Invalid email or password!")
    
    payload = {"id": str(db_user.id), "exp": time.time() + settings.JWT_EXPIRATION_TIME}
    access_token = create_access_token(payload)
    return Token(access_token=access_token)
