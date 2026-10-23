#Pydantic Schema for user


from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole

