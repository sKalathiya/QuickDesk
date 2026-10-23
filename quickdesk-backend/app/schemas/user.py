#Pydantic Schema for user


from pydantic import BaseModel, EmailStr
from app.models.user import UserRole
from datetime import datetime
import uuid

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserResponse(UserBase):
    id: uuid.UUID
    role: UserRole
