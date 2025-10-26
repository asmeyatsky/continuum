"""
Anthropic LLM Service implementation.

Provides LLM interactions using Anthropic's Claude API.
"""
import logging
from typing import Optional
from llm_service.base import LLMService, LLMResponse
from config.settings import settings

logger = logging.getLogger(__name__)


class AnthropicService(LLMService):
    """Anthropic Claude LLM service implementation."""

    def __init__(self):
        """Initialize Anthropic service."""
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        except ImportError:
            raise ImportError(
                "anthropic package not installed. "
                "Install with: pip install anthropic"
            )

        self.model = settings.ANTHROPIC_MODEL
        logger.info(f"Anthropic service initialized with model: {self.model}")

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """
        Generate text using Anthropic API.

        Args:
            prompt: The user prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt

        Returns:
            LLMResponse with generated content
        """
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            logger.debug(
                f"Generated text with {tokens_used} tokens using {self.model}"
            )

            return LLMResponse(content, tokens_used, self.model)

        except Exception as e:
            logger.error(f"Error generating text with Anthropic: {e}")
            raise

    async def generate_summary(self, text: str, max_length: int = 500) -> str:
        """Generate a summary of the given text."""
        prompt = f"""Summarize the following text in {max_length} words or less.
Focus on the main ideas and key points.

Text:
{text}

Summary:"""

        system_prompt = "You are a helpful assistant that creates clear, concise summaries."

        response = await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_length // 4,  # Rough estimate: 4 chars per token
        )

        return response.content.strip()

    async def generate_connections(self, concept: str, context: str) -> list[str]:
        """
        Generate related concepts and connections.

        Args:
            concept: The main concept
            context: Additional context

        Returns:
            List of related concept names
        """
        prompt = f"""Given the concept "{concept}" and context "{context}",
generate a list of 5-10 related concepts or ideas that connect to this concept.
Return only the concept names, one per line, without numbering or bullets."""

        system_prompt = (
            "You are an expert at finding meaningful connections between ideas. "
            "Generate only concrete, specific concepts."
        )

        response = await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=500,
        )

        # Parse the response into a list of concepts
        connections = [
            line.strip() for line in response.content.split("\n") if line.strip()
        ]
        return connections[:10]  # Limit to 10

    async def validate_concept(self, concept: str) -> bool:
        """Validate if a concept is valid and well-formed."""
        prompt = f"""Is "{concept}" a valid, well-defined concept suitable for knowledge expansion?
Answer only "yes" or "no"."""

        response = await self.generate_text(
            prompt=prompt,
            temperature=0.0,  # Deterministic for validation
            max_tokens=10,
        )

        return "yes" in response.content.lower()
