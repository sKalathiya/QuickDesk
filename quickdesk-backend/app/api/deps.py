#dependencies for the application

from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.convertors import T
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_422_UNPROCESSABLE_CONTENT
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from fastapi import Cookie, Depends
from app.core.security import get_user_id_from_access_token
import asyncio
import uuid
from app.exceptions.auth_exceptions import UnauthorizedException, InvalidUserIDException, TokenMissingException
from app.schemas.notification import Notification
from starlette.requests import Request

async def get_db():
    async with SessionLocal() as db:
        yield db    

async def get_current_user(access_token: str = Cookie(default=None), db: AsyncSession = Depends(get_db)) -> User:
    """Return the active user identified by the access-token cookie."""
    try:
        if not access_token:
            raise TokenMissingException("Unauthorized")
        user_id = uuid.UUID(get_user_id_from_access_token(access_token))
        result = await db.execute(select(User).where(User.id == user_id).limit(1))
        user = result.scalar_one_or_none()
        # Inactive accounts use the same unauthorized error as an unknown id.
        if not user or not user.isActive:
            raise InvalidUserIDException("Unauthorized")
        return user
    except UnauthorizedException as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED , detail=str(e)) from e


async def get_current_agent_user(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.AGENT:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN , detail="Forbidden")
    return user

async def get_current_employee_user(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.EMPLOYEE:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN , detail="Forbidden")
    return user


class NotificationManager:

    def __init__(self, max_history_length: int = 100):
        if max_history_length <= 0:
            raise ValueError("max_history_length must be greater than 0")
        self.max_history_length = max_history_length
        self.connection_map: dict[uuid.UUID, list[tuple[uuid.UUID, asyncio.Queue]]] = {}
    
    def add_connection(self, user_id: uuid.UUID, connection_id: uuid.UUID) -> asyncio.Queue:
        client_queue = asyncio.Queue(maxsize=self.max_history_length)
        if user_id not in self.connection_map:
            self.connection_map[user_id] = [(connection_id, client_queue)]
        else:
            self.connection_map.get(user_id).append((connection_id, client_queue))
        return client_queue

    def remove_connection(self, connection_id: uuid.UUID, user_id: uuid.UUID):
        if user_id in self.connection_map:
            match = next((connection for connection in self.connection_map.get(user_id, []) if connection[0] == connection_id), None)
            if match:
                self.connection_map[user_id].remove(match)
            if len(self.connection_map.get(user_id, [])) == 0:
                del self.connection_map[user_id]
    
    def add_agent_notification(self, notification: Notification):
        for _, connections in self.connection_map.items():
            for _, queue in connections:
                try:
                    queue.put_nowait(notification)
                except asyncio.QueueFull:
                    queue.get_nowait()
                    queue.put_nowait(notification)
                
    def add_employee_notification(self, user_id: uuid.UUID, notification: Notification):
        for _, queue in self.connection_map.get(user_id, []):
            try:
                queue.put_nowait(notification)
            except asyncio.QueueFull:
                queue.get_nowait()
                queue.put_nowait(notification)
    
    def check_is_connected(self, user_id: uuid.UUID, connection_id: uuid.UUID) -> bool:
        return any(connection[0] == connection_id for connection in self.connection_map.get(user_id, []))

    def close(self):
        for _, connections in self.connection_map.items():
            for _, queue in connections:
                queue.shutdown(immediate=True)
        self.connection_map.clear()

    


async def get_agent_notification_manager(request: Request) -> NotificationManager:
    return request.app.state.agent_notification_manager

async def get_employee_notification_manager(request: Request) -> NotificationManager:
    return request.app.state.employee_notification_manager
