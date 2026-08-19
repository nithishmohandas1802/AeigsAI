from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import AegisAIException, ErrorCode


async def aegisai_exception_handler(
    request: Request,
    exc: AegisAIException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "status": exc.status_code,
            },
        },
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    code = (
        exc.headers.get("X-AegisAI-Error-Code", ErrorCode.HTTP_ERROR)
        if exc.headers
        else ErrorCode.HTTP_ERROR
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": str(exc.detail),
                "status": exc.status_code,
            },
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    details = []

    for error in exc.errors():
        location = error.get("loc", [])

        field = ".".join(
            str(item)
            for item in location
            if item != "body"
        )

        details.append(
            {
                "field": field,
                "message": error.get(
                    "msg",
                    "Invalid value",
                ),
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.VALIDATION_ERROR,
                "message": "Request validation failed",
                "status": 422,
                "details": details,
            },
        },
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred",
                "status": 500,
            },
        },
    )
