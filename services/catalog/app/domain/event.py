from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.domain.exceptions.sold_out_error_exc import SoldOutError
from app.domain.types.venue import Venue


@dataclass(kw_only=True, slots=True, eq=False)
class Event:
    name: str
    venue: Venue
    starts_at: datetime
    capacity: int
    _spots_booked: int = field(default=0, init=False, repr=False)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name cannot be empty")

        if self.starts_at.tzinfo is None:
            raise ValueError("starts_at must have a timezone")

        if self.capacity <= 0:
            raise ValueError("capacity must be greater than 0")

    @property
    def spots_available(self) -> int:
        return self.capacity - self._spots_booked

    @property
    def sold_out(self) -> bool:
        return self.spots_available == 0

    def book_spot(self) -> None:
        if self.sold_out:
            raise SoldOutError(f"Event {self.id} is sold out")
        self._spots_booked += 1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Event):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
