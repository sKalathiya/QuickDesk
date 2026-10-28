import datetime
from sqlalchemy import UUID, Column, ForeignKey, Integer, String, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from enum import StrEnum
from app.core.database import Base
from sqlalchemy.types import TIMESTAMP

class LogType(StrEnum):
    CATEGORY_CHANGE = "CATEGORY_CHANGE"
    PRIORITY_CHANGE = "PRIORITY_CHANGE"
    RESOLUTION_DESCRIPTION_CHANGE = "RESOLUTION_DESCRIPTION_CHANGE"

def _log_type(field: str) -> LogType:
    """Map a changed ticket field name to its agent-log type."""
    if field == "category":
        return LogType.CATEGORY_CHANGE
    elif field == "priority":
        return LogType.PRIORITY_CHANGE
    elif field == "resolutionDescription":
        return LogType.RESOLUTION_DESCRIPTION_CHANGE


class AgentLogs(Base):
    __tablename__ = "agent_logs"
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"))
    ticket_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("tickets.id"))
    log_type: Mapped[LogType] = mapped_column(nullable=False)
    old_value: Mapped[str] = mapped_column(String, nullable=True)
    new_value: Mapped[str] = mapped_column(String, nullable=True)
    ai_override: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=func.now())

    