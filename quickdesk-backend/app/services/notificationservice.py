from asyncio import QueueShutDown
from app.core.notification import SSEConnection
from fastapi.sse import ServerSentEvent
from typing import AsyncIterable
from app.core.notification import NotificationManager
from app.schemas.auth import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.token_deny_list import TokenDenyList
from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST

async def get_notification(connection: SSEConnection) -> AsyncIterable[ServerSentEvent]:
    while not connection.closed:
        try:
            notification = await connection.queue.get()
            yield ServerSentEvent(data=notification.data, event=notification.event, id=str(notification.id))
        except QueueShutDown:
            break

async def get_notification_connection(session: Session, notification_manager: NotificationManager, db: AsyncSession) -> SSEConnection:
    user_id = session.user_id
    role = session.user_role
    jti = session.jti
    revoked_tokens = await db.scalar(select(TokenDenyList).where(TokenDenyList.jti == jti))
    if revoked_tokens is not None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token revoked")
    await db.close()
    connection = notification_manager.add_connection(user_id, role, jti)
    if connection is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Failed to add connection")
    return connection