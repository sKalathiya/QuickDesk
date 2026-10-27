from fastapi import APIRouter, Depends
from app.schemas.user import DashBoardResponse, UserResponse
from app.models.user import User
from app.services.userservice import get_dashboard
from app.api.deps import get_current_agent_user, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/dashboard", response_model=DashBoardResponse)
async def handle_get_dashboard(current_user: User = Depends(get_current_agent_user), db: AsyncSession = Depends(get_db)):
    return await get_dashboard(db)
