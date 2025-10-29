"""
Repository implementations for database persistence.

Provides CRUD operations for all domain entities.
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import json

from database.models import (
    ConceptNodeModel,
    GraphEdgeModel,
    ExplorationModel,
    FeedbackModel,
    GeneratedContentModel,
)
from core.concept_orchestrator import ConceptNode, Exploration, ExplorationState
from knowledge_graph.engine import GraphEdge

logger = logging.getLogger(__name__)


class ConceptNodeRepository:
    """Repository for concept nodes."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, node: ConceptNode) -> ConceptNodeModel:
        """Create a new concept node in database."""
        db_node = ConceptNodeModel(
            id=node.id,
            concept=node.concept,
            content=node.content,
            metadata=json.dumps(node.metadata) if node.metadata else None,
            created_at=node.created_at,
        )
        self.db.add(db_node)
        self.db.commit()
        self.db.refresh(db_node)
        logger.debug(f"Created concept node: {node.id}")
        return db_node

    def get_by_id(self, node_id: str) -> Optional[ConceptNodeModel]:
        """Get a concept node by ID."""
        return self.db.query(ConceptNodeModel).filter(
            ConceptNodeModel.id == node_id
        ).first()

    def get_by_concept(self, concept: str) -> List[ConceptNodeModel]:
        """Get all nodes for a concept."""
        return self.db.query(ConceptNodeModel).filter(
            ConceptNodeModel.concept == concept
        ).all()

    def list_all(self, limit: int = 100) -> List[ConceptNodeModel]:
        """List all concept nodes."""
        return self.db.query(ConceptNodeModel).limit(limit).all()

    def update_quality_score(self, node_id: str, score: float) -> Optional[ConceptNodeModel]:
        """Update quality score for a node."""
        db_node = self.get_by_id(node_id)
        if db_node:
            db_node.quality_score = score
            db_node.updated_at = datetime.utcnow()
            self.db.commit()
            logger.debug(f"Updated quality score for node {node_id}: {score}")
        return db_node

    def delete(self, node_id: str) -> bool:
        """Delete a node by ID."""
        count = self.db.query(ConceptNodeModel).filter(
            ConceptNodeModel.id == node_id
        ).delete()
        if count:
            self.db.commit()
            logger.debug(f"Deleted node: {node_id}")
        return count > 0

    def count(self) -> int:
        """Count total nodes."""
        return self.db.query(ConceptNodeModel).count()


class GraphEdgeRepository:
    """Repository for graph edges."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, edge: GraphEdge) -> GraphEdgeModel:
        """Create a new edge."""
        db_edge = GraphEdgeModel(
            id=edge.id,
            source_id=edge.source_node_id,
            target_id=edge.target_node_id,
            relationship_type=edge.relationship_type,
            weight=edge.weight,
            created_at=edge.created_at,
        )
        self.db.add(db_edge)
        self.db.commit()
        self.db.refresh(db_edge)
        logger.debug(f"Created edge: {edge.id}")
        return db_edge

    def get_by_id(self, edge_id: str) -> Optional[GraphEdgeModel]:
        """Get an edge by ID."""
        return self.db.query(GraphEdgeModel).filter(
            GraphEdgeModel.id == edge_id
        ).first()

    def get_from_node(self, source_id: str) -> List[GraphEdgeModel]:
        """Get all edges from a source node."""
        return self.db.query(GraphEdgeModel).filter(
            GraphEdgeModel.source_id == source_id
        ).all()

    def get_to_node(self, target_id: str) -> List[GraphEdgeModel]:
        """Get all edges to a target node."""
        return self.db.query(GraphEdgeModel).filter(
            GraphEdgeModel.target_id == target_id
        ).all()

    def list_all(self, limit: int = 100) -> List[GraphEdgeModel]:
        """List all edges."""
        return self.db.query(GraphEdgeModel).limit(limit).all()

    def delete(self, edge_id: str) -> bool:
        """Delete an edge."""
        count = self.db.query(GraphEdgeModel).filter(
            GraphEdgeModel.id == edge_id
        ).delete()
        if count:
            self.db.commit()
            logger.debug(f"Deleted edge: {edge_id}")
        return count > 0

    def count(self) -> int:
        """Count total edges."""
        return self.db.query(GraphEdgeModel).count()


class ExplorationRepository:
    """Repository for explorations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, exploration: Exploration) -> ExplorationModel:
        """Create a new exploration."""
        db_exploration = ExplorationModel(
            id=exploration.id,
            concept=exploration.concept,
            status=exploration.status.value if hasattr(exploration.status, 'value') else str(exploration.status),
            created_at=exploration.created_at,
            metadata=json.dumps({"task_count": len(exploration.tasks)}),
        )
        self.db.add(db_exploration)
        self.db.commit()
        self.db.refresh(db_exploration)
        logger.debug(f"Created exploration: {exploration.id}")
        return db_exploration

    def get_by_id(self, exploration_id: str) -> Optional[ExplorationModel]:
        """Get an exploration by ID."""
        return self.db.query(ExplorationModel).filter(
            ExplorationModel.id == exploration_id
        ).first()

    def get_by_concept(self, concept: str) -> List[ExplorationModel]:
        """Get all explorations for a concept."""
        return self.db.query(ExplorationModel).filter(
            ExplorationModel.concept == concept
        ).all()

    def list_recent(self, limit: int = 10) -> List[ExplorationModel]:
        """Get recent explorations."""
        return self.db.query(ExplorationModel).order_by(
            ExplorationModel.created_at.desc()
        ).limit(limit).all()

    def update_status(self, exploration_id: str, status: str) -> Optional[ExplorationModel]:
        """Update exploration status."""
        db_exploration = self.get_by_id(exploration_id)
        if db_exploration:
            db_exploration.status = status
            db_exploration.updated_at = datetime.utcnow()
            if status == "COMPLETED":
                db_exploration.completed_at = datetime.utcnow()
            self.db.commit()
            logger.debug(f"Updated exploration {exploration_id} status: {status}")
        return db_exploration

    def update_counts(self, exploration_id: str, nodes_count: int, edges_count: int) -> Optional[ExplorationModel]:
        """Update node and edge counts."""
        db_exploration = self.get_by_id(exploration_id)
        if db_exploration:
            db_exploration.nodes_count = nodes_count
            db_exploration.edges_count = edges_count
            self.db.commit()
            logger.debug(f"Updated exploration {exploration_id} counts: nodes={nodes_count}, edges={edges_count}")
        return db_exploration

    def delete(self, exploration_id: str) -> bool:
        """Delete an exploration."""
        count = self.db.query(ExplorationModel).filter(
            ExplorationModel.id == exploration_id
        ).delete()
        if count:
            self.db.commit()
            logger.debug(f"Deleted exploration: {exploration_id}")
        return count > 0

    def count(self) -> int:
        """Count total explorations."""
        return self.db.query(ExplorationModel).count()


class FeedbackRepository:
    """Repository for feedback."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, exploration_id: str, feedback_type: str, rating: float, comment: Optional[str] = None):
        """Create feedback record."""
        db_feedback = FeedbackModel(
            exploration_id=exploration_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
        )
        self.db.add(db_feedback)
        self.db.commit()
        self.db.refresh(db_feedback)
        logger.debug(f"Created feedback for exploration {exploration_id}: {rating}")
        return db_feedback

    def get_by_exploration(self, exploration_id: str) -> List[FeedbackModel]:
        """Get all feedback for an exploration."""
        return self.db.query(FeedbackModel).filter(
            FeedbackModel.exploration_id == exploration_id
        ).all()

    def get_average_rating(self, exploration_id: str) -> Optional[float]:
        """Get average rating for an exploration."""
        from sqlalchemy import func
        result = self.db.query(func.avg(FeedbackModel.rating)).filter(
            FeedbackModel.exploration_id == exploration_id
        ).scalar()
        return float(result) if result else None

    def count(self) -> int:
        """Count total feedback records."""
        return self.db.query(FeedbackModel).count()


class GeneratedContentRepository:
    """Repository for generated content."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        exploration_id: str,
        concept: str,
        content_type: str,
        content: str,
        quality_score: float = 0.0,
        generation_method: Optional[str] = None,
    ):
        """Create generated content record."""
        db_content = GeneratedContentModel(
            exploration_id=exploration_id,
            concept=concept,
            content_type=content_type,
            content=content,
            quality_score=quality_score,
            generation_method=generation_method,
        )
        self.db.add(db_content)
        self.db.commit()
        self.db.refresh(db_content)
        logger.debug(f"Created content for {concept}: {content_type}")
        return db_content

    def get_by_exploration(self, exploration_id: str, content_type: Optional[str] = None) -> List[GeneratedContentModel]:
        """Get content for an exploration."""
        query = self.db.query(GeneratedContentModel).filter(
            GeneratedContentModel.exploration_id == exploration_id
        )
        if content_type:
            query = query.filter(GeneratedContentModel.content_type == content_type)
        return query.all()

    def get_by_concept(self, concept: str) -> List[GeneratedContentModel]:
        """Get content for a concept."""
        return self.db.query(GeneratedContentModel).filter(
            GeneratedContentModel.concept == concept
        ).all()

    def count(self) -> int:
        """Count total content records."""
        return self.db.query(GeneratedContentModel).count()
