from pydantic import BaseModel
from typing import Optional
from app.models.ticket import TicketStatus, TicketPriority, TicketCategory
from datetime import datetime
import uuid
from app.schemas.user import UserResponse

class TicketBase(BaseModel):
    title: str
    description: str
    fileName: Optional[str] = None


class TicketCreate(TicketBase):
    pass

class TicketUpdate(TicketBase):
    pass

class TicketResponse(TicketBase):
    id: uuid.UUID
    status: TicketStatus
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    resolutionTime: Optional[int] = None
    resolutionDescription: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class TicketWithUser(TicketResponse):
    created_by: UserResponse