"""
SQLAlchemy models for database persistence.
"""
from sqlalchemy import Column, String, Float, DateTime, Text, Integer, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


# Association table for many-to-many relationship
concept_connections = Table(
    "concept_connections",
    Base.metadata,
    Column("source_id", String, ForeignKey("concept_nodes.id"), primary_key=True),
    Column("target_id", String, ForeignKey("concept_nodes.id"), primary_key=True),
)


class ConceptNodeModel(Base):
    """SQLAlchemy model for ConceptNode."""

    __tablename__ = "concept_nodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    concept = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=True)
    embedding = Column(Text, nullable=True)  # Stored as JSON string
    quality_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(Text, nullable=True)  # Stored as JSON string

    # Relationships
    edges_source = relationship(
        "GraphEdgeModel",
        foreign_keys="GraphEdgeModel.source_id",
        backref="source_node",
        cascade="all, delete-orphan",
    )
    edges_target = relationship(
        "GraphEdgeModel",
        foreign_keys="GraphEdgeModel.target_id",
        backref="target_node",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ConceptNodeModel(id={self.id}, concept={self.concept})>"


class GraphEdgeModel(Base):
    """SQLAlchemy model for GraphEdge."""

    __tablename__ = "graph_edges"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String, ForeignKey("concept_nodes.id"), nullable=False, index=True)
    target_id = Column(String, ForeignKey("concept_nodes.id"), nullable=False, index=True)
    relationship_type = Column(String, nullable=False)
    weight = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<GraphEdgeModel(source={self.source_id}, target={self.target_id}, type={self.relationship_type})>"


class ExplorationModel(Base):
    """SQLAlchemy model for Exploration."""

    __tablename__ = "explorations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    concept = Column(String, nullable=False, index=True)
    status = Column(String, default="PENDING", nullable=False)
    priority = Column(Integer, default=0)
    nodes_count = Column(Integer, default=0)
    edges_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    meta_data = Column(Text, nullable=True)  # Stored as JSON string

    def __repr__(self) -> str:
        return f"<ExplorationModel(id={self.id}, concept={self.concept}, status={self.status})>"


class FeedbackModel(Base):
    """SQLAlchemy model for Feedback."""

    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exploration_id = Column(String, ForeignKey("explorations.id"), nullable=False, index=True)
    feedback_type = Column(String, nullable=False)  # "quality", "accuracy", "relevance"
    rating = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<FeedbackModel(exploration_id={self.exploration_id}, rating={self.rating})>"


class GeneratedContentModel(Base):
    """SQLAlchemy model for Generated Content."""

    __tablename__ = "generated_content"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exploration_id = Column(String, ForeignKey("explorations.id"), nullable=False, index=True)
    concept = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # "text", "image", "audio", "video"
    content = Column(Text, nullable=False)
    quality_score = Column(Float, default=0.0)
    generation_method = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<GeneratedContentModel(id={self.id}, concept={self.concept}, type={self.content_type})>"
