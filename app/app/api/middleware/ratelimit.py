from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from upstash_ratelimit import Ratelimit, SlidingWindow
from upstash_redis import Redis
import os
import logging
from datetime import datetime
import json
from app.api.auth import get_current_user, APIUser
from app.core.config import settings
from app.core.redis import redis, RedisManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter implementation using Upstash Redis"""

    def __init__(self):
        self._initialize_limiters()

    def _initialize_limiters(self):
        """Initialize rate limiters if Redis is available"""
        if not RedisManager.is_connected():
            logger.warning("Redis not available. Rate limiting will be disabled.")
            self.default_limiter = None
            self.admin_limiter = None
            self.product_creation_limiter = None
            return

        try:
            # Initialize rate limiters
            self.default_limiter = Ratelimit(
                redis=redis,
                limiter=SlidingWindow(
                    max_requests=settings.RATE_LIMIT_DEFAULT,
                    window=settings.RATE_LIMIT_WINDOW,
                ),
                prefix="ratelimit:default",
            )

            self.admin_limiter = Ratelimit(
                redis=redis,
                limiter=SlidingWindow(
                    max_requests=settings.RATE_LIMIT_ADMIN,
                    window=settings.RATE_LIMIT_ADMIN_WINDOW,
                ),
                prefix="ratelimit:admin",
            )

            self.product_creation_limiter = Ratelimit(
                redis=redis,
                limiter=SlidingWindow(
                    max_requests=settings.RATE_LIMIT_PRODUCT_CREATION_MAX,
                    window=settings.RATE_LIMIT_PRODUCT_CREATION_WINDOW,
                ),
                prefix="ratelimit:product_creation",
            )
        except Exception as e:
            logger.error(f"Failed to initialize rate limiters: {str(e)}")
            self.default_limiter = None
            self.admin_limiter = None
            self.product_creation_limiter = None

    async def check_rate_limit(self, request: Request, user: APIUser) -> dict:
        """Check if request is within rate limits and return rate limit info"""
        if not self.default_limiter or not self.admin_limiter:
            logger.warning("Rate limiting disabled - Redis not available")
            return {
                "limit": settings.RATE_LIMIT_DEFAULT,
                "remaining": settings.RATE_LIMIT_DEFAULT,
                "reset": int(datetime.now().timestamp()) + settings.RATE_LIMIT_WINDOW,
                "disabled": True,
            }

        # Get identifier (user ID or IP)
        identifier = f"user:{user.uid}" if user else f"ip:{request.client.host}"

        # Select limiter based on user type
        limiter = self.admin_limiter if user.is_admin else self.default_limiter

        try:
            # Check rate limit
            response = limiter.limit(identifier)
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # Don't block requests if rate limiting fails
            return {
                "limit": settings.RATE_LIMIT_DEFAULT,
                "remaining": settings.RATE_LIMIT_DEFAULT,
                "reset": int(datetime.now().timestamp()) + settings.RATE_LIMIT_WINDOW,
                "error": str(e),
            }

        if not response.allowed:
            # Track rate limit exceeded metric
            rate_limit_exceeded.labels(
                endpoint=request.url.path
            ).inc()
            
            logger.warning(
                f"Rate limit exceeded for {identifier}. "
                f"Limit: {response.limit}, Remaining: {response.remaining}, "
                f"Reset: {datetime.fromtimestamp(response.reset)}"
            )
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": int(response.reset - datetime.now().timestamp()),
                    "limit": response.limit,
                    "remaining": response.remaining,
                },
            )

        return {
            "limit": response.limit,
            "remaining": response.remaining,
            "reset": int(response.reset),
        }

    async def check_product_creation_limit(
        self, request: Request, user: APIUser
    ) -> dict:
        """Check if user can create a new product based on config settings"""
        if not self.product_creation_limiter:
            logger.warning(
                "Product creation rate limiting disabled - Redis not available"
            )
            return {
                "limit": settings.RATE_LIMIT_PRODUCT_CREATION_MAX,
                "remaining": settings.RATE_LIMIT_PRODUCT_CREATION_MAX,
                "reset": int(datetime.now().timestamp())
                + settings.RATE_LIMIT_PRODUCT_CREATION_WINDOW,
                "disabled": True,
            }

        identifier = f"user:{user.uid}"

        try:
            response = self.product_creation_limiter.limit(identifier)
        except Exception as e:
            logger.error(f"Product creation rate limiting error: {str(e)}")
            return {
                "limit": settings.RATE_LIMIT_PRODUCT_CREATION_MAX,
                "remaining": settings.RATE_LIMIT_PRODUCT_CREATION_MAX,
                "reset": int(datetime.now().timestamp())
                + settings.RATE_LIMIT_PRODUCT_CREATION_WINDOW,
                "error": str(e),
            }

        if not response.allowed:
            # Track rate limit exceeded metric for product creation
            rate_limit_exceeded.labels(
                endpoint="product_creation"
            ).inc()
            
            logger.warning(
                f"Product creation limit exceeded for {identifier}. "
                f"Reset: {datetime.fromtimestamp(response.reset)}"
            )
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Product creation limit exceeded",
                    "message": f"You can only create {settings.RATE_LIMIT_PRODUCT_CREATION_MAX} product(s) every {settings.RATE_LIMIT_PRODUCT_CREATION_WINDOW // 3600} hours",
                    "retry_after": int(response.reset - datetime.now().timestamp()),
                    "reset": int(response.reset),
                },
            )

        return {
            "limit": response.limit,
            "remaining": response.remaining,
            "reset": int(response.reset),
        }


# Create global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit(
    request: Request, current_user: APIUser = Depends(get_current_user)
) -> dict:
    """
    FastAPI dependency for rate limiting.
    Returns rate limit information that can be used in the response.

    Usage:
    @app.get("/endpoint")
    async def endpoint(rate_limit_info: dict = Depends(rate_limit)):
        return {"message": "success", "rate_limit": rate_limit_info}
    """
    return await rate_limiter.check_rate_limit(request, current_user)


async def product_creation_rate_limit(
    request: Request, current_user: APIUser = Depends(get_current_user)
) -> dict:
    """
    FastAPI dependency for product creation rate limiting.
    Uses the existing authenticated user.
    """
    return await rate_limiter.check_product_creation_limit(request, current_user)
