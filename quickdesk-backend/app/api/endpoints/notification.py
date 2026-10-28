from fastapi import APIRouter
from fastapi.sse import EventSourceResponse
from fastapi import Depends
from starlette.status import HTTP_403_FORBIDDEN
from typing import AsyncIterable
from app.api.deps import get_notification_manager
from fastapi.sse import ServerSentEvent
from app.core.notification import NotificationManager
from app.schemas.auth import Session
from app.api.deps import get_current_user
from app.services.notificationservice import get_notification, get_notification_connection
from app.models.user import UserRole
from fastapi import HTTPException
from app.api.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/agent/stream" , response_class=EventSourceResponse)
async def handle_get_agent_notifications(session: Session = Depends(get_current_user), notification_manager: NotificationManager = Depends(get_notification_manager), db: AsyncSession = Depends(get_db)) -> AsyncIterable[ServerSentEvent]:
    if session.user_role != UserRole.AGENT:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden")
    connection = await get_notification_connection(session, notification_manager, db)
    try:    
        async for event in get_notification(connection):
            yield event
    finally:
        if notification_manager.check_is_connected(connection.id, session.user_id, session.user_role):
            notification_manager.remove_connection(connection.id, session.user_id, session.user_role)
    
@router.get("/employee/stream" , response_class=EventSourceResponse)
async def handle_get_employee_notifications(session: Session = Depends(get_current_user), notification_manager: NotificationManager = Depends(get_notification_manager), db: AsyncSession = Depends(get_db)) -> AsyncIterable[ServerSentEvent]:
    if session.user_role != UserRole.EMPLOYEE:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden")
    connection = await get_notification_connection(session, notification_manager, db)
    try:    
        async for event in get_notification(connection):
            yield event
    finally:
        if notification_manager.check_is_connected(connection.id, session.user_id, session.user_role):
            notification_manager.remove_connection(connection.id, session.user_id, session.user_role)