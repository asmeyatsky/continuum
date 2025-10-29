"""
Distributed Tracing Infrastructure with OpenTelemetry.

Provides unified tracing interface supporting multiple exporters:
- Jaeger: Full trace visualization
- OTLP: OpenTelemetry Protocol
- Console: Development/debugging
"""

import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
from enum import Enum

logger = logging.getLogger(__name__)

# Try importing OpenTelemetry components
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import SimpleMetricReader
    from opentelemetry.sdk.resources import Resource

    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False
    logger.warning("OpenTelemetry not installed. Tracing will be disabled.")

try:
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    HAS_JAEGER = True
except ImportError:
    HAS_JAEGER = False

try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter,
    )

    HAS_OTLP = True
except ImportError:
    HAS_OTLP = False

try:
    from opentelemetry.exporter.trace.in_memory_span_exporter import (
        InMemorySpanExporter,
    )

    HAS_IN_MEMORY = True
except ImportError:
    HAS_IN_MEMORY = False


class TraceExporterType(str, Enum):
    """Supported trace exporters."""

    JAEGER = "jaeger"
    OTLP = "otlp"
    IN_MEMORY = "in_memory"
    CONSOLE = "console"
    NONE = "none"


class NoOpTracer:
    """No-op tracer when OpenTelemetry is not available."""

    def start_as_current_span(self, name: str, **kwargs):
        """Return a no-op context manager."""

        @contextmanager
        def noop_span():
            yield NoOpSpan()

        return noop_span()

    def start_span(self, name: str, **kwargs):
        """Return a no-op span."""
        return NoOpSpan()

    def add_event(self, name: str, **kwargs):
        """No-op event."""
        pass

    def set_attribute(self, key: str, value: Any):
        """No-op attribute."""
        pass

    def set_attributes(self, attrs: Dict[str, Any]):
        """No-op attributes."""
        pass


class NoOpSpan:
    """No-op span."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def set_attribute(self, key: str, value: Any):
        """No-op."""
        pass

    def set_attributes(self, attrs: Dict[str, Any]):
        """No-op."""
        pass

    def add_event(self, name: str, **kwargs):
        """No-op."""
        pass

    def record_exception(self, exception: Exception):
        """No-op."""
        pass


class TracingManager:
    """
    Centralized tracing management for the Continuum system.

    Features:
    - Multiple exporter backends
    - Automatic span propagation
    - Request/response tracing
    - Performance metrics
    - Error tracking
    """

    def __init__(
        self,
        service_name: str = "continuum",
        exporter_type: str = "console",
        jaeger_host: str = "localhost",
        jaeger_port: int = 6831,
        otlp_endpoint: str = "http://localhost:4317",
        enabled: bool = True,
    ):
        """
        Initialize tracing manager.

        Args:
            service_name: Service identifier for traces
            exporter_type: Exporter backend (jaeger, otlp, in_memory, console, none)
            jaeger_host: Jaeger agent host
            jaeger_port: Jaeger agent port
            otlp_endpoint: OTLP receiver endpoint
            enabled: Enable/disable tracing
        """
        self.service_name = service_name
        self.exporter_type = exporter_type
        self.enabled = enabled
        self.tracer: Any = None
        self.meter: Any = None
        self._spans_exported = 0

        if not enabled or not HAS_OTEL:
            logger.info("Tracing disabled or OpenTelemetry not available")
            self.tracer = NoOpTracer()
            return

        try:
            # Create resource
            resource = Resource.create(
                {"service.name": service_name, "service.version": "1.0.0"}
            )

            # Create tracer provider
            tracer_provider = TracerProvider(resource=resource)

            # Add exporter based on type
            if exporter_type == "jaeger":
                self._setup_jaeger(tracer_provider, jaeger_host, jaeger_port)
            elif exporter_type == "otlp":
                self._setup_otlp(tracer_provider, otlp_endpoint)
            elif exporter_type == "in_memory":
                self._setup_in_memory(tracer_provider)
            elif exporter_type == "console":
                self._setup_console(tracer_provider)
            elif exporter_type != "none":
                logger.warning(f"Unknown exporter type: {exporter_type}")

            # Set global tracer provider
            trace.set_tracer_provider(tracer_provider)
            self.tracer = trace.get_tracer(__name__)

            logger.info(
                f"Tracing initialized with {exporter_type} exporter for {service_name}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize tracing: {e}")
            self.tracer = NoOpTracer()

    def _setup_jaeger(
        self, tracer_provider: Any, host: str, port: int
    ) -> None:
        """Setup Jaeger exporter."""
        if not HAS_JAEGER:
            logger.warning("Jaeger exporter not available")
            return

        try:
            jaeger_exporter = JaegerExporter(
                agent_host_name=host,
                agent_port=port,
            )
            tracer_provider.add_span_processor(
                SimpleSpanProcessor(jaeger_exporter)
            )
            logger.info(f"Jaeger exporter configured: {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to setup Jaeger: {e}")

    def _setup_otlp(self, tracer_provider: Any, endpoint: str) -> None:
        """Setup OTLP exporter."""
        if not HAS_OTLP:
            logger.warning("OTLP exporter not available")
            return

        try:
            otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
            tracer_provider.add_span_processor(
                SimpleSpanProcessor(otlp_exporter)
            )
            logger.info(f"OTLP exporter configured: {endpoint}")
        except Exception as e:
            logger.error(f"Failed to setup OTLP: {e}")

    def _setup_in_memory(self, tracer_provider: Any) -> None:
        """Setup in-memory exporter for testing."""
        if not HAS_IN_MEMORY:
            logger.warning("In-memory exporter not available")
            return

        try:
            exporter = InMemorySpanExporter()
            tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
            logger.info("In-memory exporter configured")
        except Exception as e:
            logger.error(f"Failed to setup in-memory exporter: {e}")

    def _setup_console(self, tracer_provider: Any) -> None:
        """Setup console exporter for development."""
        try:
            from opentelemetry.sdk.trace.export import (
                SimpleSpanProcessor,
            )

            # Create a simple console exporter
            class ConsoleSpanExporter:
                def export(self, spans):
                    for span in spans:
                        logger.info(
                            f"TRACE: {span.name} ({span.start_time}-{span.end_time}) "
                            f"status={span.status.status_code if span.status else 'UNSET'}"
                        )
                    return 0

                def shutdown(self):
                    pass

                def force_flush(self, timeout_millis=30000):
                    return True

            exporter = ConsoleSpanExporter()
            tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
            logger.info("Console exporter configured")
        except Exception as e:
            logger.error(f"Failed to setup console exporter: {e}")

    @contextmanager
    def trace_operation(
        self,
        operation_name: str,
        attributes: Optional[Dict[str, Any]] = None,
        events: Optional[Dict[str, Any]] = None,
    ):
        """
        Context manager for tracing operations.

        Args:
            operation_name: Name of the operation being traced
            attributes: Span attributes to set
            events: Events to record (name -> attributes dict)

        Example:
            with tracer.trace_operation("search_concept", attributes={"concept": "AI"}):
                # Do work here
                results = search(concept)
        """
        with self.tracer.start_as_current_span(operation_name) as span:
            if attributes:
                span.set_attributes(attributes)

            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                raise
            finally:
                if events:
                    for event_name, event_attrs in events.items():
                        span.add_event(event_name, event_attrs)

    def start_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """
        Start a new span.

        Args:
            name: Span name
            attributes: Initial attributes

        Returns:
            Span context manager
        """
        return self.tracer.start_as_current_span(name)

    def set_trace_attribute(self, key: str, value: Any) -> None:
        """Set attribute on current span."""
        try:
            span = trace.get_current_span()
            if span:
                span.set_attribute(key, value)
        except Exception:
            pass

    def add_trace_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add event to current span."""
        try:
            span = trace.get_current_span()
            if span:
                if attributes:
                    span.add_event(name, attributes)
                else:
                    span.add_event(name)
        except Exception:
            pass

    def record_exception(self, exception: Exception) -> None:
        """Record exception in current span."""
        try:
            span = trace.get_current_span()
            if span:
                span.record_exception(exception)
        except Exception:
            pass

    def get_tracer(self):
        """Get the tracer instance."""
        return self.tracer


# Global tracer instance
_tracer_instance: Optional[TracingManager] = None


def get_tracer() -> TracingManager:
    """Get the global tracer instance."""
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = TracingManager()
    return _tracer_instance


def set_tracer(tracer: TracingManager) -> None:
    """Set the global tracer instance."""
    global _tracer_instance
    _tracer_instance = tracer
    logger.info(f"Tracer set to: {tracer.__class__.__name__}")


async def initialize_tracing(
    service_name: str = "continuum",
    exporter_type: str = "console",
    jaeger_host: str = "localhost",
    jaeger_port: int = 6831,
    otlp_endpoint: str = "http://localhost:4317",
    enabled: bool = True,
) -> TracingManager:
    """
    Initialize distributed tracing.

    Args:
        service_name: Service identifier
        exporter_type: Exporter type (jaeger, otlp, in_memory, console, none)
        jaeger_host: Jaeger agent host
        jaeger_port: Jaeger agent port
        otlp_endpoint: OTLP endpoint
        enabled: Enable/disable tracing

    Returns:
        Initialized TracingManager
    """
    tracer = TracingManager(
        service_name=service_name,
        exporter_type=exporter_type,
        jaeger_host=jaeger_host,
        jaeger_port=jaeger_port,
        otlp_endpoint=otlp_endpoint,
        enabled=enabled,
    )
    set_tracer(tracer)
    return tracer
