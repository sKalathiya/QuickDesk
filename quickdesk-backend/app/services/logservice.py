from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.schemas.agent_logs import AgentLogResponse
from app.models.agent_logs import AgentLogs
from sqlalchemy import select

async def get_agent_logs(db: AsyncSession, agent_id: uuid.UUID) -> list[AgentLogResponse]:
    stmt = select(AgentLogs).where(AgentLogs.agent_id == agent_id)
    result = (await db.scalars(stmt)).all()
    return [AgentLogResponse.model_validate(log) for log in result]