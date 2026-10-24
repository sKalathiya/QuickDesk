from fastapi import APIRouter
from app.schemas.ticket import TicketResponse, TicketCreate
from fastapi import status
from app.services.ticketservice import create_ticket
from app.api.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.models.user import User
from app.api.deps import get_current_user, get_current_employee_user
from app.services.ticketservice import create_ticket, get_ticket_by_id

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("/" , status_code=status.HTTP_201_CREATED, response_model=TicketResponse)
async def handle_create_ticket(ticket: TicketCreate, user: User = Depends(get_current_employee_user), db: AsyncSession = Depends(get_db)) -> TicketResponse:
    return await create_ticket(ticket, user, db)


@router.get("/{ticket_id}", status_code=status.HTTP_200_OK, response_model=TicketResponse)
async def handle_get_ticket(ticket_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> TicketResponse:
    return await get_ticket_by_id(ticket_id, user, db)