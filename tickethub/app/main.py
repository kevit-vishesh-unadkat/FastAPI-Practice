# from contextlib import asynccontextmanager

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from pymongo.errors import DuplicateKeyError

# from tickethub.app.core.config import settings
# from tickethub.app.core.database import lifespan as database_lifespan
# from tickethub.app.core.errors import (
#     AppError,
#     app_error_handler,
#     validation_error_handler,
#     duplicate_key_handler,
#     unexpected_error_handler,
# )
# from tickethub.app.core.middleware import RequestIDMiddleware
# from tickethub.app.routers import users
# from tickethub.app.routers import bookings, events

# from app.core.config import settings


from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pymongo.errors import DuplicateKeyError

from app.core.config import settings
from app.core.database import lifespan as database_lifespan
from app.core.errors import (
    AppError,
    app_error_handler,
    validation_error_handler,
    duplicate_key_handler,
    unexpected_error_handler,
)
from app.core.middleware import RequestIDMiddleware
from app.routers import users, bookings, events


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database_lifespan(app):
        # Add inventory indexes and startup validation here.
        yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "If-Match", "Authorization"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(422, validation_error_handler)
app.add_exception_handler(DuplicateKeyError, duplicate_key_handler)
app.add_exception_handler(Exception, unexpected_error_handler)

app.include_router(users.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(bookings.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}