# How Continuum Works

## Overview

Continuum is an **AI-powered knowledge exploration and expansion engine** that automatically explores, analyzes, and expands concepts using autonomous agents and knowledge graphs.

### Core Purpose

Given a concept (e.g., "artificial intelligence"), Continuum:
1. **Explores** the concept through research, web search, and LLM reasoning
2. **Generates** related concepts, insights, and visual content
3. **Builds** a knowledge graph showing relationships
4. **Learns** from user feedback to improve results
5. **Scales** to handle multiple concurrent explorations

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI APPLICATION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ API ROUTES (HTTP Endpoints)                              │  │
│  │ - POST /api/explorations (submit concept)               │  │
│  │ - GET /api/explorations/{id} (check status)             │  │
│  │ - GET /api/knowledge-graph/search (search)              │  │
│  │ - GET /api/knowledge-graph/nodes/{id} (details)         │  │
│  │ - POST /api/feedback (user ratings)                     │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│                       ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ CONCEPT ORCHESTRATOR (Brain)                            │  │
│  │ - Receives exploration tasks                            │  │
│  │ - Coordinates 6 autonomous agents                       │  │
│  │ - Manages exploration state machine                     │  │
│  │ - Returns results to API                                │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│    ┌──────────────────┼──────────────────┐                      │
│    │                  │                  │                      │
│    ▼                  ▼                  ▼                       │
│ ┌──────────┐      ┌──────────┐      ┌──────────┐               │
│ │ AGENT 1  │      │ AGENT 2  │      │ AGENT 3  │ ...            │
│ │Research  │      │Expansion │      │Curation  │               │
│ │Agent     │      │Agent     │      │Agent     │               │
│ └──────────┘      └──────────┘      └──────────┘               │
│                       │                                         │
│    ┌──────────────────┼──────────────────┐                      │
│    │                  │                  │                      │
│    ▼                  ▼                  ▼                       │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│ │Knowledge     │  │Feedback      │  │Cache (Redis) │            │
│ │Graph         │  │System        │  │              │            │
│ │(Database)    │  │(Learning)    │  │              │            │
│ └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## How It Works: Step by Step

### Step 1: User Submits a Concept

Users make a request to explore a concept:

```bash
POST /api/explorations
{
  "concept": "artificial intelligence",
  "max_depth": 3,
  "exploration_type": "comprehensive"
}
```

### Step 2: Orchestrator Receives & Queues Task

The Concept Orchestrator receives the request and creates an exploration record:

```
┌─────────────────────────────────────────┐
│ Concept: "artificial intelligence"      │
│ Status: PENDING                         │
│ Created: 2025-10-29T10:00:00Z          │
│ ID: exp_abc123xyz                       │
└─────────────────────────────────────────┘
```

The orchestrator immediately checks if this exploration was recently completed and cached.

### Step 3: Six Autonomous Agents Execute in Sequence

If no cache hit, the six agents execute:

#### **Agent 1: Research Agent**
- Searches Wikipedia, academic papers, web sources
- Extracts key facts and definitions
- Creates initial understanding
- Identifies important historical context
- **Output**: Core research data and foundational knowledge

#### **Agent 2: Web Search Agent**
- Performs web searches using Bing/Google APIs
- Finds latest articles and news
- Identifies trending subtopics and recent developments
- Gathers current information (not in training data)
- **Output**: Recent and real-time information

#### **Agent 3: Expansion Agent**
- Uses LLM to generate related concepts
- Creates semantic relationships
- Expands scope of exploration beyond initial concept
- Identifies sub-concepts and super-concepts
- **Output**: Related concepts list and semantic connections

#### **Agent 4: Analysis Agent**
- Analyzes all gathered information
- Identifies patterns, themes, and connections
- Generates insights and summaries
- Creates relationship descriptions
- **Output**: Analysis summary with key insights

#### **Agent 5: Image Generation Agent**
- Generates visual representations (DALL-E or Stable Diffusion)
- Creates concept visualizations and diagrams
- Produces illustrative images
- Falls back to mock images if APIs unavailable
- **Output**: Image URLs or base64-encoded images

#### **Agent 6: Curation Agent**
- Filters and ranks results by relevance
- Removes duplicates and low-quality information
- Prioritizes most valuable knowledge
- Orders concepts by importance
- **Output**: Curated and ranked final results

---

## Step 4: Build Knowledge Graph

As agents execute, the knowledge graph is populated with nodes and edges:

**Nodes** (Concepts):
- Each discovered concept becomes a node
- Stores: concept name, description, frequency, importance score
- Example: "AI", "Machine Learning", "Deep Learning", "Neural Networks"

**Edges** (Relationships):
- Connections between concepts
- Types: "uses", "includes", "related_to", "similar_to", "subcategory_of"
- Example: "AI uses Machine Learning", "Machine Learning includes Deep Learning"

**Graph Visualization**:
```
                    AI
                   /|\
                  / | \
                 /  |  \
              ML   NLP  CV
             /|\    |
            / | \   |
           /  |  \  |
         DL  RL  SVM Speech

Nodes: AI, ML, NLP, CV, DL, RL, SVM, Speech Recognition, ...
Edges:
  - "AI uses ML"
  - "ML includes DL"
  - "NLP processes language"
  - "CV analyzes images"
```

---

## Step 5: Collect User Feedback

Users can rate and provide feedback on explorations:

```json
POST /api/feedback
{
  "exploration_id": "exp_abc123xyz",
  "rating": 4.5,
  "feedback": "Great exploration, but missing some NLP details",
  "useful_concepts": ["Machine Learning", "Deep Learning"],
  "missing_topics": ["Language Models", "Transformers"]
}
```

The feedback includes:
- **Rating**: 1-5 star rating
- **Comment**: Qualitative feedback
- **Useful concepts**: Which concepts were most valuable
- **Missing topics**: What should have been explored more

---

## Step 6: Learn & Improve

The feedback system learns from user responses:

1. **Stores feedback** in PostgreSQL database
2. **Analyzes patterns**: Which concepts are most useful?
3. **Adjusts weights**: Increases importance of highly-rated concepts
4. **Improves future explorations**: Learns which subtopics matter
5. **Personalizes results**: Adapts to user preferences over time

**Learning Examples**:
- If users consistently rate "Deep Learning" highly → Expand DL explorations
- If "Transformers" is frequently mentioned as missing → Add to expansion agent
- If "Ethics in AI" gets feedback → Prioritize ethics in future AI explorations

---

## Data Flow Example

Complete end-to-end flow:

```
USER REQUEST
    │
    ▼
POST /api/explorations
{concept: "artificial intelligence"}
    │
    ▼
Orchestrator creates task
    │
    ├─────────────────────────┐
    │                         │
    ▼                         │
Cache check (Redis)           │
    │                         │
    ├─ Hit → Return cached ✓  │
    │                         │
    └─ Miss → Continue...     │
              │               │
              ▼               │
          Agent 1 (Research)  │
              │               │
              ▼               │
          Agent 2 (Web Search)│
              │               │
              ▼               │
          Agent 3 (Expansion) │
              │               │
              ▼               │
          Agent 4 (Analysis)  │
              │               │
              ▼               │
          Agent 5 (Images)    │
              │               │
              ▼               │
          Agent 6 (Curation)  │
              │               │
              ▼               │
    Store results in DB       │
              │               │
              ▼               │
    Cache results (Redis)     │
              │<──────────────┘
              │
              ▼
    Return JSON response
    {
      concepts: [...],
      relationships: [...],
      images: [...],
      analysis: "...",
      metadata: {...}
    }
    │
    ▼
USER RECEIVES RESULTS
    │
    ▼
USER PROVIDES FEEDBACK
    │
    ▼
System learns & improves
```

---

## Key Components & Their Roles

### **API Routes** (`api/routes.py`)
- Entry point for all HTTP requests
- Validates input data
- Returns JSON responses
- Collects metrics for monitoring

**Endpoints**:
```
POST   /api/explorations                    Create exploration
GET    /api/explorations/{id}               Get exploration status
GET    /api/explorations/{id}/results       Get exploration results
GET    /api/knowledge-graph/search?q=...    Search knowledge graph
GET    /api/knowledge-graph/nodes/{id}      Get node details
GET    /api/knowledge-graph/edges/{id}      Get relationships
POST   /api/feedback                        Submit user feedback
GET    /health                              Health check
GET    /metrics                             Prometheus metrics
```

### **Concept Orchestrator** (`core/concept_orchestrator.py`)
The "brain" of the system that coordinates everything:

- **Receives** exploration tasks from API
- **Manages** state machine: PENDING → EXECUTING → COMPLETED
- **Coordinates** execution of 6 agents in sequence
- **Handles** timeouts and retries
- **Tracks** progress and metadata
- **Returns** structured results to API

**State Transitions**:
```
PENDING → EXECUTING → COMPLETED
             │
             └─→ FAILED (on error)
```

### **Base Agent** (`agents/base.py`)
Abstract base class that all agents implement:

```python
class BaseAgent(ABC):
    def get_agent_name(self) -> str:
        """Return agent name"""
        pass

    def process_task(self, task: ExplorationTask) -> AgentResponse:
        """
        Process an exploration task.

        Args:
            task: The exploration task to process

        Returns:
            AgentResponse with results
        """
        pass
```

Each agent extends this base class and implements the `process_task()` method.

### **Six Agent Implementations**

**1. Research Agent** (`agents/research_agent.py`)
- Searches for foundational information
- Analyzes sources and extracts facts
- Provides historical context
- **Uses**: LLM, Wikipedia API, academic sources

**2. Web Search Agent** (`agents/web_search_agent.py`)
- Performs web searches for current information
- Fetches latest articles and news
- Identifies trending topics
- **Uses**: Bing Search API, web scraping

**3. Expansion Agent** (`agents/expansion_agent.py`)
- Generates related concepts using LLM
- Creates semantic mappings
- Expands exploration scope
- **Uses**: OpenAI GPT, semantic analysis

**4. Analysis Agent** (`agents/analysis_agent.py`)
- Synthesizes all information
- Identifies patterns and relationships
- Generates insights
- **Uses**: LLM reasoning, pattern analysis

**5. Image Generation Agent** (`agents/image_adapter.py`)
- Creates visual representations
- Generates concept diagrams and illustrations
- **Uses**: DALL-E 3 or Stable Diffusion APIs

**6. Curation Agent** (`agents/curation_agent.py`)
- Filters and ranks results
- Removes duplicates
- Prioritizes quality
- **Uses**: Ranking algorithms, quality metrics

### **Knowledge Graph Engine** (`knowledge_graph/engine.py`)
Stores and queries the knowledge graph:

**Capabilities**:
- Add nodes (concepts) and edges (relationships)
- Query nodes by ID or concept name
- Search by semantic similarity
- Traverse relationships
- Calculate concept importance/frequency
- Export as JSON or graph format

**Storage Options**:
- In-memory (InMemoryKnowledgeGraphEngine)
- PostgreSQL (PostgresKnowledgeGraphEngine)

### **Feedback System** (`feedback_system/core.py`)
Learns from user feedback:

**Features**:
- Records user ratings (1-5 stars)
- Stores qualitative feedback
- Tracks useful and missing concepts
- Analyzes feedback patterns
- Suggests improvements to agents
- Personalizes results based on history

**Learning Process**:
1. Collect feedback from users
2. Analyze patterns across feedback
3. Update agent weights/parameters
4. Adjust future explorations
5. Improve result quality over time

### **Cache Manager** (`cache/manager.py`)
Optimizes performance with caching:

**Features**:
- Redis for distributed caching (production)
- Local LRU cache fallback (development)
- Automatic serialization/deserialization
- TTL-based expiration (default 1 hour)
- Cache statistics and metrics

**Cache Keys**:
```
explorations:{exploration_id}
search:{query}:{concept}
node:{node_id}
images:{concept}
```

### **Tracing System** (`tracing/`)
Distributed tracing for observability:

**Features**:
- OpenTelemetry integration
- Trace context propagation
- Jaeger export
- Console logging option
- Request-to-response tracking
- Span measurement for each agent

**Exporters**:
- Jaeger (via OTLP)
- Console (for debugging)
- File (for logging)

### **Monitoring** (`monitoring/metrics.py`)
Prometheus metrics collection:

**Metrics Collected**:
- HTTP request count/duration
- Database queries count/duration
- Cache hits/misses
- Agent execution count/duration
- Knowledge graph size (nodes/edges)
- Image generation count
- Error rates and types

**Endpoints**:
- `/metrics` - Prometheus text format
- Prometheus scrapes every 15 seconds

---

## Detailed Example: Exploring "Artificial Intelligence"

### **Request:**
```json
POST /api/explorations
{
  "concept": "artificial intelligence",
  "max_depth": 3,
  "exploration_type": "comprehensive"
}

HTTP/1.1 202 Accepted
{
  "id": "exp_abc123xyz",
  "status": "PENDING",
  "created_at": "2025-10-29T10:00:00Z"
}
```

### **What Happens Inside (Detailed Timeline):**

**T+0s: Orchestrator receives task**
- Creates exploration record in database
- Checks cache (miss)
- Starts agent execution
- Status: PENDING

**T+0-30s: Agent 1 - Research Agent**
- Searches "artificial intelligence definition"
- Gathers foundational information:
  - Definition: "Intelligence demonstrated by machines"
  - Founder: Alan Turing (1950)
  - Key milestone: Turing Test
  - Modern applications: ChatGPT, self-driving cars, medical diagnosis
- Creates nodes: Turing Test, Machine Intelligence, Automation
- Creates edges: "AI introduced by Turing", "AI powers automation"

**T+30-50s: Agent 2 - Web Search Agent**
- Searches latest AI news (2025)
- Finds trending topics:
  - Large Language Models revolution
  - Multimodal AI systems
  - AI regulation and ethics
  - AI hardware acceleration (GPUs, TPUs)
- Creates nodes: LLM, Multimodal AI, AI Regulation, GPU
- Creates edges: "Modern AI uses LLMs", "AI regulation evolving"

**T+50-65s: Agent 3 - Expansion Agent**
- LLM generates related concepts:
  - Machine Learning
  - Deep Learning
  - Natural Language Processing
  - Computer Vision
  - Robotics
  - Expert Systems
  - Reinforcement Learning
- Creates nodes for each
- Creates edges to parent concept: "AI includes {concept}"

**T+65-85s: Agent 4 - Analysis Agent**
- Analyzes all gathered information
- Generates insights:
  - "AI is rapidly evolving with new models appearing monthly"
  - "Deep Learning dominates current AI landscape"
  - "Ethics and regulation are critical considerations"
  - "Data quality drives AI performance"
  - "Transformer architecture revolutionized NLP"
- Creates analysis nodes with scores

**T+85-115s: Agent 5 - Image Generation Agent**
- Generates visualizations:
  - Image 1: AI evolution timeline (1950-2025)
  - Image 2: Relationship diagram (AI hierarchy)
  - Image 3: Deep learning architecture visualization
  - Image 4: AI applications in different industries
- Stores images (S3 or base64)

**T+115-125s: Agent 6 - Curation Agent**
- Ranks results by relevance
- Top 10 concepts:
  1. Machine Learning (score: 0.98)
  2. Deep Learning (score: 0.97)
  3. Neural Networks (score: 0.96)
  4. NLP (score: 0.92)
  5. Computer Vision (score: 0.88)
  6. Large Language Models (score: 0.95)
  7. Transformers (score: 0.93)
  8. Data (score: 0.85)
  9. Ethics (score: 0.79)
  10. Robotics (score: 0.76)

**T+125s: Store & Cache**
- Save exploration to PostgreSQL
- Cache results in Redis (1 hour TTL)
- Store in knowledge graph
- Status: COMPLETED
- Total time: ~2 minutes

### **Response:**
```json
{
  "id": "exp_abc123xyz",
  "concept": "artificial intelligence",
  "status": "COMPLETED",
  "created_at": "2025-10-29T10:00:00Z",
  "completed_at": "2025-10-29T10:02:15Z",
  "duration_seconds": 135,
  "results": {
    "core_concepts": [
      {
        "name": "Machine Learning",
        "description": "Field of AI focusing on learning from data",
        "score": 0.98,
        "rank": 1
      },
      {
        "name": "Deep Learning",
        "description": "ML using neural networks with multiple layers",
        "score": 0.97,
        "rank": 2
      },
      ...
    ],
    "key_facts": [
      "AI is transforming industries",
      "Large language models are rapidly evolving",
      "Deep Learning dominates modern AI",
      "Data quality drives AI performance",
      "Transformer architecture revolutionized NLP"
    ],
    "relationships": [
      {
        "source": "AI",
        "target": "Machine Learning",
        "relationship": "includes",
        "strength": 0.95
      },
      {
        "source": "Machine Learning",
        "target": "Deep Learning",
        "relationship": "subcategory",
        "strength": 0.92
      },
      ...
    ],
    "images": [
      {
        "description": "AI evolution timeline",
        "url": "https://..../ai_timeline_20251029.png"
      },
      {
        "description": "AI concept hierarchy",
        "url": "https://..../ai_hierarchy_20251029.png"
      },
      ...
    ],
    "analysis": "Comprehensive overview of artificial intelligence...",
    "metadata": {
      "agents_executed": 6,
      "sources_consulted": 47,
      "new_concepts_discovered": 23,
      "total_relationships": 89,
      "images_generated": 4,
      "cache_hit": false
    }
  }
}
```

### **User Provides Feedback:**
```json
POST /api/feedback
{
  "exploration_id": "exp_abc123xyz",
  "rating": 4.5,
  "feedback": "Excellent overview! More on transformers would be helpful",
  "useful_concepts": ["Deep Learning", "LLMs", "Transformers"],
  "missing_topics": ["Vision Transformers", "Prompt Engineering", "Model Scaling Laws"]
}
```

### **System Learns:**
1. **Stores feedback** in feedback table
2. **Analyzes patterns**:
   - Transformers mentioned in feedback → increase exploration depth
   - Vision Transformers missing → add to expansion agent
   - Prompt Engineering trending → prioritize in LLM explorations
3. **Adjusts weights**:
   - Deep Learning weight: +5%
   - Transformers weight: +10%
   - Vision Transformers: create new concept
4. **Improves future runs**:
   - Next AI exploration will include more on Transformers
   - Vision Transformers will be automatically explored
   - Prompt Engineering will be in expansion

---

## Production Features (Tier 3)

### **Scalability**
- **Kubernetes**: Auto-scales from 3 to 10 pods based on CPU/memory metrics
- **Load Balancer**: Distributes requests across pods
- **Horizontal Scaling**: Each pod independently processes explorations
- **Database**: PostgreSQL with connection pooling

### **Reliability**
- **Database Persistence**: All explorations and feedback stored
- **Caching**: Redis layer for fast retrieval
- **Error Handling**: Graceful degradation if agents fail
- **Retries**: Automatic retry with exponential backoff
- **Health Checks**: Liveness and readiness probes

### **Monitoring & Alerting**
- **Prometheus**: 50+ metrics collected
- **Alerts**: 18 production alert rules (critical, warning)
- **Dashboards**: Grafana integration
- **Tracing**: Jaeger distributed tracing
- **Logs**: Structured JSON logging

### **Performance**
- **Caching**: Results cached for 1 hour (configurable)
- **Concurrent Agents**: Execution optimized for parallelization
- **Database Optimization**: Indexed queries
- **API Response Times**: P95 < 1 second

### **Security**
- **RBAC**: Role-based access control in Kubernetes
- **Secrets Management**: API keys in Kubernetes secrets
- **TLS/SSL**: HTTPS for API endpoints
- **Input Validation**: All inputs validated
- **Rate Limiting**: Optional API rate limiting

### **Development**
- **Docker Compose**: Local development stack
- **Docker Images**: Optimized multi-stage builds
- **GitHub Actions**: Automated CI/CD
- **Testing**: 139+ tests (Tier 1+2) + 31 image tests (Tier 3)

---

## Configuration & Customization

### **Environment Variables**

```bash
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Database
DATABASE_URL=postgresql://user:pass@localhost/continuum
DB_ECHO=false

# Cache
CACHE_TYPE=redis
REDIS_URL=redis://localhost:6379/0

# LLM Services
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Image Generation
OPENAI_API_KEY=sk-...
STABLE_DIFFUSION_ENDPOINT=http://localhost:7860

# Feature Flags
REAL_IMAGE_GENERATION=true
REAL_WEB_SEARCH=true
DISTRIBUTED_TRACING=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/continuum.log
```

### **Agent Customization**

Each agent can be customized:

```python
# Increase research depth
RESEARCH_DEPTH=5
RESEARCH_SOURCES=100

# Expand concept generation
EXPANSION_COUNT=50
EXPANSION_DIVERSITY=0.9

# Image generation preferences
IMAGE_SIZE=1024x1024
IMAGE_QUALITY=high
IMAGE_COUNT=4

# Analysis preferences
ANALYSIS_DEPTH=3
INSIGHT_COUNT=10
```

---

## Performance Characteristics

### **Expected Performance** (100 concurrent users)

```
Health Check:
  Min:       10-20ms
  Max:       100-200ms
  P95:       50-100ms
  Throughput: 1000-2000 req/s

Exploration Submit:
  Min:       50-100ms
  Max:       500-1000ms
  P95:       200-300ms
  Throughput: 200-300 req/s

Full Exploration:
  Min:       30 seconds
  Max:       5 minutes
  P95:       2 minutes
  (Depends on agent complexity)

Search:
  Min:       100-200ms
  Max:       1000-2000ms
  P95:       500-800ms
  Throughput: 100-150 req/s
```

### **Resource Usage**

```
Memory:     2-4 GB per pod
CPU:        1-2 cores per pod
Storage:    ~100 MB per 10,000 explorations
Network:    Minimal (mostly LLM API calls)
```

---

## Troubleshooting

### **Slow Explorations**

**Cause**: Slow agent execution
**Solutions**:
1. Check LLM API latency
2. Increase concurrency
3. Use cached results
4. Reduce exploration depth

### **High Memory Usage**

**Cause**: Large cache or graph
**Solutions**:
1. Reduce cache TTL
2. Limit knowledge graph size
3. Increase pod memory limits
4. Enable Kubernetes autoscaling

### **Failed Agents**

**Cause**: External API failures
**Solutions**:
1. Check API keys and endpoints
2. Verify network connectivity
3. Use fallback/mock implementations
4. Increase retry attempts

### **Poor Result Quality**

**Cause**: Agent weights not optimal
**Solutions**:
1. Collect more feedback
2. Adjust agent parameters
3. Update LLM prompts
4. Increase sources/depth

---

## Next Steps

1. **Deploy locally**: `docker-compose up -d`
2. **Submit explorations**: `POST /api/explorations`
3. **View results**: `GET /api/explorations/{id}`
4. **Provide feedback**: `POST /api/feedback`
5. **Monitor metrics**: `GET /metrics`
6. **Deploy to production**: `kubectl apply -f k8s/`

---

## Summary

**Continuum** automatically:
- **Explores** concepts through multiple agents
- **Builds** knowledge graphs of relationships
- **Learns** from user feedback
- **Scales** to handle enterprise workloads
- **Observes** everything with comprehensive monitoring

It's like having a team of AI researchers who work 24/7 to expand knowledge, all automatically improving based on what users find valuable! 🚀
