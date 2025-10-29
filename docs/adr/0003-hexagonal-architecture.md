# ADR 0003: Hexagonal Architecture with Ports & Adapters

## Status
ACCEPTED

## Context
The system needs to integrate with multiple external services (LLMs, embeddings, databases, APIs) while keeping business logic independent of these implementations. Tight coupling to external services makes testing difficult and replacements expensive.

## Decision
Adopt **Hexagonal Architecture (Ports & Adapters pattern)**:
1. Core domain logic is independent of infrastructure
2. External dependencies are abstracted as "ports" (interfaces)
3. Concrete implementations are "adapters" that plug into ports
4. Easy to swap implementations without changing core logic

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                    │
│                   (API, CLI, UI)                        │
└─────────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│          (Use Cases, Orchestration)                      │
└─────────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────────┐
│                    Domain Layer                          │
│      (Business Rules, Entities, Value Objects)          │
│  ↑ Independent of all external dependencies ↑           │
└─────────────────────────────────────────────────────────┘
     ↕                              ↕
Ports (Interfaces)          Ports (Interfaces)
     ↕                              ↕
┌──────────────────┐   ┌──────────────────┐
│  LLM Adapters    │   │ Graph Adapters   │
├──────────────────┤   ├──────────────────┤
│ OpenAI           │   │ InMemory         │
│ Anthropic        │   │ PostgreSQL+pgv   │
│ Claude           │   │ Pinecone         │
└──────────────────┘   └──────────────────┘
```

## Port Definitions

### LLM Port (llm_service/base.py)
```python
class LLMProvider(ABC):
    @abstractmethod
    def generate_text(prompt: str, **kwargs) -> str: pass
```

### Embedding Port (embeddings/service.py)
```python
class EmbeddingService:
    def encode(text: str) -> np.ndarray: pass
```

### Knowledge Graph Port (knowledge_graph/engine.py)
```python
class KnowledgeGraphEngine(ABC):
    @abstractmethod
    def add_node(node: ConceptNode) -> bool: pass
```

## Rationale

### Testability
- Domain logic tested without external services
- Mock adapters for testing
- No API calls during unit tests

### Flexibility
- Easy to add new LLM providers (Gemini, Mistral, etc.)
- Swap storage backends without code changes
- Test different embedding models

### Independence
- Domain logic doesn't know about FastAPI, PostgreSQL, or external APIs
- Can use domain in CLI, batch processing, or other UIs
- Easy to understand and reason about business logic

### Evolution
- Upgrade to better embedding models
- Switch to different LLM provider based on cost/quality
- Add caching layer transparently

## Adapter Examples

### LLM Adapters
- `OpenAIService`: Uses OpenAI GPT API
- `AnthropicService`: Uses Anthropic Claude API
- `LocalLLMAdapter`: Uses local LLaMA or similar

### Knowledge Graph Adapters
- `InMemoryKnowledgeGraphEngine`: In-memory (dev/testing)
- `PostgresGraphAdapter`: Persistent PostgreSQL storage
- `PineconeAdapter`: Cloud vector database

## Consequences

### Positive
- ✅ Core business logic is frameworks-agnostic
- ✅ Easy to test with mocks and fakes
- ✅ Adding new implementations doesn't break existing code
- ✅ Dependency injection makes relationships explicit
- ✅ Enables working offline (mock adapters)

### Negative
- ⚠️ More interfaces and abstractions to maintain
- ⚠️ Potential performance overhead (indirection)
- ⚠️ Developers must understand hexagonal pattern
- ⚠️ Can add complexity for simple use cases

### Mitigations
- Clear documentation of ports
- Standard adapter implementations provided
- Consistent interface design across ports
- Good IDE support for interface refactoring

## Implementation Guidelines

### Adding a New Adapter
1. Find the port/interface in domain or application layer
2. Create adapter implementing the interface
3. Update dependency injection to use new adapter
4. Add integration tests for the adapter
5. Document in configuration

### Example: Adding Pinecone Vector DB
```python
# 1. Create adapter
class PineconeGraphAdapter(KnowledgeGraphEngine):
    def __init__(self, api_key: str, index_name: str):
        self.client = pinecone.Pinecone(api_key=api_key)
        self.index = self.client.Index(index_name)

    def add_node(self, node: ConceptNode) -> bool:
        # Implementation using Pinecone API
        pass

# 2. Update config
GRAPH_ENGINE = PineconeGraphAdapter(
    api_key=os.getenv("PINECONE_API_KEY"),
    index_name="continuum-index"
)

# 3. Done! No changes to business logic needed
```

## Related Decisions
- ADR-0001: Multi-Agent Architecture (agents as ports)
- ADR-0002: Semantic Knowledge Graph (pluggable embeddings)
- ADR-0005: Dependency Injection for configuration

## References
- [Hexagonal Architecture - Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Ports & Adapters Pattern](https://en.wikipedia.org/wiki/Ports_and_adapters_architecture)
- [Domain-Driven Design](https://en.wikipedia.org/wiki/Domain-driven_design)
