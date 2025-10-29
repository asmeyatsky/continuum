"""
PostgreSQL-backed knowledge graph engine.

Provides persistent graph storage using SQLAlchemy models.
"""

import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
import numpy as np
from datetime import datetime

from knowledge_graph.engine import (
    KnowledgeGraphEngine,
    GraphEdge,
    GraphQueryResult,
    ConceptNode,
)
from database.models import ConceptNodeModel, GraphEdgeModel
from database.repositories import ConceptNodeRepository, GraphEdgeRepository

logger = logging.getLogger(__name__)


class PostgreSQLKnowledgeGraphEngine(KnowledgeGraphEngine):
    """Knowledge graph engine backed by PostgreSQL."""

    def __init__(self, db: Session):
        """
        Initialize PostgreSQL knowledge graph engine.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.node_repo = ConceptNodeRepository(db)
        self.edge_repo = GraphEdgeRepository(db)
        logger.info("PostgreSQL knowledge graph engine initialized")

    def add_node(self, node: ConceptNode) -> bool:
        """Add a node to the knowledge graph."""
        try:
            # Check if node already exists
            existing = self.node_repo.get_by_id(node.id)
            if existing:
                logger.warning(f"Node {node.id} already exists")
                return False

            # Create node in database
            self.node_repo.create(node)
            logger.debug(f"Added node: {node.id} ({node.concept})")
            return True
        except Exception as e:
            logger.error(f"Error adding node: {e}")
            return False

    def add_edge(self, edge: GraphEdge) -> bool:
        """Add an edge to the knowledge graph."""
        try:
            # Verify both nodes exist
            source_node = self.node_repo.get_by_id(edge.source_node_id)
            target_node = self.node_repo.get_by_id(edge.target_node_id)

            if not source_node or not target_node:
                logger.warning(f"Cannot add edge: nodes not found")
                return False

            # Check if edge already exists
            existing = self.edge_repo.get_by_id(edge.id)
            if existing:
                logger.warning(f"Edge {edge.id} already exists")
                return False

            # Create edge in database
            self.edge_repo.create(edge)

            # Update node connections
            if edge.target_node_id not in source_node.connections:
                source_node.connections.append(edge.target_node_id)
            if edge.source_node_id not in target_node.connections:
                target_node.connections.append(edge.source_node_id)

            self.db.commit()
            logger.debug(f"Added edge: {edge.id}")
            return True
        except Exception as e:
            logger.error(f"Error adding edge: {e}")
            self.db.rollback()
            return False

    def get_node(self, node_id: str) -> Optional[ConceptNode]:
        """Get a node by ID."""
        try:
            db_node = self.node_repo.get_by_id(node_id)
            if not db_node:
                return None

            return ConceptNode(
                id=db_node.id,
                concept=db_node.concept,
                content=db_node.content,
                metadata=db_node.metadata or {},
                created_at=db_node.created_at,
                connections=db_node.connections or [],
            )
        except Exception as e:
            logger.error(f"Error getting node: {e}")
            return None

    def get_neighbors(self, node_id: str, relationship_type: Optional[str] = None) -> List[ConceptNode]:
        """Get neighboring nodes."""
        try:
            neighbors = []

            # Get edges from this node
            outgoing_edges = self.edge_repo.get_from_node(node_id)
            for edge in outgoing_edges:
                if relationship_type and edge.relationship_type != relationship_type:
                    continue
                neighbor = self.get_node(edge.target_id)
                if neighbor:
                    neighbors.append(neighbor)

            # Get edges to this node
            incoming_edges = self.edge_repo.get_to_node(node_id)
            for edge in incoming_edges:
                if relationship_type and edge.relationship_type != relationship_type:
                    continue
                neighbor = self.get_node(edge.source_id)
                if neighbor:
                    neighbors.append(neighbor)

            return neighbors
        except Exception as e:
            logger.error(f"Error getting neighbors: {e}")
            return []

    def find_similar_nodes(self, concept: str, limit: int = 10) -> List[GraphQueryResult]:
        """Find similar nodes (text-based for PostgreSQL without pgvector)."""
        try:
            results = []

            # Search by concept name
            nodes = self.node_repo.get_by_concept(concept)
            for node in nodes[:limit]:
                concept_node = ConceptNode(
                    id=node.id,
                    concept=node.concept,
                    content=node.content,
                    metadata=node.metadata or {},
                    created_at=node.created_at,
                    connections=node.connections or [],
                )
                results.append(
                    GraphQueryResult(
                        nodes=[concept_node],
                        edges=[],
                        score=1.0,
                    )
                )

            return results
        except Exception as e:
            logger.error(f"Error finding similar nodes: {e}")
            return []

    def search_nodes(self, query: str, limit: int = 10) -> List[GraphQueryResult]:
        """Search nodes by content."""
        try:
            results = []
            query_lower = query.lower()

            # Full list search (for small graphs) or implement full-text search for large ones
            all_nodes = self.node_repo.list_all(limit=1000)

            for db_node in all_nodes:
                if (query_lower in db_node.concept.lower() or
                    (db_node.content and query_lower in db_node.content.lower())):
                    concept_node = ConceptNode(
                        id=db_node.id,
                        concept=db_node.concept,
                        content=db_node.content,
                        metadata=db_node.metadata or {},
                        created_at=db_node.created_at,
                        connections=db_node.connections or [],
                    )
                    results.append(
                        GraphQueryResult(
                            nodes=[concept_node],
                            edges=[],
                            score=0.5,
                        )
                    )

                if len(results) >= limit:
                    break

            return results
        except Exception as e:
            logger.error(f"Error searching nodes: {e}")
            return []

    def get_subgraph(self, center_node_id: str, depth: int = 2) -> Tuple[List[ConceptNode], List[GraphEdge]]:
        """Get a subgraph centered around a node."""
        try:
            visited_nodes = {center_node_id}
            subgraph_nodes = []
            subgraph_edges = []

            center_node = self.get_node(center_node_id)
            if not center_node:
                return [], []

            subgraph_nodes.append(center_node)

            # BFS to get subgraph
            current_level = [center_node_id]
            current_depth = 0

            while current_level and current_depth < depth:
                next_level = []

                for node_id in current_level:
                    # Get outgoing edges
                    outgoing = self.edge_repo.get_from_node(node_id)
                    for edge in outgoing:
                        if edge.target_id not in visited_nodes:
                            visited_nodes.add(edge.target_id)
                            neighbor = self.get_node(edge.target_id)
                            if neighbor:
                                subgraph_nodes.append(neighbor)
                            next_level.append(edge.target_id)

                        # Convert to GraphEdge
                        subgraph_edges.append(
                            GraphEdge(
                                id=edge.id,
                                source_node_id=edge.source_id,
                                target_node_id=edge.target_id,
                                relationship_type=edge.relationship_type,
                                weight=edge.weight,
                                created_at=edge.created_at,
                                metadata={},
                            )
                        )

                    # Get incoming edges
                    incoming = self.edge_repo.get_to_node(node_id)
                    for edge in incoming:
                        if edge.source_id not in visited_nodes:
                            visited_nodes.add(edge.source_id)
                            neighbor = self.get_node(edge.source_id)
                            if neighbor:
                                subgraph_nodes.append(neighbor)
                            next_level.append(edge.source_id)

                current_level = next_level
                current_depth += 1

            return subgraph_nodes, subgraph_edges
        except Exception as e:
            logger.error(f"Error getting subgraph: {e}")
            return [], []

    def get_node_count(self) -> int:
        """Get total number of nodes."""
        return self.node_repo.count()

    def get_edge_count(self) -> int:
        """Get total number of edges."""
        return self.edge_repo.count()

    def clear(self):
        """Clear all nodes and edges."""
        try:
            self.db.query(GraphEdgeModel).delete()
            self.db.query(ConceptNodeModel).delete()
            self.db.commit()
            logger.info("Knowledge graph cleared")
        except Exception as e:
            logger.error(f"Error clearing graph: {e}")
            self.db.rollback()
