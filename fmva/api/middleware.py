from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import traceback

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException:
            raise
        except ValueError as ve:
            # Handle validation errors gracefully
            logger.warning(f"Validation error: {str(ve)}")
            return JSONResponse(
                status_code=400,
                content={"error": "ValidationError", "message": str(ve)}
            )
        except Exception as e:
            # Catch all unexpected errors to prevent 500 crashes returning HTML
            logger.error(f"Unhandled exception: {str(e)}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={"error": "InternalServerError", "message": "An unexpected error occurred during valuation."}
            )
