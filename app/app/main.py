# FastAPI application entry point with Sentry integration, CORS configuration, and scheduler management
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
import os

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.handlers import validation_exception_handler
from app.core.sentry import init_sentry
from app.api.auth import get_current_user, APIUser
from app.api.middleware.ratelimit import rate_limit

logger = logging.getLogger(__name__)

# Initialize Sentry in production
init_sentry()


# lifespan manages application startup and shutdown events, handling scheduler initialization and cleanup in production.
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for application startup/shutdown events.
    Properly handles scheduler initialization and cleanup.
    Only initializes scheduler in production environment.
    """
    if settings.PRODUCTION:
        try:
            await scheduler.start()
            logger.info("Scheduler initialized successfully in production mode")
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {str(e)}")
            # Don't raise the exception - let the API continue running

    yield

    if settings.PRODUCTION:
        try:
            await scheduler.shutdown()
            logger.info("Scheduler shut down successfully")
        except Exception as e:
            logger.error(f"Failed to shutdown scheduler: {str(e)}")


# app is the main FastAPI application instance with lifespan management and OpenAPI configuration
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json" if not settings.PRODUCTION else None,
    docs_url="/docs" if not settings.PRODUCTION else None,
    redoc_url="/redoc" if not settings.PRODUCTION else None,
    lifespan=lifespan,
)

# Register exception handlers
# app.exception_handler(404)(not_found_handler)
app.exception_handler(422)(validation_exception_handler)


# read_root serves as the authenticated root endpoint, returning a welcome message for authenticated users
@app.get("/")
@app.get("")
async def read_root(
    current_user: APIUser = Depends(get_current_user),
    rate_limit_info: dict = Depends(rate_limit),
) -> dict[str, str]:
    """
    Root endpoint that returns a welcome message.
    """
    return {"message": "Welcome to the Production API service!"}


# Configure CORS middleware to allow cross-origin requests with appropriate security settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,  # Allows cookies or credentials
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Specific allowed origins:
# app.add_middleware(
#     CORSMiddleware,
#     allow_origin_regex=(
#         r'^https:\/\/.*\.pipedream\.net$|'
#         r'^https:\/\/.*\.dirtyboots\.ai$|'
#         r'^https:\/\/.*\.beuseful\.ai$|'
#         r'^https:\/\/beusefulllc\.app\.n8n\.cloud$|'
#     ),
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Include API router for versioned API endpoints
app.include_router(api_router)
