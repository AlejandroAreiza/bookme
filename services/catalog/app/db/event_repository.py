from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.event import Event


class EventRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Event]: ...

    @abstractmethod
    def get_by_id(self, event_id: UUID) -> Event | None: ...

    @abstractmethod
    def add(self, event: Event) -> Event: ...

    @abstractmethod
    def remove(self, event_id: UUID) -> None: ...
