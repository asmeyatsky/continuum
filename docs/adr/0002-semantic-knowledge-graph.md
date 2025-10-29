# ADR 0002: Semantic Knowledge Graph with Embeddings

## Status
ACCEPTED

## Context
The Continuum system needs to store and query concept relationships. Traditional keyword-based search is insufficient for finding semantically related concepts. We need a system that understands semantic similarity while remaining efficient and scalable.

## Decision
Implement a **semantic knowledge graph** using:
1. **Graph Structure**: Nodes (ConceptNode) and edges (GraphEdge) for explicit relationships
2. **Semantic Search**: Sentence Transformers embeddings for implicit similarity
3. **Hybrid Retrieval**: Combine graph traversal with embedding similarity search

## Architecture

```
InMemoryKnowledgeGraphEngine
├── Nodes: Dict[node_id → ConceptNode]
├── Edges: Dict[edge_id → GraphEdge]
├── Embeddings: Dict[node_id → np.ndarray]
└── Methods:
    ├── add_node(node) - O(1) with embedding generation
    ├── add_edge(edge) - O(1) relationship establishment
    ├── find_similar_nodes(concept, limit) - Cosine similarity search
    ├── get_neighbors(node_id) - Graph traversal
    └── get_subgraph(center_id, depth) - BFS-based subgraph extraction
```

## Rationale

### Semantic Understanding
- Embeddings capture semantic meaning beyond keyword matching
- Cosine similarity finds conceptually related nodes
- Enables finding analogies and connections humans would make

### Hybrid Approach
- Explicit edges: Fast, precise relationships (expands_to, related_to)
- Implicit similarity: Discovers unexpected connections
- Combines structure (graph) with semantics (embeddings)

### Scalability Path
- In-memory: Fast prototyping and testing
- Transition to vector DB: Scales to millions of nodes
- PostgreSQL + pgvector: Production-ready semantic search

### Flexibility
- Optional embedding service (graceful degradation)
- Fallback to simple text matching if transformers unavailable
- Easy to swap embedding models

## Consequences

### Positive
- ✅ Finds semantically related concepts (not just keywords)
- ✅ Discovers unexpected connections and analogies
- ✅ Efficient hybrid querying (graph + embeddings)
- ✅ Clear path to production scale

### Negative
- ⚠️ Embedding generation adds latency (~100ms per node)
- ⚠️ Memory overhead for storing embeddings (large vectors)
- ⚠️ Model-dependent results (quality varies by embedding model)
- ⚠️ Complexity of maintaining semantic consistency

### Mitigations
- Cache embeddings to avoid recomputation
- Use proven models (Sentence Transformers, OpenAI embeddings)
- Validate semantic similarity with human feedback
- Monitor embedding quality metrics

## Implementation Trade-offs

### Embedding Model Choice
- **Sentence Transformers** (current): Open-source, no API limits, good quality
- **OpenAI Embeddings**: Superior quality, requires API, per-token cost
- **Gradient Boosting Models**: Fast, less accurate semantic understanding

Decision: Start with Sentence Transformers, optionally upgrade to OpenAI embeddings

## Migration Path to Production

### Phase 1 (Current)
- In-memory storage
- Sentence Transformers embeddings
- Fast prototyping

### Phase 2
- Vector database (Pinecone, Weaviate)
- Persistent graph storage (PostgreSQL)
- Real-time embedding updates

### Phase 3
- Distributed graph processing
- Multi-model embedding combinations
- Advanced semantic analysis

## Related Decisions
- ADR-0003: Hexagonal Architecture (EmbeddingService as port)
- ADR-0004: Resilience Patterns (fallback to text matching)

## References
- [Sentence Transformers](https://www.sbert.net/)
- [Vector Search](https://en.wikipedia.org/wiki/Nearest_neighbor_search)
- [Knowledge Graphs](https://en.wikipedia.org/wiki/Knowledge_graph)
