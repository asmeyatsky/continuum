"""
Image Generation Integration - Multiple providers for image creation.

Supports:
- OpenAI DALL-E: High quality, natural language
- Local Stable Diffusion: Self-hosted, no API costs
- Fallback: Mock generated images
"""

import logging
import asyncio
import base64
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


class ImageProvider(ABC):
    """Abstract base class for image generation providers."""

    @abstractmethod
    async def generate(
        self, prompt: str, count: int = 1, size: str = "1024x1024"
    ) -> List[Dict[str, Any]]:
        """
        Generate images from prompt.

        Returns:
            List of image objects with 'url', 'data', 'prompt' keys
        """
        pass


class DALLEProvider(ImageProvider):
    """OpenAI DALL-E 3 image generation."""

    def __init__(self, api_key: str):
        """
        Initialize DALL-E provider.

        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/images/generations"
        self.model = "dall-e-3"

    async def generate(
        self, prompt: str, count: int = 1, size: str = "1024x1024"
    ) -> List[Dict[str, Any]]:
        """Generate images using DALL-E."""
        if not HAS_HTTPX:
            logger.warning("httpx not available for DALL-E")
            return []

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": self.model,
                "prompt": prompt,
                "n": min(count, 1),  # DALL-E 3 only supports n=1
                "size": size,
                "quality": "standard",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for image in data.get("data", []):
                    results.append(
                        {
                            "url": image.get("url", ""),
                            "prompt": prompt,
                            "provider": "dalle",
                            "size": size,
                        }
                    )

                logger.info(f"DALL-E: Generated {len(results)} images")
                return results

        except Exception as e:
            logger.error(f"DALL-E error: {e}")
            return []


class StableDiffusionProvider(ImageProvider):
    """Stable Diffusion (self-hosted or API)."""

    def __init__(self, endpoint: str, api_key: Optional[str] = None):
        """
        Initialize Stable Diffusion provider.

        Args:
            endpoint: API endpoint (e.g., http://localhost:7860)
            api_key: Optional API key for managed services
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.base_url = f"{endpoint}/api/txt2img"

    async def generate(
        self, prompt: str, count: int = 1, size: str = "512x512"
    ) -> List[Dict[str, Any]]:
        """Generate images using Stable Diffusion."""
        if not HAS_HTTPX:
            logger.warning("httpx not available for Stable Diffusion")
            return []

        try:
            # Parse size
            width, height = map(int, size.split("x"))

            payload = {
                "prompt": prompt,
                "steps": 20,
                "sampler_index": "euler",
                "width": width,
                "height": height,
                "n_iter": count,
                "batch_size": count,
            }

            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for i, image_data in enumerate(data.get("images", [])):
                    results.append(
                        {
                            "url": f"data:image/png;base64,{image_data}",
                            "data": image_data,
                            "prompt": prompt,
                            "provider": "stable_diffusion",
                            "size": size,
                        }
                    )

                logger.info(f"Stable Diffusion: Generated {len(results)} images")
                return results

        except Exception as e:
            logger.error(f"Stable Diffusion error: {e}")
            return []


class ImageGenerationFactory:
    """Factory for creating image generation providers."""

    @staticmethod
    def create_provider(
        provider_name: str,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> Optional[ImageProvider]:
        """
        Create image generation provider.

        Args:
            provider_name: 'dalle' or 'stable_diffusion'
            api_key: API key (DALL-E) or token (Stable Diffusion)
            endpoint: Endpoint URL (Stable Diffusion)

        Returns:
            Initialized provider or None if not configured
        """
        provider_name = provider_name.lower()

        if provider_name == "dalle":
            if api_key:
                logger.info("Initializing DALL-E provider")
                return DALLEProvider(api_key)
            logger.warning("DALL-E API key not configured")

        elif provider_name == "stable_diffusion":
            if endpoint:
                logger.info("Initializing Stable Diffusion provider")
                return StableDiffusionProvider(endpoint, api_key)
            logger.warning("Stable Diffusion endpoint not configured")

        else:
            logger.warning(f"Unknown image provider: {provider_name}")

        return None

    @staticmethod
    def get_available_providers(
        openai_api_key: Optional[str] = None,
        stable_diffusion_endpoint: Optional[str] = None,
    ) -> List[str]:
        """Get list of configured image providers."""
        available = []

        if openai_api_key:
            available.append("dalle")
        if stable_diffusion_endpoint:
            available.append("stable_diffusion")

        return available

    @staticmethod
    def create_default_provider(
        openai_api_key: Optional[str] = None,
        stable_diffusion_endpoint: Optional[str] = None,
    ) -> Optional[ImageProvider]:
        """Create default image generation provider (first available)."""
        available = ImageGenerationFactory.get_available_providers(
            openai_api_key, stable_diffusion_endpoint
        )

        if available:
            provider_name = available[0]
            if provider_name == "dalle":
                return DALLEProvider(openai_api_key)
            elif provider_name == "stable_diffusion":
                return StableDiffusionProvider(stable_diffusion_endpoint)

        logger.warning("No image generation providers configured")
        return None


async def generate_images(
    prompt: str,
    provider: Optional[str] = None,
    count: int = 1,
    size: str = "1024x1024",
    openai_api_key: Optional[str] = None,
    stable_diffusion_endpoint: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Generate images from prompt.

    Args:
        prompt: Image description
        provider: Optional specific provider ('dalle', 'stable_diffusion')
        count: Number of images to generate
        size: Image size (e.g., '1024x1024')
        openai_api_key: OpenAI API key
        stable_diffusion_endpoint: Stable Diffusion endpoint

    Returns:
        List of generated image objects
    """
    if provider:
        image_provider = ImageGenerationFactory.create_provider(
            provider, openai_api_key, stable_diffusion_endpoint
        )
    else:
        image_provider = ImageGenerationFactory.create_default_provider(
            openai_api_key, stable_diffusion_endpoint
        )

    if not image_provider:
        logger.warning("No image generation provider available")
        return []

    return await image_provider.generate(prompt, count, size)
