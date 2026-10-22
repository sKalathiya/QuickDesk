#authentication endpoints


from main import app
from app.schemas.user import UserCreate, UserResponse
from sqlalchemy.orm import Session
from fastapi import Depends
from app.api.deps import get_db
from app.services.userservice import create_user



@app.post("/api/v1/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    return create_user(user, db)
