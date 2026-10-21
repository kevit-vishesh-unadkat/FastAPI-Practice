from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

API_KEY = "my-secret-key"


@app.middleware("http")
async def authentication_middleware(request: Request, call_next):

    # Allow public endpoints
    if request.url.path in ["/", "/menu", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)

    # Read API key from request headers
    api_key = request.headers.get("X-API-Key")

    # Reject requests without the correct key
    if api_key != API_KEY:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or missing API key"}
        )

    return await call_next(request)


@app.get("/")
async def home():
    return {"message": "Public endpoint"}


@app.get("/menu")
async def get_menu():
    return {"items": ["Pizza", "Burger"]}


@app.get("/admin")
async def admin():
    return {"message": "Welcome to the admin panel"}