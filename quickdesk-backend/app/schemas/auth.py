from pydantic import BaseModel, EmailStr, Field, ConfigDict
import re
import uuid
from app.models.user import UserRole

class Session(BaseModel):
    user_id: uuid.UUID
    user_role: UserRole
    jti: uuid.UUID

class Token(BaseModel):
    access_token: str

class UserLogin(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True, extra="forbid")
    email: EmailStr
    password: str


#Password should contain at least one lowercase letter, one uppercase letter, one number, and one special character    
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$")

class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True, extra="forbid")
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=18, pattern=PASSWORD_REGEX)