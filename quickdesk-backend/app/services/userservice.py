#user service

from sqlalchemy import tuple_
from app.models.user import User
from app.schemas.user import DashBoardResponse
from app.models.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql.functions import func
from app.models.agent_logs import AgentLogs
from sqlalchemy import or_


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
    tickets_by_status = {
        status: 0 for status in TicketStatus
    }
    tickets_by_category = {
        category: 0 for category in TicketCategory
    }
    tickets_by_priority = {
        priority: 0 for priority in TicketPriority
    }
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

    stmt = select(func.count(AgentLogs.id).label("total_logs_overridden")).where(AgentLogs.ai_override == True)
    result = (await db.scalar(stmt))
    total_logs_overridden = result if result is not None else 0
    stmt = select(func.count(Ticket.id).label("total_tickets_overridden")).where(or_(Ticket.ai_category.isnot(TicketCategory.NOT_SPECIFIED), Ticket.ai_priority.isnot(TicketPriority.NOT_SPECIFIED)))
    result = (await db.scalar(stmt))
    total_tickets_classified_by_ai = result if result is not None else 0
    agent_overridden_tickets_percentage = (total_logs_overridden / total_tickets_classified_by_ai) * 100 if total_tickets_classified_by_ai > 0 else 0
    return DashBoardResponse.model_validate({
        "total_tickets": total_count,
        "tickets_by_status": tickets_by_status,
        "tickets_by_category": tickets_by_category,
        "tickets_by_priority": tickets_by_priority,
        "median_resolution_time": median_resolution_time,
        "agent_overridden_tickets_percentage": agent_overridden_tickets_percentage,
    })