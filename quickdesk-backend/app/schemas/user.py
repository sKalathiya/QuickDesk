#Pydantic Schema for user

from app.models.ticket import TicketCategory, TicketPriority, TicketStatus
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole
from datetime import datetime
import uuid

class UserBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True, extra="forbid")
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr

class UserResponse(UserBase):
    id: uuid.UUID
    role: UserRole
    created_at: datetime


class DashBoardResponse(BaseModel):
    total_tickets: int
    tickets_by_category: dict[TicketCategory, int]
    tickets_by_priority: dict[TicketPriority, int]
    tickets_by_status: dict[TicketStatus, int]
    median_resolution_time: float