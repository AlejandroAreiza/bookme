from uuid import UUID

from app.db.event_repository import EventRepository
from app.domain.event import Event


class InMemoryEventRepository(EventRepository):
    def __init__(self, events: list[Event] | None = None) -> None:
        self._events: dict[UUID, Event] = {e.id: e for e in events or []}

    def get_all(self) -> list[Event]:
        return list(self._events.values())

    def get_by_id(self, event_id: UUID) -> Event | None:
        return self._events.get(event_id)

    def add(self, event: Event) -> Event:
        self._events[event.id] = event
        return self._events[event.id]

    def remove(self, event_id: UUID) -> None:
        del self._events[event_id]
