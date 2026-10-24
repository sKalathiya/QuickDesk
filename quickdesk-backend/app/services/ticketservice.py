from app.schemas.ticket import TicketCreate, TicketResponse
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ticket import Ticket
from sqlalchemy import select
from fastapi import HTTPException
from fastapi import status
import uuid
from app.models.user import UserRole
from app.api.deps import Pagination


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
    tickets = await db.scalars(select(Ticket).where(Ticket.user_id == user.id))
    return [TicketResponse.model_validate(ticket) for ticket in tickets]


async def get_ticket_by_id(ticket_id: str, user: User, db: AsyncSession) -> TicketResponse:
    try:
        ticket_id = uuid.UUID(ticket_id)
    except (ValueError, AttributeError) as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Invalid ticket ID") from e
    if user.role == UserRole.EMPLOYEE:
        stmt = select(Ticket).where(Ticket.id == ticket_id, Ticket.user_id == user.id).limit(1)
    else:
        stmt = select(Ticket).where(Ticket.id == ticket_id).limit(1)
    ticket = await db.scalar(stmt)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return TicketResponse.model_validate(ticket)

async def get_all_tickets(user: User, db: AsyncSession, pagination: Pagination) -> list[TicketResponse]:
    if user.role == UserRole.EMPLOYEE:
        stmt = select(Ticket).where(Ticket.user_id == user.id).offset(pagination.get_skip()).limit(pagination.get_limit())
    else:
        stmt = select(Ticket).offset(pagination.get_skip()).limit(pagination.get_limit())
    tickets = await db.scalars(stmt)
    return [TicketResponse.model_validate(ticket) for ticket in tickets]