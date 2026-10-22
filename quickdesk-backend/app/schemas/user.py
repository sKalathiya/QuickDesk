#Pydantic Schema for user


from pydantic import BaseModel, Field, EmailStr
import uuid
from app.models.user import UserRole

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    #Password should contain at least one lowercase letter, one uppercase letter, one number, and one special character
    password: str = Field(min_length=8, max_length=18, regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,18}$")
    role: UserRole = Field(default=UserRole.EMPLOYEE)


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: UserRole

