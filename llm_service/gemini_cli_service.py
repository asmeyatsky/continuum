"""
Gemini CLI LLM Service implementation.

Provides LLM interactions using the gemini-cli command-line tool.
"""
import logging
import subprocess
from typing import Optional
from llm_service.base import LLMService, LLMResponse
from config.settings import settings

logger = logging.getLogger(__name__)


class GeminiCLIService(LLMService):
    """Gemini CLI LLM service implementation."""

    def __init__(self):
        """Initialize Gemini CLI service."""
        # Check if gemini-cli is installed
        try:
            result = subprocess.run(['gemini', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                raise ValueError("gemini-cli command not found. Install with: npm install -g @google/gemini")
        except FileNotFoundError:
            raise ValueError("gemini-cli command not found. Install with: npm install -g @google/gemini")
        except subprocess.TimeoutExpired:
            raise ValueError("gemini-cli command timed out. Check installation.")

        self.model = settings.GEMINI_CLI_MODEL or "gemini-pro"
        logger.info(f"Gemini CLI service initialized with model: {self.model}")

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """
        Generate text using Gemini CLI.

        Args:
            prompt: The user prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt

        Returns:
            LLMResponse with generated content
        """
        import asyncio
        import shlex
        
        try:
            # Prepare the command
            cmd = ["gemini", "generate", "-m", self.model, "--no-stream"]
            
            # Combine system prompt with user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{full_prompt}"
            
            # Use subprocess to execute the command
            proc = await asyncio.create_subprocess_exec(
                'gemini', 'generate', '-m', self.model, '--no-stream',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate(input=full_prompt.encode())
            
            if proc.returncode != 0:
                raise Exception(f"Gemini CLI error: {stderr.decode()}")
            
            content = stdout.decode().strip()
            # Estimate tokens used (rough estimate)
            tokens_used = len(content.split()) if content else 0

            logger.debug(
                f"Generated text with approximately {tokens_used} tokens using {self.model}"
            )

            return LLMResponse(content, tokens_used, self.model)

        except Exception as e:
            logger.error(f"Error generating text with Gemini CLI: {e}")
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