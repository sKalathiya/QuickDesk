import uuid
from sqlalchemy.orm import mapped_column, Mapped
from app.core.database import Base
import datetime
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING
from pydantic import ConfigDict

# This is only True for IDEs/Linters; it is False during app execution
if TYPE_CHECKING:
    from .user import User  

class TicketCategory(Enum):
    IT = "IT"
    HR = "HR"
    FINANCE = "Finance"
    ADMIN = "Admin"
    OTHER = "Other"

class TicketPriority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class TicketStatus(Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"

class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True , default=uuid.uuid4)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    fileName: Mapped[str] = mapped_column(nullable=True)
    resolutionTime: Mapped[int] = mapped_column(nullable=True)
    resolutionDescription: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(nullable=False, default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(nullable=False, default=func.now())
    status: Mapped[TicketStatus] = mapped_column(nullable=False, default=TicketStatus.OPEN)
    priority: Mapped[TicketPriority] = mapped_column(nullable=True)
    category: Mapped[TicketCategory] = mapped_column(nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_by: Mapped["User"] = relationship("User", back_populates="tickets" )

    model_config = ConfigDict(from_attributes=True)