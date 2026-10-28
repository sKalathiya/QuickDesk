from asyncio import QueueShutDown
from app.core.notification import SSEConnection
from fastapi.sse import ServerSentEvent
from typing import AsyncIterable
from app.core.notification import NotificationManager
from app.schemas.auth import Session
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

async def get_notification(connection: SSEConnection) -> AsyncIterable[ServerSentEvent]:
    while not connection.closed:
        try:
            notification = await connection.queue.get()
            yield ServerSentEvent(data=notification.event.value, event=notification.event, id=str(notification.id))
        except QueueShutDown:
            break

async def get_notification_connection(session: Session, notification_manager: NotificationManager) -> SSEConnection:
    user_id = session.user_id
    role = session.user_role
    jti = session.jti
    connection = notification_manager.add_connection(user_id, role, jti)
    if connection is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Failed to add connection")
    return connection