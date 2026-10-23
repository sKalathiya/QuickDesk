#authentication endpoints


from app.schemas.auth import UserCreate, UserLogin, Token
from app.schemas.user import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.api.deps import get_db
from fastapi import APIRouter
from fastapi import status
from app.services.authservice import login_user, create_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register" , status_code=status.HTTP_201_CREATED , response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)) -> UserResponse:
    return await create_user(user, db)


@router.post("/login" , status_code=status.HTTP_200_OK , response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)) -> Token:
    token =  await login_user(user, db)
    #add token in response cookie
    return token

