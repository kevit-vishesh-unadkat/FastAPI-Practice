from fastapi import FastAPI,HTTPException,Request
import time

app=FastAPI()

@app.middleware("http")
async def timing_middleware(request:Request , call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    elapsed_time = time.perf_counter() - start_time

    response.headers["X-Process-Time"] = f"{elapsed_time:.4f}"

    return response


@app.get("/fast")
async def fast_endpoint():
    return {"message": "Fast response"}


@app.get("/slow")
async def slow_endpoint():
    time.sleep(2)
    return {"message": "Slow response"}