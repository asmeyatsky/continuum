"""
Cache Manager - Abstract cache interface supporting multiple backends.

Provides a unified interface for caching across the system with support for:
- Redis (distributed, multi-instance)
- In-memory (local, fallback)
- No-op (disabled)
"""

import logging
import json
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a cached entry with metadata."""

    def __init__(self, key: str, value: Any, ttl: Optional[int] = None):
        self.key = key
        self.value = value
        self.ttl = ttl
        self.created_at = datetime.now()
        self.accessed_at = datetime.now()
        self.access_count = 0

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl is None:
            return False
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.ttl

    def update_access(self):
        """Update access timestamp and count."""
        self.accessed_at = datetime.now()
        self.access_count += 1


class CacheManager(ABC):
    """Abstract base class for cache implementations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        pass

    @abstractmethod
    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """Store value in cache with optional TTL in seconds."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Remove value from cache."""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cached values."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class LocalMemoryCache(CacheManager):
    """In-memory cache implementation for local/development use."""

    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self._hits = 0
        self._misses = 0

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        if key not in self._cache:
            self._misses += 1
            return None

        entry = self._cache[key]

        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            return None

        entry.update_access()
        self._hits += 1
        logger.debug(f"Cache hit: {key}")
        return entry.value

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """Store value in cache."""
        if len(self._cache) >= self.max_size:
            # Remove least recently used entry
            lru_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].accessed_at,
            )
            del self._cache[lru_key]
            logger.debug(f"Evicted LRU entry: {lru_key}")

        self._cache[key] = CacheEntry(key, value, ttl)
        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
        return True

    async def delete(self, key: str) -> bool:
        """Remove value from cache."""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache delete: {key}")
            return True
        return False

    async def clear(self) -> bool:
        """Clear all cached values."""
        self._cache.clear()
        logger.info("Cache cleared")
        return True

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if key not in self._cache:
            return False

        entry = self._cache[key]
        if entry.is_expired():
            del self._cache[key]
            return False

        return True

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0

        return {
            "type": "local_memory",
            "entries": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "total_requests": total,
        }


class NoOpCache(CacheManager):
    """No-op cache implementation when caching is disabled."""

    async def get(self, key: str) -> Optional[Any]:
        """Always returns None."""
        return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """No-op."""
        return True

    async def delete(self, key: str) -> bool:
        """No-op."""
        return True

    async def clear(self) -> bool:
        """No-op."""
        return True

    async def exists(self, key: str) -> bool:
        """Always returns False."""
        return False

    async def get_stats(self) -> Dict[str, Any]:
        """Return empty stats."""
        return {"type": "no_op", "enabled": False}


# Global cache instance
_cache_instance: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Get the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = LocalMemoryCache()
    return _cache_instance


def set_cache(cache: CacheManager):
    """Set the global cache instance."""
    global _cache_instance
    _cache_instance = cache
    logger.info(f"Cache backend set to: {cache.__class__.__name__}")


async def initialize_cache(
    cache_type: str = "local", redis_url: Optional[str] = None
) -> CacheManager:
    """
    Initialize cache based on type.

    Args:
        cache_type: "redis", "local", or "none"
        redis_url: Redis URL if using Redis

    Returns:
        Initialized cache manager
    """
    if cache_type == "redis":
        try:
            from cache.redis_cache import RedisCache

            if not redis_url:
                raise ValueError("redis_url required for Redis cache")

            cache = RedisCache(redis_url)
            await cache.connect()
            set_cache(cache)
            logger.info("Redis cache initialized successfully")
            return cache
        except Exception as e:
            logger.warning(
                f"Failed to initialize Redis cache: {e}, falling back to local memory"
            )
            cache = LocalMemoryCache()
            set_cache(cache)
            return cache

    elif cache_type == "local":
        cache = LocalMemoryCache()
        set_cache(cache)
        logger.info("Local memory cache initialized")
        return cache

    else:
        cache = NoOpCache()
        set_cache(cache)
        logger.info("No-op cache initialized (caching disabled)")
        return cache
