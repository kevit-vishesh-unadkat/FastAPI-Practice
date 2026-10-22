from logging import FATAL

from fastapi import FastAPI,HTTPException,Request,Query
from pydantic import BaseModel,Field
from slowapi import Limiter,_rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

app=FastAPI()

limiter=Limiter(key_func=get_remote_address)

app.state.limiter=limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)


class OrderCreate(BaseModel):
    product_id:int=Field(gt=0)
    quantity:int=Field(gt=0)



products = [
    {"id": 1, "name": "Laptop", "price": 55000, "stock": 10},
    {"id": 2, "name": "Mouse", "price": 700, "stock": 50},
    {"id": 3, "name": "Keyboard", "price": 1500, "stock": 30},
    {"id": 4, "name": "Monitor", "price": 12000, "stock": 15},
    {"id": 5, "name": "Headphones", "price": 2000, "stock": 20},
]

orders = []
next_order_id = 1



@app.get("/")
def home():
    return {
        "message": "Welcome to the Rate-Limited Product API",
        "available_endpoints": [
            "GET /products",
            "GET /products/search",
            "GET /products/{product_id}",
            "POST /orders",
            "GET /orders",
        ]
    }


@app.get("/products")
@limiter.limit("3/minute")
def get_product(
        request:Request,
        page:int=Query(default=1,gt=1),
        limit:int=Query(default=3,ge=1,le=10),
):
    total=len(products)

    start=(page-1)*limit
    end=start+limit

    return {
        "page": page,
        "limit": limit,
        "total_products": total,
        "products": products[start:end],
    }


@app.get("/products/search")
@limiter.limit("5/minute")
def search_products(
    request: Request,
    keyword: str = Query(min_length=1),
):
    results = [
        product
        for product in products
        if keyword.lower() in product["name"].lower()
    ]

    return {
        "keyword": keyword,
        "total_results": len(results),
        "products": results,
    }


@app.get("/orders")
@limiter.limit("5/minute")
def get_order(request:Request):
    return {
        "total orders":len(orders),
        "orders":orders
    }


@app.get("/products/{product_id}")
@limiter.limit("10/minute")
def get_product(request: Request, product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=404,
        detail="Product not found",
    )


# -------------------------
# Create an order
# -------------------------

@app.post("/orders", status_code=201)
@limiter.limit("3/minute")
def create_order(request: Request, order: OrderCreate):

    global next_order_id

    # Find the requested product
    product = next(
        (p for p in products if p["id"] == order.product_id),
        None,
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    # Check available stock
    if order.quantity > product["stock"]:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock",
        )

    # Calculate the order total
    total_price = product["price"] * order.quantity

    # Reduce stock
    product["stock"] -= order.quantity

    # Create the order
    new_order = {
        "id": next_order_id,
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": order.quantity,
        "total_price": total_price,
    }

    orders.append(new_order)
    next_order_id += 1

    return {
        "message": "Order created successfully",
        "order": new_order,
    }