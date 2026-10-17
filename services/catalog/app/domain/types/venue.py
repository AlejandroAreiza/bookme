from dataclasses import dataclass
from enum import StrEnum


class VenueType(StrEnum):
    ARENA = "ARENA"
    STADIUM = "STADIUM"
    THEATER = "THEATER"
    CONCERT_HALL = "CONCERT_HALL"
    CLUB = "CLUB"
    CONFERENCE_CENTER = "CONFERENCE_CENTER"
    EXHIBITION_HALL = "EXHIBITION_HALL"
    OUTDOOR = "OUTDOOR"
    CINEMA = "CINEMA"
    ONLINE = "ONLINE"


@dataclass(frozen=True)
class Venue:
    name: str
    type: VenueType

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("venue name cannot be empty")
        if not self.type:
            raise ValueError("venue type cannot be empty")
