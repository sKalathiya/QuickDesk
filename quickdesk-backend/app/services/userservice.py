#user service

from app.schemas.user import UserCreate, UserResponse
from sqlalchemy.orm import Session
from app.models.user import User
from fastapi import HTTPException
from app.core.security import hash_password

#Create a new user
def create_user(user: UserCreate, db: Session) -> UserResponse:
    existing: bool = db.query(User).filter(User.email == user.email).first() is not None
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse(id=new_user.id, name=new_user.name, email=new_user.email, role=new_user.role)
