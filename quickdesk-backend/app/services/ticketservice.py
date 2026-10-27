from app.schemas.ticket import TicketCreate, TicketResponse, TicketAgentUpdate, TicketAgentResolve
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ticket import Ticket, TicketStatus
from sqlalchemy import select, func
import uuid
from app.models.user import UserRole
from app.schemas.ticket import TicketFilter, TicketListResponse
from app.models.agent_logs import AgentLogs, _log_type
from app.exceptions.ticket_exceptios import TicketNotFoundException, TicketInvalidIDException, TicketInvalidStatusException
from app.core.notification import NotificationManager
from app.schemas.notification import Notification, NotificationEvent

async def create_ticket(ticket: TicketCreate, user: User, db: AsyncSession, notification_manager: NotificationManager) -> TicketResponse:
    """Insert a ticket for the caller and commit it."""
    try:
        new_ticket = Ticket(
            title=ticket.title,
            description=ticket.description,
            fileName=ticket.fileName if ticket.fileName else None,
            user_id=user.id,
        )
        db.add(new_ticket)
        # Flush to assign an id before the response is built; the commit below persists the row.
        await db.flush()
        await db.refresh(new_ticket)
        ticketResponse = TicketResponse.model_validate(new_ticket)
        await db.commit()
    except Exception:
        # Drop the flushed insert if the response build or the commit fails.
        await db.rollback()
        raise 
    try:
        notification_manager.add_agent_notification(Notification(event=NotificationEvent.TICKET_CREATED))
    except Exception:
        pass
    return ticketResponse
    


async def get_tickets_by_user(user: User, db: AsyncSession) -> list[TicketResponse]:
    tickets = await db.scalars(select(Ticket).where(Ticket.user_id == user.id))
    return [TicketResponse.model_validate(ticket) for ticket in tickets]


async def get_ticket_by_id(ticket_id: str, user: User, db: AsyncSession) -> TicketResponse:
    """Return one ticket, limited to the caller's own row when the caller is an employee."""
    try:
        ticket_id = uuid.UUID(ticket_id)
    except (ValueError, AttributeError) as e:
        raise TicketInvalidIDException("Invalid ticket ID") from e
    # Employees may only read a ticket they opened; other roles may read any ticket.
    if user.role == UserRole.EMPLOYEE:
        stmt = select(Ticket).where(Ticket.id == ticket_id, Ticket.user_id == user.id).limit(1)
    else:
        stmt = select(Ticket).where(Ticket.id == ticket_id).limit(1)
    ticket = await db.scalar(stmt)
    if not ticket:
        raise TicketNotFoundException("Ticket not found")
    return TicketResponse.model_validate(ticket)

async def get_all_tickets(user: User, db: AsyncSession, ticket_filter: TicketFilter) -> TicketListResponse:
    """Return one page of tickets, scoped to the caller when the caller is an employee."""
    # Employees only see their own tickets; other roles see the full list.
    filters = []
    if ticket_filter.category:
        filters.append(Ticket.category == ticket_filter.category)
    if ticket_filter.priority:
        filters.append(Ticket.priority == ticket_filter.priority)
    if ticket_filter.status:
        filters.append(Ticket.status == ticket_filter.status)
    if ticket_filter.title:
        filters.append(Ticket.title.icontains(ticket_filter.title , autoescape=True))
    if user.role == UserRole.EMPLOYEE:
        filters.append(Ticket.user_id == user.id)
    total = await db.scalar(select(func.count()).select_from(Ticket).where(*filters))
    stmt = select(Ticket).where(*filters).order_by(Ticket.created_at.desc() , Ticket.id.desc()).offset(ticket_filter.get_skip()).limit(ticket_filter.page_size)
    tickets = (await db.scalars(stmt)).all()
    return TicketListResponse.model_validate({
        "tickets": [TicketResponse.model_validate(ticket) for ticket in tickets], 
        "total": total, 
        "page": ticket_filter.page, 
        "page_size": ticket_filter.page_size, 
        "has_next": total > ticket_filter.get_skip() + ticket_filter.page_size,
        "has_previous": ticket_filter.page > 1
        })


async def update_ticket_by_agent(ticket_id: str, ticket: TicketAgentUpdate, agent_user: User, db: AsyncSession) -> TicketResponse:
    """Apply an agent's field changes and record each change in the agent log."""
    try:
        try:
            ticket_id = uuid.UUID(ticket_id)
        except (ValueError, AttributeError) as e:
            raise TicketInvalidIDException("Invalid ticket ID") from e
        # Lock the ticket so two agents cannot write it at once.
        stmt  = select(Ticket).where(Ticket.id == ticket_id).limit(1).with_for_update()
        db_ticket = await db.scalar(stmt)
        if not db_ticket:
            raise TicketNotFoundException("Ticket not found")
        log_stmts = []
        for key, value in ticket.model_dump(exclude_unset=True, exclude_none=True).items():
            if value == getattr(db_ticket, key):
                continue
            log_stmts.append(AgentLogs(ticket_id=db_ticket.id, agent_id=agent_user.id, log_type=_log_type(key), old_value=str(getattr(db_ticket, key)), new_value=str(value)))
            setattr(db_ticket, key, value)
        db.add_all(log_stmts)
        await db.flush()
        await db.refresh(db_ticket)
        ticketResponse = TicketResponse.model_validate(db_ticket)
        await db.commit()
        return ticketResponse
    except Exception:
        # Drop the partial log and field writes if any step fails.
        await db.rollback()
        raise
    
        
async def resolve_ticket_by_agent(ticket_id: str, ticket: TicketAgentResolve, agent_user: User, db: AsyncSession, notification_manager: NotificationManager) -> TicketResponse:
    try:
        try:
            ticket_id = uuid.UUID(ticket_id)
        except (ValueError, AttributeError) as e:
            raise TicketInvalidIDException("Invalid ticket ID") from e
        stmt = select(Ticket).where(Ticket.id == ticket_id).limit(1).with_for_update()
        db_ticket = await db.scalar(stmt)
        if not db_ticket:
            raise TicketNotFoundException("Ticket not found")
        if db_ticket.status != TicketStatus.OPEN:
            raise TicketInvalidStatusException("Ticket is not open")
        log_stmt = AgentLogs(ticket_id=db_ticket.id, agent_id=agent_user.id, log_type=_log_type("resolutionDescription"), old_value=str(db_ticket.resolutionDescription), new_value=str(ticket.resolutionDescription))
        db.add(log_stmt)
        db_ticket.resolutionDescription = ticket.resolutionDescription
        db_ticket.resolved_at= func.now()
        db_ticket.status = TicketStatus.RESOLVED
        await db.flush()
        await db.refresh(db_ticket)
        ticketResponse = TicketResponse.model_validate(db_ticket)
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    try:
        notification_manager.add_employee_notification(db_ticket.user_id, Notification(event=NotificationEvent.TICKET_RESOLVED))
    except Exception:
        pass
    return ticketResponse