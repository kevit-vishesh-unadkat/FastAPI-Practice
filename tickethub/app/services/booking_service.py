from datetime import datetime, timedelta, timezone

from tickethub.app.core.errors import AppError
from tickethub.app.repo.booking_repository import BookingRepository


class BookingService:
    def __init__(self, repository: BookingRepository):
        self.repository = repository

    async def create(self, payload):
        data = payload.model_dump()

        event = await self.repository.events.find_one({
            "_id": self._object_id(data["event_id"]),
            "status": "published",
        })
        if not event:
            raise AppError(404, "EVENT_NOT_FOUND", "Published event not found.")

        user = await self.repository.users.find_one({
            "_id": self._object_id(data["user_id"]),
            "is_active": True,
        })
        if not user:
            raise AppError(404, "USER_NOT_FOUND", "Active user not found.")

        tier = next(
            (item for item in event["ticket_tiers"]
             if item["name"] == data["tier"]),
            None,
        )
        if tier is None:
            raise AppError(422, "INVALID_TIER", "Ticket tier does not exist.")

        reserved = await self.repository.reserve(
            data["event_id"], data["tier"], data["quantity"]
        )
        if not reserved:
            raise AppError(409, "SOLD_OUT", "Not enough tickets remain.")

        booking = {
            **data,
            "amount_inr": tier["price_inr"] * data["quantity"],
            "status": "pending_payment",
            "hold_expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
        }

        try:
            return await self.repository.create(booking)
        except Exception:
            # Compensating release; production systems should make this
            # reliable and idempotent, or use a MongoDB transaction.
            await self.repository.release(
                data["event_id"], data["tier"], data["quantity"]
            )
            raise

    @staticmethod
    def _object_id(value: str):
        from bson import ObjectId

        if not ObjectId.is_valid(value):
            raise AppError(422, "INVALID_ID", "Malformed resource ID.")
        return ObjectId(value)

    async def get(self, booking_id: str):
        booking = await self.repository.get_by_id(booking_id)
        if not booking:
            raise AppError(404, "BOOKING_NOT_FOUND", "Booking not found.")
        return booking

    async def list(self, skip: int, limit: int):
        return await self.repository.list(skip, limit)