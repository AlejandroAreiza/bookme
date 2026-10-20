"""Unit tests for the Event entity, grouped by use case.

Naming: Test<UseCase>::test_<scenario>_<expected result>
Rule: bookings are only added through book_spot() and only read through
spots_available / sold_out (never through the private _spots_booked).
"""

from datetime import UTC, datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest

from app.domain.event import Event
from app.domain.exceptions.sold_out_error_exc import SoldOutError
from app.domain.types.venue import Venue, VenueType

VENUE = Venue("Royal Albert Hall", VenueType.CONCERT_HALL)
STARTS_AT = datetime(2026, 11, 1, 20, 0, tzinfo=UTC)
CAPACITY = 2


def create_event(**changes: Any) -> Event:
    data: dict[str, Any] = {
        "name": "Concert",
        "venue": VENUE,
        "starts_at": STARTS_AT,
        "capacity": CAPACITY,
        **changes,
    }
    return Event(**data)


def create_event_with_bookings(spots_booked: int, **changes: Any) -> Event:
    event = create_event(**changes)
    for _ in range(spots_booked):
        event.book_spot()
    return event


class TestCreateEvent:
    """Use case: an organizer publishes a new event."""

    def test_new_event_starts_with_all_spots_available(self) -> None:
        event = create_event()
        assert event.spots_available == CAPACITY
        assert not event.sold_out

    def test_new_event_cannot_be_created_with_spots_booked(self) -> None:
        with pytest.raises(TypeError):
            create_event(_spots_booked=1)

    def test_new_event_gets_a_generated_id(self) -> None:
        assert isinstance(create_event().id, UUID)

    def test_each_new_event_gets_a_different_id(self) -> None:
        ids = {create_event().id for _ in range(5)}
        assert len(ids) == 5

    def test_event_in_any_timezone_is_accepted(self) -> None:
        madrid_summer = timezone(timedelta(hours=2))
        event = create_event(
            starts_at=datetime(2026, 11, 1, 20, 0, tzinfo=madrid_summer)
        )
        assert event.starts_at.tzinfo is madrid_summer

    @pytest.mark.parametrize(
        ("changes", "message"),
        [
            ({"name": ""}, "name cannot be empty"),
            ({"name": "   "}, "name cannot be empty"),
            ({"starts_at": datetime(2026, 11, 1, 20, 0)}, "timezone"),
            ({"capacity": 0}, "capacity"),
            ({"capacity": -1}, "capacity"),
        ],
        ids=[
            "empty-name",
            "blank-name",
            "start-time-without-timezone",
            "zero-capacity",
            "negative-capacity",
        ],
    )
    def test_event_with_invalid_data_is_rejected(
        self, changes: dict[str, Any], message: str
    ) -> None:
        with pytest.raises(ValueError, match=message):
            create_event(**changes)


class TestCheckAvailability:
    """Use case: an attendee checks how many spots are left."""

    @pytest.mark.parametrize(
        ("spots_booked", "expected_available", "expected_sold_out"),
        [(0, 2, False), (1, 1, False), (2, 0, True)],
        ids=["empty-event", "half-full-event", "full-event"],
    )
    def test_available_spots_and_sold_out_reflect_bookings(
        self, spots_booked: int, expected_available: int, expected_sold_out: bool
    ) -> None:
        event = create_event_with_bookings(spots_booked)
        assert event.spots_available == expected_available
        assert event.sold_out is expected_sold_out


class TestBookSpot:
    """Use case: an attendee books a spot."""

    def test_booking_a_spot_reduces_available_spots_by_one(self) -> None:
        event = create_event()
        event.book_spot()
        assert event.spots_available == CAPACITY - 1

    def test_booking_the_last_spot_makes_the_event_sold_out(self) -> None:
        event = create_event_with_bookings(CAPACITY - 1)
        event.book_spot()
        assert event.sold_out

    def test_booking_a_sold_out_event_is_rejected(self) -> None:
        event = create_event_with_bookings(CAPACITY)
        with pytest.raises(SoldOutError, match=str(event.id)):
            event.book_spot()

    def test_rejected_booking_leaves_spots_unchanged(self) -> None:
        event = create_event_with_bookings(CAPACITY)
        with pytest.raises(SoldOutError):
            event.book_spot()
        assert event.spots_available == 0


class TestEventIdentity:
    """Rule: an event is identified by its id, not by its other values."""

    def test_events_with_same_id_are_the_same_event(self) -> None:
        event = create_event()
        same_event_later = create_event_with_bookings(1, id=event.id)
        assert event == same_event_later

    def test_events_with_different_ids_are_different_events(self) -> None:
        assert create_event() != create_event(id=uuid4())

    def test_event_is_never_equal_to_a_non_event(self) -> None:
        event = create_event()
        assert event != event.id

    def test_same_event_counts_once_in_a_set(self) -> None:
        event = create_event()
        same_event_later = create_event_with_bookings(1, id=event.id)
        assert len({event, same_event_later}) == 1
