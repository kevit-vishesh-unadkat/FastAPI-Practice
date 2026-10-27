from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, Request, Response

from app.repo.event_repository import EventRepository
from app.schemas.event import EventCreate, EventUpdate, EventRead
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["Events"])


def get_service(request: Request):
    return EventService(EventRepository(request.app.state.db))


Service = Annotated[EventService, Depends(get_service)]


@router.post("/", response_model=EventRead, status_code=201)
async def create_event(payload: EventCreate, service: Service):
    return await service.create(payload)


@router.get("/{event_id}", response_model=EventRead)
async def get_event(event_id: str, service: Service):
    return await service.get(event_id)


@router.get("/")
async def list_events(
    request: Request,
    city: str | None = None,
    status: str | None = None,
    starts_after: datetime | None = None,
    starts_before: datetime | None = None,
    q: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = None,
):
    filters = {}

    if city:
        filters["venue.city"] = {
            "$regex": f"^{city}$",
            "$options": "i",
        }

    if status:
        filters["status"] = status

    date_filter = {}
    if starts_after:
        date_filter["$gte"] = starts_after
    if starts_before:
        date_filter["$lte"] = starts_before
    if date_filter:
        filters["starts_at"] = date_filter

    if q:
        filters["$text"] = {"$search": q}

    repo = EventRepository(request.app.state.db)
    return await repo.list(filters, limit, cursor)


@router.patch("/{event_id}", response_model=EventRead)
async def update_event(
    event_id: str,
    payload: EventUpdate,
    service: Service,
    if_match: Annotated[str | None, Header()] = None,
):
    from app.core.errors import AppError

    if if_match is None:
        raise AppError(
            428, "PRECONDITION_REQUIRED", "The If-Match header is required."
        )

    try:
        version = int(if_match.strip('"'))
        if version < 1:
            raise ValueError
    except ValueError as exc:
        raise AppError(
            422, "INVALID_VERSION", "If-Match must contain a positive version."
        ) from exc

    return await service.update(event_id, version, payload)


@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: str,
    service: Service,
):
    await service.delete(event_id)
    return Response(status_code=204)