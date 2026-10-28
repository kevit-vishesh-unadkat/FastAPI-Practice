from datetime import datetime
from typing import Literal

from pydantic import Field

from tickethub.app.schemas.common import StrictSchema


class BookingCreate(StrictSchema):
    event_id: str
    user_id: str
    tier: str = Field(min_length=1, max_length=80)
    quantity: int = Field(ge=1, le=6)


class BookingUpdate(StrictSchema):
    # Only the fields that can safely be edited directly.
    # Status and amount are controlled by business workflows.
    quantity: int | None = Field(default=None, ge=1, le=6)


class BookingRead(StrictSchema):
    id: str
    event_id: str
    user_id: str
    tier: str
    quantity: int
    amount_inr: int
    status: Literal[
        "pending_payment",
        "confirmed",
        "cancelled",
        "expired",
    ]
    hold_expires_at: datetime