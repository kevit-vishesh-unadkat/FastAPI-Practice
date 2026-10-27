from enum import Enum
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query, status
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

app = FastAPI(title="Food Management API")


# -------------------- ENUM --------------------

class FoodCategory(str, Enum):
    VEG = "veg"
    NON_VEG = "non_veg"
    DESSERT = "dessert"


# -------------------- NESTED MODEL --------------------

class Ingredient(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=50)
    quantity: float = Field(gt=0)
    unit: str = Field(min_length=1, max_length=20)


# -------------------- CREATE MODEL --------------------

class FoodCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=50)
    price: float = Field(gt=0, le=10000)
    category: FoodCategory
    available: bool = True
    ingredients: list[Ingredient] = Field(min_length=1)

    preparation_minutes: int = Field(ge=1, le=300)
    cooking_minutes: int = Field(ge=1, le=300)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Food name cannot be empty")

        return value

    @model_validator(mode="after")
    def validate_total_time(self):
        total = self.preparation_minutes + self.cooking_minutes

        if total > 480:
            raise ValueError("Total preparation and cooking time is too long")

        return self


# -------------------- UPDATE MODEL --------------------

class FoodUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=2, max_length=50)
    price: float | None = Field(default=None, gt=0, le=10000)
    category: FoodCategory | None = None
    available: bool | None = None
    ingredients: list[Ingredient] | None = Field(
        default=None, min_length=1
    )
    preparation_minutes: int | None = Field(default=None, ge=1, le=300)
    cooking_minutes: int | None = Field(default=None, ge=1, le=300)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value is not None:
            value = value.strip()

            if not value:
                raise ValueError("Food name cannot be empty")

        return value

    @model_validator(mode="after")
    def validate_not_null(self):
        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")

        return self


# -------------------- RESPONSE MODEL --------------------

class FoodResponse(BaseModel):
    id: int
    name: str
    price: float
    category: FoodCategory
    available: bool
    ingredients: list[Ingredient]
    preparation_minutes: int
    cooking_minutes: int


# -------------------- TEMPORARY STORAGE --------------------

foods: dict[int, dict] = {}
next_id = 1


def get_food_or_404(food_id: int) -> dict:
    food = foods.get(food_id)

    if food is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found",
        )

    return food


# -------------------- CREATE --------------------

@app.post(
    "/foods",
    response_model=FoodResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_food(food: FoodCreate):
    global next_id

    food_data = food.model_dump(mode="json")
    food_data["id"] = next_id

    foods[next_id] = food_data
    next_id += 1

    return food_data


# -------------------- READ ALL --------------------

@app.get("/foods", response_model=list[FoodResponse])
def get_all_foods(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    category: FoodCategory | None = None,
):
    result = list(foods.values())

    if category is not None:
        result = [
            food for food in result
            if food["category"] == category.value
        ]

    return result[skip:skip + limit]


# -------------------- READ ONE --------------------

@app.get("/foods/{food_id}", response_model=FoodResponse)
def get_food(
    food_id: Annotated[int, Path(gt=0)]
):
    return get_food_or_404(food_id)


# -------------------- FULL UPDATE --------------------

@app.put("/foods/{food_id}", response_model=FoodResponse)
def replace_food(
    food_id: Annotated[int, Path(gt=0)],
    food: FoodCreate,
):
    existing = get_food_or_404(food_id)

    updated_data = food.model_dump(mode="json")
    updated_data["id"] = existing["id"]

    foods[food_id] = updated_data

    return updated_data


# -------------------- PARTIAL UPDATE --------------------

@app.patch("/foods/{food_id}", response_model=FoodResponse)
def update_food(
    food_id: Annotated[int, Path(gt=0)],
    food: FoodUpdate,
):
    existing = get_food_or_404(food_id)

    updates = food.model_dump(
        exclude_unset=True,
        mode="json",
    )

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one field to update",
        )

    candidate = {**existing, **updates}

    # Validate relationships between fields after merging.
    FoodCreate.model_validate({
        key: value
        for key, value in candidate.items()
        if key != "id"
    })

    foods[food_id] = candidate

    return candidate


# -------------------- DELETE --------------------

@app.delete("/foods/{food_id}")
def delete_food(
    food_id: Annotated[int, Path(gt=0)]
):
    get_food_or_404(food_id)

    del foods[food_id]

    return {"message": "Food deleted successfully"}
