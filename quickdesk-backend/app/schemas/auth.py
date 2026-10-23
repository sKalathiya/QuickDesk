from pydantic import BaseModel, EmailStr, Field
import re

class Token(BaseModel):
    access_token: str
    expires_in: int


class UserLogin(BaseModel):
    email: EmailStr
    password: str


#Password should contain at least one lowercase letter, one uppercase letter, one number, and one special character    
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$")

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=18, pattern=PASSWORD_REGEX)