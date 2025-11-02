"""
Google Gemini LLM Service implementation.

Provides LLM interactions using Google's Gemini API.
"""
import logging
from typing import Optional
from llm_service.base import LLMService, LLMResponse
from config.settings import settings

logger = logging.getLogger(__name__)


class GeminiService(LLMService):
    """Google Gemini LLM service implementation."""

    def __init__(self):
        """Initialize Gemini service."""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        try:
            import google.generativeai as genai
            from google.generativeai import GenerativeModel
            self.genai = genai
            self.genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Create the generative model instance
            self.model = GenerativeModel(settings.GEMINI_MODEL)
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Install with: pip install google-generativeai"
            )

        logger.info(f"Gemini service initialized with model: {settings.GEMINI_MODEL}")

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """
        Generate text using Gemini API.

        Args:
            prompt: The user prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt

        Returns:
            LLMResponse with generated content
        """
        try:
            # Combine system prompt with user prompt if system prompt provided
            final_prompt = prompt
            if system_prompt:
                final_prompt = f"{system_prompt}\n\n{prompt}"

            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            response = await self.model.generate_content_async(
                final_prompt,
                generation_config=generation_config
            )

            content = response.text
            # Gemini doesn't always return token count, so we'll estimate
            tokens_used = len(content.split()) if content else 0

            logger.debug(
                f"Generated text with approximately {tokens_used} tokens using {settings.GEMINI_MODEL}"
            )

            return LLMResponse(content, tokens_used, settings.GEMINI_MODEL)

        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
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