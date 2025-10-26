"""
Retry logic with exponential backoff and jitter.
"""
import asyncio
import logging
import random
from typing import Callable, Any, TypeVar, Optional
from functools import wraps

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number."""
        delay = self.initial_delay * (
            self.exponential_base ** (attempt - 1)
        )
        delay = min(delay, self.max_delay)

        if self.jitter:
            # Add random jitter: ±10% of delay
            jitter_amount = delay * 0.1
            delay += random.uniform(-jitter_amount, jitter_amount)

        return max(0, delay)


def retry_async(config: Optional[RetryConfig] = None):
    """
    Decorator for retrying async functions with exponential backoff.

    Args:
        config: RetryConfig instance

    Returns:
        Decorated async function
    """
    config = config or RetryConfig()

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt}/{config.max_attempts} failed for {func.__name__}: {e}"
                    )

                    if attempt < config.max_attempts:
                        delay = config.get_delay(attempt)
                        logger.info(
                            f"Retrying {func.__name__} after {delay:.2f}s delay"
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"All {config.max_attempts} attempts failed for {func.__name__}"
                        )

            raise last_exception

        return wrapper  # type: ignore

    return decorator


def retry_sync(config: Optional[RetryConfig] = None):
    """
    Decorator for retrying sync functions with exponential backoff.

    Args:
        config: RetryConfig instance

    Returns:
        Decorated function
    """
    config = config or RetryConfig()

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt}/{config.max_attempts} failed for {func.__name__}: {e}"
                    )

                    if attempt < config.max_attempts:
                        delay = config.get_delay(attempt)
                        logger.info(
                            f"Retrying {func.__name__} after {delay:.2f}s delay"
                        )
                        import time

                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {config.max_attempts} attempts failed for {func.__name__}"
                        )

            raise last_exception

        return wrapper  # type: ignore

    return decorator
