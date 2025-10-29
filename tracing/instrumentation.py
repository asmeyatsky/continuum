"""
Component Instrumentation - Pre-built tracing for core system components.

Provides instrumentation for:
- Concept Orchestrator: Exploration workflow tracing
- Agents: Individual agent operations
- Knowledge Graph: Graph operations and queries
- API Handlers: HTTP request/response tracing
"""

import logging
from typing import Optional, Any

from tracing.tracer import get_tracer

logger = logging.getLogger(__name__)


class OrchestratorInstrumentation:
    """Instrumentation for the Concept Orchestrator."""

    @staticmethod
    def trace_exploration_submission(concept: str, exploration_id: str):
        """Trace exploration submission."""
        tracer = get_tracer()
        tracer.add_trace_event(
            "exploration_submitted",
            {
                "concept": concept,
                "exploration_id": exploration_id,
            },
        )

    @staticmethod
    def trace_task_processing(
        task_id: str, task_type: str, agent_name: str, success: bool
    ):
        """Trace task processing."""
        tracer = get_tracer()
        tracer.add_trace_event(
            "task_processed",
            {
                "task_id": task_id,
                "task_type": task_type,
                "agent": agent_name,
                "success": success,
            },
        )

    @staticmethod
    def trace_exploration_status(exploration_id: str, status: str, task_count: int):
        """Trace exploration status update."""
        tracer = get_tracer()
        tracer.add_trace_event(
            "exploration_status",
            {
                "exploration_id": exploration_id,
                "status": status,
                "task_count": task_count,
            },
        )


class AgentInstrumentation:
    """Instrumentation for agents."""

    @staticmethod
    def trace_agent_execution(
        agent_name: str,
        task_id: str,
        success: bool,
        confidence: float,
        data_size: Optional[int] = None,
    ):
        """Trace agent execution."""
        tracer = get_tracer()
        attributes = {
            "agent": agent_name,
            "task_id": task_id,
            "success": success,
            "confidence": confidence,
        }

        if data_size is not None:
            attributes["data_size_bytes"] = data_size

        tracer.add_trace_event("agent_executed", attributes)

    @staticmethod
    def trace_agent_result(
        agent_name: str, result_type: str, key_metrics: dict
    ):
        """Trace agent result with metrics."""
        tracer = get_tracer()
        attributes = {
            "agent": agent_name,
            "result_type": result_type,
            **key_metrics,
        }
        tracer.add_trace_event("agent_result", attributes)


class KnowledgeGraphInstrumentation:
    """Instrumentation for Knowledge Graph operations."""

    @staticmethod
    def trace_node_operation(
        operation: str,
        node_id: str,
        concept: str,
        success: bool,
    ):
        """Trace node operation (add, update, delete, etc.)."""
        tracer = get_tracer()
        tracer.add_trace_event(
            f"graph_node_{operation}",
            {
                "node_id": node_id,
                "concept": concept,
                "success": success,
            },
        )

    @staticmethod
    def trace_edge_operation(
        operation: str,
        source_id: str,
        target_id: str,
        relationship_type: str,
        success: bool,
    ):
        """Trace edge operation."""
        tracer = get_tracer()
        tracer.add_trace_event(
            f"graph_edge_{operation}",
            {
                "source_id": source_id,
                "target_id": target_id,
                "relationship": relationship_type,
                "success": success,
            },
        )

    @staticmethod
    def trace_search_operation(
        query_type: str,
        query: str,
        result_count: int,
        duration_ms: float,
    ):
        """Trace graph search operation."""
        tracer = get_tracer()
        tracer.add_trace_event(
            "graph_search",
            {
                "query_type": query_type,
                "query": query[:100],  # Truncate long queries
                "result_count": result_count,
                "duration_ms": duration_ms,
            },
        )


class APIInstrumentation:
    """Instrumentation for API endpoints."""

    @staticmethod
    def trace_http_request(
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
    ):
        """Trace HTTP request."""
        tracer = get_tracer()
        attributes = {
            "http.method": method,
            "http.url.path": path,
            "http.status_code": status_code,
            "duration_ms": duration_ms,
        }

        if user_id:
            attributes["user_id"] = user_id

        tracer.add_trace_event("http_request", attributes)

    @staticmethod
    def trace_api_error(
        method: str,
        path: str,
        error_type: str,
        error_message: str,
        status_code: int,
    ):
        """Trace API error."""
        tracer = get_tracer()
        tracer.add_trace_event(
            "api_error",
            {
                "http.method": method,
                "http.url.path": path,
                "error_type": error_type,
                "error_message": error_message[:200],
                "http.status_code": status_code,
            },
        )


class CacheInstrumentation:
    """Instrumentation for caching operations."""

    @staticmethod
    def trace_cache_hit(cache_type: str, key: str):
        """Trace cache hit."""
        tracer = get_tracer()
        tracer.add_trace_event(
            "cache_hit",
            {
                "cache_type": cache_type,
                "key": key[:100],
            },
        )

    @staticmethod
    def trace_cache_miss(cache_type: str, key: str):
        """Trace cache miss."""
        tracer = get_tracer()
        tracer.add_trace_event(
            "cache_miss",
            {
                "cache_type": cache_type,
                "key": key[:100],
            },
        )

    @staticmethod
    def trace_cache_operation(
        operation: str,
        cache_type: str,
        key: str,
        success: bool,
        duration_ms: float,
    ):
        """Trace cache operation."""
        tracer = get_tracer()
        tracer.add_trace_event(
            f"cache_{operation}",
            {
                "cache_type": cache_type,
                "key": key[:100],
                "success": success,
                "duration_ms": duration_ms,
            },
        )


class DatabaseInstrumentation:
    """Instrumentation for database operations."""

    @staticmethod
    def trace_db_query(
        operation: str,
        table: str,
        success: bool,
        duration_ms: float,
        row_count: Optional[int] = None,
    ):
        """Trace database query."""
        tracer = get_tracer()
        attributes = {
            "db.operation": operation,
            "db.table": table,
            "success": success,
            "duration_ms": duration_ms,
        }

        if row_count is not None:
            attributes["db.row_count"] = row_count

        tracer.add_trace_event("db_query", attributes)

    @staticmethod
    def trace_db_transaction(
        transaction_id: str,
        operation_count: int,
        success: bool,
        duration_ms: float,
    ):
        """Trace database transaction."""
        tracer = get_tracer()
        tracer.add_trace_event(
            "db_transaction",
            {
                "transaction_id": transaction_id,
                "operation_count": operation_count,
                "success": success,
                "duration_ms": duration_ms,
            },
        )


class ExternalServiceInstrumentation:
    """Instrumentation for external service calls."""

    @staticmethod
    def trace_external_call(
        service_name: str,
        operation: str,
        status: str,
        duration_ms: float,
        success: bool,
    ):
        """Trace call to external service."""
        tracer = get_tracer()
        tracer.add_trace_event(
            "external_service_call",
            {
                "service": service_name,
                "operation": operation,
                "status": status,
                "duration_ms": duration_ms,
                "success": success,
            },
        )

    @staticmethod
    def trace_web_search(
        provider: str,
        query: str,
        result_count: int,
        duration_ms: float,
        success: bool,
    ):
        """Trace web search operation."""
        tracer = get_tracer()
        tracer.add_trace_event(
            "web_search",
            {
                "provider": provider,
                "query": query[:100],
                "result_count": result_count,
                "duration_ms": duration_ms,
                "success": success,
            },
        )


def instrument_system(tracer_instance: Optional[Any] = None):
    """
    Instrument the entire system.

    This function should be called during application startup.

    Args:
        tracer_instance: Optional tracer instance to use
    """
    try:
        if tracer_instance:
            from tracing.tracer import set_tracer
            set_tracer(tracer_instance)

        logger.info("System instrumentation initialized")

    except Exception as e:
        logger.error(f"Failed to instrument system: {e}")
