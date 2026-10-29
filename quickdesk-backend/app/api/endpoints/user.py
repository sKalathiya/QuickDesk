from fastapi import APIRouter, Depends
from app.schemas.user import DashBoardResponse, UserResponse
from app.models.user import User
from app.services.userservice import get_dashboard
from app.api.deps import get_current_agent_user, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.agent_logs import AgentLogResponse
from app.services.logservice import get_ticket_logs
import uuid
from app.schemas.auth import Session
from app.exceptions.ticket_exceptios import TicketInvalidIDException
from fastapi import HTTPException
from starlette import status
from sqlalchemy import select

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/dashboard", response_model=DashBoardResponse)
async def handle_get_dashboard(session: Session = Depends(get_current_agent_user), db: AsyncSession = Depends(get_db)):
    return await get_dashboard(db)


@router.get("/logs/{ticket_id}" , response_model=list[AgentLogResponse])
async def handle_get_logs(ticket_id: str, session: Session = Depends(get_current_agent_user), db: AsyncSession = Depends(get_db)):
    try:
        return await get_ticket_logs(db, ticket_id)
    except TicketInvalidIDException as e: 
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e

@router.get("/current-user", response_model=UserResponse)
async def handle_get_current_user(session: Session = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == session.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)