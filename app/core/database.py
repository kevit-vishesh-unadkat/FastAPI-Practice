from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient, ASCENDING, TEXT, DESCENDING

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncMongoClient(settings.mongodb_url)
    await client.aconnect()

    db = client[settings.database_name]
    app.state.db = db

    # Unique email prevents duplicate users, even under concurrent requests.
    await db.users.create_index(
        [("email", ASCENDING)],
        unique=True,
        name="uq_users_email",
    )

    await db.events.create_index(
        [("status", ASCENDING), ("starts_at", ASCENDING)],
        name="ix_events_status_start",
    )

    await db.events.create_index(
        [("title", TEXT)],
        name="ix_events_title_text",
    )

    await db.bookings.create_index(
        [("status", ASCENDING), ("hold_expires_at", ASCENDING)],
        name="ix_bookings_status_hold",
    )

    await db.bookings.create_index(
        [("event_id", ASCENDING), ("user_id", ASCENDING)],
        name="ix_bookings_event_user",
    )

    try:
        yield
    finally:
        await client.close()