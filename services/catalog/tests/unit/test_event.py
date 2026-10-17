"""Unit tests for the Event entity, grouped by use case.

Naming: Test<UseCase>::test_<scenario>_<expected result>
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


class TestCreateEvent:
    """Use case: an organizer publishes a new event."""

    def test_new_event_starts_with_no_seats_booked(self) -> None:
        event = create_event()
        assert event.seats_booked == 0
        assert event.seats_available == CAPACITY

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
        "seats_booked",
        [0, 1, CAPACITY],
        ids=["no-seats-booked", "some-seats-booked", "all-seats-booked"],
    )
    def test_event_with_seats_booked_within_capacity_is_accepted(
        self, seats_booked: int
    ) -> None:
        assert create_event(seats_booked=seats_booked).seats_booked == seats_booked

    @pytest.mark.parametrize(
        ("changes", "message"),
        [
            ({"name": ""}, "name cannot be empty"),
            ({"name": "   "}, "name cannot be empty"),
            ({"starts_at": datetime(2026, 11, 1, 20, 0)}, "timezone"),
            ({"capacity": 0}, "capacity"),
            ({"capacity": -1}, "capacity"),
            ({"seats_booked": -1}, "seats_booked"),
            ({"seats_booked": CAPACITY + 1}, "seats_booked"),
        ],
        ids=[
            "empty-name",
            "blank-name",
            "start-time-without-timezone",
            "zero-capacity",
            "negative-capacity",
            "negative-seats-booked",
            "more-seats-booked-than-capacity",
        ],
    )
    def test_event_with_invalid_data_is_rejected(
        self, changes: dict[str, Any], message: str
    ) -> None:
        with pytest.raises(ValueError, match=message):
            create_event(**changes)


class TestCheckAvailability:
    """Use case: an attendee checks how many seats are left."""

    @pytest.mark.parametrize(
        ("seats_booked", "expected_available", "expected_sold_out"),
        [(0, 2, False), (1, 1, False), (2, 0, True)],
        ids=["empty-event", "half-full-event", "full-event"],
    )
    def test_available_seats_and_sold_out_reflect_bookings(
        self, seats_booked: int, expected_available: int, expected_sold_out: bool
    ) -> None:
        event = create_event(seats_booked=seats_booked)
        assert event.seats_available == expected_available
        assert event.is_sold_out is expected_sold_out


class TestBookSeat:
    """Use case: an attendee books a seat."""

    def test_booking_a_seat_reduces_available_seats_by_one(self) -> None:
        event = create_event()
        event.book_seat()
        assert event.seats_booked == 1
        assert event.seats_available == CAPACITY - 1

    def test_booking_the_last_seat_makes_the_event_sold_out(self) -> None:
        event = create_event(seats_booked=CAPACITY - 1)
        event.book_seat()
        assert event.is_sold_out

    def test_booking_a_sold_out_event_is_rejected(self) -> None:
        event = create_event(seats_booked=CAPACITY)
        with pytest.raises(SoldOutError, match=str(event.id)):
            event.book_seat()

    def test_rejected_booking_leaves_seats_unchanged(self) -> None:
        event = create_event(seats_booked=CAPACITY)
        with pytest.raises(SoldOutError):
            event.book_seat()
        assert event.seats_booked == CAPACITY


class TestEventIdentity:
    """Rule: an event is identified by its id, not by its other values."""

    def test_events_with_same_id_are_the_same_event(self) -> None:
        event = create_event()
        same_event_later = create_event(id=event.id, seats_booked=1)
        assert event == same_event_later

    def test_events_with_different_ids_are_different_events(self) -> None:
        assert create_event() != create_event(id=uuid4())

    def test_event_is_never_equal_to_a_non_event(self) -> None:
        event = create_event()
        assert event != event.id

    def test_same_event_counts_once_in_a_set(self) -> None:
        event = create_event()
        same_event_later = create_event(id=event.id, seats_booked=1)
        assert len({event, same_event_later}) == 1
