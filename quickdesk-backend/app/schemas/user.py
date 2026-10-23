#Pydantic Schema for user


from pydantic import BaseModel, EmailStr
import uuid
from app.models.user import UserRole


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: UserRole

