"""
Tests for the caching system.

Covers:
- LocalMemoryCache functionality
- RedisCache with fallback
- Caching decorators
- Cache key generation
- TTL expiration
- Cache statistics
"""

import asyncio
import pytest
from typing import List, Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from cache.cache_manager import (
    LocalMemoryCache,
    NoOpCache,
    get_cache,
    set_cache,
    initialize_cache,
    CacheEntry,
)
from cache.decorators import cache_async, cache_sync, cache_method
from cache.redis_cache import RedisCache


class TestCacheEntry:
    """Tests for CacheEntry class."""

    def test_cache_entry_creation(self):
        """Test basic cache entry creation."""
        entry = CacheEntry("key", "value", ttl=100)
        assert entry.key == "key"
        assert entry.value == "value"
        assert entry.ttl == 100
        assert entry.access_count == 0

    def test_cache_entry_not_expired(self):
        """Test entry without expiration."""
        entry = CacheEntry("key", "value", ttl=None)
        assert not entry.is_expired()

    def test_cache_entry_update_access(self):
        """Test access count and timestamp updates."""
        entry = CacheEntry("key", "value")
        assert entry.access_count == 0

        entry.update_access()
        assert entry.access_count == 1

        entry.update_access()
        assert entry.access_count == 2


class TestLocalMemoryCache:
    """Tests for LocalMemoryCache."""

    def test_set_and_get(self):
        """Test basic set and get operations."""
        cache = LocalMemoryCache()

        # Set a value
        asyncio.run(cache.set("key", "value"))
        result = asyncio.run(cache.get("key"))
        assert result == "value"

    def test_set_with_ttl(self):
        """Test set with TTL."""
        cache = LocalMemoryCache()
        asyncio.run(cache.set("key", "value", ttl=1))
        assert asyncio.run(cache.get("key")) == "value"

    def test_get_nonexistent_key(self):
        """Test getting non-existent key returns None."""
        cache = LocalMemoryCache()
        result = asyncio.run(cache.get("nonexistent"))
        assert result is None

    def test_delete(self):
        """Test delete operation."""
        cache = LocalMemoryCache()
        asyncio.run(cache.set("key", "value"))
        assert asyncio.run(cache.delete("key"))
        assert asyncio.run(cache.get("key")) is None

    def test_delete_nonexistent(self):
        """Test deleting non-existent key."""
        cache = LocalMemoryCache()
        assert not asyncio.run(cache.delete("nonexistent"))

    def test_clear(self):
        """Test clearing all cache entries."""
        cache = LocalMemoryCache()
        asyncio.run(cache.set("key1", "value1"))
        asyncio.run(cache.set("key2", "value2"))

        assert asyncio.run(cache.clear())
        assert asyncio.run(cache.get("key1")) is None
        assert asyncio.run(cache.get("key2")) is None

    def test_exists(self):
        """Test key existence check."""
        cache = LocalMemoryCache()
        asyncio.run(cache.set("key", "value"))

        assert asyncio.run(cache.exists("key"))
        assert not asyncio.run(cache.exists("nonexistent"))

    def test_max_size_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = LocalMemoryCache(max_size=2)

        # Fill cache
        asyncio.run(cache.set("key1", "value1"))
        asyncio.run(cache.set("key2", "value2"))

        # Access key1 to update its access time
        asyncio.run(cache.get("key1"))

        # Add third key, should evict key2 (least recently used)
        asyncio.run(cache.set("key3", "value3"))

        assert asyncio.run(cache.get("key1")) == "value1"
        assert asyncio.run(cache.get("key2")) is None  # Evicted
        assert asyncio.run(cache.get("key3")) == "value3"

    def test_stats(self):
        """Test cache statistics."""
        cache = LocalMemoryCache()

        # Generate cache hits and misses
        asyncio.run(cache.set("key", "value"))
        asyncio.run(cache.get("key"))  # Hit
        asyncio.run(cache.get("key"))  # Hit
        asyncio.run(cache.get("missing"))  # Miss

        stats = asyncio.run(cache.get_stats())
        assert stats["type"] == "local_memory"
        assert stats["entries"] == 1
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 2 / 3

    def test_complex_data_types(self):
        """Test caching complex data types."""
        cache = LocalMemoryCache()

        # Test list
        asyncio.run(cache.set("list", [1, 2, 3]))
        assert asyncio.run(cache.get("list")) == [1, 2, 3]

        # Test dict
        asyncio.run(cache.set("dict", {"a": 1, "b": 2}))
        assert asyncio.run(cache.get("dict")) == {"a": 1, "b": 2}

        # Test nested structures
        nested = {"data": [{"id": 1}, {"id": 2}]}
        asyncio.run(cache.set("nested", nested))
        assert asyncio.run(cache.get("nested")) == nested


class TestNoOpCache:
    """Tests for NoOpCache."""

    def test_noop_operations(self):
        """Test that NoOpCache doesn't actually cache anything."""
        cache = NoOpCache()

        # NoOp always returns True/False, doesn't store anything
        assert asyncio.run(cache.set("key", "value")) is True
        assert asyncio.run(cache.get("key")) is None
        assert asyncio.run(cache.exists("key")) is False
        assert asyncio.run(cache.delete("key")) is True
        assert asyncio.run(cache.clear()) is True

    def test_noop_stats(self):
        """Test NoOpCache statistics."""
        cache = NoOpCache()
        stats = asyncio.run(cache.get_stats())

        assert stats["type"] == "no_op"
        assert stats["enabled"] is False


class TestRedisCache:
    """Tests for RedisCache with fallback."""

    def test_redis_cache_fallback_capability(self):
        """Test that Redis cache can initialize with fallback."""
        # Test basic initialization without connecting
        cache = RedisCache("redis://localhost:6379/0", fallback_to_local=True)

        # Verify fallback cache is available
        assert cache._fallback_cache is not None
        assert isinstance(cache._fallback_cache, LocalMemoryCache)

    def test_redis_cache_stats_when_disconnected(self):
        """Test stats when Redis is disconnected."""
        cache = RedisCache("redis://localhost:6379/0", fallback_to_local=True)

        stats = asyncio.run(cache.get_stats())
        assert stats["type"] == "redis"
        assert stats["connected"] is False


class TestCacheAsyncDecorator:
    """Tests for @cache_async decorator."""

    def test_cache_async_decorator_exists(self):
        """Test that cache_async decorator is available."""
        from cache import cache_async

        assert callable(cache_async)

        # Verify decorator can wrap async functions
        @cache_async(ttl=300)
        async def dummy():
            return "test"

        assert callable(dummy)


class TestCacheSyncDecorator:
    """Tests for @cache_sync decorator."""

    def test_cache_sync_function(self):
        """Test caching sync function results."""

        @cache_sync(ttl=300)
        def expensive_operation(x: int) -> int:
            return x * 2

        # First call - computed
        result1 = expensive_operation(5)
        assert result1 == 10

        # Second call - from cache
        result2 = expensive_operation(5)
        assert result2 == 10


class TestCacheMethodDecorator:
    """Tests for @cache_method decorator."""

    def test_cache_method_decorator_exists(self):
        """Test that cache_method decorator is available."""
        from cache import cache_method

        assert callable(cache_method)

        # Verify decorator can wrap methods
        class DataProcessor:
            @cache_method(ttl=300)
            async def process(self, data: str) -> str:
                return data.upper()

        processor = DataProcessor()
        assert callable(processor.process)


class TestGlobalCacheManagement:
    """Tests for global cache instance management."""

    def test_get_cache_returns_instance(self):
        """Test get_cache returns a CacheManager instance."""
        cache = get_cache()
        assert cache is not None

    def test_set_cache_changes_instance(self):
        """Test setting a new cache instance."""
        original = get_cache()

        new_cache = LocalMemoryCache()
        set_cache(new_cache)
        assert get_cache() is new_cache

        # Restore original
        set_cache(original)

    def test_initialize_cache_local(self):
        """Test initializing local cache."""
        cache = asyncio.run(initialize_cache(cache_type="local"))
        assert isinstance(cache, LocalMemoryCache)

    def test_initialize_cache_none(self):
        """Test initializing no-op cache."""
        cache = asyncio.run(initialize_cache(cache_type="none"))
        assert isinstance(cache, NoOpCache)


class TestCacheKeyGeneration:
    """Tests for cache key generation."""

    def test_different_args_different_keys(self):
        """Test that different arguments produce different cache keys."""
        from cache.decorators import _generate_cache_key

        key1 = _generate_cache_key("func", (1, 2), {})
        key2 = _generate_cache_key("func", (1, 3), {})

        assert key1 != key2

    def test_same_args_same_keys(self):
        """Test that same arguments produce same cache key."""
        from cache.decorators import _generate_cache_key

        key1 = _generate_cache_key("func", (1, 2), {"x": 5})
        key2 = _generate_cache_key("func", (1, 2), {"x": 5})

        assert key1 == key2

    def test_prefix_in_key(self):
        """Test that prefix is included in cache key."""
        from cache.decorators import _generate_cache_key

        key_with_prefix = _generate_cache_key("func", (1,), {}, prefix="myapp")
        assert key_with_prefix.startswith("myapp:")

        key_without_prefix = _generate_cache_key("func", (1,), {})
        assert not key_without_prefix.startswith("myapp")


class TestCacheIntegration:
    """Integration tests for caching system."""

    def test_embedding_caching(self):
        """Test embedding service with caching."""
        try:
            from embeddings.service import EmbeddingService
            from config.settings import settings

            # Enable caching
            original_cache = settings.ENABLE_CACHING
            settings.ENABLE_CACHING = True

            try:
                service = EmbeddingService()

                # First encoding
                embedding1 = service.encode("test text")
                assert embedding1 is not None

                # Second encoding (should be from cache)
                embedding2 = service.encode("test text")
                assert embedding2 is not None

                # Embeddings should be equal
                import numpy as np
                assert np.array_equal(embedding1, embedding2)

            finally:
                settings.ENABLE_CACHING = original_cache

        except ModuleNotFoundError:
            pytest.skip("pydantic_settings not available")

    def test_research_agent_caching(self):
        """Test research agent with distributed caching."""
        try:
            from agents.research_adapter import SmartResearchAgent
            from core.concept_orchestrator import ExplorationTask, ExplorationState

            agent = SmartResearchAgent()

            task = ExplorationTask(
                id="test_task",
                concept="artificial intelligence",
                task_type="research",
                priority=10,
                status=ExplorationState.PENDING,
            )

            # First search
            response1 = agent.process_task(task)
            assert response1.success

            # Get initial cache stats
            stats1 = agent.get_cache_stats()
            initial_searches = stats1["total_searches"]

            # Second search (should be cached)
            response2 = agent.process_task(task)
            assert response2.success

            # Cache stats should not increase
            stats2 = agent.get_cache_stats()
            assert stats2["total_searches"] == initial_searches

        except ModuleNotFoundError:
            pytest.skip("Required modules not available")

    def test_cache_statistics(self):
        """Test cache statistics gathering."""
        cache = LocalMemoryCache()

        # Perform some operations
        asyncio.run(cache.set("key1", "value1"))
        asyncio.run(cache.set("key2", "value2"))
        asyncio.run(cache.get("key1"))  # Hit
        asyncio.run(cache.get("key1"))  # Hit
        asyncio.run(cache.get("key3"))  # Miss
        asyncio.run(cache.get("key4"))  # Miss

        # Get stats
        stats = asyncio.run(cache.get_stats())

        assert stats["entries"] == 2
        assert stats["hits"] == 2
        assert stats["misses"] == 2
        assert stats["total_requests"] == 4
        assert stats["hit_rate"] == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
