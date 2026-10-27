from bson import ObjectId
from pymongo import ReturnDocument


def serialize(document: dict) -> dict:
    document["id"] = str(document.pop("_id"))
    return document


class UserRepository:
    def __init__(self, db):
        self.collection = db.users

    async def create(self, data: dict) -> dict:
        result = await self.collection.insert_one(data)
        return await self.get_by_id(str(result.inserted_id))

    async def get_by_id(self, user_id: str):
        if not ObjectId.is_valid(user_id):
            return None

        document = await self.collection.find_one({"_id": ObjectId(user_id)})
        return serialize(document) if document else None

    async def list(self, skip: int = 0, limit: int = 20):
        cursor = self.collection.find().sort("_id", 1).skip(skip).limit(limit)
        return [serialize(item) async for item in cursor]

    async def update(self, user_id: str, changes: dict):
        if not ObjectId.is_valid(user_id):
            return None

        document = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": changes},
            return_document=ReturnDocument.AFTER,
        )
        return serialize(document) if document else None

    async def delete(self, user_id: str) -> bool:
        if not ObjectId.is_valid(user_id):
            return False

        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count == 1