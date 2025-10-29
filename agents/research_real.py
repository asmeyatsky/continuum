"""
Real web search implementations for the Research Agent.

Provides actual web search functionality via various APIs.
"""

import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import httpx
import asyncio

from config.settings import settings

logger = logging.getLogger(__name__)


class WebSearchProvider(ABC):
    """Abstract base class for web search providers."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web.

        Returns:
            List of search results with 'title', 'url', 'snippet' keys
        """
        pass


class BraveSearchProvider(WebSearchProvider):
    """Brave Search API integration."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search using Brave Search API."""
        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key,
            }
            params = {
                "q": query,
                "count": max_results,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("web", {}).get("results", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("description", ""),
                        "type": "web",
                    })

                logger.info(f"Brave Search: Found {len(results)} results for '{query}'")
                return results

        except Exception as e:
            logger.error(f"Brave Search error: {e}")
            return []


class GoogleSearchProvider(WebSearchProvider):
    """Google Custom Search API integration."""

    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API."""
        try:
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(max_results, 10),
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("items", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "type": "web",
                    })

                logger.info(f"Google Search: Found {len(results)} results for '{query}'")
                return results

        except Exception as e:
            logger.error(f"Google Search error: {e}")
            return []


class TavilySearchProvider(WebSearchProvider):
    """Tavily AI Search API integration."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search using Tavily AI Search API."""
        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": max_results,
                "include_answer": False,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("results", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", ""),
                        "type": "web",
                    })

                logger.info(f"Tavily Search: Found {len(results)} results for '{query}'")
                return results

        except Exception as e:
            logger.error(f"Tavily Search error: {e}")
            return []


class WebSearchFactory:
    """Factory for creating web search providers."""

    _providers: Dict[str, type] = {
        "brave": BraveSearchProvider,
        "google": GoogleSearchProvider,
        "tavily": TavilySearchProvider,
    }

    @staticmethod
    def create_provider(provider_name: str) -> Optional[WebSearchProvider]:
        """
        Create a web search provider.

        Args:
            provider_name: 'brave', 'google', or 'tavily'

        Returns:
            Initialized provider or None if not configured
        """
        provider_name = provider_name.lower()

        if provider_name == "brave":
            api_key = settings.BRAVE_SEARCH_API_KEY
            if api_key:
                logger.info("Initializing Brave Search provider")
                return BraveSearchProvider(api_key)
            logger.warning("Brave Search API key not configured")

        elif provider_name == "google":
            api_key = settings.GOOGLE_SEARCH_API_KEY
            search_engine_id = settings.GOOGLE_SEARCH_ENGINE_ID
            if api_key and search_engine_id:
                logger.info("Initializing Google Search provider")
                return GoogleSearchProvider(api_key, search_engine_id)
            logger.warning("Google Search API key or search engine ID not configured")

        elif provider_name == "tavily":
            api_key = settings.TAVILY_API_KEY
            if api_key:
                logger.info("Initializing Tavily Search provider")
                return TavilySearchProvider(api_key)
            logger.warning("Tavily API key not configured")

        else:
            logger.warning(f"Unknown search provider: {provider_name}")

        return None

    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of configured web search providers."""
        available = []

        if settings.BRAVE_SEARCH_API_KEY:
            available.append("brave")
        if settings.GOOGLE_SEARCH_API_KEY and settings.GOOGLE_SEARCH_ENGINE_ID:
            available.append("google")
        if settings.TAVILY_API_KEY:
            available.append("tavily")

        return available

    @staticmethod
    def create_default_provider() -> Optional[WebSearchProvider]:
        """Create a default web search provider (first available)."""
        available = WebSearchFactory.get_available_providers()

        if available:
            provider_name = available[0]
            logger.info(f"Using default web search provider: {provider_name}")
            return WebSearchFactory.create_provider(provider_name)

        logger.warning("No web search providers configured")
        return None


async def search_web(query: str, provider: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using configured providers.

    Args:
        query: Search query
        provider: Optional specific provider ('brave', 'google', 'tavily')
        max_results: Maximum number of results

    Returns:
        List of search results
    """
    if provider:
        search_provider = WebSearchFactory.create_provider(provider)
    else:
        search_provider = WebSearchFactory.create_default_provider()

    if not search_provider:
        logger.warning("No web search provider available")
        return []

    return await search_provider.search(query, max_results)
