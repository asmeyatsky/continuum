"""
Tests for the distributed tracing system.

Covers:
- TracingManager initialization
- Different exporter types
- Span creation and attribute setting
- Decorator functionality
- Component instrumentation
"""

import asyncio
import pytest
from typing import Optional

from tracing.tracer import (
    TracingManager,
    TraceExporterType,
    get_tracer,
    set_tracer,
    initialize_tracing,
    NoOpTracer,
)
from tracing.decorators import trace_operation, trace_async, trace_method
from tracing.instrumentation import (
    OrchestratorInstrumentation,
    AgentInstrumentation,
    KnowledgeGraphInstrumentation,
)


class TestTracingManagerInitialization:
    """Tests for TracingManager initialization."""

    def test_tracer_initialization_console(self):
        """Test tracer initialization with console exporter."""
        tracer = TracingManager(
            service_name="test_service",
            exporter_type="console",
            enabled=True,
        )
        assert tracer is not None
        assert tracer.service_name == "test_service"
        assert tracer.exporter_type == "console"

    def test_tracer_initialization_disabled(self):
        """Test tracer initialization when disabled."""
        tracer = TracingManager(
            service_name="test_service",
            enabled=False,
        )
        assert isinstance(tracer.tracer, NoOpTracer)

    def test_tracer_initialization_none_exporter(self):
        """Test tracer initialization with none exporter."""
        tracer = TracingManager(
            service_name="test_service",
            exporter_type="none",
            enabled=True,
        )
        assert tracer is not None

    def test_tracer_initialization_invalid_exporter(self):
        """Test tracer initialization with invalid exporter type."""
        tracer = TracingManager(
            service_name="test_service",
            exporter_type="invalid",
            enabled=True,
        )
        # Should not raise, should initialize with fallback
        assert tracer is not None

    def test_global_tracer_instance(self):
        """Test global tracer instance management."""
        original = get_tracer()
        assert original is not None

        new_tracer = TracingManager(service_name="new_service", enabled=False)
        set_tracer(new_tracer)
        assert get_tracer() is new_tracer

        # Restore original
        set_tracer(original)


class TestTraceOperation:
    """Tests for @trace_operation decorator."""

    def test_trace_operation_decorator(self):
        """Test basic trace_operation decorator."""

        @trace_operation("test_operation")
        def compute(x: int, y: int) -> int:
            return x + y

        result = compute(3, 5)
        assert result == 8

    def test_trace_operation_with_exception(self):
        """Test trace_operation handles exceptions."""

        @trace_operation("failing_operation")
        def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_func()

    def test_trace_operation_default_name(self):
        """Test trace_operation uses function name as default."""

        @trace_operation()
        def my_function():
            return "result"

        result = my_function()
        assert result == "result"

    def test_trace_operation_with_args_tracking(self):
        """Test trace_operation can track arguments."""

        @trace_operation("func_with_args", include_args=True)
        def func_with_args(x: int, y: str):
            return f"{x}:{y}"

        result = func_with_args(5, "test")
        assert result == "5:test"

    def test_trace_operation_with_result_tracking(self):
        """Test trace_operation can track results."""

        @trace_operation("func_with_result", include_result=True)
        def func_with_result(x: int) -> int:
            return x * 2

        result = func_with_result(5)
        assert result == 10


class TestTraceAsync:
    """Tests for @trace_async decorator."""

    def test_trace_async_decorator(self):
        """Test async trace_async decorator."""

        @trace_async("async_operation")
        async def async_func(x: int):
            await asyncio.sleep(0.01)
            return x * 2

        result = asyncio.run(async_func(5))
        assert result == 10

    def test_trace_async_with_exception(self):
        """Test trace_async handles async exceptions."""

        @trace_async("failing_async")
        async def failing_async():
            await asyncio.sleep(0.01)
            raise RuntimeError("Async error")

        with pytest.raises(RuntimeError):
            asyncio.run(failing_async())

    def test_trace_async_default_name(self):
        """Test trace_async uses function name as default."""

        @trace_async()
        async def my_async_func():
            return "async_result"

        result = asyncio.run(my_async_func())
        assert result == "async_result"


class TestTraceMethod:
    """Tests for @trace_method decorator."""

    def test_trace_method_decorator(self):
        """Test trace_method decorator on instance methods."""

        class DataProcessor:
            @trace_method("process")
            async def process(self, value: int) -> int:
                await asyncio.sleep(0.01)
                return value * 2

        processor = DataProcessor()
        result = asyncio.run(processor.process(5))
        assert result == 10

    def test_trace_method_sync(self):
        """Test trace_method on sync methods."""

        class Calculator:
            @trace_method("add")
            def add(self, a: int, b: int) -> int:
                return a + b

        calc = Calculator()
        result = calc.add(3, 5)
        assert result == 8

    def test_trace_method_with_exception(self):
        """Test trace_method handles exceptions."""

        class ErrorClass:
            @trace_method("fail")
            def fail(self):
                raise ValueError("Method error")

        obj = ErrorClass()
        with pytest.raises(ValueError):
            obj.fail()


class TestInstrumentation:
    """Tests for instrumentation helpers."""

    def test_orchestrator_instrumentation(self):
        """Test orchestrator instrumentation."""
        # Should not raise
        OrchestratorInstrumentation.trace_exploration_submission(
            concept="AI", exploration_id="exp_123"
        )

        OrchestratorInstrumentation.trace_task_processing(
            task_id="task_1",
            task_type="research",
            agent_name="ResearchAgent",
            success=True,
        )

        OrchestratorInstrumentation.trace_exploration_status(
            exploration_id="exp_123",
            status="running",
            task_count=5,
        )

    def test_agent_instrumentation(self):
        """Test agent instrumentation."""
        # Should not raise
        AgentInstrumentation.trace_agent_execution(
            agent_name="ResearchAgent",
            task_id="task_1",
            success=True,
            confidence=0.95,
            data_size=1024,
        )

        AgentInstrumentation.trace_agent_result(
            agent_name="ResearchAgent",
            result_type="sources",
            key_metrics={"source_count": 5},
        )

    def test_knowledge_graph_instrumentation(self):
        """Test knowledge graph instrumentation."""
        # Should not raise
        KnowledgeGraphInstrumentation.trace_node_operation(
            operation="add",
            node_id="node_1",
            concept="machine learning",
            success=True,
        )

        KnowledgeGraphInstrumentation.trace_edge_operation(
            operation="add",
            source_id="node_1",
            target_id="node_2",
            relationship_type="related_to",
            success=True,
        )

        KnowledgeGraphInstrumentation.trace_search_operation(
            query_type="semantic_search",
            query="AI concepts",
            result_count=10,
            duration_ms=45.5,
        )


class TestNoOpTracer:
    """Tests for NoOpTracer fallback."""

    def test_noop_tracer_operations(self):
        """Test NoOpTracer doesn't fail on operations."""
        from tracing.tracer import NoOpTracer

        tracer = NoOpTracer()

        # Should all be no-ops and not raise
        with tracer.start_as_current_span("test_span"):
            span = tracer.start_span("inner_span")
            tracer.add_event("test_event")
            tracer.set_attribute("key", "value")
            tracer.set_attributes({"key1": "value1"})


class TestTracingIntegration:
    """Integration tests for tracing system."""

    def test_decorator_integration(self):
        """Test decorators work with real tracer."""

        @trace_operation("calc_sum")
        def sum_values(a: int, b: int) -> int:
            return a + b

        result = sum_values(3, 5)
        assert result == 8

    def test_async_decorator_integration(self):
        """Test async decorator works."""

        @trace_async("fetch_data")
        async def fetch():
            await asyncio.sleep(0.001)
            return {"data": "test"}

        result = asyncio.run(fetch())
        assert result["data"] == "test"

    def test_method_decorator_integration(self):
        """Test method decorator works."""

        class Service:
            @trace_method("process_request")
            async def process(self, request_id: str) -> str:
                await asyncio.sleep(0.001)
                return f"processed_{request_id}"

        service = Service()
        result = asyncio.run(service.process("req_1"))
        assert result == "processed_req_1"


class TestTracingConfiguration:
    """Tests for tracing configuration."""

    def test_tracer_with_custom_service_name(self):
        """Test tracer with custom service name."""
        tracer = TracingManager(
            service_name="custom_service",
            exporter_type="none",
            enabled=True,
        )
        assert tracer.service_name == "custom_service"

    def test_tracer_with_jaeger_config(self):
        """Test tracer with Jaeger configuration."""
        tracer = TracingManager(
            service_name="jaeger_test",
            exporter_type="jaeger",
            jaeger_host="custom-host",
            jaeger_port=6832,
            enabled=True,
        )
        assert tracer is not None

    def test_tracer_with_otlp_config(self):
        """Test tracer with OTLP configuration."""
        tracer = TracingManager(
            service_name="otlp_test",
            exporter_type="otlp",
            otlp_endpoint="http://collector:4317",
            enabled=True,
        )
        assert tracer is not None


class TestInitializeTracingAsync:
    """Tests for async tracing initialization."""

    def test_initialize_tracing_async(self):
        """Test async tracing initialization."""

        async def init_test():
            tracer = await initialize_tracing(
                service_name="async_test",
                exporter_type="none",
                enabled=True,
            )
            assert tracer is not None
            assert tracer.service_name == "async_test"

        asyncio.run(init_test())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
