#security for the application

from uuid import UUID
from pwdlib import PasswordHash
from fastapi.exceptions import HTTPException
import jwt
from app.core.config import settings
from app.exceptions.auth_exceptions import InvalidTokenException

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(payload: dict) -> str:
    """Sign a JWT payload that must include id and exp claims."""
    if "id" not in payload or "exp" not in payload or "jti" not in payload:
        raise ValueError("Payload missing required claim information!")
    return jwt.encode(payload, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM)
    



def get_user_id_from_access_token(token:str) -> (str, str):
    """Return the id claim from a verified access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY.get_secret_value(), algorithms=[settings.JWT_ALGORITHM], options={"require": ["id", "exp", "jti"]})
        return payload["id"], payload["jti"]
    except (jwt.ExpiredSignatureError , jwt.InvalidTokenError, jwt.MissingRequiredClaimError) as e:
        # Map an expired, invalid, or incomplete token to an unauthorized error.
        raise InvalidTokenException("Unauthorized") from e

