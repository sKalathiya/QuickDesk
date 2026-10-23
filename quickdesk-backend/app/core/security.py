#security for the application

from uuid import UUID
from pwdlib import PasswordHash
from fastapi.exceptions import HTTPException
import jwt
from app.core.config import settings

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(payload: dict) -> str:
    try:
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") from e



def get_user_id_from_access_token(token:str) -> str:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
        return payload["id"]
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e
