from logging import FATAL

from fastapi import FastAPI,HTTPException,Request
from slowapi import Limiter,_rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

app=FastAPI()

# create the the rate limiter
limiter=Limiter(key_func=get_remote_address)

# Register the rate limiter with fastapi
app.state.limiter=limiter

# handle the rate limiter error

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)


@app.get("/")
def home():
    return {
        "message":"Hello From VIshesh Unadkat"
    }

@app.get("/products")
@limiter.limit("5/minute")
async def get_product(request:Request):
    return {
        "message": "Products fetched successfully",
        "products": ["Laptop", "Mouse", "Keyboard"]
    }

@app.get("/login")
@limiter.limit("3/minute")
async def login(request:Request):
    return {
        "message":"Login Endpoint Accessed"
    }


