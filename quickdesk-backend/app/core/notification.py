import uuid
import asyncio
from app.schemas.notification import Notification

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

    