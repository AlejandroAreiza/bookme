"""API tests for /events, grouped by use case.

Each test gets its own fresh in-memory repository through dependency_overrides,
so tests never share or change the app's sample data.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.events import get_event_repository
from app.db.in_memory_event_repository import InMemoryEventRepository
from app.domain.event import Event
from app.domain.types.venue import Venue, VenueType
from app.main import app

CAPACITY = 2


def create_event(name: str = "Jazz Night", spots_booked: int = 0) -> Event:
    event = Event(
        name=name,
        venue=Venue("Royal Albert Hall", VenueType.CONCERT_HALL),
        starts_at=datetime(2026, 11, 1, 20, 0, tzinfo=UTC),
        capacity=CAPACITY,
    )
    for _ in range(spots_booked):
        event.book_spot()
    return event


def valid_event_body(**changes: Any) -> dict[str, Any]:
    return {
        "name": "Rock Night",
        "venue": {"name": "Teatro de la Comedia", "type": "THEATER"},
        "starts_at": "2026-12-01T21:00:00Z",
        "capacity": 50,
        **changes,
    }


@pytest.fixture
def repository() -> InMemoryEventRepository:
    return InMemoryEventRepository(
        [create_event("Jazz Night"), create_event("Sold Out Show", CAPACITY)]
    )


@pytest.fixture
def client(repository: InMemoryEventRepository) -> Iterator[TestClient]:
    app.dependency_overrides[get_event_repository] = lambda: repository
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestHealth:
    def test_health_check_returns_ok(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestListEvents:
    """Use case: an attendee browses all events."""

    def test_listing_events_returns_every_event(self, client: TestClient) -> None:
        response = client.get("/events")
        assert response.status_code == 200
        names = {event["name"] for event in response.json()}
        assert names == {"Jazz Night", "Sold Out Show"}

    def test_listed_event_shows_availability(self, client: TestClient) -> None:
        events = {event["name"]: event for event in client.get("/events").json()}
        assert events["Jazz Night"]["spots_available"] == CAPACITY
        assert events["Jazz Night"]["sold_out"] is False
        assert events["Sold Out Show"]["spots_available"] == 0
        assert events["Sold Out Show"]["sold_out"] is True

    def test_listing_with_no_events_returns_empty_list(self) -> None:
        app.dependency_overrides[get_event_repository] = InMemoryEventRepository
        try:
            response = TestClient(app).get("/events")
        finally:
            app.dependency_overrides.clear()
        assert response.status_code == 200
        assert response.json() == []


class TestGetEvent:
    """Use case: an attendee opens one event."""

    def test_existing_event_is_returned(
        self, client: TestClient, repository: InMemoryEventRepository
    ) -> None:
        event = repository.get_all()[0]
        response = client.get(f"/events/{event.id}")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == str(event.id)
        assert body["name"] == event.name
        assert body["venue"] == {"name": "Royal Albert Hall", "type": "CONCERT_HALL"}

    def test_unknown_event_returns_404(self, client: TestClient) -> None:
        missing_id = uuid4()
        response = client.get(f"/events/{missing_id}")
        assert response.status_code == 404
        assert response.json() == {"detail": f"Event {missing_id} not found"}

    def test_invalid_id_returns_422(self, client: TestClient) -> None:
        assert client.get("/events/not-a-uuid").status_code == 422


class TestCreateEvent:
    """Use case: an organizer publishes a new event."""

    def test_valid_event_is_created_with_201(self, client: TestClient) -> None:
        response = client.post("/events", json=valid_event_body())
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "Rock Night"
        assert body["spots_available"] == 50
        assert body["sold_out"] is False
        assert "id" in body

    def test_created_event_can_be_retrieved(self, client: TestClient) -> None:
        created = client.post("/events", json=valid_event_body()).json()
        response = client.get(f"/events/{created['id']}")
        assert response.status_code == 200
        assert response.json() == created

    @pytest.mark.parametrize(
        "changes",
        [
            {"name": ""},
            {"capacity": 0},
            {"capacity": -1},
            {"starts_at": "2026-12-01T21:00:00"},
            {"venue": {"name": "Somewhere", "type": "SPACESHIP"}},
        ],
        ids=[
            "empty-name",
            "zero-capacity",
            "negative-capacity",
            "start-time-without-timezone",
            "unknown-venue-type",
        ],
    )
    def test_invalid_event_is_rejected_with_422(
        self, client: TestClient, changes: dict[str, Any]
    ) -> None:
        response = client.post("/events", json=valid_event_body(**changes))
        assert response.status_code == 422

    def test_rejected_event_is_not_saved(
        self, client: TestClient, repository: InMemoryEventRepository
    ) -> None:
        client.post("/events", json=valid_event_body(capacity=0))
        assert len(repository.get_all()) == 2
