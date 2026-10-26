from fastapi import APIRouter
from app.schemas.ticket import TicketResponse, TicketCreate, TicketAgentUpdate, TicketAgentResolve
from fastapi import status
from app.services.ticketservice import create_ticket
from app.api.deps import get_current_agent_user, get_db, Pagination
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.models.user import User
from app.api.deps import get_current_user, get_current_employee_user
from app.services.ticketservice import create_ticket, get_ticket_by_id, get_all_tickets, update_ticket_by_agent, resolve_ticket_by_agent
from app.exceptions.ticket_exceptios import TicketInvalidIDException, TicketNotFoundException, TicketInvalidStatusException
from fastapi import HTTPException


router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("/" , status_code=status.HTTP_201_CREATED, response_model=TicketResponse)
async def handle_create_ticket(ticket: TicketCreate, user: User = Depends(get_current_employee_user), db: AsyncSession = Depends(get_db)) -> TicketResponse:
    """Create a ticket for the signed-in employee."""
    try:
        return await create_ticket(ticket, user, db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get("/{ticket_id}", status_code=status.HTTP_200_OK, response_model=TicketResponse)
async def handle_get_ticket(ticket_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> TicketResponse:
    """Return one ticket for the current user."""
    try:
        return await get_ticket_by_id(ticket_id, user, db)
    except TicketInvalidIDException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e
    except TicketNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise 

@router.get("/", status_code=status.HTTP_200_OK, response_model=list[TicketResponse])
async def handle_get_all_tickets(pagination: Pagination = Depends(), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[TicketResponse]:
    """Return one page of tickets for the current user."""
    return await get_all_tickets(user, db, pagination)
   

@router.put("/agent/update/{ticket_id}", status_code=status.HTTP_200_OK, response_model=TicketResponse)
async def handle_agent_update_ticket(ticket_id: str, ticket: TicketAgentUpdate, user: User = Depends(get_current_agent_user), db: AsyncSession = Depends(get_db)) -> TicketResponse:
    try:
        return await update_ticket_by_agent(ticket_id, ticket, user, db)
    except TicketInvalidIDException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e
    except TicketNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise 

@router.put("/agent/resolve/{ticket_id}", status_code=status.HTTP_200_OK, response_model=TicketResponse)
async def handle_agent_resolve_ticket(ticket_id: str, ticket: TicketAgentResolve, agent_user: User = Depends(get_current_agent_user), db: AsyncSession = Depends(get_db)) -> TicketResponse:
    """Resolve a ticket for the signed-in agent. Rejects an invalid ticket status."""
    try:
        return await resolve_ticket_by_agent(ticket_id, ticket, agent_user, db)
    except TicketInvalidIDException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e
    except TicketNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except TicketInvalidStatusException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e
    except Exception as e:
        raise 
