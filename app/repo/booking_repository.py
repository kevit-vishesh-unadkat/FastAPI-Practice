from bson import ObjectId

from app.repo.user_repository import serialize


class BookingRepository:
    def __init__(self, db):
        self.collection = db.bookings
        self.inventory = db.inventory
        self.events = db.events
        self.users = db.users

    async def get_by_id(self, booking_id: str):
        if not ObjectId.is_valid(booking_id):
            return None

        doc = await self.collection.find_one({"_id": ObjectId(booking_id)})
        return serialize(doc) if doc else None

    async def list(self, skip: int = 0, limit: int = 20):
        cursor = self.collection.find().sort("_id", 1).skip(skip).limit(limit)
        return [serialize(doc) async for doc in cursor]

    async def reserve(self, event_id: str, tier: str, quantity: int):
        result = await self.inventory.update_one(
            {
                "event_id": event_id,
                "tier": tier,
                "remaining": {"$gte": quantity},
            },
            {"$inc": {"remaining": -quantity}},
        )
        return result.modified_count == 1

    async def release(self, event_id: str, tier: str, quantity: int):
        result = await self.inventory.update_one(
            {
                "event_id": event_id,
                "tier": tier,
                "remaining": {"$lte": 50_000},
                "quota": {"$gte": quantity},
            },
            {"$inc": {"remaining": quantity}},
        )
        return result.modified_count == 1

    async def create(self, data: dict):
        result = await self.collection.insert_one(data)
        return await self.get_by_id(str(result.inserted_id))

    async def update(self, booking_id: str, changes: dict):
        if not ObjectId.is_valid(booking_id):
            return None

        # Never use this generic method to modify amount or status.
        doc = await self.collection.find_one_and_update(
            {
                "_id": ObjectId(booking_id),
                "status": "pending_payment",
            },
            {"$set": changes},
            return_document=True,
        )
        return serialize(doc) if doc else None

    async def delete(self, booking_id: str):
        if not ObjectId.is_valid(booking_id):
            return False

        result = await self.collection.delete_one({
            "_id": ObjectId(booking_id),
            "status": "pending_payment",
        })
        return result.deleted_count == 1