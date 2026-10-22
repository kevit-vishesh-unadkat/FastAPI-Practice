import time
from copy import deepcopy
from inspect import FullArgSpec

from fastapi import FastAPI,HTTPException,Query
from pydantic import BaseModel,Field

app=FastAPI()

class ProductCreate(BaseModel):
    name: str = Field(min_length=2)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)


# in memory product storge

products = [
    {"id": 1, "name": "Laptop", "price": 55000, "quantity": 10},
    {"id": 2, "name": "Mouse", "price": 700, "quantity": 50},
    {"id": 3, "name": "Keyboard", "price": 1500, "quantity": 30},
    {"id": 4, "name": "Monitor", "price": 12000, "quantity": 15},
    {"id": 5, "name": "Headphones", "price": 2000, "quantity": 20},
]

next_id = 6

# cache configuraition

CACHE_TTL=30

cache={}

def get_cache_data(key):
    """Return cached data if it exist and hasn't expired"""

    entry=cache.get(key)

    if entry is None:
        return None

    expiry_time, cached_value = entry

    if time.monotonic() >= expiry_time:
        cache.pop(key, None)
        return None

    return deepcopy(cached_value)

def set_cache_data(key,value):
    """Store data in the cache with TTL"""

    expiry_time=time.monotonic()+CACHE_TTL

    cache[key]=(
        expiry_time,
        deepcopy(value)
    )

def invalidate_cache():
    """Clear cached product-list results."""

    cache.clear()

# Create Product

@app.post("/products")
def create_product(product:ProductCreate):
    global next_id

    new_product={
        "id":next_id,
        **product.model_dump(),
    }

    products.append(new_product)
    next_id += 1

    invalidate_cache()

    return {
        "message": "Product created successfully",
        "product": new_product,
    }