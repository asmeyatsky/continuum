# Distributed Tracing Setup Guide

This guide explains how to set up and use distributed tracing with OpenTelemetry in Continuum.

## Overview

Continuum's tracing system provides comprehensive observability across the entire platform:
- **Request tracing**: Track requests from API entry to completion
- **Component tracing**: Monitor individual agents, knowledge graph, cache operations
- **Performance metrics**: Automatic timing for all traced operations
- **Error tracking**: Record exceptions and failures
- **Multi-exporter support**: Send traces to Jaeger, OTLP, or console

## Quick Start (Development)

By default, tracing uses the console exporter for development:

```python
from tracing import initialize_tracing, trace_operation
import asyncio

async def main():
    # Initialize tracing
    tracer = await initialize_tracing(
        service_name="continuum",
        exporter_type="console",
        enabled=True
    )

    # Trace operations
    @trace_operation("my_operation")
    def my_function():
        return "result"

    result = my_function()
    print(result)

asyncio.run(main())
```

## Configuration

Update `.env` to control tracing:

```env
# Enable/disable tracing
TRACING_ENABLED=true

# Exporter type: console, jaeger, otlp, in_memory, none
TRACING_EXPORTER=console

# Jaeger configuration
TRACING_JAEGER_HOST=localhost
TRACING_JAEGER_PORT=6831

# OTLP configuration
TRACING_OTLP_ENDPOINT=http://localhost:4317
```

## Setup by Exporter Type

### 1. Console Exporter (Development)

**Pros**: No external services, immediate feedback
**Cons**: Not suitable for production, trace events logged to stdout
**Best for**: Development and debugging

**Setup**:
```env
TRACING_ENABLED=true
TRACING_EXPORTER=console
```

**Output**:
```
INFO:root:TRACE: my_operation (1234567890.123-1234567891.456) status=UNSET
```

### 2. Jaeger (Full Trace Visualization)

**Pros**: Beautiful UI, full trace visualization, service dependency graphs
**Cons**: Requires running Jaeger server
**Best for**: Development with UI, staging/production visibility

#### Setup Steps

**1. Run Jaeger**

Using Docker (recommended):
```bash
docker run -d \
  -p 6831:6831/udp \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest
```

Using Homebrew:
```bash
brew install jaeger
jaeger-all-in-one
```

**2. Configure Continuum**

```env
TRACING_ENABLED=true
TRACING_EXPORTER=jaeger
TRACING_JAEGER_HOST=localhost
TRACING_JAEGER_PORT=6831
```

**3. Access Jaeger UI**

Open http://localhost:16686 in your browser:
- View all services and traces
- See service dependencies
- Analyze span timing
- View error logs

**4. Python Example**

```python
from tracing import initialize_tracing, trace_operation
import asyncio

async def main():
    await initialize_tracing(
        service_name="continuum",
        exporter_type="jaeger",
        jaeger_host="localhost",
        jaeger_port=6831,
        enabled=True
    )

    @trace_operation("search_concept")
    def search(concept: str):
        return f"results for {concept}"

    result = search("machine learning")

asyncio.run(main())
```

### 3. OTLP (OpenTelemetry Protocol)

**Pros**: Vendor-neutral, works with any OTLP receiver
**Cons**: Requires OTLP collector
**Best for**: Production with vendor flexibility

#### Setup Steps

**1. Run OTLP Collector**

Using Docker:
```bash
docker run -d \
  -p 4317:4317 \
  -v ./otel-collector-config.yaml:/etc/otel/config.yaml \
  otel/opentelemetry-collector:latest
```

**otel-collector-config.yaml**:
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

exporters:
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [jaeger]
```

**2. Configure Continuum**

```env
TRACING_ENABLED=true
TRACING_EXPORTER=otlp
TRACING_OTLP_ENDPOINT=http://localhost:4317
```

**3. Python Example**

```python
await initialize_tracing(
    service_name="continuum",
    exporter_type="otlp",
    otlp_endpoint="http://localhost:4317",
    enabled=True
)
```

### 4. In-Memory Exporter (Testing)

**Pros**: No external dependencies, fast
**Cons**: Traces only in memory, lost on restart
**Best for**: Unit testing, integration testing

```env
TRACING_ENABLED=true
TRACING_EXPORTER=in_memory
```

### 5. No Tracing

```env
TRACING_ENABLED=false
TRACING_EXPORTER=none
```

## Using Tracing in Your Code

### Decorators

#### @trace_operation (Sync)

```python
from tracing import trace_operation

@trace_operation("expensive_computation")
def calculate(x: int, y: int) -> int:
    # Automatically traced
    return x + y

result = calculate(3, 5)
```

#### @trace_async (Async)

```python
from tracing import trace_async

@trace_async("fetch_data")
async def get_data(url: str):
    # Automatically traced
    return await http_client.get(url)

result = await get_data("https://api.example.com/data")
```

#### @trace_method (Instance Methods)

```python
from tracing import trace_method

class DataProcessor:
    @trace_method("process_task")
    async def process(self, task_id: str):
        # Automatically traced with class context
        return await self._do_work(task_id)

processor = DataProcessor()
result = await processor.process("task_123")
```

#### Options

```python
# Include arguments in trace
@trace_operation("my_op", include_args=True)
def func(x: int, y: str):
    pass

# Include result in trace
@trace_operation("my_op", include_result=True)
def func() -> str:
    return "result"

# Both
@trace_operation("my_op", include_args=True, include_result=True)
def func(x: int) -> int:
    return x * 2
```

### Manual Span Management

```python
from tracing import get_tracer
import time

tracer = get_tracer()

# Trace a block of code
with tracer.trace_operation(
    "batch_processing",
    attributes={"batch_size": 100}
):
    # Do work
    process_batch(items)

    # Add events during execution
    tracer.add_trace_event(
        "batch_checkpoint",
        {"processed": 50}
    )
```

### Component Instrumentation

Pre-built instrumentation for key components:

```python
from tracing import OrchestratorInstrumentation

# Trace exploration submission
OrchestratorInstrumentation.trace_exploration_submission(
    concept="artificial intelligence",
    exploration_id="exp_123"
)

# Trace task processing
OrchestratorInstrumentation.trace_task_processing(
    task_id="task_1",
    task_type="research",
    agent_name="ResearchAgent",
    success=True
)
```

Available instrumentation classes:
- `OrchestratorInstrumentation`: Exploration workflow
- `AgentInstrumentation`: Individual agent operations
- `KnowledgeGraphInstrumentation`: Graph operations
- `APIInstrumentation`: HTTP requests
- `CacheInstrumentation`: Cache operations
- `DatabaseInstrumentation`: Database queries
- `ExternalServiceInstrumentation`: External API calls

## Performance Tracing

Monitor operations that exceed time thresholds:

```python
from tracing import trace_performance

# Alert if operation takes >100ms
@trace_performance(threshold_ms=100)
def critical_path():
    # Must complete in <100ms
    perform_calculation()
```

Logs warning if threshold exceeded and adds alert to span.

## Integration with Components

### Orchestrator Tracing

```python
from core.concept_orchestrator import DefaultConceptOrchestrator
from tracing import OrchestratorInstrumentation

orchestrator = DefaultConceptOrchestrator()

# Traces automatically recorded
exploration_id = orchestrator.submit_exploration_request("AI")
OrchestratorInstrumentation.trace_exploration_submission(
    concept="AI",
    exploration_id=exploration_id
)
```

### Agent Tracing

```python
from agents.research_adapter import SmartResearchAgent
from tracing import AgentInstrumentation

agent = SmartResearchAgent()
response = agent.process_task(task)

AgentInstrumentation.trace_agent_execution(
    agent_name="ResearchAgent",
    task_id=task.id,
    success=response.success,
    confidence=response.confidence
)
```

### Knowledge Graph Tracing

```python
from knowledge_graph.engine import InMemoryKnowledgeGraphEngine
from tracing import KnowledgeGraphInstrumentation

engine = InMemoryKnowledgeGraphEngine()
success = engine.add_node(node)

KnowledgeGraphInstrumentation.trace_node_operation(
    operation="add",
    node_id=node.id,
    concept=node.concept,
    success=success
)
```

## Viewing Traces

### Console Output

Traces appear in logs when using console exporter:
```
INFO:root:TRACE: search_concept (1234567890.123-1234567891.456) status=UNSET
```

### Jaeger UI

1. Open http://localhost:16686
2. Select service from dropdown
3. Select operation to view
4. Explore traces with timing and details

### Metrics and Statistics

Get trace statistics:

```python
from tracing import get_tracer

tracer = get_tracer()

# Get current span for inspection
# (implementation specific to exporter)
```

## Advanced Configuration

### Custom Service Attributes

```python
from tracing import TracingManager

tracer = TracingManager(
    service_name="continuum",
    exporter_type="jaeger"
)

# Resource contains service metadata
# Available in all traces
```

### Batch Span Processing

For high-throughput systems, use batch span processing:

```python
# Configured via OpenTelemetry SDK
# Set environment variables:
# OTEL_BSP_SCHEDULE_DELAY=5000  # Send every 5 seconds
# OTEL_BSP_MAX_QUEUE_SIZE=2048
```

### Sampling

Reduce tracing overhead by sampling:

```python
# Configure sampling rate (0.0 to 1.0)
# OTEL_TRACES_SAMPLER=parentbased_traceidratio
# OTEL_TRACES_SAMPLER_ARG=0.1  # Sample 10% of traces
```

## Production Best Practices

### 1. Use Jaeger for Production

```env
TRACING_ENABLED=true
TRACING_EXPORTER=jaeger
TRACING_JAEGER_HOST=jaeger-agent.monitoring
TRACING_JAEGER_PORT=6831
```

### 2. Run Jaeger in HA Mode

```yaml
# Docker Compose
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
      - MEMORY_MAX_TRACES=10000
```

### 3. Configure Sampling

Sample at 10% for production:
```env
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.1
```

### 4. Set Retention Policy

Configure trace retention in Jaeger:
```env
BADGER_SPAN_STORAGE_TTL=168h  # Keep traces for 7 days
```

### 5. Monitor Tracer Health

```python
async def health_check():
    tracer = get_tracer()
    # Check if tracer is functional
    with tracer.trace_operation("health_check"):
        pass
```

## Troubleshooting

### Traces Not Appearing in Jaeger

**Check**:
1. Jaeger is running: `docker ps | grep jaeger`
2. Jaeger endpoint accessible: `curl localhost:6831`
3. Configuration matches: `echo $TRACING_JAEGER_HOST`
4. OpenTelemetry installed: `pip list | grep opentelemetry`

**Solution**:
```bash
# Restart Jaeger
docker restart <jaeger_container>

# Verify connectivity
docker exec <app_container> curl -i http://jaeger:6831
```

### High Memory Usage

**Problem**: Tracer buffering too many spans

**Solution**:
```env
# Reduce batch size
OTEL_BSP_MAX_QUEUE_SIZE=256
OTEL_BSP_MAX_EXPORT_BATCH_SIZE=64
```

### Missing Attributes

**Problem**: Expected attributes not in trace

**Solution**:
```python
# Explicitly add attributes
with tracer.trace_operation("op") as span:
    span.set_attributes({
        "user_id": user_id,
        "request_id": request_id,
    })
```

### OpenTelemetry Not Installed

**Error**: `ModuleNotFoundError: No module named 'opentelemetry'`

**Solution**:
```bash
pip install -r requirements.txt
# or specifically:
pip install opentelemetry-api opentelemetry-sdk
```

## Performance Impact

Tracing overhead:
- **Console exporter**: <1ms per span
- **Jaeger exporter**: ~1-5ms per span (UDP)
- **OTLP exporter**: ~5-10ms per span (gRPC)

Recommend sampling (10-20%) for high-throughput production.

## Testing with Tracing

### Unit Tests

```python
import pytest
from tracing import trace_operation, initialize_tracing

@pytest.fixture
def tracer():
    return initialize_tracing(
        exporter_type="in_memory",
        enabled=True
    )

def test_operation_traced(tracer):
    @trace_operation("test_op")
    def my_func():
        return "result"

    result = my_func()
    assert result == "result"
```

### Integration Tests

```python
async def test_full_flow():
    tracer = await initialize_tracing(
        exporter_type="in_memory",
        enabled=True
    )

    # Run full system
    result = await run_orchestration("test_concept")

    # Verify tracing occurred
    assert result.success
```

## Next Steps

- [Set up Jaeger](https://www.jaegertracing.io/docs/latest/deployment/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Distributed Tracing Best Practices](https://opentelemetry.io/docs/concepts/signals/traces/)
- [Monitoring with Prometheus](./SETUP_PROMETHEUS.md) (coming soon)

## Resources

- [OpenTelemetry](https://opentelemetry.io/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OTLP Specification](https://github.com/open-telemetry/opentelemetry-specification)
- [Distributed Tracing Patterns](https://opentelemetry.io/docs/specs/otel/overview/)
