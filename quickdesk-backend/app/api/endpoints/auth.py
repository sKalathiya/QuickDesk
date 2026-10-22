#authentication endpoints


from app.schemas.user import UserCreate, UserCreateResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.api.deps import get_db
from app.services.userservice import create_user
from fastapi import APIRouter
from fastapi import status


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register" , status_code=status.HTTP_201_CREATED , response_model=UserCreateResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)) -> UserCreateResponse:
    return await create_user(user, db)
