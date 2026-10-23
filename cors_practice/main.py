from fastapi.responses import JSONResponse
from fastapi import FastAPI,HTTPException,Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500","http://localhost:5500"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

foods = [
    {"id": 1, "name": "Pizza", "price": 250},
    {"id": 2, "name": "Burger", "price": 120},
]

class Food(BaseModel):
    name:str
    price:float


@app.get("/")
def Home():
    return {
        "message":"Hello From Vishesh"
    }

@app.post("/foods",status_code=201)
def create_food(food:Food):
    """this function is use to create a food"""

    new_food={
        "name":food.name,
        "price":food.price
    }

    foods.append(new_food)

    return {
        "message":"food is created successfully",
        "data":new_food
    }

@app.get("/foods")

def get_food():
    if foods is None:
        raise HTTPException(status_code=404,detail="food is not found")
    return {
        "message":"List of Foods",
        "data":foods
    }

@app.get("/foods/{food_id}")
def get_food_by_id(food_id:int):
    for food in foods:
        if food["id"]==food_id:
            return food
    raise HTTPException(
        status_code=404,
        detail="food is not found"
    )

@app.put("/foods/{food_id}")
def update_food(food_id:int,update_food:Food):
    """this food is used to update a food"""

    for food in foods:
        if food["id"]==food_id:
            food["name"]=update_food.name
            food["price"]=update_food.price
            return {
                "message":"update a food",
                "data":food
            }

    raise HTTPException(
        status_code=404,
        detail="food is not found"
    )

@app.delete("/foods/{food_id}")
def delete_food(food_id:int):
    """this function is to delete a food"""

    for food in foods:
        if food["id"]==food_id:
            foods.remove(food)
            return {
                JSONResponse(status_code=200,
                content={"message":"food is deleted successfully"})
            }
            raise HTTPException(
                status_code=404,
                detail="food is not found"
            )