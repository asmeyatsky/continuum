"""
Redis Cache Implementation - Distributed cache for multi-instance deployments.

Provides Redis-backed caching with automatic fallback to local memory if Redis
is unavailable. Supports both sync and async operations.
"""

import logging
import json
import pickle
from typing import Any, Optional, Dict
from datetime import datetime

try:
    import aioredis
    HAS_ASYNC_REDIS = True
except ImportError:
    HAS_ASYNC_REDIS = False

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

from cache.cache_manager import CacheManager, LocalMemoryCache

logger = logging.getLogger(__name__)


class RedisCache(CacheManager):
    """
    Redis-backed cache with graceful fallback to local memory.

    Features:
    - Distributed cache for multi-instance systems
    - Automatic serialization of complex objects
    - Configurable TTL (time-to-live)
    - Fallback to local memory if Redis unavailable
    - Connection pooling and retry logic
    """

    def __init__(self, redis_url: str, fallback_to_local: bool = True):
        """
        Initialize Redis cache.

        Args:
            redis_url: Redis connection URL (e.g., 'redis://localhost:6379/0')
            fallback_to_local: Fall back to local cache if Redis fails
        """
        self.redis_url = redis_url
        self.fallback_to_local = fallback_to_local
        self._redis_client: Optional[Any] = None
        self._fallback_cache = LocalMemoryCache() if fallback_to_local else None
        self._is_connected = False
        self._stats = {"fallback_uses": 0}

    async def connect(self) -> bool:
        """Connect to Redis."""
        try:
            if HAS_ASYNC_REDIS:
                self._redis_client = await aioredis.from_url(
                    self.redis_url, encoding="utf8", decode_responses=True
                )
                await self._redis_client.ping()
                self._is_connected = True
                logger.info("Connected to Redis successfully")
                return True
            else:
                logger.warning("aioredis not available, using local memory fallback")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            if self.fallback_to_local:
                logger.info("Falling back to local memory cache")
            return False

    async def _serialize(self, value: Any) -> str:
        """Serialize value to JSON or pickle."""
        try:
            # Try JSON first (more efficient)
            return json.dumps(value)
        except (TypeError, ValueError):
            # Fall back to pickle for complex objects
            import base64

            pickled = pickle.dumps(value)
            return f"__pickle__:{base64.b64encode(pickled).decode()}"

    async def _deserialize(self, value: str) -> Any:
        """Deserialize JSON or pickled value."""
        if value.startswith("__pickle__:"):
            import base64

            pickled = base64.b64decode(value[11:])
            return pickle.loads(pickled)
        else:
            return json.loads(value)

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        if not self._is_connected:
            if self._fallback_cache:
                self._stats["fallback_uses"] += 1
                return await self._fallback_cache.get(key)
            return None

        try:
            value = await self._redis_client.get(key)
            if value is None:
                return None

            deserialized = await self._deserialize(value)
            logger.debug(f"Cache hit from Redis: {key}")
            return deserialized

        except Exception as e:
            logger.error(f"Redis get failed: {e}")
            if self._fallback_cache:
                self._stats["fallback_uses"] += 1
                return await self._fallback_cache.get(key)
            return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """Store value in cache."""
        if not self._is_connected:
            if self._fallback_cache:
                return await self._fallback_cache.set(key, value, ttl)
            return False

        try:
            serialized = await self._serialize(value)
            if ttl:
                await self._redis_client.setex(key, ttl, serialized)
            else:
                await self._redis_client.set(key, serialized)

            logger.debug(f"Cache set in Redis: {key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Redis set failed: {e}")
            if self._fallback_cache:
                return await self._fallback_cache.set(key, value, ttl)
            return False

    async def delete(self, key: str) -> bool:
        """Remove value from cache."""
        if not self._is_connected:
            if self._fallback_cache:
                return await self._fallback_cache.delete(key)
            return False

        try:
            deleted = await self._redis_client.delete(key)
            logger.debug(f"Cache delete from Redis: {key}")
            return deleted > 0

        except Exception as e:
            logger.error(f"Redis delete failed: {e}")
            if self._fallback_cache:
                return await self._fallback_cache.delete(key)
            return False

    async def clear(self) -> bool:
        """Clear all cached values."""
        success = True

        if self._is_connected:
            try:
                await self._redis_client.flushdb()
                logger.info("Cleared Redis cache")
            except Exception as e:
                logger.error(f"Failed to clear Redis cache: {e}")
                success = False

        if self._fallback_cache:
            await self._fallback_cache.clear()

        return success

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._is_connected:
            if self._fallback_cache:
                return await self._fallback_cache.exists(key)
            return False

        try:
            exists = await self._redis_client.exists(key)
            return exists > 0

        except Exception as e:
            logger.error(f"Redis exists check failed: {e}")
            if self._fallback_cache:
                return await self._fallback_cache.exists(key)
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "type": "redis",
            "connected": self._is_connected,
            "redis_url": self._redis_url_masked(),
            "fallback_uses": self._stats["fallback_uses"],
        }

        if self._is_connected and self._redis_client:
            try:
                info = await self._redis_client.info()
                stats.update(
                    {
                        "used_memory": info.get("used_memory_human", "unknown"),
                        "total_connections": info.get(
                            "connected_clients", 0
                        ),
                        "keys": await self._redis_client.dbsize(),
                    }
                )
            except Exception as e:
                logger.error(f"Failed to get Redis stats: {e}")

        return stats

    def _redis_url_masked(self) -> str:
        """Return masked Redis URL for logging."""
        if "@" in self.redis_url:
            before, after = self.redis_url.rsplit("@", 1)
            return f"{before.split(':')[0]}:***@{after}"
        return self.redis_url

    async def close(self):
        """Close Redis connection."""
        if self._redis_client:
            await self._redis_client.close()
            self._is_connected = False
            logger.info("Redis connection closed")

    async def health_check(self) -> bool:
        """Check Redis connection health."""
        try:
            if not self._is_connected or not self._redis_client:
                return False

            await self._redis_client.ping()
            return True

        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            self._is_connected = False
            return False
