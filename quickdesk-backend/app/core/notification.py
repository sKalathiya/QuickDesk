import uuid
import asyncio

from dataclasses import dataclass, field
from app.schemas.notification import Notification
from app.models.user import UserRole


@dataclass
class SSEConnection:
    jti: uuid.UUID
    queue: asyncio.Queue[Notification]
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    closed: bool = False

class NotificationManager:

    def __init__(self, max_queue_size: int = 100, max_connection_size: int = 10):
        if max_queue_size <= 0:
            raise ValueError("max_queue_size must be greater than 0")
        self.max_queue_size = max_queue_size
        if max_connection_size <= 0:
            raise ValueError("max_connection_size must be greater than 0")
        self.max_connection_size = max_connection_size
        self.connection_map: dict[UserRole, dict[uuid.UUID, list[SSEConnection]]] = {role: {} for role in UserRole}
    
    def add_connection(self, user_id: uuid.UUID, role: UserRole, jti: uuid.UUID) -> SSEConnection:
        client_queue = asyncio.Queue[Notification](maxsize=self.max_queue_size)
        sseConnection = SSEConnection(jti=jti, queue=client_queue)
        connection_map = self.connection_map.get(role)
        if connection_map is None:
            return None
        if user_id not in connection_map:
            connection_map[user_id] = [sseConnection]
        else:
            if len(connection_map[user_id]) >= self.max_connection_size:
                return None
            connection_map[user_id].append(sseConnection)
        return sseConnection

    def remove_connection(self, id: uuid.UUID, user_id: uuid.UUID, role: UserRole):
        connection_map = self.connection_map.get(role)
        if not connection_map:
            return
        connections = connection_map.get(user_id)
        if not connections:
            return
        for connection in [c for c in connections if c.id == id]:
            self._stop(connection)
            connections.remove(connection)
        if not connections:
            del connection_map[user_id]
    
    def terminate_connection(self, jti:uuid.UUID, user_id: uuid.UUID, role: UserRole):
        connection_map = self.connection_map.get(role)
        if not connection_map:
            return
        connections = connection_map.get(user_id)
        if not connections:
            return
        for connection in [c for c in connections if c.jti == jti]:
            self._stop(connection)
            connections.remove(connection)
        if not connections:
            del connection_map[user_id]

    @staticmethod
    def _publish(notification: Notification, queue: asyncio.Queue[Notification]):
        try:
            while queue.full():
                queue.get_nowait()
            queue.put_nowait(notification)
        except asyncio.QueueShutDown:
            pass
    
    @staticmethod
    def _stop(connection: SSEConnection):
        connection.queue.shutdown(immediate=True)
        connection.closed = True
    
    def add_agent_notification(self, notification: Notification):
        connection_map = self.connection_map.get(UserRole.AGENT)
        if not connection_map:
            return
        for _, connections in connection_map.items():
            for connection in connections:
                self._publish(notification, connection.queue)
                
    def add_employee_notification(self, user_id: uuid.UUID, notification: Notification):
        connection_map = self.connection_map.get(UserRole.EMPLOYEE)
        if not connection_map:
            return
        connections = connection_map.get(user_id)
        if not connections:
            return
        for connection in connections:
            self._publish(notification, connection.queue)
    
    def check_is_connected(self, id: uuid.UUID, user_id: uuid.UUID, role: UserRole) -> bool:
        connection_map = self.connection_map.get(role)
        if not connection_map:
            return False
        connections = connection_map.get(user_id)
        if not connections:
            return False
        return any(connection.id == id for connection in connections)

    def shutdown(self):
        for role in self.connection_map.keys():
            for _, connections in self.connection_map[role].items():
                for connection in connections:
                    self._stop(connection)
            self.connection_map[role].clear()
