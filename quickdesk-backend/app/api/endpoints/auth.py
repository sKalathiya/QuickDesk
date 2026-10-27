#authentication endpoints


from app.schemas.auth import UserCreate, UserLogin, Token
from app.schemas.user import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.api.deps import get_db
from fastapi import APIRouter
from fastapi import status
from app.services.authservice import login_user, create_user, logout_user
from fastapi import Response
from app.models.user import User
from app.api.deps import get_current_agent_user, get_current_user
from app.exceptions.auth_exceptions import UserAlreadyExistsException
from fastapi import HTTPException
from app.exceptions.auth_exceptions import InvalidCredentialsException
from app.exceptions.auth_exceptions import TokenAlreadyDeniedException
from app.schemas.auth import Session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register" , status_code=status.HTTP_201_CREATED , response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)) -> UserResponse:
    try:
        return await create_user(user, db)
    except UserAlreadyExistsException as e:
        # An existing account is a conflict, not a malformed registration.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
   

@router.post("/login" , status_code=status.HTTP_200_OK)
async def login(user: UserLogin, response: Response, db: AsyncSession = Depends(get_db)) -> None:
    try:
        token =  await login_user(user, db)
    except InvalidCredentialsException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    response.set_cookie(key="access_token", value=token.access_token, httponly=True, samesite="strict", secure=True)
    return

@router.post("/logout", status_code = status.HTTP_200_OK)
async def logout(response: Response, session: Session = Depends(get_current_user)) -> None:
    try:
        await logout_user(response, session.jti)
    except TokenAlreadyDeniedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
