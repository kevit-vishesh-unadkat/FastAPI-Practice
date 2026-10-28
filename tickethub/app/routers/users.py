from typing import Annotated

from fastapi import APIRouter, Depends, Request, Query, Response, status

from tickethub.app.repo.user_repository import UserRepository
from tickethub.app.schemas.users import UserCreate, UserUpdate, UserRead
from tickethub.app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_service(request: Request) -> UserService:
    return UserService(UserRepository(request.app.state.db))


Service = Annotated[UserService, Depends(get_service)]


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(payload: UserCreate, service: Service):
    return await service.create(payload)


@router.get("/", response_model=list[UserRead])
async def list_users(
    service: Service,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return await service.list(skip, limit)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, service: Service):
    return await service.get(user_id)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: str, payload: UserUpdate, service: Service):
    return await service.update(user_id, payload)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str, service: Service):
    await service.delete(user_id)
    return Response(status_code=204)