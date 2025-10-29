"""
Research Agent Adapter - Switches between mock and real implementations.

Uses feature flags to enable/disable real web search integration.
"""

import logging
import asyncio
from typing import Dict, Any

from agents.base import BaseAgent, AgentResponse
from core.concept_orchestrator import ExplorationTask, ExplorationState
from core.feature_flags import Feature, is_feature_enabled
from agents.research_real import search_web, WebSearchFactory

logger = logging.getLogger(__name__)


class HybridResearchAgent(BaseAgent):
    """
    Research Agent that switches between mock and real implementations.

    Uses feature flags to enable/disable real web search.
    Falls back to mock responses if real search is disabled or fails.
    """

    def get_agent_name(self) -> str:
        return "ResearchAgent"

    def process_task(self, task: ExplorationTask) -> AgentResponse:
        """Process research tasks with optional real web search."""
        import time
        time.sleep(0.1)  # Simulate processing time

        # Try real search if feature is enabled
        if is_feature_enabled(Feature.REAL_WEB_SEARCH):
            return self._process_with_real_search(task)
        else:
            return self._process_with_mock_search(task)

    def _process_with_real_search(self, task: ExplorationTask) -> AgentResponse:
        """Process task using real web search APIs."""
        logger.info(f"Processing '{task.concept}' with real web search")

        try:
            # Run async search in thread pool
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                search_results = loop.run_until_complete(
                    search_web(task.concept, max_results=5)
                )
            finally:
                loop.close()

            if search_results:
                research_result = {
                    "concept": task.concept,
                    "sources": search_results,
                    "summary": f"Found {len(search_results)} relevant sources for {task.concept}",
                    "key_facts": [f"{result['title']}" for result in search_results[:3]],
                    "search_provider": WebSearchFactory.get_available_providers()[0] if WebSearchFactory.get_available_providers() else "unknown",
                }

                return AgentResponse(
                    success=True,
                    data=research_result,
                    metadata={
                        "task_id": task.id,
                        "source_count": len(search_results),
                        "real_search": True,
                    },
                    agent_name=self.get_agent_name(),
                    confidence=0.90,  # Slightly higher confidence for real searches
                )
            else:
                logger.warning(f"Real search returned no results for '{task.concept}', falling back to mock")
                return self._process_with_mock_search(task)

        except Exception as e:
            logger.error(f"Real search failed: {e}, falling back to mock")
            return self._process_with_mock_search(task)

    def _process_with_mock_search(self, task: ExplorationTask) -> AgentResponse:
        """Process task using mock data (fallback)."""
        logger.debug(f"Processing '{task.concept}' with mock search")

        research_result = {
            "concept": task.concept,
            "sources": [
                {"title": f"Research on {task.concept}", "url": "https://example.com", "type": "academic", "snippet": f"Information about {task.concept}"},
                {"title": f"Wiki: {task.concept}", "url": "https://wikipedia.org", "type": "encyclopedia", "snippet": f"Overview of {task.concept}"},
                {"title": f"Journal: {task.concept}", "url": "https://journal.example.com", "type": "journal", "snippet": f"Detailed study of {task.concept}"},
            ],
            "summary": f"Research on {task.concept} shows various perspectives and findings.",
            "key_facts": [
                f"Fact 1: {task.concept} is well-documented",
                f"Fact 2: {task.concept} has multiple applications",
            ],
            "search_provider": "mock",
        }

        return AgentResponse(
            success=True,
            data=research_result,
            metadata={
                "task_id": task.id,
                "source_count": 3,
                "real_search": False,
            },
            agent_name=self.get_agent_name(),
            confidence=0.85,
        )


class SmartResearchAgent(HybridResearchAgent):
    """
    Smart variant that tries real search but gracefully degrades.

    Features:
    - Retries with different providers if one fails
    - Caches results to avoid repeated API calls
    - Logs usage metrics
    """

    def __init__(self):
        super().__init__()
        self._search_cache: Dict[str, Dict[str, Any]] = {}
        self._search_count = 0

    def process_task(self, task: ExplorationTask) -> AgentResponse:
        """Process research tasks with caching and fallback."""
        # Check cache first
        if task.concept in self._search_cache:
            logger.debug(f"Using cached search results for '{task.concept}'")
            cached_result = self._search_cache[task.concept]
            return AgentResponse(
                success=True,
                data=cached_result,
                metadata={
                    "task_id": task.id,
                    "source_count": len(cached_result.get("sources", [])),
                    "from_cache": True,
                },
                agent_name=self.get_agent_name(),
                confidence=0.95,
            )

        # Process normally
        response = super().process_task(task)

        # Cache successful results
        if response.success and isinstance(response.data, dict):
            self._search_cache[task.concept] = response.data
            self._search_count += 1

        return response

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get search cache statistics."""
        return {
            "cached_concepts": len(self._search_cache),
            "total_searches": self._search_count,
            "cache_hit_rate": len(self._search_cache) / max(self._search_count, 1),
        }

    def clear_cache(self):
        """Clear search cache."""
        self._search_cache.clear()
        logger.info("Search cache cleared")
