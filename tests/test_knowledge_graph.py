"""
Comprehensive tests for the Knowledge Graph Engine.

This module tests:
- Node management (add, retrieve, count)
- Edge management (add, retrieve, count)
- Graph querying (neighbors, subgraph)
- Semantic search and similarity
- Data integrity and constraints
"""

import pytest
from datetime import datetime
from core.concept_orchestrator import ConceptNode
from knowledge_graph.engine import (
    InMemoryKnowledgeGraphEngine,
    GraphEdge,
    GraphQueryResult,
)


class TestNodeOperations:
    """Tests for node creation and management."""

    def test_add_single_node(self):
        """Test adding a single node to the graph."""
        graph = InMemoryKnowledgeGraphEngine()
        node = ConceptNode(
            id="node1",
            concept="Artificial Intelligence",
            content="AI is the simulation of human intelligence",
            metadata={"category": "technology"},
            created_at=datetime.now(),
            connections=[]
        )

        result = graph.add_node(node)

        assert result is True
        assert graph.get_node_count() == 1
        assert graph.get_node("node1") is not None

    def test_add_multiple_nodes(self):
        """Test adding multiple nodes."""
        graph = InMemoryKnowledgeGraphEngine()

        for i in range(10):
            node = ConceptNode(
                id=f"node_{i}",
                concept=f"Concept {i}",
                content=f"Content {i}",
                metadata={"index": i},
                created_at=datetime.now(),
                connections=[]
            )
            graph.add_node(node)

        assert graph.get_node_count() == 10

    def test_add_duplicate_node_returns_false(self):
        """Test that adding a duplicate node returns False."""
        graph = InMemoryKnowledgeGraphEngine()
        node = ConceptNode(
            id="node1",
            concept="Test Concept",
            content="Test content",
            metadata={},
            created_at=datetime.now(),
            connections=[]
        )

        result1 = graph.add_node(node)
        result2 = graph.add_node(node)

        assert result1 is True
        assert result2 is False
        assert graph.get_node_count() == 1

    def test_get_nonexistent_node(self):
        """Test retrieving a non-existent node."""
        graph = InMemoryKnowledgeGraphEngine()
        node = graph.get_node("nonexistent")

        assert node is None

    def test_get_node_by_id(self):
        """Test retrieving a node by ID."""
        graph = InMemoryKnowledgeGraphEngine()
        original = ConceptNode(
            id="test_node",
            concept="Test Concept",
            content="Test content",
            metadata={"test": True},
            created_at=datetime.now(),
            connections=[]
        )

        graph.add_node(original)
        retrieved = graph.get_node("test_node")

        assert retrieved is not None
        assert retrieved.id == original.id
        assert retrieved.concept == original.concept
        assert retrieved.metadata == original.metadata


class TestEdgeOperations:
    """Tests for edge creation and management."""

    def test_add_edge_between_nodes(self):
        """Test adding an edge between two nodes."""
        graph = InMemoryKnowledgeGraphEngine()

        # Create and add nodes
        node1 = ConceptNode(
            id="node1",
            concept="Concept 1",
            content="Content 1",
            metadata={},
            created_at=datetime.now(),
            connections=[]
        )
        node2 = ConceptNode(
            id="node2",
            concept="Concept 2",
            content="Content 2",
            metadata={},
            created_at=datetime.now(),
            connections=[]
        )

        graph.add_node(node1)
        graph.add_node(node2)

        # Create and add edge
        edge = GraphEdge(
            id="edge1",
            source_node_id="node1",
            target_node_id="node2",
            relationship_type="related_to",
            weight=0.8,
            created_at=datetime.now(),
            metadata={}
        )

        result = graph.add_edge(edge)

        assert result is True
        assert graph.get_edge_count() == 1

    def test_add_edge_with_nonexistent_nodes(self):
        """Test that adding an edge with non-existent nodes fails."""
        graph = InMemoryKnowledgeGraphEngine()

        edge = GraphEdge(
            id="edge1",
            source_node_id="nonexistent1",
            target_node_id="nonexistent2",
            relationship_type="related_to",
            weight=0.8,
            created_at=datetime.now(),
            metadata={}
        )

        result = graph.add_edge(edge)

        assert result is False
        assert graph.get_edge_count() == 0

    def test_add_duplicate_edge_returns_false(self):
        """Test that adding a duplicate edge returns False."""
        graph = InMemoryKnowledgeGraphEngine()

        # Create nodes
        node1 = ConceptNode(
            id="node1", concept="C1", content="content1",
            metadata={}, created_at=datetime.now(), connections=[]
        )
        node2 = ConceptNode(
            id="node2", concept="C2", content="content2",
            metadata={}, created_at=datetime.now(), connections=[]
        )

        graph.add_node(node1)
        graph.add_node(node2)

        # Add edge twice
        edge = GraphEdge(
            id="edge1", source_node_id="node1", target_node_id="node2",
            relationship_type="related_to", weight=0.8,
            created_at=datetime.now(), metadata={}
        )

        result1 = graph.add_edge(edge)
        result2 = graph.add_edge(edge)

        assert result1 is True
        assert result2 is False
        assert graph.get_edge_count() == 1

    def test_add_bidirectional_edge_updates_connections(self):
        """Test that adding an edge updates connections bidirectionally."""
        graph = InMemoryKnowledgeGraphEngine()

        node1 = ConceptNode(
            id="node1", concept="C1", content="content1",
            metadata={}, created_at=datetime.now(), connections=[]
        )
        node2 = ConceptNode(
            id="node2", concept="C2", content="content2",
            metadata={}, created_at=datetime.now(), connections=[]
        )

        graph.add_node(node1)
        graph.add_node(node2)

        edge = GraphEdge(
            id="edge1", source_node_id="node1", target_node_id="node2",
            relationship_type="related_to", weight=0.8,
            created_at=datetime.now(), metadata={}
        )

        graph.add_edge(edge)

        # Check that connections are updated
        node1_updated = graph.get_node("node1")
        node2_updated = graph.get_node("node2")

        assert "node2" in node1_updated.connections
        assert "node1" in node2_updated.connections


class TestNeighborRetrieval:
    """Tests for retrieving neighboring nodes."""

    def test_get_neighbors_single(self):
        """Test getting neighbors of a node with one connection."""
        graph = InMemoryKnowledgeGraphEngine()

        # Create nodes
        nodes = [
            ConceptNode(
                id=f"node{i}", concept=f"C{i}", content=f"content{i}",
                metadata={}, created_at=datetime.now(), connections=[]
            )
            for i in range(3)
        ]

        for node in nodes:
            graph.add_node(node)

        # Add edges: node0 -> node1 -> node2
        edge1 = GraphEdge(
            id="edge1", source_node_id="node0", target_node_id="node1",
            relationship_type="related_to", weight=0.8,
            created_at=datetime.now(), metadata={}
        )
        edge2 = GraphEdge(
            id="edge2", source_node_id="node1", target_node_id="node2",
            relationship_type="related_to", weight=0.7,
            created_at=datetime.now(), metadata={}
        )

        graph.add_edge(edge1)
        graph.add_edge(edge2)

        # Get neighbors of node1
        neighbors = graph.get_neighbors("node1")

        assert len(neighbors) == 2
        neighbor_ids = [n.id for n in neighbors]
        assert "node0" in neighbor_ids
        assert "node2" in neighbor_ids

    def test_get_neighbors_by_relationship_type(self):
        """Test getting neighbors filtered by relationship type."""
        graph = InMemoryKnowledgeGraphEngine()

        # Create nodes
        nodes = [
            ConceptNode(
                id=f"node{i}", concept=f"C{i}", content=f"content{i}",
                metadata={}, created_at=datetime.now(), connections=[]
            )
            for i in range(3)
        ]

        for node in nodes:
            graph.add_node(node)

        # Add edges with different relationship types
        edge1 = GraphEdge(
            id="edge1", source_node_id="node0", target_node_id="node1",
            relationship_type="related_to", weight=0.8,
            created_at=datetime.now(), metadata={}
        )
        edge2 = GraphEdge(
            id="edge2", source_node_id="node0", target_node_id="node2",
            relationship_type="expands_to", weight=0.7,
            created_at=datetime.now(), metadata={}
        )

        graph.add_edge(edge1)
        graph.add_edge(edge2)

        # Get neighbors with specific relationship type
        related_neighbors = graph.get_neighbors("node0", relationship_type="related_to")
        assert len(related_neighbors) == 1
        assert related_neighbors[0].id == "node1"

        expanded_neighbors = graph.get_neighbors("node0", relationship_type="expands_to")
        assert len(expanded_neighbors) == 1
        assert expanded_neighbors[0].id == "node2"

    def test_get_neighbors_nonexistent_node(self):
        """Test getting neighbors of a non-existent node."""
        graph = InMemoryKnowledgeGraphEngine()
        neighbors = graph.get_neighbors("nonexistent")

        assert isinstance(neighbors, list)
        assert len(neighbors) == 0

    def test_get_neighbors_isolated_node(self):
        """Test getting neighbors of an isolated node."""
        graph = InMemoryKnowledgeGraphEngine()

        node = ConceptNode(
            id="isolated", concept="Isolated", content="content",
            metadata={}, created_at=datetime.now(), connections=[]
        )

        graph.add_node(node)
        neighbors = graph.get_neighbors("isolated")

        assert len(neighbors) == 0


class TestGraphQueries:
    """Tests for graph query operations."""

    def test_find_similar_nodes_with_embeddings(self):
        """Test finding similar nodes."""
        graph = InMemoryKnowledgeGraphEngine()

        # Add nodes with related content
        nodes = [
            ConceptNode(
                id="ai", concept="Artificial Intelligence",
                content="AI is about creating intelligent machines",
                metadata={}, created_at=datetime.now(), connections=[]
            ),
            ConceptNode(
                id="ml", concept="Machine Learning",
                content="ML is a subset of AI focused on learning algorithms",
                metadata={}, created_at=datetime.now(), connections=[]
            ),
            ConceptNode(
                id="dl", concept="Deep Learning",
                content="DL uses neural networks for learning",
                metadata={}, created_at=datetime.now(), connections=[]
            ),
            ConceptNode(
                id="biology", concept="Biology",
                content="Study of living organisms",
                metadata={}, created_at=datetime.now(), connections=[]
            ),
        ]

        for node in nodes:
            graph.add_node(node)

        # Find similar to "Artificial Intelligence"
        similar = graph.find_similar_nodes("Artificial Intelligence", limit=3)

        assert isinstance(similar, list)
        assert len(similar) > 0

    def test_search_nodes(self):
        """Test searching nodes by content."""
        graph = InMemoryKnowledgeGraphEngine()

        node1 = ConceptNode(
            id="node1", concept="Python Programming",
            content="Python is a versatile programming language",
            metadata={}, created_at=datetime.now(), connections=[]
        )
        node2 = ConceptNode(
            id="node2", concept="Java Programming",
            content="Java is an object-oriented language",
            metadata={}, created_at=datetime.now(), connections=[]
        )

        graph.add_node(node1)
        graph.add_node(node2)

        results = graph.search_nodes("Python", limit=10)

        assert len(results) >= 1
        assert any(r.nodes[0].id == "node1" for r in results)

    def test_search_nodes_no_matches(self):
        """Test searching with no matching results."""
        graph = InMemoryKnowledgeGraphEngine()

        node = ConceptNode(
            id="node1", concept="Test",
            content="Test content",
            metadata={}, created_at=datetime.now(), connections=[]
        )

        graph.add_node(node)
        results = graph.search_nodes("NonExistentTerm", limit=10)

        assert len(results) == 0


class TestSubgraphRetrieval:
    """Tests for subgraph retrieval."""

    def test_get_subgraph_single_depth(self):
        """Test getting subgraph with depth 1."""
        graph = InMemoryKnowledgeGraphEngine()

        # Create a simple tree: 0 -> 1, 0 -> 2
        nodes = [
            ConceptNode(
                id=f"node{i}", concept=f"C{i}", content=f"content{i}",
                metadata={}, created_at=datetime.now(), connections=[]
            )
            for i in range(3)
        ]

        for node in nodes:
            graph.add_node(node)

        # Add edges from node0 to node1 and node2
        edge1 = GraphEdge(
            id="edge1", source_node_id="node0", target_node_id="node1",
            relationship_type="related_to", weight=0.8,
            created_at=datetime.now(), metadata={}
        )
        edge2 = GraphEdge(
            id="edge2", source_node_id="node0", target_node_id="node2",
            relationship_type="related_to", weight=0.7,
            created_at=datetime.now(), metadata={}
        )

        graph.add_edge(edge1)
        graph.add_edge(edge2)

        # Get subgraph with depth 1
        sub_nodes, sub_edges = graph.get_subgraph("node0", depth=1)

        assert len(sub_nodes) == 3  # node0, node1, node2
        assert len(sub_edges) == 2  # edge1, edge2

    def test_get_subgraph_nonexistent_node(self):
        """Test getting subgraph for non-existent node."""
        graph = InMemoryKnowledgeGraphEngine()

        sub_nodes, sub_edges = graph.get_subgraph("nonexistent", depth=1)

        assert len(sub_nodes) == 0
        assert len(sub_edges) == 0

    def test_get_subgraph_with_depth(self):
        """Test getting subgraph respects depth limit."""
        graph = InMemoryKnowledgeGraphEngine()

        # Create a chain: 0 -> 1 -> 2 -> 3 -> 4
        for i in range(5):
            node = ConceptNode(
                id=f"node{i}", concept=f"C{i}", content=f"content{i}",
                metadata={}, created_at=datetime.now(), connections=[]
            )
            graph.add_node(node)

        for i in range(4):
            edge = GraphEdge(
                id=f"edge{i}", source_node_id=f"node{i}", target_node_id=f"node{i+1}",
                relationship_type="related_to", weight=0.8,
                created_at=datetime.now(), metadata={}
            )
            graph.add_edge(edge)

        # Get subgraph with depth 2 from node0
        sub_nodes, sub_edges = graph.get_subgraph("node0", depth=2)

        # Should include node0, node1, node2, node3
        assert len(sub_nodes) <= 4


class TestGraphStatistics:
    """Tests for graph statistics and metrics."""

    def test_get_node_count(self):
        """Test getting the total number of nodes."""
        graph = InMemoryKnowledgeGraphEngine()

        for i in range(10):
            node = ConceptNode(
                id=f"node{i}", concept=f"C{i}", content=f"content{i}",
                metadata={}, created_at=datetime.now(), connections=[]
            )
            graph.add_node(node)

        assert graph.get_node_count() == 10

    def test_get_edge_count(self):
        """Test getting the total number of edges."""
        graph = InMemoryKnowledgeGraphEngine()

        # Create 5 nodes and connect them
        for i in range(5):
            node = ConceptNode(
                id=f"node{i}", concept=f"C{i}", content=f"content{i}",
                metadata={}, created_at=datetime.now(), connections=[]
            )
            graph.add_node(node)

        # Add 4 edges (chain)
        for i in range(4):
            edge = GraphEdge(
                id=f"edge{i}", source_node_id=f"node{i}", target_node_id=f"node{i+1}",
                relationship_type="related_to", weight=0.8,
                created_at=datetime.now(), metadata={}
            )
            graph.add_edge(edge)

        assert graph.get_edge_count() == 4

    def test_empty_graph_statistics(self):
        """Test statistics on an empty graph."""
        graph = InMemoryKnowledgeGraphEngine()

        assert graph.get_node_count() == 0
        assert graph.get_edge_count() == 0
