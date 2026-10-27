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
            tuple_(),
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
        if row.status is None and row.category is None and row.priority is None:
            total_count = row.count
        elif row.status:
            tickets_by_status[row.status] = row.count
        elif row.category:
            tickets_by_category[row.category] = row.count
        elif row.priority:
            tickets_by_priority[row.priority] = row.count

    interval = Ticket.resolved_at - Ticket.created_at
    interval_seconds = func.extract('epoch', interval)
    stmt = select(
        func.percentile_cont(0.5).within_group(interval_seconds).label("median_resolution_time"),
    ).where(Ticket.status == TicketStatus.RESOLVED , Ticket.resolved_at.isnot(None) , Ticket.created_at.isnot(None))
    result = (await db.scalar(stmt))
    median_resolution_time = result if result is not None else 0
        
    return DashBoardResponse.model_validate({
        "total_tickets": total_count,
        "tickets_by_status": tickets_by_status,
        "tickets_by_category": tickets_by_category,
        "tickets_by_priority": tickets_by_priority,
        "median_resolution_time": median_resolution_time,
    })