# ADR 0004: Comprehensive Testing Strategy

## Status
ACCEPTED

## Context
High-quality software requires comprehensive testing to catch bugs early, prevent regressions, and ensure reliability. The Continuum system's complexity (multi-agent, knowledge graphs, external APIs) demands a structured testing approach.

## Decision
Implement **multi-level testing strategy**:
1. **Unit Tests** (70%): Domain logic, agents, graph operations
2. **Integration Tests** (20%): API endpoints, component interactions
3. **End-to-End Tests** (10%): Full system workflows
4. **Target Coverage**: 80%+ across all modules

## Test Pyramid Architecture

```
                    △
                   ╱ ╲  E2E Tests (10%)
                  ╱   ╲ Complex workflows
                 ╱─────╲
                ╱       ╲ Integration Tests (20%)
               ╱         ╲ API endpoints, components
              ╱───────────╲
             ╱             ╲ Unit Tests (70%)
            ╱               ╲ Logic, functions, classes
           ╱─────────────────╲
```

## Test Categories & Coverage

### Unit Tests
**Target: 80%+ coverage per module**

- **Core Orchestrator** (25+ tests)
  - Exploration submission and lifecycle
  - Task queue management
  - State transitions
  - Edge cases and error conditions

- **Multi-Agent System** (39+ tests)
  - Each agent behavior verification
  - Response format validation
  - Agent manager coordination
  - Task execution results

- **Knowledge Graph** (22+ tests)
  - Node/edge operations
  - Graph queries and traversals
  - Semantic similarity search
  - Subgraph extraction
  - Constraint validation

- **Domain Models**
  - Entity validation
  - Value object creation
  - Aggregate consistency

### Integration Tests
**Target: 85%+ endpoint coverage**

- **API Endpoints** (39+ tests)
  - Concept submission endpoints
  - Status retrieval
  - Knowledge graph queries
  - Search functionality
  - Feedback submission
  - Error handling and validation
  - Concurrent request handling

- **Component Interactions**
  - Orchestrator + Agent Manager
  - Knowledge Graph + Agents
  - LLM Service integration
  - Feedback System

### End-to-End Tests
**Target: Critical user workflows**

- Complete concept exploration workflow
- Multi-step expansion with feedback
- System resilience under load
- Data consistency across components

## Test Implementation Details

### Unit Testing
```python
# Example: Orchestrator tests
class TestExplorationSubmission:
    def test_submit_exploration_returns_valid_id(self):
        orchestrator = DefaultConceptOrchestrator()
        exploration_id = orchestrator.submit_exploration_request("Test")
        assert exploration_id is not None

class TestAgents:
    def test_agent_manager_executes_task(self):
        manager = AgentManager()
        task = ExplorationTask(...)
        responses = manager.execute_task(task)
        assert len(responses) == 6  # All agents respond
```

### Integration Testing
```python
# Example: API endpoint tests
@pytest.fixture
def client(setup_test_app):
    app, _ = setup_test_app
    return TestClient(app)

def test_submit_concept_returns_200(client):
    response = client.post("/api/concepts/expand",
                          json={"concept": "AI"})
    assert response.status_code == 200
```

### Mocking Strategy

#### Adapters
- Mock LLM responses for consistent testing
- Mock external APIs (embeddings, search)
- Fake databases for unit tests

#### Real Components Used in Tests
- Domain models (no external dependencies)
- Knowledge graph (in-memory)
- Orchestrator and agent logic

## Test Coverage Tools

### Pytest Configuration
```python
# pytest.ini
[pytest]
minversion = 8.0
testpaths = tests/
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### Coverage Tracking
```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

### Coverage Targets by Module
| Module | Target | Current |
|--------|--------|---------|
| core/ | 85% | 92% ✅ |
| agents/ | 80% | 95% ✅ |
| knowledge_graph/ | 80% | 88% ✅ |
| api/ | 85% | 90% ✅ |
| resilience/ | 75% | 80% ✅ |
| **Overall** | **80%** | **89% ✅** |

## Test Data & Fixtures

### Reusable Fixtures
```python
@pytest.fixture
def orchestrator():
    return DefaultConceptOrchestrator()

@pytest.fixture
def test_concept_node():
    return ConceptNode(
        id="test_1",
        concept="Test Concept",
        content="Test content",
        metadata={},
        created_at=datetime.now(),
        connections=[]
    )
```

### Test Data Builders
```python
class ExplorationBuilder:
    @staticmethod
    def create_valid_exploration():
        return DefaultConceptOrchestrator()

    @staticmethod
    def create_with_tasks(task_count: int):
        orch = DefaultConceptOrchestrator()
        # ... setup logic
        return orch
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Test Maintenance

### Adding New Tests
1. Follow existing test structure and naming conventions
2. Use descriptive test names: `test_<feature>_<scenario>_<expectation>`
3. Arrange-Act-Assert pattern
4. Aim for focused, single-responsibility tests

### Refactoring Tests
- Keep tests updated when refactoring code
- Remove redundant tests
- Add tests for new features
- Maintain coverage above 80%

## Consequences

### Positive
- ✅ Catch bugs early in development cycle
- ✅ Enable confident refactoring
- ✅ Serve as documentation of expected behavior
- ✅ Reduce debugging time
- ✅ Improve code quality through TDD

### Negative
- ⚠️ Test writing adds development time
- ⚠️ Test maintenance overhead
- ⚠️ False positives/negatives with external mocks
- ⚠️ Tests can become brittle with design changes

### Mitigations
- Use test automation and CI/CD
- Refactor tests alongside code
- Use flexible mocking strategies
- Focus on integration tests for critical paths

## Related Decisions
- ADR-0003: Hexagonal Architecture (enables testing with mocks)
- ADR-0005: Dependency Injection (testability)

## Testing Resources
- [pytest Documentation](https://docs.pytest.org/)
- [Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html)
- [Given-When-Then](https://cucumber.io/docs/gherkin/)
