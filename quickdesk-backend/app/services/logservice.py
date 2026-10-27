from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.schemas.agent_logs import AgentLogResponse
from app.models.agent_logs import AgentLogs
from sqlalchemy import select
from app.exceptions.ticket_exceptios import TicketInvalidIDException

async def get_ticket_logs(db: AsyncSession, ticket_id: uuid.UUID) -> list[AgentLogResponse]:
    try:
        ticket_id = uuid.UUID(ticket_id)
    except (ValueError, AttributeError) as e:
        raise TicketInvalidIDException("Invalid ticket ID") from e
    stmt = select(AgentLogs).where(AgentLogs.ticket_id == ticket_id).order_by(AgentLogs.created_at.desc(), AgentLogs.id.desc())
    result = (await db.scalars(stmt)).all()
    return [AgentLogResponse.model_validate(log) for log in result]