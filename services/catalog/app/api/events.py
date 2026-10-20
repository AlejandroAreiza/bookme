from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.db.event_repository import EventRepository
from app.db.in_memory_event_repository import InMemoryEventRepository
from app.db.sample_events import create_sample_events
from app.schemas.event import EventCreate, EventResponse

router = APIRouter(prefix="/events", tags=["events"])


event_repository: EventRepository = InMemoryEventRepository(create_sample_events())


def get_event_repository() -> EventRepository:
    return event_repository


RepositoryDep = Annotated[EventRepository, Depends(get_event_repository)]


@router.get("")
def list_events(
    repository: RepositoryDep,
) -> list[EventResponse]:
    return [EventResponse.model_validate(event) for event in repository.get_all()]


@router.get("/{event_id}")
def get_event(
    event_id: UUID,
    repository: RepositoryDep,
) -> EventResponse:
    event = repository.get_by_id(event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found",
        )
    return EventResponse.model_validate(event)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_event(
    body: EventCreate,
    repository: RepositoryDep,
) -> EventResponse:
    event = body.to_domain()
    repository.add(event)
    return EventResponse.model_validate(event)
