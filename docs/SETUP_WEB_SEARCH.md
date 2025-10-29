# Web Search Integration Guide

This guide explains how to set up and use real web search capabilities in Continuum.

## Overview

Continuum supports three web search providers:
- **Brave Search** - Privacy-focused, fast, no tracking
- **Google Custom Search** - Comprehensive, many results
- **Tavily AI Search** - AI-optimized for research

By default, the system uses mock search results. Enable real search via feature flags.

## Feature Flags

### Enable Real Web Search

Set in `.env`:
```env
FEATURE_REAL_WEB_SEARCH=true
```

Or at runtime:
```python
from core.feature_flags import get_feature_flags, Feature
flags = get_feature_flags()
flags.enable(Feature.REAL_WEB_SEARCH)
```

### Disable (Fallback to Mock)

```env
FEATURE_REAL_WEB_SEARCH=false
```

Or:
```python
flags.disable(Feature.REAL_WEB_SEARCH)
```

## Setup by Provider

### 1. Brave Search

**Pros**: Privacy-focused, fast, reasonable limits
**Cons**: Smaller result set than Google
**Cost**: Free tier available, paid plans from $5/month

#### Setup Steps

1. Get API Key: https://api.search.brave.com/
2. Sign up for free tier (100 searches/day)
3. Add to `.env`:
   ```env
   BRAVE_SEARCH_API_KEY=your_api_key_here
   FEATURE_REAL_WEB_SEARCH=true
   ```

4. Verify:
   ```bash
   python3 -c "
   from agents.research_real import BraveSearchProvider
   import asyncio

   provider = BraveSearchProvider('your_api_key')
   results = asyncio.run(provider.search('artificial intelligence'))
   print(f'Found {len(results)} results')
   "
   ```

### 2. Google Custom Search

**Pros**: Most comprehensive, familiar results
**Cons**: Limited free queries (100/day), requires search engine ID
**Cost**: $5 per 1000 queries after free tier

#### Setup Steps

1. Create Custom Search Engine:
   - Go: https://programmablesearchengine.google.com/
   - Create new search engine (can search "entire web")

2. Get API Key:
   - Go: https://console.cloud.google.com/
   - Create project
   - Enable Custom Search API
   - Create API key

3. Add to `.env`:
   ```env
   GOOGLE_SEARCH_API_KEY=your_api_key_here
   GOOGLE_SEARCH_ENGINE_ID=your_engine_id_here
   FEATURE_REAL_WEB_SEARCH=true
   ```

4. Verify:
   ```bash
   python3 -c "
   from agents.research_real import GoogleSearchProvider
   import asyncio

   provider = GoogleSearchProvider(
       'api_key',
       'engine_id'
   )
   results = asyncio.run(provider.search('machine learning'))
   print(f'Found {len(results)} results')
   "
   ```

### 3. Tavily AI Search

**Pros**: AI-optimized for research, good for complex queries
**Cons**: Newer service, smaller result set
**Cost**: Free tier available, paid plans available

#### Setup Steps

1. Get API Key: https://tavily.com/
2. Sign up and copy API key
3. Add to `.env`:
   ```env
   TAVILY_API_KEY=your_api_key_here
   FEATURE_REAL_WEB_SEARCH=true
   ```

4. Verify:
   ```bash
   python3 -c "
   from agents.research_real import TavilySearchProvider
   import asyncio

   provider = TavilySearchProvider('your_api_key')
   results = asyncio.run(provider.search('neural networks'))
   print(f'Found {len(results)} results')
   "
   ```

## Using in Your Code

### Simple Usage

```python
from agents.research_adapter import SmartResearchAgent
from core.concept_orchestrator import ExplorationTask, ExplorationState

# Create agent
agent = SmartResearchAgent()

# Create task
task = ExplorationTask(
    id="task_123",
    concept="Artificial Intelligence",
    task_type="research",
    priority=10,
    status=ExplorationState.PENDING
)

# Process (automatically uses real search if enabled)
response = agent.process_task(task)

print(f"Found {len(response.data['sources'])} sources")
print(f"Real search: {response.metadata['real_search']}")
```

### Using Specific Provider

```python
from agents.research_real import search_web
import asyncio

# Search with specific provider
results = asyncio.run(search_web(
    query="machine learning",
    provider="brave",  # or "google", "tavily"
    max_results=10
))

for result in results:
    print(f"- {result['title']}")
    print(f"  {result['snippet']}")
    print(f"  {result['url']}\n")
```

### Check Available Providers

```python
from agents.research_real import WebSearchFactory

available = WebSearchFactory.get_available_providers()
print(f"Available providers: {available}")

# Use default provider
provider = WebSearchFactory.create_default_provider()
if provider:
    print(f"Using provider: {provider.__class__.__name__}")
```

### With Caching

```python
from agents.research_adapter import SmartResearchAgent

agent = SmartResearchAgent()

# First search (calls API)
response1 = agent.process_task(task)

# Second search same concept (uses cache)
response2 = agent.process_task(task)

# Check cache stats
stats = agent.get_cache_stats()
print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")

# Clear cache if needed
agent.clear_cache()
```

## Cost Optimization

### 1. Use Caching
- `SmartResearchAgent` automatically caches results
- Avoid duplicate searches for same concepts

### 2. Set Appropriate Limits
```python
# Use fewer results when possible
results = asyncio.run(search_web(
    "AI concepts",
    max_results=3  # Instead of 10
))
```

### 3. Choose Right Provider
- **Brave**: Best for quick searches, privacy-focused
- **Google**: Best for comprehensive results
- **Tavily**: Best for AI-optimized research

### 4. Batch Requests
```python
# Good: Batch multiple searches
concepts = ["AI", "ML", "DL", "NLP"]
for concept in concepts:
    results = asyncio.run(search_web(concept))
    # Process results

# Avoid: Individual requests with delay
for concept in concepts:
    time.sleep(1)  # Unnecessary delay
    results = asyncio.run(search_web(concept))
```

### 5. Monitor Usage
```python
from agents.research_adapter import SmartResearchAgent

agent = SmartResearchAgent()
# ... process tasks ...

stats = agent.get_cache_stats()
print(f"Concepts cached: {stats['cached_concepts']}")
print(f"Total searches: {stats['total_searches']}")
print(f"Cache efficiency: {stats['cache_hit_rate']:.2%}")
```

## Fallback Behavior

The system gracefully degrades if:
1. Feature flag is disabled → Uses mock data
2. API keys not configured → Uses mock data
3. API call fails → Falls back to mock data
4. Network timeout → Retries then falls back to mock

Example with real failures:

```python
# Even without API keys, this works:
response = agent.process_task(task)
# Returns mock data with success=True
```

## Testing

### Test with Mock Data
```bash
# Default (mock search)
FEATURE_REAL_WEB_SEARCH=false pytest tests/
```

### Test with Real Search
```bash
# Real search enabled
BRAVE_SEARCH_API_KEY=your_key \
FEATURE_REAL_WEB_SEARCH=true \
pytest tests/
```

### Integration Test Example

```python
import pytest
from agents.research_adapter import SmartResearchAgent
from core.feature_flags import get_feature_flags, Feature

@pytest.mark.asyncio
async def test_real_search_integration():
    """Test real web search integration."""
    flags = get_feature_flags()
    flags.enable(Feature.REAL_WEB_SEARCH)

    agent = SmartResearchAgent()
    task = ExplorationTask(
        id="test_task",
        concept="quantum computing",
        task_type="research",
        priority=10,
        status=ExplorationState.PENDING
    )

    response = agent.process_task(task)

    assert response.success
    assert len(response.data['sources']) > 0
    assert response.metadata['real_search'] is True
```

## Troubleshooting

### "No web search providers configured"
- Ensure API key is set in `.env` or environment
- Verify `FEATURE_REAL_WEB_SEARCH=true`
- Check API key validity

### "Real search returned no results"
- Try different search terms
- Check search provider status
- Ensure network connectivity
- System will fallback to mock data

### Rate Limiting
- Implement delays: `asyncio.sleep(0.5)` between searches
- Use caching to reduce API calls
- Consider upgrading to paid tier

### High Costs
- Enable caching
- Reduce `max_results` parameter
- Use Brave Search (most cost-effective)
- Filter results before processing

## Production Best Practices

1. **Use API Keys from Environment Only**
   ```python
   # Good
   api_key = os.getenv('BRAVE_SEARCH_API_KEY')

   # Bad - commits key to git
   api_key = "your_key_123"
   ```

2. **Monitor API Usage**
   - Set up quota alerts in provider dashboards
   - Log API calls for auditing
   - Track cache statistics

3. **Implement Circuit Breaker**
   ```python
   from resilience.circuit_breaker import CircuitBreaker

   search_breaker = CircuitBreaker(
       failure_threshold=5,
       recovery_timeout=300
   )
   ```

4. **Set Timeouts**
   ```python
   # All searches timeout after 10 seconds
   # (Configured in research_real.py)
   ```

5. **Log All Searches**
   - Enable debug logging to track API usage
   - Monitor error rates

## Advanced: Custom Provider

Create your own search provider:

```python
from agents.research_real import WebSearchProvider

class CustomSearchProvider(WebSearchProvider):
    async def search(self, query: str, max_results: int = 5):
        # Your implementation
        return [{
            "title": "...",
            "url": "...",
            "snippet": "...",
            "type": "web"
        }]
```

## Resources

- [Brave Search API](https://api.search.brave.com/)
- [Google Custom Search](https://programmablesearchengine.google.com/)
- [Tavily AI Search](https://tavily.com/)

## Next Steps

- Set up distributed tracing to monitor API latency
- Implement Redis caching for multi-instance consistency
- Configure rate limiting for production
- Add search result ranking/filtering
