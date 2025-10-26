"""
Base LLM service interface for the Continuum application.

Provides abstract interface for LLM interactions.
"""
from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class LLMResponse:
    """Response from LLM service."""

    def __init__(self, content: str, tokens_used: int, model: str):
        self.content = content
        self.tokens_used = tokens_used
        self.model = model

    def __repr__(self) -> str:
        return f"LLMResponse(tokens={self.tokens_used}, model={self.model})"


class LLMService(ABC):
    """Abstract base class for LLM services."""

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """
        Generate text using the LLM.

        Args:
            prompt: The user prompt
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt

        Returns:
            LLMResponse with generated content
        """
        pass

    @abstractmethod
    async def generate_summary(self, text: str, max_length: int = 500) -> str:
        """Generate a summary of the given text."""
        pass

    @abstractmethod
    async def generate_connections(self, concept: str, context: str) -> list[str]:
        """
        Generate related concepts and connections.

        Args:
            concept: The main concept
            context: Additional context

        Returns:
            List of related concept names
        """
        pass

    @abstractmethod
    async def validate_concept(self, concept: str) -> bool:
        """Validate if a concept is valid and well-formed."""
        pass
