from app.schemas.ticket import TicketCreate, TicketResponse
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ticket import Ticket
from sqlalchemy import select
from fastapi import HTTPException
from fastapi import status
import uuid


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
    return TicketResponse.model_validate(new_ticket)


async def get_tickets_by_user(user: User, db: AsyncSession) -> list[TicketResponse]:
    result = await db.execute(select(Ticket).where(Ticket.user_id == user.id))
    tickets = result.scalars().all()

    return [TicketResponse.model_validate(ticket) for ticket in tickets]


async def get_ticket_by_id_and_user(ticket_id: str, user: User, db: AsyncSession) -> TicketResponse:
    try:
        ticket_id = uuid.UUID(ticket_id)
    except (ValueError, AttributeError) as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Invalid ticket ID") from e
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id, Ticket.user_id == user.id).limit(1))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return TicketResponse.model_validate(ticket)

