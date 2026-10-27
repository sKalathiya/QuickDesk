import uuid
import asyncio

from dataclasses import dataclass
from app.schemas.notification import Notification

@dataclass
class SSEConnection:
    closed: bool = False
    jti: uuid.UUID
    queue: asyncio.Queue[Notification]

class NotificationManager:

    def __init__(self, max_history_length: int = 100):
        if max_history_length <= 0:
            raise ValueError("max_history_length must be greater than 0")
        self.max_history_length = max_history_length
        self.connection_map: dict[uuid.UUID, list[SSEConnection]] = {}
    
    def add_connection(self, user_id: uuid.UUID, jti: uuid.UUID) -> SSEConnection:
        client_queue = asyncio.Queue[Notification](maxsize=self.max_history_length)
        sseConnection = SSEConnection(jti=jti, queue=client_queue)
        if user_id not in self.connection_map:
            self.connection_map[user_id] = [sseConnection]
        else:
            self.connection_map.get(user_id).append(sseConnection)
        return sseConnection

    def remove_connection(self, jti: uuid.UUID, user_id: uuid.UUID):
        if user_id in self.connection_map:
            match = next((connection for connection in self.connection_map.get(user_id, []) if connection.jti == jti), None)
            if match:
                self.connection_map[user_id].remove(match)
            if len(self.connection_map.get(user_id, [])) == 0:
                del self.connection_map[user_id]

    @staticmethod
    def _publish(notification: Notification, queue: asyncio.Queue[Notification]):
        try:
            queue.put_nowait(notification)
        except asyncio.QueueFull:
            queue.get_nowait()
            queue.put_nowait(notification)
    
    @staticmethod
    def _stop(connection: SSEConnection):
        connection.queue.shutdown(immediate=True)
        connection.closed = True
    
    def add_agent_notification(self, notification: Notification):
        for _, connections in self.connection_map.items():
            for connection in connections:
                self._publish(notification, connection.queue)
                
    def add_employee_notification(self, user_id: uuid.UUID, notification: Notification):
        for connection in self.connection_map.get(user_id, []):
            self._publish(notification, connection.queue)
    
    def check_is_connected(self, user_id: uuid.UUID, jti: uuid.UUID) -> bool:
        return any(connection.jti == jti for connection in self.connection_map.get(user_id, []))

    def close(self):
        for _, connections in self.connection_map.items():
            for connection in connections:
                connection.queue.shutdown(immediate=True)
        self.connection_map.clear()

    def stop_connection(self, jti: uuid.UUID, user_id: uuid.UUID):
        for connection in self.connection_map.get(user_id, []):
            if connection.jti == jti:
                self._stop(connection)
                self.remove_connection(connection.jti, user_id=user_id)

    