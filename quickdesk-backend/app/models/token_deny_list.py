from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, String
import uuid
from app.core.database import Base

class TokenDenyList(Base):
    __tablename__ = "token_deny_list"
    jti: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
 