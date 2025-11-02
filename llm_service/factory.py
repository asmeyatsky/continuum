"""
Factory for creating LLM service instances.

Selects the appropriate LLM service based on configuration.
"""
import logging
from typing import Literal
from llm_service.base import LLMService
from config.settings import settings

logger = logging.getLogger(__name__)


def get_llm_service() -> LLMService:
    """
    Get an LLM service instance based on configuration.

    Returns:
        LLMService instance (OpenAI, Anthropic, Qwen, Gemini, or Gemini-CLI)

    Raises:
        ValueError: If LLM_PROVIDER is not supported
    """
    provider = settings.LLM_PROVIDER.lower()

    if provider == "openai":
        from llm_service.openai_service import OpenAIService
        logger.info("Using OpenAI LLM service")
        return OpenAIService()

    elif provider == "anthropic":
        from llm_service.anthropic_service import AnthropicService
        logger.info("Using Anthropic LLM service")
        return AnthropicService()

    elif provider == "qwen":
        from llm_service.qwen_service import QwenService
        logger.info("Using Qwen LLM service")
        return QwenService()

    elif provider == "gemini":
        from llm_service.gemini_service import GeminiService
        logger.info("Using Google Gemini LLM service")
        return GeminiService()

    elif provider == "gemini-cli":
        from llm_service.gemini_cli_service import GeminiCLIService
        logger.info("Using Gemini CLI LLM service")
        return GeminiCLIService()

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers: openai, anthropic, qwen, gemini, gemini-cli"
        )
