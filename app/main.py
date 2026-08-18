from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.routers.health import router as health_router
from app.config.settings import settings
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from app.exceptions import AegisAIException
from app.exception_handlers import (
    aegisai_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,

)

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)

app.add_exception_handler(
    AegisAIException,
    aegisai_exception_handler,
)

app.add_exception_handler(
    HTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    general_exception_handler,
)

app.include_router(health_router)
app.include_router(user_router)
app.include_router(auth_router)
