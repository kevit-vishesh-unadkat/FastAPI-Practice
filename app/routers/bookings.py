from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response

from app.core.errors import AppError
from app.repo.booking_repository import BookingRepository
from app.schemas.booking import BookingCreate, BookingRead
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def get_service(request: Request):
    return BookingService(BookingRepository(request.app.state.db))


Service = Annotated[BookingService, Depends(get_service)]


@router.post("/", response_model=BookingRead, status_code=201)
async def create_booking(payload: BookingCreate, service: Service):
    return await service.create(payload)


@router.get("/", response_model=list[BookingRead])
async def list_bookings(
    service: Service,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return await service.list(skip, limit)


@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking(booking_id: str, service: Service):
    return await service.get(booking_id)


@router.patch("/{booking_id}", response_model=BookingRead)
async def update_booking(
    booking_id: str,
    service: Service,
):
    # Implement an explicit, safe update workflow before enabling PATCH.
    raise AppError(
        409,
        "BOOKING_UPDATE_NOT_ALLOWED",
        "Booking changes require a dedicated booking workflow.",
    )


@router.delete("/{booking_id}", status_code=204)
async def delete_booking(booking_id: str, service: Service):
    # Never delete first and release inventory later without consistency
    # protection. Cancellation must be implemented as an atomic workflow.
    raise AppError(
        409,
        "BOOKING_DELETE_NOT_ALLOWED",
        "Use the booking cancellation workflow.",
    )