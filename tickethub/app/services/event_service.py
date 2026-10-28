from tickethub.app.core.errors import AppError
from app.repo.event_repository import EventRepository

EVENT_TRANSITIONS = {
    "draft": {"published", "cancelled"},
    "published": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


class EventService:
    def __init__(self, repository: EventRepository):
        self.repository = repository

    async def create(self, payload):
        return await self.repository.create(
            payload.model_dump(mode="python")
        )

    async def get(self, event_id: str):
        event = await self.repository.get_by_id(event_id)
        if not event:
            raise AppError(404, "EVENT_NOT_FOUND", "Event not found.")
        return event

    async def list(self, filters: dict, limit: int, cursor: str | None):
        return await self.repository.list(filters, limit, cursor)

    async def update(
        self,
        event_id: str,
        expected_version: int,
        payload,
    ):
        current = await self.get(event_id)
        changes = payload.model_dump(exclude_unset=True)

        if not changes:
            raise AppError(422, "EMPTY_PATCH", "Provide at least one field.")

        new_status = changes.get("status", current["status"])
        if new_status != current["status"]:
            if new_status not in EVENT_TRANSITIONS[current["status"]]:
                raise AppError(
                    409,
                    "ILLEGAL_TRANSITION",
                    "The requested event status transition is not allowed.",
                )

        if new_status == "cancelled":
            from datetime import datetime, timezone

            if current["starts_at"] <= datetime.now(timezone.utc):
                raise AppError(
                    409,
                    "ILLEGAL_TRANSITION",
                    "An event cannot be cancelled after it starts.",
                )

        merged = {**current, **changes}

        # Validate cross-field constraints against the complete updated event.
        from tickethub.app.schemas.event import EventCreate

        try:
            EventCreate.model_validate({
                key: merged[key]
                for key in (
                    "title", "venue", "starts_at", "ends_at",
                    "capacity", "ticket_tiers", "organizer_id",
                )
            })
        except Exception as exc:
            raise AppError(
                422, "INVALID_EVENT", "The updated event is invalid."
            ) from exc

        updated = await self.repository.update_versioned(
            event_id, expected_version, changes
        )
        if updated:
            return updated

        # Distinguish stale version from missing event.
        if await self.repository.get_by_id(event_id) is None:
            raise AppError(404, "EVENT_NOT_FOUND", "Event not found.")

        raise AppError(
            409, "VERSION_CONFLICT", "The event has been modified by another request."
        )

    async def delete(self, event_id: str):
        event = await self.get(event_id)

        if event["status"] != "draft":
            raise AppError(
                409, "ILLEGAL_TRANSITION", "Only draft events can be deleted."
            )

        deleted = await self.repository.delete(event_id)
        if not deleted:
            raise AppError(409, "VERSION_CONFLICT", "The event changed.")