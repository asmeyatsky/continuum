"""
Prometheus Metrics - Application monitoring and metrics collection.

Provides:
- HTTP request metrics (count, duration, status)
- Database metrics (queries, connections)
- Cache metrics (hits, misses, evictions)
- Business metrics (explorations, agents, generations)
"""

import logging
import time
from typing import Callable, Optional
from functools import wraps

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    CollectorRegistry,
    REGISTRY,
)

logger = logging.getLogger(__name__)

# Create custom registry
metrics_registry = REGISTRY

# ============================================================================
# HTTP Metrics
# ============================================================================

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=metrics_registry,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1, 2, 5),
    registry=metrics_registry,
)

http_request_size_bytes = Histogram(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint"],
    registry=metrics_registry,
)

http_response_size_bytes = Histogram(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint", "status"],
    registry=metrics_registry,
)

# ============================================================================
# Database Metrics
# ============================================================================

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
    buckets=(0.001, 0.01, 0.05, 0.1, 0.5, 1),
    registry=metrics_registry,
)

db_queries_total = Counter(
    "db_queries_total",
    "Total database queries",
    ["operation", "table", "status"],
    registry=metrics_registry,
)

db_connections_active = Gauge(
    "db_connections_active",
    "Active database connections",
    registry=metrics_registry,
)

db_connection_pool_size = Gauge(
    "db_connection_pool_size",
    "Database connection pool size",
    registry=metrics_registry,
)

# ============================================================================
# Cache Metrics
# ============================================================================

cache_hits_total = Counter(
    "cache_hits_total",
    "Total cache hits",
    ["cache_type", "key_prefix"],
    registry=metrics_registry,
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total cache misses",
    ["cache_type", "key_prefix"],
    registry=metrics_registry,
)

cache_evictions_total = Counter(
    "cache_evictions_total",
    "Total cache evictions",
    ["cache_type"],
    registry=metrics_registry,
)

cache_size_bytes = Gauge(
    "cache_size_bytes",
    "Cache size in bytes",
    ["cache_type"],
    registry=metrics_registry,
)

cache_entries = Gauge(
    "cache_entries",
    "Number of cache entries",
    ["cache_type"],
    registry=metrics_registry,
)

# ============================================================================
# Business Metrics
# ============================================================================

explorations_submitted_total = Counter(
    "explorations_submitted_total",
    "Total explorations submitted",
    ["source"],
    registry=metrics_registry,
)

explorations_completed_total = Counter(
    "explorations_completed_total",
    "Total explorations completed",
    ["status"],
    registry=metrics_registry,
)

exploration_duration_seconds = Histogram(
    "exploration_duration_seconds",
    "Exploration duration in seconds",
    ["concept"],
    buckets=(1, 5, 10, 30, 60, 300, 600),
    registry=metrics_registry,
)

agent_executions_total = Counter(
    "agent_executions_total",
    "Total agent executions",
    ["agent_name", "status"],
    registry=metrics_registry,
)

agent_execution_duration_seconds = Histogram(
    "agent_execution_duration_seconds",
    "Agent execution duration in seconds",
    ["agent_name"],
    buckets=(0.01, 0.1, 0.5, 1, 5, 10),
    registry=metrics_registry,
)

knowledge_graph_nodes_total = Gauge(
    "knowledge_graph_nodes_total",
    "Total knowledge graph nodes",
    registry=metrics_registry,
)

knowledge_graph_edges_total = Gauge(
    "knowledge_graph_edges_total",
    "Total knowledge graph edges",
    registry=metrics_registry,
)

images_generated_total = Counter(
    "images_generated_total",
    "Total images generated",
    ["provider"],
    registry=metrics_registry,
)

# ============================================================================
# System Metrics
# ============================================================================

application_info = Info(
    "application",
    "Application information",
    registry=metrics_registry,
)

tracing_spans_total = Counter(
    "tracing_spans_total",
    "Total tracing spans created",
    ["service", "span_name"],
    registry=metrics_registry,
)

errors_total = Counter(
    "errors_total",
    "Total errors",
    ["error_type", "location"],
    registry=metrics_registry,
)


# ============================================================================
# Decorator for automatic metric collection
# ============================================================================


def track_metrics(
    operation_name: str = None,
    labels: dict = None,
):
    """
    Decorator to automatically track operation metrics.

    Args:
        operation_name: Name of the operation for metrics
        labels: Additional labels to apply
    """

    def decorator(func: Callable):
        name = operation_name or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"{name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{name} failed after {duration:.3f}s: {e}")
                raise

        return wrapper

    return decorator


# ============================================================================
# Utility functions
# ============================================================================


def record_http_request(
    method: str,
    endpoint: str,
    status_code: int,
    duration: float,
    request_size: int = 0,
    response_size: int = 0,
):
    """Record HTTP request metrics."""
    http_requests_total.labels(method=method, endpoint=endpoint, status=status_code).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(
        duration
    )
    if request_size > 0:
        http_request_size_bytes.labels(method=method, endpoint=endpoint).observe(
            request_size
        )
    if response_size > 0:
        http_response_size_bytes.labels(
            method=method, endpoint=endpoint, status=status_code
        ).observe(response_size)


def record_db_query(
    operation: str,
    table: str,
    duration: float,
    success: bool = True,
):
    """Record database query metrics."""
    status = "success" if success else "failure"
    db_query_duration_seconds.labels(operation=operation, table=table).observe(
        duration
    )
    db_queries_total.labels(operation=operation, table=table, status=status).inc()


def record_cache_hit(cache_type: str, key_prefix: str = ""):
    """Record cache hit."""
    cache_hits_total.labels(cache_type=cache_type, key_prefix=key_prefix).inc()


def record_cache_miss(cache_type: str, key_prefix: str = ""):
    """Record cache miss."""
    cache_misses_total.labels(cache_type=cache_type, key_prefix=key_prefix).inc()


def record_exploration_submitted(source: str = "api"):
    """Record exploration submission."""
    explorations_submitted_total.labels(source=source).inc()


def record_exploration_completed(status: str):
    """Record exploration completion."""
    explorations_completed_total.labels(status=status).inc()


def record_agent_execution(agent_name: str, success: bool, duration: float):
    """Record agent execution."""
    status = "success" if success else "failure"
    agent_executions_total.labels(agent_name=agent_name, status=status).inc()
    agent_execution_duration_seconds.labels(agent_name=agent_name).observe(duration)


def record_image_generation(provider: str):
    """Record image generation."""
    images_generated_total.labels(provider=provider).inc()


def initialize_metrics(app_name: str = "continuum", version: str = "1.0.0"):
    """Initialize application metrics."""
    application_info.info({"application": app_name, "version": version})
    logger.info(f"Metrics initialized for {app_name} v{version}")
