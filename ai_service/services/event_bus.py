import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Type

class BusinessEvent:
    """Base class for all business events in the system."""
    def __init__(self, tenant_id: str, event_type: str, data: Dict[str, Any]):
        self.event_id = str(uuid.uuid4())
        self.tenant_id = tenant_id
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "tenant_id": self.tenant_id,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp
        }


class EventSubscriber:
    """Interface for event subscribers."""
    def handle_event(self, event: BusinessEvent) -> None:
        raise NotImplementedError("Subscribers must implement handle_event")


class EventBus:
    """
    Central event bus for the AI Business Operating System.
    Decouples workflow orchestration from downstream side-effects (e.g., Audit, Ledger, Notifications).
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._subscribers = {}  # type: Dict[str, List[EventSubscriber]]
            cls._instance._wildcard_subscribers = []  # type: List[EventSubscriber]
        return cls._instance

    def subscribe(self, event_type: str, subscriber: EventSubscriber) -> None:
        """Subscribe to a specific event type, or '*' for all events."""
        if event_type == "*":
            if subscriber not in self._wildcard_subscribers:
                self._wildcard_subscribers.append(subscriber)
            return

        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if subscriber not in self._subscribers[event_type]:
            self._subscribers[event_type].append(subscriber)

    def publish(self, event: BusinessEvent) -> None:
        """Publish an event to all registered subscribers synchronously."""
        # Notify specific subscribers
        if event.event_type in self._subscribers:
            for sub in self._subscribers[event.event_type]:
                try:
                    sub.handle_event(event)
                except Exception as e:
                    print(f"Error in subscriber {sub.__class__.__name__} handling {event.event_type}: {e}")

        # Notify wildcard subscribers
        for sub in self._wildcard_subscribers:
            try:
                sub.handle_event(event)
            except Exception as e:
                print(f"Error in wildcard subscriber {sub.__class__.__name__} handling {event.event_type}: {e}")

# Global singleton instance
event_bus = EventBus()
