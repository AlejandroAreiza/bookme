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
    seats_booked: int = 0
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name cannot be empty")

        if self.starts_at.tzinfo is None:
            raise ValueError("starts_at must have a timezone")

        if self.capacity <= 0:
            raise ValueError("capacity must be greater than 0")

        if not 0 <= self.seats_booked <= self.capacity:
            raise ValueError(
                "seats_booked is out of range and must be between 0 and capacity"
            )

    @property
    def seats_available(self) -> int:
        return self.capacity - self.seats_booked

    @property
    def is_sold_out(self) -> bool:
        return self.seats_available == 0

    def book_seat(self) -> None:
        if self.is_sold_out:
            raise SoldOutError(f"Event {self.id} is sold out")
        self.seats_booked += 1

    # An Event is an entity: two Event objects are the same event when they
    # have the same id, even if other values (like seats_booked) differ.
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Event):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
