from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError


class AppError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message


def error_body(request: Request, code: str, message: str):
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": getattr(request.state, "request_id", "unknown"),
        }
    }


async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(request, exc.code, exc.message),
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content=error_body(
            request,
            "VALIDATION_ERROR",
            "Request contains invalid or unexpected fields.",
        ),
    )


async def duplicate_key_handler(request: Request, exc: DuplicateKeyError):
    return JSONResponse(
        status_code=409,
        content=error_body(
            request,
            "DUPLICATE_RESOURCE",
            "A resource with a unique field already exists.",
        ),
    )


async def unexpected_error_handler(request: Request, exc: Exception):
    # Log the exception and traceback privately in production.
    return JSONResponse(
        status_code=500,
        content=error_body(
            request,
            "INTERNAL_ERROR",
            "An unexpected server error occurred.",
        ),
    )