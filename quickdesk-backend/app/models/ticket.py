import uuid
from sqlalchemy.orm import mapped_column, Mapped
from app.core.database import Base
import datetime
from enum import StrEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING
from pydantic import ConfigDict
from sqlalchemy.types import TIMESTAMP

# This is only True for IDEs/Linters; it is False during app execution
if TYPE_CHECKING:
    from .user import User  

class TicketCategory(StrEnum):
    IT = "IT"
    HR = "HR"
    FINANCE = "FINANCE"
    ADMIN = "ADMIN"
    OTHER = "OTHER"
    NOT_SPECIFIED = "NOT_SPECIFIED"

class TicketPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    NOT_SPECIFIED = "NOT_SPECIFIED"

class TicketStatus(StrEnum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"

class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True , default=uuid.uuid4)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    fileName: Mapped[str] = mapped_column(nullable=True)
    resolutionDescription: Mapped[str] = mapped_column(nullable=True)
    ai_resolution_description: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),nullable=False, default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),nullable=False, default=func.now(), onupdate=func.now())
    resolved_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),nullable=True)
    status: Mapped[TicketStatus] = mapped_column(nullable=False, default=TicketStatus.OPEN)
    priority: Mapped[TicketPriority] = mapped_column( nullable=False, default=TicketPriority.NOT_SPECIFIED)
    category: Mapped[TicketCategory] = mapped_column(nullable=False, default=TicketCategory.NOT_SPECIFIED)
    ai_priority: Mapped[TicketPriority] = mapped_column( nullable=False, default=TicketPriority.NOT_SPECIFIED)
    ai_category: Mapped[TicketCategory] = mapped_column(nullable=False, default=TicketCategory.NOT_SPECIFIED)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_by: Mapped["User"] = relationship("User", back_populates="tickets" )

