from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import AegisAIException


async def aegisai_exception_handler(
    request: Request,
    exc: AegisAIException,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "status": 409,
            }
        },
    )