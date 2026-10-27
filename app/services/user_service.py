from app.core.errors import AppError
from app.repo.user_repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create(self, payload):
        data = payload.model_dump()
        data["role"] = "attendee"
        data["is_active"] = True
        return await self.repository.create(data)

    async def get(self, user_id: str):
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise AppError(404, "USER_NOT_FOUND", "User not found.")
        return user

    async def list(self, skip: int, limit: int):
        return await self.repository.list(skip, limit)

    async def update(self, user_id: str, payload):
        changes = payload.model_dump(exclude_unset=True)
        if not changes:
            raise AppError(422, "EMPTY_PATCH", "Provide fields to update.")

        user = await self.repository.update(user_id, changes)
        if not user:
            raise AppError(404, "USER_NOT_FOUND", "User not found.")
        return user

    async def delete(self, user_id: str):
        if not await self.repository.delete(user_id):
            raise AppError(404, "USER_NOT_FOUND", "User not found.")