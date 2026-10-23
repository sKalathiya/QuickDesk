#authentication endpoints


from app.schemas.auth import UserCreate, UserLogin, Token
from app.schemas.user import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.api.deps import get_db
from fastapi import APIRouter
from fastapi import status
from app.services.authservice import login_user, create_user
from fastapi import Response
from app.models.user import User
from app.api.deps import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register" , status_code=status.HTTP_201_CREATED , response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)) -> UserResponse:
    return await create_user(user, db)


@router.post("/login" , status_code=status.HTTP_200_OK)
async def login(user: UserLogin, response: Response, db: AsyncSession = Depends(get_db)) -> None:
    token =  await login_user(user, db)
    response.set_cookie(key="access_token", value=token.access_token, httponly=True, samesite="strict", secure=True)
    return

@router.post("/logout", status_code = status.HTTP_200_OK)
async def logout(response: Response, current_user: User = Depends(get_current_user)) -> None:
    response.delete_cookie(key="access_token", httponly=True, samesite="strict", secure=True)
    return