#authentication endpoints


from app.schemas.user import UserCreate, UserCreateResponse
from sqlalchemy.orm import Session
from fastapi import Depends
from app.api.deps import get_db
from app.services.userservice import create_user
from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)) -> UserCreateResponse:
    return create_user(user, db)
