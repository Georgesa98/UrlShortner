import psutil
import redis
from django.conf import settings
from config.redis_utils import get_redis_client
from enum import Enum
from datetime import datetime
from django.utils import timezone
from django.db import connection
from django.core.cache import cache


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class SystemService:
    """Service for system health monitoring and diagnostics."""

    def __init__(self) -> None:
        """Initialize the SystemService with Redis client."""
        try:
            self.redis_client = get_redis_client()
        except Exception:
            self.redis_client = None

    def _check_redis(self) -> dict:
        if not self.redis_client:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": "Redis client not initialized",
            }
        try:
            start = timezone.now()
            self.redis_client.ping()
            latency_ms = (timezone.now() - start).total_seconds() * 1000
            info = self.redis_client.info()
            memory_used_mb = info.get("used_memory", 0) / (1024 * 1024)
            connected_clients = info.get("connected_clients", 0)
            status = HealthStatus.HEALTHY
            if latency_ms > 500:
                status = HealthStatus.UNHEALTHY
            elif latency_ms > 100:
                status = HealthStatus.DEGRADED
            return {
                "status": status,
                "latency_ms": round(latency_ms, 2),
                "memory_used_mb": round(memory_used_mb, 2),
                "connected_clients": connected_clients,
                "uptime_seconds": info.get("uptime_in_seconds"),
                "host": settings.REDIS_HOST,
                "port": settings.REDIS_PORT,
                "db": settings.REDIS_DB,
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    def _check_celery(self) -> dict:
        try:
            broker_url = settings.CELERY_BROKER_URL
            celery_redis = redis.from_url(broker_url)
            start = timezone.now()
            celery_redis.ping()
            latency_ms = (timezone.now() - start).total_seconds() * 1000
            info = celery_redis.info()
            status = HealthStatus.HEALTHY
            if latency_ms > 500:
                status = HealthStatus.UNHEALTHY
            elif latency_ms > 100:
                status = HealthStatus.DEGRADED

            return {
                "status": status,
                "latency_ms": round(latency_ms, 2),
                "broker_url": (
                    broker_url.split("@")[-1] if "@" in broker_url else broker_url
                ),
                "broker_connected": True,
                "timezone": settings.CELERY_TIMEZONE,
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "error_type": type(e).__name__,
                "broker_connected": False,
            }

    def _check_disk(self) -> dict:
        try:
            disk = psutil.disk_usage("/")
            percent_used = disk.percent
            status = HealthStatus.HEALTHY
            if percent_used > 90:
                status = HealthStatus.UNHEALTHY
            elif percent_used > 80:
                status = HealthStatus.DEGRADED

            return {
                "status": status,
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent_used": percent_used,
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    def _check_memory(self) -> dict:
        try:
            memory = psutil.virtual_memory()
            percent_used = memory.percent
            status = HealthStatus.HEALTHY
            if percent_used > 90:
                status = HealthStatus.UNHEALTHY
            elif percent_used > 80:
                status = HealthStatus.DEGRADED

            return {
                "status": status,
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent_used": percent_used,
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    def _check_database(self) -> dict:
        try:
            start = timezone.now()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
            latency_ms = (timezone.now() - start).total_seconds() * 1000

            db_settings = settings.DATABASES["default"]

            status = HealthStatus.HEALTHY
            if latency_ms > 5000:
                status = HealthStatus.UNHEALTHY
            elif latency_ms > 1000:
                status = HealthStatus.DEGRADED
            return {
                "status": status,
                "latency_ms": round(latency_ms, 2),
                "vendor": "postgresql",
                "database": db_settings.get("NAME", "unknown"),
                "host": db_settings.get("HOST", "unknown"),
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "type": type(e).__name__,
            }

    def _check_cache(self) -> dict:
        try:
            start = timezone.now()
            test_key = "__health_check__"
            test_value = "ok"
            cache.set(test_key, test_value, 10)
            result = cache.get(test_key)
            cache.delete(test_key)
            latency_ms = (timezone.now() - start).total_seconds() * 1000
            status = HealthStatus.HEALTHY
            if latency_ms > 500:
                status = HealthStatus.UNHEALTHY
            elif latency_ms > 100:
                status = HealthStatus.DEGRADED
            return {
                "status": status,
                "latency_ms": round(latency_ms, 2),
                "cache": "RedisCache",
                "read_write_ok": result == test_value,
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "type": type(e).__name__,
            }

    def get_system_health(self) -> dict:
        """Get comprehensive system health report.

        Returns:
            dict: Health status for all system components including database, cache, Redis, Celery, disk, and memory.
        """
        components = {
            "database": self._check_database(),
            "cache": self._check_cache(),
            "redis": self._check_redis(),
            "celery": self._check_celery(),
            "disk": self._check_disk(),
            "memory": self._check_memory(),
        }
        statuses = [c["status"] for c in components.values()]
        if all(s == HealthStatus.HEALTHY for s in statuses):
            overall_status = HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED

        return {
            "status": overall_status,
            "timestamp": timezone.now().isoformat(),
            "components": components,
            "metadata": {
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
                "debug": settings.DEBUG,
            },
        }
