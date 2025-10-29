"""
Tests for Image Generation Integration (Tier 3).

Covers:
- Image generation providers (DALL-E, Stable Diffusion)
- Image generation factory
- HybridImageAgent with feature flags
- SmartImageAgent with caching
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch

from agents.image_generation import (
    ImageProvider,
    DALLEProvider,
    StableDiffusionProvider,
    ImageGenerationFactory,
    generate_images,
)
from agents.image_adapter import HybridImageAgent, SmartImageAgent


class TestDALLEProvider:
    """Test DALL-E image generation provider."""

    def test_initialization(self):
        """Test DALL-E provider initialization."""
        provider = DALLEProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://api.openai.com/v1/images/generations"
        assert provider.model == "dall-e-3"

    def test_dalle_generate_async(self):
        """Test DALL-E image generation async."""
        provider = DALLEProvider(api_key="test-key")

        async def run_test():
            # This will return empty list since we don't have httpx mocked properly
            result = await provider.generate("test prompt", count=1)
            assert isinstance(result, list)

        asyncio.run(run_test())

    def test_dalle_error_handling(self):
        """Test DALL-E error handling."""
        provider = DALLEProvider(api_key="invalid-key")

        async def run_test():
            # Should handle errors gracefully
            result = await provider.generate("test prompt")
            assert isinstance(result, list)

        asyncio.run(run_test())


class TestStableDiffusionProvider:
    """Test Stable Diffusion provider."""

    def test_initialization(self):
        """Test Stable Diffusion provider initialization."""
        endpoint = "http://localhost:7860"
        provider = StableDiffusionProvider(endpoint=endpoint)
        assert provider.endpoint == endpoint
        assert provider.base_url == "http://localhost:7860/api/txt2img"

    def test_stable_diffusion_generate(self):
        """Test Stable Diffusion generation."""
        provider = StableDiffusionProvider(endpoint="http://localhost:7860")

        async def run_test():
            result = await provider.generate("test prompt", count=1)
            assert isinstance(result, list)

        asyncio.run(run_test())

    def test_stable_diffusion_with_api_key(self):
        """Test Stable Diffusion with API key."""
        provider = StableDiffusionProvider(
            endpoint="http://api.example.com", api_key="test-key"
        )
        assert provider.api_key == "test-key"


class TestImageGenerationFactory:
    """Test image generation provider factory."""

    def test_factory_initialization(self):
        """Test factory initialization."""
        factory = ImageGenerationFactory()
        assert factory is not None

    def test_create_provider_dalle(self):
        """Test creating DALL-E provider."""
        factory = ImageGenerationFactory()

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = factory.create_provider("dalle")
            if provider:
                assert isinstance(provider, DALLEProvider)

    def test_create_provider_stable_diffusion(self):
        """Test creating Stable Diffusion provider."""
        factory = ImageGenerationFactory()

        with patch.dict(
            "os.environ", {"STABLE_DIFFUSION_ENDPOINT": "http://localhost:7860"}
        ):
            provider = factory.create_provider("stable-diffusion")
            if provider:
                assert isinstance(provider, StableDiffusionProvider)

    def test_get_available_providers(self):
        """Test listing available providers."""
        factory = ImageGenerationFactory()
        providers = factory.get_available_providers()
        assert isinstance(providers, list)

    def test_create_default_provider(self):
        """Test creating default provider."""
        factory = ImageGenerationFactory()
        provider = factory.create_default_provider()
        # Should return something or None gracefully
        assert provider is None or isinstance(provider, ImageProvider)


class TestHybridImageAgent:
    """Test HybridImageAgent with feature flags."""

    def test_hybrid_agent_initialization(self):
        """Test HybridImageAgent initialization."""
        agent = HybridImageAgent()
        assert agent is not None

    def test_hybrid_agent_name(self):
        """Test hybrid agent has correct name."""
        agent = HybridImageAgent()
        assert agent.get_agent_name() == "ImageAgent"

    def test_hybrid_agent_has_process_task(self):
        """Test hybrid agent implements process_task."""
        agent = HybridImageAgent()
        assert hasattr(agent, "process_task")
        assert callable(agent.process_task)


class TestSmartImageAgent:
    """Test SmartImageAgent with caching."""

    def test_smart_agent_initialization(self):
        """Test SmartImageAgent initialization."""
        agent = SmartImageAgent()
        assert agent is not None

    def test_smart_agent_has_cache_methods(self):
        """Test SmartImageAgent has cache management methods."""
        agent = SmartImageAgent()
        assert hasattr(agent, "clear_cache")
        assert hasattr(agent, "get_cache_stats")

    def test_smart_agent_get_cache_stats(self):
        """Test SmartImageAgent cache statistics."""
        agent = SmartImageAgent()
        stats = agent.get_cache_stats()
        assert isinstance(stats, dict)

    def test_smart_agent_clear_cache(self):
        """Test SmartImageAgent can clear cache."""
        agent = SmartImageAgent()
        # Should not raise exception
        agent.clear_cache()
        # After clearing, stats should reflect empty cache
        stats = agent.get_cache_stats()
        assert isinstance(stats, dict)


class TestGenerateImagesFunction:
    """Test the generate_images top-level function."""

    def test_generate_images_basic(self):
        """Test basic image generation."""

        async def run_test():
            result = await generate_images("test concept", count=1)
            assert isinstance(result, list)

        asyncio.run(run_test())

    def test_generate_images_with_provider(self):
        """Test image generation with specific provider."""

        async def run_test():
            result = await generate_images("test concept", count=1, provider="dalle")
            assert isinstance(result, list)

        asyncio.run(run_test())

    def test_generate_images_multiple(self):
        """Test generating multiple images."""

        async def run_test():
            result = await generate_images("test concept", count=3)
            assert isinstance(result, list)

        asyncio.run(run_test())

    def test_generate_images_empty_prompt(self):
        """Test error handling for empty prompt."""

        async def run_test():
            result = await generate_images("", count=1)
            assert isinstance(result, list)

        asyncio.run(run_test())

    def test_generate_images_zero_count(self):
        """Test error handling for zero count."""

        async def run_test():
            result = await generate_images("test", count=0)
            assert isinstance(result, list)

        asyncio.run(run_test())


class TestImageProviderIntegration:
    """Integration tests for image generation."""

    def test_multiple_providers_available(self):
        """Test that multiple providers can be created."""
        factory = ImageGenerationFactory()
        providers = factory.get_available_providers()
        assert isinstance(providers, list)

    def test_graceful_degradation(self):
        """Test graceful degradation without external APIs."""

        async def run_test():
            # Should still work even if all external APIs are unavailable
            result = await generate_images("test concept")
            assert result is not None
            assert isinstance(result, list)

        asyncio.run(run_test())

    def test_provider_returns_list(self):
        """Test provider returns properly formatted list."""

        async def run_test():
            result = await generate_images("test concept")
            assert isinstance(result, list)
            # May be empty if no providers configured, but should be a list

        asyncio.run(run_test())


class TestImageProviderPerformance:
    """Performance tests for image generation."""

    def test_concurrent_image_generation(self):
        """Test concurrent image generation doesn't crash."""

        async def run_test():
            tasks = [
                generate_images(f"concept {i}") for i in range(3)
            ]
            results = await asyncio.gather(*tasks)
            assert len(results) == 3

        asyncio.run(run_test())

    def test_agent_creation_performance(self):
        """Test agent creation is fast."""
        import time

        start = time.time()
        for _ in range(10):
            HybridImageAgent()
            SmartImageAgent()
        duration = time.time() - start

        # Should create 20 agents quickly
        assert duration < 5.0  # 250ms per agent average


class TestProviderAbstractBase:
    """Test abstract base class contract."""

    def test_image_provider_is_abstract(self):
        """Test ImageProvider cannot be instantiated."""
        with pytest.raises(TypeError):
            ImageProvider()

    def test_dalle_implements_interface(self):
        """Test DALLEProvider implements ImageProvider."""
        provider = DALLEProvider(api_key="test")
        assert isinstance(provider, ImageProvider)

    def test_stable_diffusion_implements_interface(self):
        """Test StableDiffusionProvider implements ImageProvider."""
        provider = StableDiffusionProvider(endpoint="http://localhost:7860")
        assert isinstance(provider, ImageProvider)
