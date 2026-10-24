from sqlalchemy import func
import uuid
from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
import enum
from datetime import datetime
from typing import List
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING
from pydantic import ConfigDict


if TYPE_CHECKING:
    from .ticket import Ticket  

class UserRole(enum.Enum):
    AGENT = "agent"
    EMPLOYEE = "employee"

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    isActive: Mapped[bool] = mapped_column(nullable=False, default=True)
    role: Mapped[UserRole] = mapped_column(nullable=False, default=UserRole.EMPLOYEE)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="created_by")

    model_config = ConfigDict(from_attributes=True)



