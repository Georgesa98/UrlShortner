import redis
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

_redis_client = None


def get_redis_client():
    """Get singleton Redis client with connection pooling.

    Returns:
        redis.Redis: Configured Redis client instance with pooling.
    """
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30,
            )
            logger.info("Redis client initialized with connection pooling")
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            raise
    return _redis_client


def check_redis_connection():
    """Check if Redis connection is healthy.

    Returns:
        bool: True if connection is working, False otherwise.
    """
    try:
        client = get_redis_client()
        client.ping()
        return True
    except redis.ConnectionError as e:
        logger.error(f"Redis connection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking Redis: {e}")
        return False
