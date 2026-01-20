"""
Knowledge Graph Engine for the Infinite Concept Expansion Engine.

This component implements a dynamic, self-organizing knowledge representation
with autonomous schema induction, real-time node/edge creation, and similarity-based retrieval.
"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from core.concept_orchestrator import ConceptNode
try:
    from embeddings.service import EmbeddingService
except ImportError:
    EmbeddingService = None

import uuid
from datetime import datetime

try:
    import numpy as np
    NDArray = np.ndarray
except ImportError:
    np = None
    NDArray = Any

logger = logging.getLogger(__name__)


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

    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        self.nodes: Dict[str, ConceptNode] = {}
        self.edges: Dict[str, GraphEdge] = {}
        self.embeddings: Dict[str, NDArray] = {}  # Sentence Transformer embeddings

        # Initialize embedding service
        try:
            if embedding_service:
                self.embedding_service = embedding_service
            elif EmbeddingService:
                self.embedding_service = EmbeddingService()
                logger.info("Using Sentence Transformer embeddings for semantic search")
            else:
                self.embedding_service = None
                logger.warning("EmbeddingService not available. Using fallback.")
        except Exception as e:
            logger.warning(f"Could not load embedding service: {e}. Using fallback.")
            self.embedding_service = None
    
    def add_node(self, node: ConceptNode) -> bool:
        """Add a node to the knowledge graph"""
        if node.id in self.nodes:
            return False

        self.nodes[node.id] = node

        # Generate embedding for semantic search
        try:
            if self.embedding_service:
                # Use Sentence Transformer embeddings
                text_to_embed = f"{node.concept} {node.content}"
                self.embeddings[node.id] = self.embedding_service.encode(text_to_embed)
                logger.debug(
                    f"Generated embedding for node {node.id} ({node.concept})"
                )
            else:
                # Fallback to simple embedding
                self.embeddings[node.id] = self._generate_fallback_embedding(
                    node.content
                )
        except Exception as e:
            logger.error(f"Error generating embedding for node {node.id}: {e}")
            # Continue without embedding
            pass

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
        """Find nodes similar to the given concept using semantic embeddings"""
        if not self.nodes:
            return []

        try:
            similarities = []

            if self.embedding_service and self.embeddings:
                # Use Sentence Transformer embeddings for semantic search
                query_embedding = self.embedding_service.encode(concept)

                # Find similar embeddings
                embedding_list = list(self.embeddings.values())
                node_ids = list(self.embeddings.keys())

                if embedding_list:
                    results = self.embedding_service.find_similar(
                        query_embedding,
                        np.array(embedding_list),
                        top_k=limit,
                        threshold=0.0,
                    )

                    similarities = [
                        (node_ids[idx], score) for idx, score in results
                    ]
                    logger.debug(
                        f"Found {len(similarities)} similar nodes using embeddings"
                    )
            else:
                # Fallback to simple text matching
                query_lower = concept.lower()
                for node_id, node in self.nodes.items():
                    if query_lower in node.concept.lower():
                        similarities.append((node_id, 0.8))
                    elif query_lower in node.content.lower():
                        similarities.append((node_id, 0.5))

            # Sort by similarity descending
            similarities.sort(key=lambda x: x[1], reverse=True)

            # Return top results
            results = []
            for node_id, similarity in similarities[:limit]:
                results.append(
                    GraphQueryResult(
                        nodes=[self.nodes[node_id]],
                        edges=[],  # Edges not included in this implementation
                        score=float(similarity),
                    )
                )

            return results
        except Exception as e:
            logger.error(f"Error finding similar nodes: {e}")
            return []
    
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
    
    def _generate_fallback_embedding(self, text: str) -> NDArray:
        """
        Generate a fallback embedding for the text.

        Used when Sentence Transformers is not available.
        This is a basic word-frequency based embedding and should not be used in production.
        """
        # Simple TF-IDF-like fallback using character frequency
        text_lower = text.lower() if text else ""

        if np is None:
            # Return a simple list if numpy is not available
            return [0.0] * 384

        # Create a 384-dimensional embedding (matching Sentence Transformer output)
        embedding = np.zeros(384, dtype=np.float32)

        # Simple character frequency encoding
        char_freq = {}
        for char in text_lower:
            if char.isalnum():
                char_freq[char] = char_freq.get(char, 0) + 1

        # Map character frequencies to embedding dimensions
        if char_freq:
            max_freq = max(char_freq.values())
            chars = sorted(char_freq.keys())
            for i, char in enumerate(chars):
                if i < len(embedding):
                    embedding[i] = char_freq[char] / max_freq

        # Add text length encoding
        text_length = len(text_lower)
        for i in range(len(embedding) // 4, min(len(embedding) // 4 + 10, len(embedding))):
            embedding[i] = min(text_length / 1000, 1.0)

        return embedding.astype(np.float32)
    
    def get_node_count(self) -> int:
        """Get the total number of nodes in the graph"""
        return len(self.nodes)
    
    def get_edge_count(self) -> int:
        """Get the total number of edges in the graph"""
        return len(self.edges)