from app.core.notification import NotificationManager
from app.schemas.notification import Notification
from fastapi.sse import ServerSentEvent
from app.models.user import User
from app.core.database import AsyncSession
import uuid
from app.schemas.auth import Session
from typing import AsyncIterable

async def get_notification(session: Session, manager: NotificationManager) -> AsyncIterable[ServerSentEvent]:
    try:
        user_id = session.user.id
        jti = session.jti
        connection = manager.add_connection(user_id, jti)
        while not connection.closed:
            notification = await connection.queue.get()
            if connection.closed:
                break
            yield ServerSentEvent(data=notification.event.value, event=notification.event, id=str(notification.id))
    finally:
        manager.stop_connection(jti, user_id)