"""
Image Generation Agent Adapter - Switches between real and mock implementations.

Uses feature flags to enable/disable real image generation.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List

from agents.base import BaseAgent, AgentResponse
from core.concept_orchestrator import ExplorationTask, ExplorationState
from core.feature_flags import Feature, is_feature_enabled
from agents.image_generation import generate_images
from config.settings import settings
from cache import get_cache

logger = logging.getLogger(__name__)


class HybridImageAgent(BaseAgent):
    """
    Image Generation Agent that switches between mock and real implementations.

    Uses feature flags to enable/disable real image generation.
    Falls back to mock responses if real generation is disabled or fails.
    """

    def get_agent_name(self) -> str:
        return "ImageAgent"

    def process_task(self, task: ExplorationTask) -> AgentResponse:
        """Process image generation tasks."""
        import time

        time.sleep(0.1)  # Simulate processing time

        # Try real generation if feature is enabled
        if is_feature_enabled(Feature.REAL_IMAGE_GENERATION):
            return self._process_with_real_generation(task)
        else:
            return self._process_with_mock_generation(task)

    def _process_with_real_generation(self, task: ExplorationTask) -> AgentResponse:
        """Process task using real image generation APIs."""
        logger.info(f"Generating images for '{task.concept}' with real generation")

        try:
            # Run async generation in thread pool
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                images = loop.run_until_complete(
                    generate_images(
                        prompt=f"Concept art illustration of {task.concept}",
                        count=3,
                        size="1024x1024",
                        openai_api_key=settings.OPENAI_API_KEY,
                        stable_diffusion_endpoint=settings.STABLE_DIFFUSION_ENDPOINT,
                    )
                )
            finally:
                loop.close()

            if images:
                generation_result = {
                    "concept": task.concept,
                    "images": images,
                    "summary": f"Generated {len(images)} images for {task.concept}",
                    "image_count": len(images),
                }

                return AgentResponse(
                    success=True,
                    data=generation_result,
                    metadata={
                        "task_id": task.id,
                        "image_count": len(images),
                        "real_generation": True,
                    },
                    agent_name=self.get_agent_name(),
                    confidence=0.90,
                )
            else:
                logger.warning(
                    f"Real generation returned no images for '{task.concept}', falling back to mock"
                )
                return self._process_with_mock_generation(task)

        except Exception as e:
            logger.error(f"Real generation failed: {e}, falling back to mock")
            return self._process_with_mock_generation(task)

    def _process_with_mock_generation(self, task: ExplorationTask) -> AgentResponse:
        """Process task using mock generated images."""
        logger.debug(f"Generating mock images for '{task.concept}'")

        generation_result = {
            "concept": task.concept,
            "images": [
                {
                    "url": f"https://placeholder.com/1024x1024?text={task.concept}+1",
                    "prompt": f"Concept art of {task.concept}",
                    "provider": "mock",
                    "size": "1024x1024",
                },
                {
                    "url": f"https://placeholder.com/1024x1024?text={task.concept}+2",
                    "prompt": f"Abstract representation of {task.concept}",
                    "provider": "mock",
                    "size": "1024x1024",
                },
                {
                    "url": f"https://placeholder.com/1024x1024?text={task.concept}+3",
                    "prompt": f"Detailed illustration of {task.concept}",
                    "provider": "mock",
                    "size": "1024x1024",
                },
            ],
            "summary": f"Generated 3 mock images for {task.concept}",
            "image_count": 3,
        }

        return AgentResponse(
            success=True,
            data=generation_result,
            metadata={
                "task_id": task.id,
                "image_count": 3,
                "real_generation": False,
            },
            agent_name=self.get_agent_name(),
            confidence=0.85,
        )


class SmartImageAgent(HybridImageAgent):
    """
    Smart image generation variant with caching and fallback.

    Features:
    - Distributed caching to avoid duplicate generations
    - Automatic fallback to mock if real generation fails
    - Usage metrics tracking
    """

    def __init__(self):
        super().__init__()
        self._local_cache: Dict[str, Dict[str, Any]] = {}
        self._generation_count = 0
        self._cache = get_cache()

    def process_task(self, task: ExplorationTask) -> AgentResponse:
        """Process image generation with caching and fallback."""
        # Check distributed cache first
        cache_result = asyncio.run(self._get_cached_result(task.concept))
        if cache_result is not None:
            logger.debug(f"Using cached images for '{task.concept}'")
            return AgentResponse(
                success=True,
                data=cache_result,
                metadata={
                    "task_id": task.id,
                    "image_count": len(cache_result.get("images", [])),
                    "from_cache": True,
                },
                agent_name=self.get_agent_name(),
                confidence=0.95,
            )

        # Process normally
        response = super().process_task(task)

        # Cache successful results
        if response.success and isinstance(response.data, dict):
            asyncio.run(self._cache_result(task.concept, response.data))
            self._local_cache[task.concept] = response.data
            self._generation_count += 1

        return response

    async def _get_cached_result(
        self, concept: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached result from distributed cache."""
        try:
            cache_key = f"images:generation:{concept}"
            cached = await self._cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Distributed cache hit for '{concept}'")
            return cached
        except Exception as e:
            logger.error(f"Error retrieving from distributed cache: {e}")
            # Fall back to local cache
            return self._local_cache.get(concept)

    async def _cache_result(
        self, concept: str, result: Dict[str, Any]
    ) -> None:
        """Cache result in distributed cache."""
        try:
            cache_key = f"images:generation:{concept}"
            # Cache for 7 days by default
            await self._cache.set(cache_key, result, 604800)
            logger.debug(f"Cached generation result for '{concept}'")
        except Exception as e:
            logger.error(f"Error caching result: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get generation cache statistics."""
        return {
            "local_cached_concepts": len(self._local_cache),
            "total_generations": self._generation_count,
            "cache_hit_rate": len(self._local_cache)
            / max(self._generation_count, 1),
            "cache_type": self._cache.__class__.__name__,
        }

    async def clear_cache(self):
        """Clear both local and distributed caches."""
        self._local_cache.clear()
        await self._cache.clear()
        logger.info("Image cache cleared (local and distributed)")
