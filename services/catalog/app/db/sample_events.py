from datetime import UTC, datetime

from app.domain.event import Event
from app.domain.types.venue import Venue, VenueType


def create_sample_events() -> list[Event]:
    CAPACITY = 10
    empty_event = Event(
        name="CODE",
        venue=Venue("The outstanding FABRIC Club", VenueType.CLUB),
        starts_at=datetime(2026, 11, 1, 20, 0, tzinfo=UTC),
        capacity=CAPACITY,
    )

    spots_left_event = Event(
        name="America's Got Talent",
        venue=Venue("Teatro de la Comedia", VenueType.THEATER),
        starts_at=datetime(2026, 11, 1, 20, 0, tzinfo=UTC),
        capacity=CAPACITY,
    )
    for _ in range(CAPACITY - 5):
        spots_left_event.book_spot()

    sold_out_event = Event(
        name="LMYLMF Shakira",
        venue=Venue("Iberdrola Music", VenueType.STADIUM),
        starts_at=datetime(2026, 11, 1, 20, 0, tzinfo=UTC),
        capacity=CAPACITY,
    )
    for _ in range(CAPACITY):
        sold_out_event.book_spot()

    return [empty_event, spots_left_event, sold_out_event]
