"""
Tracing Decorators - Easy instrumentation for functions and methods.

Provides decorators for automatic span creation and error tracking:
- @trace_operation: Basic operation tracing
- @trace_async: Async function tracing with timing
- @trace_method: Instance method tracing with class context
"""

import logging
import time
from typing import Callable, Optional, Dict, Any
from functools import wraps
import traceback

from tracing.tracer import get_tracer

logger = logging.getLogger(__name__)


def trace_operation(
    operation_name: Optional[str] = None,
    include_args: bool = False,
    include_result: bool = False,
):
    """
    Decorator for tracing sync operations.

    Args:
        operation_name: Name for the span (defaults to function name)
        include_args: Include function arguments in span
        include_result: Include return value in span

    Example:
        @trace_operation("expensive_computation")
        def compute(x: int, y: int) -> int:
            return x + y
    """

    def decorator(func: Callable) -> Callable:
        span_name = operation_name or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            tracer = get_tracer()
            attributes = {"function": func.__name__}

            if include_args:
                attributes["args"] = str(args)
                attributes["kwargs"] = str(kwargs)

            try:
                with tracer.trace_operation(span_name, attributes=attributes) as span:
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time

                    span.set_attribute("duration_ms", elapsed * 1000)

                    if include_result:
                        span.set_attribute("result", str(result))

                    return result
            except Exception as e:
                tracer.record_exception(e)
                logger.error(f"Error in {span_name}: {e}")
                raise

        return wrapper

    return decorator


def trace_async(
    operation_name: Optional[str] = None,
    include_args: bool = False,
    include_result: bool = False,
):
    """
    Decorator for tracing async operations.

    Args:
        operation_name: Name for the span (defaults to function name)
        include_args: Include function arguments in span
        include_result: Include return value in span

    Example:
        @trace_async("fetch_data")
        async def get_data(url: str):
            return await http_client.get(url)
    """

    def decorator(func: Callable) -> Callable:
        span_name = operation_name or func.__name__

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            tracer = get_tracer()
            attributes = {"function": func.__name__}

            if include_args:
                attributes["args"] = str(args)
                attributes["kwargs"] = str(kwargs)

            try:
                with tracer.trace_operation(span_name, attributes=attributes) as span:
                    start_time = time.time()
                    result = await func(*args, **kwargs)
                    elapsed = time.time() - start_time

                    span.set_attribute("duration_ms", elapsed * 1000)

                    if include_result:
                        span.set_attribute("result", str(result))

                    return result
            except Exception as e:
                tracer.record_exception(e)
                logger.error(f"Error in {span_name}: {e}")
                raise

        return wrapper

    return decorator


def trace_method(
    operation_name: Optional[str] = None,
    include_args: bool = False,
    include_result: bool = False,
):
    """
    Decorator for tracing instance methods.

    Args:
        operation_name: Name for the span (defaults to method name)
        include_args: Include function arguments in span
        include_result: Include return value in span

    Example:
        class DataProcessor:
            @trace_method("process_task")
            async def process(self, task_id: str):
                return await self._do_processing(task_id)
    """

    def decorator(func: Callable) -> Callable:
        span_name = operation_name or func.__name__

        @wraps(func)
        async def async_wrapper(self, *args, **kwargs) -> Any:
            tracer = get_tracer()
            attributes = {
                "method": func.__name__,
                "class": self.__class__.__name__,
            }

            if include_args:
                attributes["args"] = str(args)
                attributes["kwargs"] = str(kwargs)

            try:
                with tracer.trace_operation(span_name, attributes=attributes) as span:
                    start_time = time.time()
                    result = await func(self, *args, **kwargs)
                    elapsed = time.time() - start_time

                    span.set_attribute("duration_ms", elapsed * 1000)

                    if include_result:
                        span.set_attribute("result", str(result)[:100])

                    return result
            except Exception as e:
                tracer.record_exception(e)
                logger.error(f"Error in {self.__class__.__name__}.{span_name}: {e}")
                raise

        @wraps(func)
        def sync_wrapper(self, *args, **kwargs) -> Any:
            tracer = get_tracer()
            attributes = {
                "method": func.__name__,
                "class": self.__class__.__name__,
            }

            if include_args:
                attributes["args"] = str(args)
                attributes["kwargs"] = str(kwargs)

            try:
                with tracer.trace_operation(span_name, attributes=attributes) as span:
                    start_time = time.time()
                    result = func(self, *args, **kwargs)
                    elapsed = time.time() - start_time

                    span.set_attribute("duration_ms", elapsed * 1000)

                    if include_result:
                        span.set_attribute("result", str(result)[:100])

                    return result
            except Exception as e:
                tracer.record_exception(e)
                logger.error(f"Error in {self.__class__.__name__}.{span_name}: {e}")
                raise

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def trace_performance(
    threshold_ms: int = 100,
    log_level: str = "warning",
):
    """
    Decorator that alerts when operation exceeds time threshold.

    Args:
        threshold_ms: Alert if operation takes longer than this (milliseconds)
        log_level: Logging level for alerts (warning, error, etc.)

    Example:
        @trace_performance(threshold_ms=50)
        def critical_path():
            # Must complete in <50ms
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            tracer = get_tracer()
            span_name = f"{func.__name__}_perf"

            with tracer.trace_operation(span_name) as span:
                start_time = time.time()
                result = func(*args, **kwargs)
                elapsed_ms = (time.time() - start_time) * 1000

                if elapsed_ms > threshold_ms:
                    msg = f"{func.__name__} took {elapsed_ms:.2f}ms (threshold: {threshold_ms}ms)"
                    logger.log(getattr(logging, log_level.upper()), msg)
                    span.set_attribute("performance_alert", True)
                    span.set_attribute("duration_ms", elapsed_ms)

                return result

        return wrapper

    return decorator
