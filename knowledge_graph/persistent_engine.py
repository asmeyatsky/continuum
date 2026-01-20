"""
Persistent Knowledge Graph Engine implementation.

This component implements the KnowledgeGraphEngine interface using
SQLAlchemy repositories for data persistence.
"""
import logging
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
import json

from core.concept_orchestrator import ConceptNode
from knowledge_graph.engine import (
    KnowledgeGraphEngine,
    GraphEdge,
    GraphQueryResult,
    InMemoryKnowledgeGraphEngine
)
from database.repositories import ConceptNodeRepository, GraphEdgeRepository
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class PersistentKnowledgeGraphEngine(KnowledgeGraphEngine):
    """
    Persistent implementation of the knowledge graph engine.
    Uses SQLAlchemy repositories to store nodes and edges in a database.
    """

    def __init__(self, db_session: Session, embedding_service=None):
        """
        Initialize with database session.
        
        Args:
            db_session: SQLAlchemy session
            embedding_service: Optional embedding service for semantic search
        """
        self.db = db_session
        self.node_repo = ConceptNodeRepository(db_session)
        self.edge_repo = GraphEdgeRepository(db_session)
        self.embedding_service = embedding_service
        
        # We also keep an in-memory cache for performance if needed,
        # or delegate complex graph algos to networkx if we load the whole graph.
        # For now, we'll rely on DB queries.
        
        if self.embedding_service:
            logger.info("Persistent Graph Engine initialized with embedding service")
        else:
            logger.warning("Persistent Graph Engine initialized WITHOUT embedding service")

    def add_node(self, node: ConceptNode) -> bool:
        """Add a node to the knowledge graph"""
        # Check if exists
        if self.node_repo.get_by_id(node.id):
            return False
            
        try:
            self.node_repo.create(node)
            return True
        except Exception as e:
            logger.error(f"Error adding node {node.id}: {e}")
            self.db.rollback()
            return False

    def add_edge(self, edge: GraphEdge) -> bool:
        """Add an edge to the knowledge graph"""
        # Check if exists
        if self.edge_repo.get_by_id(edge.id):
            return False
            
        try:
            self.edge_repo.create(edge)
            return True
        except Exception as e:
            logger.error(f"Error adding edge {edge.id}: {e}")
            self.db.rollback()
            return False

    def get_node(self, node_id: str) -> Optional[ConceptNode]:
        """Get a node by ID"""
        db_node = self.node_repo.get_by_id(node_id)
        if not db_node:
            return None
            
        # Convert DB model back to domain object
        metadata = {}
        if db_node.metadata:
            try:
                metadata = json.loads(db_node.metadata)
            except:
                pass
                
        return ConceptNode(
            id=db_node.id,
            concept=db_node.concept,
            content=db_node.content,
            metadata=metadata,
            created_at=db_node.created_at
        )

    def get_neighbors(self, node_id: str, relationship_type: Optional[str] = None) -> List[ConceptNode]:
        """Get neighboring nodes of a given node"""
        # Get edges where this node is source
        out_edges = self.edge_repo.get_from_node(node_id)
        # Get edges where this node is target
        in_edges = self.edge_repo.get_to_node(node_id)
        
        neighbor_ids = set()
        
        for edge in out_edges:
            if relationship_type is None or edge.relationship_type == relationship_type:
                neighbor_ids.add(edge.target_id)
                
        for edge in in_edges:
            if relationship_type is None or edge.relationship_type == relationship_type:
                neighbor_ids.add(edge.source_id)
                
        neighbors = []
        for nid in neighbor_ids:
            node = self.get_node(nid)
            if node:
                neighbors.append(node)
                
        return neighbors

    def find_similar_nodes(self, concept: str, limit: int = 10) -> List[GraphQueryResult]:
        """
        Find nodes similar to the given concept.
        
        NOTE: This implementation currently fetches all nodes to perform 
        semantic search in memory if vector DB is not set up.
        For production with large graphs, this should utilize pgvector.
        """
        # TODO: Implement pgvector support for true scalable semantic search
        
        # For now, we'll fetch recent/all nodes and use the embedding service 
        # similar to the in-memory engine, but this is not scalable.
        # A better approach for now is simple text search if no vector DB.
        
        if not self.embedding_service:
            return self.search_nodes(concept, limit)
            
        # If we have embedding service, we can try to be smarter.
        # But without vector DB, we can't efficiently search.
        # Fallback to search_nodes for this iteration.
        return self.search_nodes(concept, limit)

    def search_nodes(self, query: str, limit: int = 10) -> List[GraphQueryResult]:
        """Search nodes by content (simple SQL LIKE)"""
        # We'll implement a basic text search here
        # In a real app, use Full Text Search (Postgres TSVECTOR)
        
        # Get all nodes (warning: slow for large DBs)
        # Optimization: Just search by concept name for now
        
        # This is a limitation of the current repo interface, 
        # we'll do a direct query on the session for flexibility
        from database.models import ConceptNodeModel
        
        search = f"%{query}%"
        results = self.db.query(ConceptNodeModel).filter(
            (ConceptNodeModel.concept.ilike(search)) | 
            (ConceptNodeModel.content.ilike(search))
        ).limit(limit).all()
        
        graph_results = []
        for db_node in results:
            node = self.get_node(db_node.id)
            if node:
                graph_results.append(GraphQueryResult(
                    nodes=[node],
                    edges=[],
                    score=1.0 if query.lower() == db_node.concept.lower() else 0.5
                ))
                
        return graph_results

    def get_subgraph(self, center_node_id: str, depth: int = 2) -> Tuple[List[ConceptNode], List[GraphEdge]]:
        """Get a subgraph centered around a node"""
        if depth > 2:
            logger.warning("Depth > 2 not recommended for persistent graph queries without graph DB")
            depth = 2
            
        visited_ids = {center_node_id}
        nodes_map = {}
        edges_list = []
        
        # Get center node
        center_node = self.get_node(center_node_id)
        if not center_node:
            return [], []
            
        nodes_map[center_node_id] = center_node
        
        current_level = [center_node_id]
        
        for _ in range(depth):
            next_level = []
            for nid in current_level:
                # Get all connected edges
                out_edges = self.edge_repo.get_from_node(nid)
                in_edges = self.edge_repo.get_to_node(nid)
                
                all_edges = out_edges + in_edges
                
                for db_edge in all_edges:
                    # Convert DB edge to domain edge
                    edge = GraphEdge(
                        id=db_edge.id,
                        source_node_id=db_edge.source_id,
                        target_node_id=db_edge.target_id,
                        relationship_type=db_edge.relationship_type,
                        weight=db_edge.weight,
                        created_at=db_edge.created_at,
                        metadata={}
                    )
                    edges_list.append(edge)
                    
                    # Identify neighbor
                    neighbor_id = edge.target_node_id if edge.source_node_id == nid else edge.source_node_id
                    
                    if neighbor_id not in visited_ids:
                        visited_ids.add(neighbor_id)
                        next_level.append(neighbor_id)
                        
                        # Fetch neighbor node
                        neighbor = self.get_node(neighbor_id)
                        if neighbor:
                            nodes_map[neighbor_id] = neighbor
                            
            current_level = next_level
            
        return list(nodes_map.values()), edges_list
