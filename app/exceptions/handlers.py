from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions.custom_exceptions import GeospatialAPIException
from app.core.logging import logger


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers centralized exception handlers on the FastAPI application.
    """
    @app.exception_handler(GeospatialAPIException)
    async def custom_exception_handler(request: Request, exc: GeospatialAPIException):
        logger.warning(f"Domain exception on {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "status_code": exc.status_code
            }
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Log the full exception internally without revealing details to client
        logger.error(f"Unhandled exception processing {request.url.path}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "An unexpected error occurred during processing.",
                "status_code": 500
            }
        )
