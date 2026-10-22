from sqlalchemy import Column, String, UUID, func, DateTime
from sqlalchemy.types import Enum as SQLAlchemyEnum
import uuid
from app.core.database import Base
import enum

class UserRole(enum.Enum):
    AGENT = "agent"
    EMPLOYEE = "employee"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    created_at = Column(DateTime, nullable=False, default=func.now())



