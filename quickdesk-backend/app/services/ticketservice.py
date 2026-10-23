from app.schemas.ticket import TicketCreate, TicketResponse
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ticket import Ticket


async def create_ticket(ticket: TicketCreate, user: User, db: AsyncSession) -> TicketResponse:
    new_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        fileName=ticket.fileName if ticket.fileName else None,
        created_by=user,
    )
    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)
    return TicketResponse(
        id=str(new_ticket.id), 
        title=new_ticket.title, 
        description=new_ticket.description, 
        fileName=new_ticket.fileName if new_ticket.fileName else None, 
        resolutionTime=new_ticket.resolutionTime if new_ticket.resolutionTime else None, 
        resolutionDescription=new_ticket.resolutionDescription if new_ticket.resolutionDescription else None, 
        status=new_ticket.status, 
        priority=new_ticket.priority if new_ticket.priority else None, 
        category=new_ticket.category if new_ticket.category else None, 
        created_at=new_ticket.created_at, 
        updated_at=new_ticket.updated_at,
    )
