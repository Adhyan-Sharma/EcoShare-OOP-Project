"""
Notification and NotificationService hierarchy demonstrating Abstraction and Strategy/Observer Pattern.
Decouples business actions from dispatch channels (Console, In-App Log, Email stub).
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any


class NotificationService(ABC):
    """
    Abstract Service Interface demonstrating Abstraction.
    Allows swapping notification delivery channels without touching business logic.
    """
    @abstractmethod
    def send(self, recipient_name: str, recipient_email: str, message: str) -> bool:
        """Dispatches a notification to the specified recipient."""
        pass


class InMemoryNotificationService(NotificationService):
    """
    Concrete implementation recording notifications in-memory with timestamps,
    ideal for web dashboards, inspection, and lab viva demonstrations.
    """
    def __init__(self):
        self._logs: List[Dict[str, Any]] = []

    def send(self, recipient_name: str, recipient_email: str, message: str) -> bool:
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "recipient_name": recipient_name,
            "recipient_email": recipient_email,
            "message": message
        }
        self._logs.insert(0, record)
        print(f"[EcoShare Notification] To: {recipient_name} ({recipient_email}) -> {message}")
        return True

    def get_recent_notifications(self, limit: int = 15) -> List[Dict[str, Any]]:
        return self._logs[:limit]
