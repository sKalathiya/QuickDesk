from asyncio import QueueShutDown
from starlette.status import HTTP_400_BAD_REQUEST
from app.core.notification import NotificationManager
from fastapi.sse import ServerSentEvent
from app.schemas.auth import Session
from typing import AsyncIterable
from fastapi import HTTPException

async def get_notification(session: Session, manager: NotificationManager) -> AsyncIterable[ServerSentEvent]:
    try:
        user_id = session.user_id
        jti = session.jti
        role = session.user_role
        connection = manager.add_connection(user_id, role,jti)
        if connection is None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Failed to add connection")
        while not connection.closed:
            try:
                notification = await connection.queue.get()
            except QueueShutDown:
                break
            if connection.closed:
                break
            yield ServerSentEvent(data=notification.event.value, event=notification.event, id=str(notification.id))
    finally:
        if manager.check_is_connected(connection.id, user_id, role):
            manager.remove_connection(connection.id, user_id, role)