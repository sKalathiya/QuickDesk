from fastapi import APIRouter
from app.schemas.ticket import TicketResponse, TicketCreate, TicketAgentUpdate, TicketAgentResolve
from fastapi import status
from app.services.ticketservice import create_ticket
from app.api.deps import get_current_agent_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.models.user import User
from app.api.deps import get_current_user, get_current_employee_user
from app.services.ticketservice import create_ticket, get_ticket_by_id, get_all_tickets, update_ticket_by_agent, resolve_ticket_by_agent
from app.exceptions.ticket_exceptios import TicketInvalidIDException, TicketNotFoundException, TicketInvalidStatusException
from fastapi import HTTPException
from app.schemas.ticket import TicketFilter, TicketListResponse
from typing import Annotated
from fastapi import Query
from app.api.deps import get_employee_notification_manager, get_agent_notification_manager
from app.core.notification import NotificationManager
from app.schemas.auth import Session


router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("/" , status_code=status.HTTP_201_CREATED, response_model=TicketResponse)
async def handle_create_ticket(ticket: TicketCreate, user: User = Depends(get_current_employee_user), db: AsyncSession = Depends(get_db), notification_manager: NotificationManager = Depends(get_agent_notification_manager)) -> TicketResponse:
    """Create a ticket for the signed-in employee."""
    return await create_ticket(ticket, user, db, notification_manager)
   


@router.get("/{ticket_id}", status_code=status.HTTP_200_OK, response_model=TicketResponse)
async def handle_get_ticket(ticket_id: str, session: Session = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> TicketResponse:
    """Return one ticket for the current user."""
    try:
        return await get_ticket_by_id(ticket_id, session.user, db)
    except TicketInvalidIDException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e
    except TicketNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

@router.get("/", status_code=status.HTTP_200_OK, response_model=TicketListResponse)
async def handle_get_all_tickets(ticket_filter: Annotated[TicketFilter, Query()], session: Session = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> TicketListResponse:
    """Return one page of tickets for the current user."""
    return await get_all_tickets(session.user, db, ticket_filter)
   

@router.put("/agent/update/{ticket_id}", status_code=status.HTTP_200_OK, response_model=TicketResponse)
async def handle_agent_update_ticket(ticket_id: str, ticket: TicketAgentUpdate, user: User = Depends(get_current_agent_user), db: AsyncSession = Depends(get_db)) -> TicketResponse:
    try:
        return await update_ticket_by_agent(ticket_id, ticket, user, db)
    except TicketInvalidIDException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e
    except TicketNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

@router.put("/agent/resolve/{ticket_id}", status_code=status.HTTP_200_OK, response_model=TicketResponse)
async def handle_agent_resolve_ticket(ticket_id: str, ticket: TicketAgentResolve, agent_user: User = Depends(get_current_agent_user), db: AsyncSession = Depends(get_db), notification_manager: NotificationManager = Depends(get_employee_notification_manager)) -> TicketResponse:
    """Resolve a ticket for the signed-in agent. Rejects an invalid ticket status."""
    try:
        return await resolve_ticket_by_agent(ticket_id, ticket, agent_user, db, notification_manager)
    except TicketInvalidIDException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e
    except TicketNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except TicketInvalidStatusException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e
