from bson import ObjectId
from pymongo import ReturnDocument

from app.repo.user_repository import serialize


class EventRepository:
    def __init__(self, db):
        self.collection = db.events

    async def create(self, data: dict):
        data["status"] = "draft"
        data["version"] = 1
        data["ticket_tiers"] = [
            {**tier, "reserved": 0} for tier in data["ticket_tiers"]
        ]

        result = await self.collection.insert_one(data)
        return await self.get_by_id(str(result.inserted_id))

    async def get_by_id(self, event_id: str):
        if not ObjectId.is_valid(event_id):
            return None

        doc = await self.collection.find_one({"_id": ObjectId(event_id)})
        return serialize(doc) if doc else None

    async def list(self, filters: dict, limit: int, after=None):
        query = dict(filters)
        if after:
            query["_id"] = {"$gt": ObjectId(after)}

        cursor = (
            self.collection.find(query)
            .sort("_id", 1)
            .limit(limit + 1)
        )
        documents = [serialize(doc) async for doc in cursor]

        has_more = len(documents) > limit
        items = documents[:limit]
        next_cursor = items[-1]["id"] if has_more and items else None

        return {"items": items, "next_cursor": next_cursor}

    async def update_versioned(
        self,
        event_id: str,
        expected_version: int,
        changes: dict,
    ):
        if not ObjectId.is_valid(event_id):
            return None

        doc = await self.collection.find_one_and_update(
            {
                "_id": ObjectId(event_id),
                "version": expected_version,
            },
            {
                "$set": changes,
                "$inc": {"version": 1},
            },
            return_document=ReturnDocument.AFTER,
        )
        return serialize(doc) if doc else None

    async def delete(self, event_id: str):
        if not ObjectId.is_valid(event_id):
            return False

        result = await self.collection.delete_one(
            {
                "_id": ObjectId(event_id),
                "status": "draft",
            }
        )
        return result.deleted_count == 1

    async def reserve_seats(self, event_id: str, tier: str, quantity: int):
        """Atomically reserve seats only if that tier has sufficient quota."""
        if not ObjectId.is_valid(event_id):
            return None

        doc = await self.collection.find_one_and_update(
            {
                "_id": ObjectId(event_id),
                "status": "published",
                "ticket_tiers": {
                    "$elemMatch": {
                        "name": tier,
                        "$expr": {
                            "$lte": [
                                {"$add": ["$ticket_tiers.reserved", quantity]},
                                "$ticket_tiers.quota",
                            ]
                        },
                    }
                },
            },
            {
                "$inc": {
                    "ticket_tiers.$.reserved": quantity,
                    "version": 1,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return serialize(doc) if doc else None

    async def release_seats(self, event_id: str, tier: str, quantity: int):
        if not ObjectId.is_valid(event_id):
            return False

        result = await self.collection.update_one(
            {
                "_id": ObjectId(event_id),
                "ticket_tiers": {
                    "$elemMatch": {
                        "name": tier,
                        "reserved": {"$gte": quantity},
                    }
                },
            },
            {
                "$inc": {
                    "ticket_tiers.$.reserved": -quantity,
                    "version": 1,
                }
            },
        )
        return result.modified_count == 1