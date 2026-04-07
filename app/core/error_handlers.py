"""
Error handling module for the FastAPI application. Defines custom exception handlers for
application-specific errors, validation errors, and unexpected exceptions. Each handler
logs the error and returns a structured JSON response with an appropriate HTTP status code
and error message.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.exceptions import AppBaseError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers custom exception handlers for the FastAPI application, including handlers for
    application-specific errors, validation errors, and unexpected exceptions.
    """
    @app.exception_handler(AppBaseError)
    async def handle_app_base_error(request: Request, exc: AppBaseError) -> JSONResponse:
        logger.error("Application error: %s", exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
            },
        )

    @app.exception_handler(ValidationError)
    async def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
        logger.warning("Validation error: %s", str(exc))
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Invalid request or response validation error.",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unexpected unhandled error: %s", str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected internal error occurred.",
            },
        )
