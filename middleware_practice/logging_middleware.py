from fastapi import FastAPI,HTTPException,Request

app=FastAPI()

@app.middleware("http")
async def logging_middleware(request:Request, call_next):

    print(f"Incoming Request : {request.method} {request.url.path}")

    response=await call_next(request)

    print(f"Response Status : {response.status_code}")

    return response


@app.get("/")
async def home():
    return {
        "message":"Hello From Vishesh"
    }

@app.get("/menu")
async def get_menu():
    return {
        "items":["Pizza","Burger","Pasta"]
    }


# The logging middleware automatically handles requests to both / and /menu