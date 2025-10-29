"""
Distributed Tracing Module - OpenTelemetry integration.

Provides:
- TracingManager: Core tracing infrastructure
- Decorators: @trace_operation, @trace_async, @trace_method
- Instrumentation: Pre-built tracing for components
"""

from tracing.tracer import (
    TracingManager,
    TraceExporterType,
    get_tracer,
    set_tracer,
    initialize_tracing,
)

from tracing.decorators import (
    trace_operation,
    trace_async,
    trace_method,
    trace_performance,
)

from tracing.instrumentation import (
    OrchestratorInstrumentation,
    AgentInstrumentation,
    KnowledgeGraphInstrumentation,
    APIInstrumentation,
    CacheInstrumentation,
    DatabaseInstrumentation,
    ExternalServiceInstrumentation,
    instrument_system,
)

__all__ = [
    # Core
    "TracingManager",
    "TraceExporterType",
    "get_tracer",
    "set_tracer",
    "initialize_tracing",
    # Decorators
    "trace_operation",
    "trace_async",
    "trace_method",
    "trace_performance",
    # Instrumentation
    "OrchestratorInstrumentation",
    "AgentInstrumentation",
    "KnowledgeGraphInstrumentation",
    "APIInstrumentation",
    "CacheInstrumentation",
    "DatabaseInstrumentation",
    "ExternalServiceInstrumentation",
    "instrument_system",
]
