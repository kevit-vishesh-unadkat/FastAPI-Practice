from contextlib import asynccontextmanager
from typing import Annotated

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from database import (
    users_collection,
    tasks_collection,
    check_database_connection,
    close_database_connection,
    initialize_database,
)
from schemas import (
    UserCreate,
    UserResponse,
    TokenResponse,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    check_database_connection()
    initialize_database()
    yield
    close_database_connection()


app = FastAPI(
    title="FastAPI MongoDB Auth CRUD",
    lifespan=lifespan,
)


CurrentUser = Annotated[dict, Depends(get_current_user)]


def user_response(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
    }


def task_response(task: dict) -> dict:
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task["description"],
        "completed": task["completed"],
        "owner_id": str(task["owner_id"]),
    }


def get_owned_task(task_id: str, user_id: ObjectId) -> dict:
    if not ObjectId.is_valid(task_id):
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    task = tasks_collection.find_one({
        "_id": ObjectId(task_id),
        "owner_id": user_id,
    })

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


# ---------------- REGISTER ----------------

@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(data: UserCreate):
    user = {
        "username": data.username,
        "email": str(data.email).lower(),
        "hashed_password": hash_password(data.password),
        "role": "user",
    }

    try:
        result = users_collection.insert_one(user)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail="Username or email already exists",
        )

    user["_id"] = result.inserted_id
    return user_response(user)


# ---------------- LOGIN ----------------

@app.post("/login", response_model=TokenResponse)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = users_collection.find_one({
        "username": form.username
    })

    if (
        user is None
        or not verify_password(
            form.password,
            user["hashed_password"],
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(str(user["_id"])),
        "token_type": "bearer",
    }


# ---------------- CURRENT PROFILE ----------------

@app.get("/users/me", response_model=UserResponse)
def get_profile(current_user: CurrentUser):
    return user_response(current_user)


# ---------------- CREATE TASK ----------------

@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(data: TaskCreate, current_user: CurrentUser):
    task = {
        "title": data.title,
        "description": data.description,
        "completed": data.completed,
        "owner_id": current_user["_id"],
    }

    result = tasks_collection.insert_one(task)
    task["_id"] = result.inserted_id

    return task_response(task)


# ---------------- READ ALL MY TASKS ----------------

@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(current_user: CurrentUser):
    tasks = tasks_collection.find({
        "owner_id": current_user["_id"]
    })

    return [task_response(task) for task in tasks]


# ---------------- READ ONE TASK ----------------

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, current_user: CurrentUser):
    task = get_owned_task(task_id, current_user["_id"])
    return task_response(task)


# ---------------- UPDATE TASK ----------------

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    data: TaskUpdate,
    current_user: CurrentUser,
):
    task = get_owned_task(task_id, current_user["_id"])
    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=422,
            detail="Provide at least one field to update",
        )

    if any(value is None for value in changes.values()):
        raise HTTPException(
            status_code=422,
            detail="Task fields cannot be null",
        )

    tasks_collection.update_one(
        {"_id": task["_id"], "owner_id": current_user["_id"]},
        {"$set": changes},
    )

    updated_task = tasks_collection.find_one({
        "_id": task["_id"],
        "owner_id": current_user["_id"],
    })

    return task_response(updated_task)


# ---------------- DELETE TASK ----------------

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str, current_user: CurrentUser):
    task = get_owned_task(task_id, current_user["_id"])

    tasks_collection.delete_one({
        "_id": task["_id"],
        "owner_id": current_user["_id"],
    })

    return {"message": "Task deleted successfully"}


# ---------------- ADMIN ONLY ----------------

@app.get("/admin/users", response_model=list[UserResponse])
def get_all_users(
    admin: Annotated[dict, Depends(require_admin)]
):
    users = users_collection.find({})

    return [user_response(user) for user in users]
