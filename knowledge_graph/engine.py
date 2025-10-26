"""
Knowledge Graph Engine for the Infinite Concept Expansion Engine.

This component implements a dynamic, self-organizing knowledge representation
with autonomous schema induction, real-time node/edge creation, and similarity-based retrieval.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from core.concept_orchestrator import ConceptNode
import uuid
from datetime import datetime


@dataclass
class GraphEdge:
    """Represents an edge in the knowledge graph"""
    id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    weight: float
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class GraphQueryResult:
    """Result of a knowledge graph query"""
    nodes: List[ConceptNode]
    edges: List[GraphEdge]
    score: float


class KnowledgeGraphEngine(ABC):
    """Abstract base class for the knowledge graph engine"""
    
    @abstractmethod
    def add_node(self, node: ConceptNode) -> bool:
        """Add a node to the knowledge graph"""
        pass
    
    @abstractmethod
    def add_edge(self, edge: GraphEdge) -> bool:
        """Add an edge to the knowledge graph"""
        pass
    
    @abstractmethod
    def get_node(self, node_id: str) -> Optional[ConceptNode]:
        """Get a node by ID"""
        pass
    
    @abstractmethod
    def get_neighbors(self, node_id: str, relationship_type: Optional[str] = None) -> List[ConceptNode]:
        """Get neighboring nodes of a given node"""
        pass
    
    @abstractmethod
    def find_similar_nodes(self, concept: str, limit: int = 10) -> List[GraphQueryResult]:
        """Find nodes similar to the given concept"""
        pass
    
    @abstractmethod
    def search_nodes(self, query: str, limit: int = 10) -> List[GraphQueryResult]:
        """Search nodes by content"""
        pass
    
    @abstractmethod
    def get_subgraph(self, center_node_id: str, depth: int = 2) -> Tuple[List[ConceptNode], List[GraphEdge]]:
        """Get a subgraph centered around a node"""
        pass


class InMemoryKnowledgeGraphEngine(KnowledgeGraphEngine):
    """In-memory implementation of the knowledge graph engine for development"""
    
    def __init__(self):
        self.nodes: Dict[str, ConceptNode] = {}
        self.edges: Dict[str, GraphEdge] = {}
        self.embeddings: Dict[str, List[float]] = {}  # Simple embedding storage
    
    def add_node(self, node: ConceptNode) -> bool:
        """Add a node to the knowledge graph"""
        if node.id in self.nodes:
            return False
        
        self.nodes[node.id] = node
        # Generate a simple embedding based on the content
        self.embeddings[node.id] = self._generate_embedding(node.content)
        return True
    
    def add_edge(self, edge: GraphEdge) -> bool:
        """Add an edge to the knowledge graph"""
        if edge.id in self.edges:
            return False
        
        # Verify source and target nodes exist
        if edge.source_node_id not in self.nodes or edge.target_node_id not in self.nodes:
            return False
        
        self.edges[edge.id] = edge
        # Also add to node's connections
        if edge.target_node_id not in self.nodes[edge.source_node_id].connections:
            self.nodes[edge.source_node_id].connections.append(edge.target_node_id)
        if edge.source_node_id not in self.nodes[edge.target_node_id].connections:
            self.nodes[edge.target_node_id].connections.append(edge.source_node_id)
        
        return True
    
    def get_node(self, node_id: str) -> Optional[ConceptNode]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    def get_neighbors(self, node_id: str, relationship_type: Optional[str] = None) -> List[ConceptNode]:
        """Get neighboring nodes of a given node"""
        if node_id not in self.nodes:
            return []
        
        neighbors = []
        for edge_id, edge in self.edges.items():
            # Check if this edge involves our node
            if edge.source_node_id == node_id or edge.target_node_id == node_id:
                if relationship_type is None or edge.relationship_type == relationship_type:
                    # Get the other node in the relationship
                    neighbor_id = edge.target_node_id if edge.source_node_id == node_id else edge.source_node_id
                    neighbor = self.nodes.get(neighbor_id)
                    if neighbor:
                        neighbors.append(neighbor)
        
        return neighbors
    
    def find_similar_nodes(self, concept: str, limit: int = 10) -> List[GraphQueryResult]:
        """Find nodes similar to the given concept using simple cosine similarity"""
        if not self.nodes:
            return []
        
        # Generate embedding for the query concept
        query_embedding = self._generate_embedding(concept)
        
        # Calculate similarities
        similarities = []
        for node_id, node in self.nodes.items():
            if node_id in self.embeddings:
                similarity = self._cosine_similarity(query_embedding, self.embeddings[node_id])
                similarities.append((node_id, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        results = []
        for node_id, similarity in similarities[:limit]:
            results.append(GraphQueryResult(
                nodes=[self.nodes[node_id]],
                edges=[],  # Edges not included in this simple implementation
                score=similarity
            ))
        
        return results
    
    def search_nodes(self, query: str, limit: int = 10) -> List[GraphQueryResult]:
        """Search nodes by content"""
        results = []
        query_lower = query.lower()
        
        for node in self.nodes.values():
            # Simple text matching - in a real implementation, this would use embeddings
            if query_lower in node.concept.lower() or query_lower in node.content.lower():
                results.append(GraphQueryResult(
                    nodes=[node],
                    edges=[],
                    score=0.5  # Placeholder score
                ))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]
    
    def get_subgraph(self, center_node_id: str, depth: int = 2) -> Tuple[List[ConceptNode], List[GraphEdge]]:
        """Get a subgraph centered around a node"""
        if center_node_id not in self.nodes:
            return [], []
        
        visited_nodes = {center_node_id}
        subgraph_nodes = [self.nodes[center_node_id]]
        subgraph_edges = []
        
        # Use BFS to get the subgraph up to the specified depth
        current_level = [center_node_id]
        current_depth = 0
        
        while current_level and current_depth < depth:
            next_level = []
            
            for node_id in current_level:
                # Find all edges connected to this node
                for edge in self.edges.values():
                    if edge.source_node_id == node_id or edge.target_node_id == node_id:
                        # Get the other node in the relationship
                        other_node_id = edge.target_node_id if edge.source_node_id == node_id else edge.source_node_id
                        
                        # If we haven't visited this node yet
                        if other_node_id not in visited_nodes:
                            visited_nodes.add(other_node_id)
                            subgraph_nodes.append(self.nodes[other_node_id])
                            subgraph_edges.append(edge)
                            next_level.append(other_node_id)
            
            current_level = next_level
            current_depth += 1
        
        return subgraph_nodes, subgraph_edges
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate a simple embedding for the text (in a real implementation, use proper embeddings)"""
        # Simple hash-based embedding - not suitable for production, just for demonstration
        import hashlib
        import struct
        
        # Create a hash of the text
        hash_input = text.lower().encode('utf-8')
        hash_obj = hashlib.sha256(hash_input)
        hash_hex = hash_obj.hexdigest()
        
        # Convert hash to a list of floats
        embedding = []
        for i in range(0, len(hash_hex), 8):  # Take 8 chars at a time
            hex_chunk = hash_hex[i:i+8]
            if len(hex_chunk) == 8:
                # Convert hex to integer, then to float in range [0, 1]
                int_val = int(hex_chunk, 16)
                float_val = (int_val % 10000) / 10000.0
                embedding.append(float_val)
        
        # Keep embedding to 16 dimensions
        return (embedding * (16 // len(embedding) + 1))[:16]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Calculate magnitudes
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(a * a for a in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def get_node_count(self) -> int:
        """Get the total number of nodes in the graph"""
        return len(self.nodes)
    
    def get_edge_count(self) -> int:
        """Get the total number of edges in the graph"""
        return len(self.edges)