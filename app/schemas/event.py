from datetime import datetime
from typing import Literal

from pydantic import Field, model_validator

from app.schemas.common import StrictSchema


class Venue(StrictSchema):
    name: str = Field(min_length=2, max_length=120)
    city: str = Field(min_length=2, max_length=100)


class TicketTier(StrictSchema):
    name: str = Field(min_length=1, max_length=80)
    price_inr: int = Field(ge=0)
    quota: int = Field(ge=1)


class EventCreate(StrictSchema):
    title: str = Field(min_length=5, max_length=120)
    venue: Venue
    starts_at: datetime
    ends_at: datetime
    capacity: int = Field(ge=1, le=50_000)
    ticket_tiers: list[TicketTier] = Field(min_length=1)
    organizer_id: str

    @model_validator(mode="after")
    def validate_event(self):
        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise ValueError("Event dates must include a timezone.")

        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be later than starts_at.")

        if sum(tier.quota for tier in self.ticket_tiers) > self.capacity:
            raise ValueError("Ticket tier quotas exceed event capacity.")

        names = [tier.name.casefold() for tier in self.ticket_tiers]
        if len(names) != len(set(names)):
            raise ValueError("Ticket tier names must be unique.")

        return self


class EventUpdate(StrictSchema):
    title: str | None = Field(default=None, min_length=5, max_length=120)
    venue: Venue | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    capacity: int | None = Field(default=None, ge=1, le=50_000)
    ticket_tiers: list[TicketTier] | None = Field(default=None, min_length=1)
    status: Literal["draft", "published", "completed", "cancelled"] | None = None


class EventRead(StrictSchema):
    id: str
    title: str
    venue: Venue
    starts_at: datetime
    ends_at: datetime
    capacity: int
    ticket_tiers: list[TicketTier]
    status: Literal["draft", "published", "completed", "cancelled"]
    organizer_id: str
    version: int