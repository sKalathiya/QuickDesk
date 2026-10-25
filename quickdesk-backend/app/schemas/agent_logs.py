from pydantic import BaseModel, ConfigDict
import uuid
import datetime
from app.models.agent_logs import LogType
from enum import Enum


class AgentLogBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    agent_id: uuid.UUID
    ticket_id: uuid.UUID
    log_type: LogType
    old_value: str | None = None
    new_value: str | None = None

class AgentLogCreate(AgentLogBase):
    pass


class AgentLogResponse(AgentLogBase):
    id: uuid.UUID
    created_at: datetime.datetime