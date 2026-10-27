from fastapi import APIRouter, Depends
from app.schemas.user import DashBoardResponse, UserResponse
from app.models.user import User
from app.services.userservice import get_dashboard
from app.api.deps import get_current_agent_user, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.agent_logs import AgentLogResponse
from app.services.logservice import get_agent_logs

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/dashboard", response_model=DashBoardResponse)
async def handle_get_dashboard(current_user: User = Depends(get_current_agent_user), db: AsyncSession = Depends(get_db)):
    return await get_dashboard(db)


@router.get("/logs" , response_model=list[AgentLogResponse])
async def handle_get_logs(current_agent: User = Depends(get_current_agent_user), db: AsyncSession = Depends(get_db)):
    return await get_agent_logs(db, current_agent.id)