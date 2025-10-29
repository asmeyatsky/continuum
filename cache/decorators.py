"""
Caching Decorators - Easy-to-use decorators for caching function/method results.

Provides decorators for both sync and async functions with configurable TTL,
key generation, and conditional caching.
"""

import logging
import asyncio
import hashlib
import json
from typing import Callable, Any, Optional
from functools import wraps

from cache.cache_manager import get_cache

logger = logging.getLogger(__name__)


def _generate_cache_key(
    func_name: str, args: tuple, kwargs: dict, prefix: str = ""
) -> str:
    """
    Generate a cache key from function arguments.

    Args:
        func_name: Function name
        args: Positional arguments
        kwargs: Keyword arguments
        prefix: Optional prefix for key grouping

    Returns:
        Cache key string
    """
    key_data = {
        "func": func_name,
        "args": args,
        "kwargs": kwargs,
    }

    key_str = json.dumps(key_data, default=str, sort_keys=True)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()

    if prefix:
        return f"{prefix}:{func_name}:{key_hash}"
    return f"{func_name}:{key_hash}"


def cache_async(
    ttl: Optional[int] = 3600,
    prefix: str = "",
    condition: Optional[Callable[[Any], bool]] = None,
):
    """
    Decorator for caching async function results.

    Args:
        ttl: Time-to-live in seconds (None for no expiration)
        prefix: Prefix for cache key
        condition: Optional callable to determine if result should be cached

    Example:
        @cache_async(ttl=300, prefix="search")
        async def search_web(query: str) -> List[Dict]:
            # Web search implementation
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            cache = get_cache()
            cache_key = _generate_cache_key(func.__name__, args, kwargs, prefix)

            # Try to get from cache
            cached = await cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                return cached

            # Call original function
            result = await func(*args, **kwargs)

            # Cache result if condition met
            should_cache = condition is None or condition(result)
            if should_cache:
                await cache.set(cache_key, result, ttl)
                logger.debug(
                    f"Cached {func.__name__} result: {cache_key} (TTL: {ttl}s)"
                )

            return result

        return wrapper

    return decorator


def cache_sync(
    ttl: Optional[int] = 3600,
    prefix: str = "",
    condition: Optional[Callable[[Any], bool]] = None,
):
    """
    Decorator for caching sync function results.

    Args:
        ttl: Time-to-live in seconds (None for no expiration)
        prefix: Prefix for cache key
        condition: Optional callable to determine if result should be cached

    Example:
        @cache_sync(ttl=600, prefix="embedding")
        def get_embedding(text: str) -> List[float]:
            # Embedding computation
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            cache = get_cache()
            cache_key = _generate_cache_key(func.__name__, args, kwargs, prefix)

            # Try to get from cache (sync wrapper)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an async context, use sync fallback
                    logger.warning(
                        f"Cannot use sync cache decorator in async context: {func.__name__}"
                    )
                    return func(*args, **kwargs)

                cached = loop.run_until_complete(cache.get(cache_key))
                if cached is not None:
                    logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                    return cached

            except RuntimeError:
                # No event loop, create one
                cached = asyncio.run(cache.get(cache_key))
                if cached is not None:
                    logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                    return cached

            # Call original function
            result = func(*args, **kwargs)

            # Cache result if condition met
            should_cache = condition is None or condition(result)
            if should_cache:
                try:
                    loop = asyncio.get_event_loop()
                    if not loop.is_running():
                        loop.run_until_complete(cache.set(cache_key, result, ttl))
                    # If loop is running, skip caching to avoid issues
                except RuntimeError:
                    asyncio.run(cache.set(cache_key, result, ttl))

                logger.debug(
                    f"Cached {func.__name__} result: {cache_key} (TTL: {ttl}s)"
                )

            return result

        return wrapper

    return decorator


def cache_method(
    ttl: Optional[int] = 3600,
    prefix: str = "",
    condition: Optional[Callable[[Any], bool]] = None,
):
    """
    Decorator for caching instance method results.

    Uses instance name and method name in cache key for isolation.

    Args:
        ttl: Time-to-live in seconds
        prefix: Prefix for cache key
        condition: Optional callable to determine if result should be cached

    Example:
        class Agent:
            @cache_method(ttl=300)
            async def process_task(self, task_id: str):
                # Processing logic
                pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(self, *args, **kwargs) -> Any:
            cache = get_cache()
            instance_prefix = f"{self.__class__.__name__}:{prefix or func.__name__}"
            cache_key = _generate_cache_key(
                func.__name__, args, kwargs, instance_prefix
            )

            # Try cache
            cached = await cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {instance_prefix}: {cache_key}")
                return cached

            # Call function
            result = await func(self, *args, **kwargs)

            # Cache if condition met
            should_cache = condition is None or condition(result)
            if should_cache:
                await cache.set(cache_key, result, ttl)
                logger.debug(
                    f"Cached {instance_prefix} result: {cache_key} (TTL: {ttl}s)"
                )

            return result

        def sync_wrapper(self, *args, **kwargs) -> Any:
            cache = get_cache()
            instance_prefix = f"{self.__class__.__name__}:{prefix or func.__name__}"
            cache_key = _generate_cache_key(
                func.__name__, args, kwargs, instance_prefix
            )

            # Try cache
            try:
                cached = asyncio.run(cache.get(cache_key))
                if cached is not None:
                    logger.debug(f"Cache hit for {instance_prefix}: {cache_key}")
                    return cached
            except RuntimeError:
                pass

            # Call function
            result = func(self, *args, **kwargs)

            # Cache if condition met
            should_cache = condition is None or condition(result)
            if should_cache:
                try:
                    asyncio.run(cache.set(cache_key, result, ttl))
                    logger.debug(
                        f"Cached {instance_prefix} result: {cache_key} (TTL: {ttl}s)"
                    )
                except RuntimeError:
                    pass

            return result

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def invalidate_cache(prefix: str = ""):
    """
    Decorator that clears cache after function execution.

    Useful for mutations that should invalidate cached data.

    Args:
        prefix: Cache key prefix to invalidate

    Example:
        @invalidate_cache(prefix="embedding")
        async def update_embedding(concept_id: str, new_vector: List[float]):
            # Update logic
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            result = await func(*args, **kwargs)

            # Invalidate cache
            cache = get_cache()
            logger.info(f"Invalidating cache for prefix: {prefix}")
            await cache.clear()

            return result

        def sync_wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            # Invalidate cache
            try:
                cache = get_cache()
                asyncio.run(cache.clear())
                logger.info(f"Invalidating cache for prefix: {prefix}")
            except RuntimeError:
                logger.warning("Cannot invalidate cache in sync context")

            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
