#user service

from app.models.user import User
from app.schemas.user import DashBoardResponse
from app.models.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import statistics


async def get_dashboard(db: AsyncSession) -> DashBoardResponse:
    tickets = (await db.scalars(select(Ticket))).all()
    median_resolution_time = statistics.median([(ticket.resolved_at - ticket.created_at).total_seconds() for ticket in tickets if ticket.status == TicketStatus.RESOLVED])
    return DashBoardResponse.model_validate({
        "total_tickets": len(tickets),
        "tickets_by_category": {category: len([ticket for ticket in tickets if ticket.category == category]) for category in TicketCategory},  
        "tickets_by_priority": {priority: len([ticket for ticket in tickets if ticket.priority == priority]) for priority in TicketPriority},
        "tickets_by_status": {status: len([ticket for ticket in tickets if ticket.status == status]) for status in TicketStatus},
        "median_resolution_time": median_resolution_time
    })