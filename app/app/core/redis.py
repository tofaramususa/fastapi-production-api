from upstash_redis import Redis
from app.core.config import settings
from typing import Optional
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class RedisConnectionError(Exception):
    """Custom exception for Redis connection errors"""

    pass


class RedisManager:
    _instance: Optional[Redis] = None
    _is_connected: bool = False

    @classmethod
    def get_instance(cls) -> Redis:
        if cls._instance is None:
            try:
                if (
                    not settings.UPSTASH_REDIS_REST_URL
                    or not settings.UPSTASH_REDIS_REST_TOKEN
                ):
                    logger.warning(
                        "Redis credentials not configured. Rate limiting will be disabled."
                    )
                    raise RedisConnectionError("Redis credentials not configured")

                cls._instance = Redis.from_env()
                # Test the connection
                cls._instance.ping()
                cls._is_connected = True
                logger.info("Successfully connected to Redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                cls._is_connected = False
                raise RedisConnectionError(f"Failed to connect to Redis: {str(e)}")
        return cls._instance

    @classmethod
    def is_connected(cls) -> bool:
        """Check if Redis is connected and working"""
        if not cls._is_connected:
            return False
        try:
            cls._instance.ping()
            return True
        except Exception:
            cls._is_connected = False
            return False

    @classmethod
    def reset_connection(cls) -> None:
        """Reset the Redis connection"""
        cls._instance = None
        cls._is_connected = False


# Global redis instance
try:
    redis = RedisManager.get_instance()
except RedisConnectionError:
    logger.warning("Redis connection failed. Rate limiting will be disabled.")
    redis = None
