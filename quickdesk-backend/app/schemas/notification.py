from enum import StrEnum
import uuid
from pydantic import BaseModel, Field


class NotificationEvent(StrEnum):
    TICKET_CREATED = "TICKET_CREATED"
    TICKET_RESOLVED = "TICKET_RESOLVED"


class Notification(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event: NotificationEvent