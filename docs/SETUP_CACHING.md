# Caching System Setup Guide

This guide explains how to set up and use the distributed caching system in Continuum.

## Overview

Continuum supports three caching backends:
- **Local Memory Cache** (default) - Single instance, fast, no persistence
- **Redis Cache** - Distributed, multi-instance, persistent
- **No-Op Cache** - Disabled, useful for testing

## Quick Start (Local Development)

By default, the system uses local memory caching with 1-hour TTL:

```python
from cache import get_cache, initialize_cache

# Already initialized by default
cache = get_cache()

# Store a value
await cache.set("my_key", {"data": "value"}, ttl=3600)

# Retrieve a value
result = await cache.get("my_key")

# Delete a value
await cache.delete("my_key")

# Get cache statistics
stats = await cache.get_stats()
print(f"Cache hits: {stats.get('hits', 'N/A')}")
```

## Configuration

Update `.env` to control caching behavior:

```env
# Enable/disable caching
ENABLE_CACHING=true

# Cache backend: local, redis, or none
CACHE_TYPE=local

# TTL for cached values (seconds)
CACHE_TTL_SECONDS=3600

# Max size of local cache (entries)
CACHE_MAX_SIZE=1000

# Redis URL (required if CACHE_TYPE=redis)
REDIS_URL=redis://localhost:6379/0
```

## Setup by Cache Type

### 1. Local Memory Cache (Default)

**Pros**: No dependencies, fast, good for development
**Cons**: Not shared between instances, data lost on restart
**Best for**: Development, testing, single-instance deployments

**Setup**:
```env
CACHE_TYPE=local
ENABLE_CACHING=true
CACHE_MAX_SIZE=1000
CACHE_TTL_SECONDS=3600
```

**Usage**:
```python
from cache import initialize_cache, get_cache
import asyncio

async def demo():
    cache = get_cache()
    await cache.set("key", "value", ttl=300)
    value = await cache.get("key")
    print(value)

asyncio.run(demo())
```

### 2. Redis Cache

**Pros**: Distributed, multi-instance sharing, persistent, high performance
**Cons**: Requires Redis server, additional dependency
**Best for**: Production, multi-instance deployments, microservices

#### Setup Steps

**1. Install Redis**

macOS (using Homebrew):
```bash
brew install redis
brew services start redis
```

Ubuntu/Debian:
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

Docker:
```bash
docker run -d -p 6379:6379 --name continuum-redis redis:7-alpine
```

**2. Install Python Dependencies**

```bash
pip install redis aioredis
# or
pip install -r requirements.txt
```

**3. Configure Environment**

```env
CACHE_TYPE=redis
REDIS_URL=redis://localhost:6379/0
ENABLE_CACHING=true
CACHE_TTL_SECONDS=3600
```

**4. Initialize Cache**

```python
from cache import initialize_cache
import asyncio

async def setup():
    cache = await initialize_cache(
        cache_type="redis",
        redis_url="redis://localhost:6379/0"
    )
    print(f"Cache initialized: {cache.__class__.__name__}")

asyncio.run(setup())
```

**5. Verify Connection**

```bash
python3 -c "
import asyncio
from cache import initialize_cache

async def test():
    cache = await initialize_cache('redis', 'redis://localhost:6379/0')
    stats = await cache.get_stats()
    print(f'Redis stats: {stats}')

asyncio.run(test())
"
```

### 3. No-Op Cache (Disabled)

**Pros**: Useful for testing, debugging
**Cons**: No caching, performance impact
**Best for**: Testing, temporary debugging

```env
CACHE_TYPE=none
ENABLE_CACHING=false
```

## Using Caching in Your Code

### Caching Function Results

```python
from cache import cache_async, cache_sync

# Async function caching
@cache_async(ttl=300, prefix="embedding")
async def get_embedding(text: str):
    # Expensive computation
    return [0.1, 0.2, 0.3]

# Sync function caching
@cache_sync(ttl=600, prefix="analysis")
def analyze_text(text: str):
    # Analysis logic
    return {"score": 0.95}
```

### Caching Method Results

```python
from cache import cache_method

class ResearchAgent:
    @cache_method(ttl=1800, prefix="research")
    async def search_concept(self, concept: str):
        # Search logic
        return {"sources": [...]}

agent = ResearchAgent()
result = await agent.search_concept("AI")  # Computed
result = await agent.search_concept("AI")  # Retrieved from cache
```

### Conditional Caching

```python
from cache import cache_async

# Only cache successful results
def should_cache(result):
    return result.get("success", False)

@cache_async(ttl=300, condition=should_cache)
async def fetch_data(url: str):
    # Fetch logic
    return {"success": True, "data": [...]}
```

### Invalidating Cache

```python
from cache import invalidate_cache

@invalidate_cache(prefix="embedding")
async def update_embedding(concept_id: str):
    # Update logic
    # Cache is cleared after execution
    pass
```

## Integration Points

### 1. Embeddings Service

Embeddings are automatically cached when `ENABLE_CACHING=true`:

```python
from embeddings.service import EmbeddingService

service = EmbeddingService()

# First call - computed and cached
embedding1 = service.encode("artificial intelligence")

# Second call - retrieved from cache
embedding2 = service.encode("artificial intelligence")
```

### 2. Research Agent

Web search results are cached by default:

```python
from agents.research_adapter import SmartResearchAgent
from core.concept_orchestrator import ExplorationTask, ExplorationState

agent = SmartResearchAgent()

task = ExplorationTask(
    id="task_1",
    concept="machine learning",
    task_type="research",
    priority=10,
    status=ExplorationState.PENDING
)

# First search - calls API and caches result
response1 = agent.process_task(task)

# Second search - retrieved from cache
response2 = agent.process_task(task)

# Get cache statistics
stats = agent.get_cache_stats()
print(f"Cache type: {stats['cache_type']}")
```

### 3. Knowledge Graph

Semantic search results can be cached:

```python
from knowledge_graph.engine import InMemoryKnowledgeGraphEngine

engine = InMemoryKnowledgeGraphEngine()

# Add nodes
engine.add_node(node1)
engine.add_node(node2)

# Find similar (cached if caching enabled)
similar = engine.find_similar_nodes(query_embedding, threshold=0.7)
```

## Performance Optimization

### 1. Cache Key Design

Good cache keys should:
- Include all parameters that affect the result
- Be concise but unique
- Use consistent prefixes for grouping

```python
# Good
cache_key = f"embedding:{model_name}:{text[:100]}"
cache_key = f"research:web:{concept}"

# Avoid - too long, includes unstable data
cache_key = f"result:{timestamp}:{full_text}"
```

### 2. TTL Configuration

Choose appropriate TTLs for different data:

```env
# Embeddings - stable, long TTL
CACHE_TTL_SECONDS=86400  # 24 hours

# API results - medium TTL
CACHE_TTL_SECONDS=3600   # 1 hour

# Session data - short TTL
CACHE_TTL_SECONDS=300    # 5 minutes
```

### 3. Local Cache Size Management

```python
# Configure max size to prevent memory issues
from cache import LocalMemoryCache

cache = LocalMemoryCache(max_size=5000)

# LRU (Least Recently Used) entries are evicted automatically
```

### 4. Multi-Instance Deployment

When using Redis, all instances share the cache:

```
Instance 1              Instance 2
    |                       |
    +--------> Redis <------+
              (shared cache)
```

**Benefit**: Reduce redundant API calls across instances

**Example**:
```
Instance 1: Searches "AI" → Result cached in Redis
Instance 2: Searches "AI" → Retrieves from shared Redis cache
Instance 3: Searches "AI" → Retrieves from shared Redis cache
```

## Monitoring & Statistics

### Get Cache Statistics

```python
from cache import get_cache
import asyncio

async def monitor():
    cache = get_cache()
    stats = await cache.get_stats()

    print(f"Cache Type: {stats['type']}")
    print(f"Hit Rate: {stats.get('hit_rate', 'N/A'):.2%}")
    print(f"Size: {stats.get('entries', 'N/A')}")

asyncio.run(monitor())
```

### Monitor Research Agent

```python
agent = SmartResearchAgent()

# Process some tasks...
response = agent.process_task(task)

# Get statistics
stats = agent.get_cache_stats()
print(f"Cache Type: {stats['cache_type']}")
print(f"Cached Concepts: {stats['local_cached_concepts']}")
print(f"Hit Rate: {stats['cache_hit_rate']:.2%}")
```

### Redis Monitoring

```bash
# Monitor Redis commands in real-time
redis-cli monitor

# Get Redis stats
redis-cli info

# Check keys
redis-cli KEYS "research:*"

# Clear specific pattern
redis-cli DEL "research:*"
```

## Cost Optimization

### 1. Use Caching Strategically

```python
# Cache expensive operations
@cache_async(ttl=3600)
async def get_embedding(text: str):
    # Expensive embedding computation
    pass

# Don't cache cheap operations
async def validate_input(data: str):
    # Fast validation - no caching needed
    pass
```

### 2. Set Appropriate TTLs

```env
# Balance between freshness and cache efficiency
CACHE_TTL_SECONDS=3600  # 1 hour for web search
```

### 3. Monitor Cache Hit Rate

```python
stats = await cache.get_stats()
hit_rate = stats.get('hit_rate', 0)

if hit_rate < 0.5:
    # Low hit rate - consider:
    # 1. Increasing TTL
    # 2. Widening cache key matching
    # 3. Increasing local cache size
```

### 4. Avoid Cache Stampede

```python
# Good - set reasonable TTL, distribute updates
@cache_async(ttl=300)  # 5 minutes
async def search(query: str):
    return await api.search(query)

# Bad - cache never expires, then all keys expire together
@cache_async(ttl=None)
async def search(query: str):
    return await api.search(query)
```

## Troubleshooting

### Redis Connection Failed

```
Error: Connection refused
```

**Solution**: Ensure Redis is running
```bash
redis-cli ping  # Should return PONG
brew services restart redis  # or sudo systemctl restart redis-server
```

### Memory Issues with Local Cache

```
MemoryError: Cannot allocate memory
```

**Solution**: Reduce local cache size or switch to Redis
```env
CACHE_TYPE=redis  # Use distributed Redis cache
CACHE_MAX_SIZE=500  # Or reduce local cache size
```

### Cache Key Conflicts

**Problem**: Different data sharing same cache key

**Solution**: Use better prefixes
```python
# Before - collisions
cache_key = f"embedding:{text}"

# After - better isolation
cache_key = f"embedding:{model_name}:{text[:100]}"
```

### Cache not Working

**Check**:
1. Is `ENABLE_CACHING=true`?
2. What is `CACHE_TYPE`?
3. If Redis: Is `REDIS_URL` correct and Redis running?

```python
from cache import get_cache

cache = get_cache()
print(f"Cache type: {cache.__class__.__name__}")
print(f"Is connected: {hasattr(cache, '_is_connected') and cache._is_connected}")
```

## Production Best Practices

1. **Use Redis for Multi-Instance Deployments**
   ```env
   CACHE_TYPE=redis
   REDIS_URL=redis://prod-redis.example.com:6379/0
   ```

2. **Set Reasonable TTLs**
   ```env
   CACHE_TTL_SECONDS=3600
   ```

3. **Monitor Cache Hit Rate**
   - Target: >70% hit rate
   - If below 50%: Increase TTL or reduce key complexity

4. **Implement Cache Warming**
   ```python
   async def warm_cache():
       # Pre-load frequently accessed data
       for concept in popular_concepts:
           await cache.set(f"research:{concept}", result, ttl=86400)
   ```

5. **Plan for Cache Invalidation**
   ```python
   @invalidate_cache(prefix="research")
   async def update_knowledge_graph():
       # Update graph
       # Cache is invalidated after
       pass
   ```

6. **Regular Backups**
   ```bash
   # For Redis
   redis-cli BGSAVE
   ```

## Performance Metrics

Typical improvements with caching enabled:

| Operation | Without Cache | With Cache | Improvement |
|-----------|---------------|-----------|-------------|
| Embedding | 150ms | 1ms | 150x |
| Web Search | 2000ms | 1ms | 2000x |
| Semantic Search | 500ms | 10ms | 50x |
| Knowledge Graph Query | 100ms | 2ms | 50x |

## Testing with Caching

### Run Tests with Caching Enabled

```bash
CACHE_TYPE=local pytest tests/ -v
```

### Run Tests with Redis

```bash
CACHE_TYPE=redis REDIS_URL=redis://localhost:6379/1 pytest tests/ -v
```

### Run Tests without Caching

```bash
CACHE_TYPE=none pytest tests/ -v
```

## Next Steps

- [Setting Up Web Search](./SETUP_WEB_SEARCH.md)
- [Setting Up PostgreSQL](./SETUP_POSTGRES.md)
- [Feature Flags Guide](./FEATURE_FLAGS.md)
- [Distributed Tracing Setup](./SETUP_TRACING.md) (coming soon)

## Resources

- [Redis Documentation](https://redis.io/documentation)
- [aioredis Documentation](https://aioredis.readthedocs.io/)
- [Caching Best Practices](https://docs.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
