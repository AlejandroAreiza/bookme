from datetime import datetime
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.domain.event import Event
from app.domain.types.venue import Venue, VenueType

# ---------- Responses (domain → JSON) ----------


class VenueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    type: VenueType


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    venue: VenueResponse
    starts_at: datetime
    capacity: int
    spots_available: int
    sold_out: bool


# ---------- Requests (JSON → domain) ----------
# Same rules as the domain, so bad input gets a 422 instead of crashing with a 500.


class VenueCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    type: VenueType


class EventCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    venue: VenueCreate
    starts_at: AwareDatetime  # rejects dates without a timezone
    capacity: int = Field(gt=0)

    def to_domain(self) -> Event:
        return Event(
            name=self.name,
            venue=Venue(self.venue.name, self.venue.type),
            starts_at=self.starts_at,
            capacity=self.capacity,
        )
