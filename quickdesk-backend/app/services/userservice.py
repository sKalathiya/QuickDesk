#user service

from sqlalchemy import tuple_
from app.models.user import User
from app.schemas.user import DashBoardResponse
from app.models.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql.functions import func


async def get_dashboard(db: AsyncSession) -> DashBoardResponse:
    stmt = select(
        Ticket.status,
        Ticket.category,
        Ticket.priority,
        func.count(Ticket.id).label("count"),
    ).group_by(
        func.grouping_sets(
            Ticket.status,
            Ticket.category,
            Ticket.priority,
        )
    )
    result = (await db.scalars(stmt)).all()
    total_count = 0
    tickets_by_status = {}
    tickets_by_category = {}
    tickets_by_priority = {}
    for row in result:
        if row.status:
            tickets_by_status[row.status] = row.count
        if row.category:
            tickets_by_category[row.category] = row.count
        if row.priority:
            tickets_by_priority[row.priority] = row.count

    stmt = select(
        func.avg(Ticket.resolved_at - Ticket.created_at).label("average_resolution_time"),
    ).where(Ticket.status == TicketStatus.RESOLVED and Ticket.resolved_at is not None and Ticket.created_at is not None)
    result = (await db.scalar(stmt))
    average_resolution_time = result.total_seconds() if result is not None else 0
        
    return DashBoardResponse.model_validate({
        "total_tickets": total_count,
        "tickets_by_status": tickets_by_status,
        "tickets_by_category": tickets_by_category,
        "tickets_by_priority": tickets_by_priority,
        "average_resolution_time": average_resolution_time,
    })