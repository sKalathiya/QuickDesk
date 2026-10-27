from fastapi import APIRouter
from fastapi.responses import EventSourceResponse
from fastapi import Depends
from app.api.deps import get_current_agent_user, get_current_employee_user
from app.models.user import User
from typing import AsyncIterable
from app.api.deps import get_agent_notification_manager, get_employee_notification_manager
from fastapi.sse import ServerSentEvent
from app.api.deps import NotificationManager
from app.services.notificationservice import get_notifications
import uuid
import asyncio

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/agent/stream" , response_class=EventSourceResponse)
async def handle_get_agent_notifications(user: User = Depends(get_current_agent_user), notification_manager: NotificationManager = Depends(get_agent_notification_manager)) -> AsyncIterable[ServerSentEvent]:
    try:
        user_id = user.id
        connection_id = uuid.uuid4()
        client_queue = notification_manager.add_connection(user_id, connection_id)
        while True:
            notification = await client_queue.get()
            yield ServerSentEvent(data=notification.data, event=notification.event, id=str(notification.id))
    finally:
        if notification_manager.check_is_connected(user_id, connection_id):
            notification_manager.remove_connection(connection_id, user_id)
        

@router.get("/employee/stream" , response_class=EventSourceResponse)
async def handle_get_employee_notifications(user: User = Depends(get_current_employee_user), notification_manager: NotificationManager = Depends(get_employee_notification_manager)) -> AsyncIterable[ServerSentEvent]:
    try:
        user_id = user.id
        connection_id = uuid.uuid4()
        client_queue = notification_manager.add_connection(user_id, connection_id)
        while True:
            notification = await client_queue.get()
            yield ServerSentEvent(data=notification.data, event=notification.event, id=str(notification.id))
    finally:
        if notification_manager.check_is_connected(user_id, connection_id):
            notification_manager.remove_connection(connection_id, user_id)