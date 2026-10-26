from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from app.models.ticket import TicketStatus, TicketPriority, TicketCategory
from datetime import datetime
import uuid
from app.schemas.user import UserResponse

class TicketBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True, extra="forbid")
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    fileName: Optional[str] = Field(default=None, min_length=1, max_length=255)


class TicketCreate(TicketBase):
    pass

class TicketUpdate(TicketBase):
    pass

class TicketAgentUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True, extra="forbid")
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None

class TicketAgentResolve(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True, extra="forbid")
    resolutionDescription: str = Field(..., min_length=1, max_length=4000)

class TicketResponse(TicketBase):
    id: uuid.UUID
    status: TicketStatus
    priority: TicketPriority
    category: TicketCategory
    resolutionDescription: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

class TicketWithUser(TicketResponse):
    created_by: UserResponse


class TicketFilter(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True, extra="forbid")
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    page: int = Field(ge=1, le=1000)
    page_size: Optional[int] = Field(default=10, ge=1, le=100)

    def get_skip(self) -> int:
        return (self.page - 1) * self.page_size

class TicketListResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True, extra="forbid")
    tickets: list[TicketResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool