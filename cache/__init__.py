"""
Cache Module - Unified caching infrastructure with Redis support.

Provides:
- CacheManager: Abstract cache interface
- RedisCache: Distributed Redis-backed cache
- LocalMemoryCache: In-memory cache for development
- Decorators: @cache_async, @cache_sync, @cache_method, @invalidate_cache
"""

from cache.cache_manager import (
    CacheManager,
    LocalMemoryCache,
    NoOpCache,
    get_cache,
    set_cache,
    initialize_cache,
)

from cache.redis_cache import RedisCache

from cache.decorators import (
    cache_async,
    cache_sync,
    cache_method,
    invalidate_cache,
)

__all__ = [
    "CacheManager",
    "LocalMemoryCache",
    "NoOpCache",
    "RedisCache",
    "get_cache",
    "set_cache",
    "initialize_cache",
    "cache_async",
    "cache_sync",
    "cache_method",
    "invalidate_cache",
]
