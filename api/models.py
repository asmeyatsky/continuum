"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ConceptInputRequest(BaseModel):
    """Request to submit a concept for expansion."""
    concept: str = Field(..., min_length=1, max_length=500)
    context: Optional[str] = Field(None, max_length=2000)


class ConceptExpansionResponse(BaseModel):
    """Response from concept expansion."""
    exploration_id: str
    concept: str
    status: str
    nodes_count: int
    connections_count: int


class ConceptNodeResponse(BaseModel):
    """Response model for a concept node."""
    id: str
    concept: str
    content: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    connections: List[str]


class GraphEdgeResponse(BaseModel):
    """Response model for a graph edge."""
    source: str
    target: str
    relationship_type: str
    weight: float


class KnowledgeGraphResponse(BaseModel):
    """Response model for knowledge graph."""
    nodes: List[ConceptNodeResponse]
    edges: List[GraphEdgeResponse]
    total_nodes: int
    total_edges: int


class FeedbackRequest(BaseModel):
    """Request to submit feedback."""
    exploration_id: str
    feedback_type: str  # "quality", "accuracy", "relevance"
    rating: float = Field(..., ge=0.0, le=1.0)
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Response from feedback submission."""
    success: bool
    message: str


class ContentGenerationRequest(BaseModel):
    """Request to generate content."""
    concept: str
    content_type: str  # "text", "image", "audio", "video"
    style: Optional[str] = None


class ContentGenerationResponse(BaseModel):
    """Response from content generation."""
    content_id: str
    concept: str
    content_type: str
    content: str
    quality_score: float


class VisualizationRequest(BaseModel):
    """Request to generate visualization."""
    exploration_id: str
    visualization_type: str  # "3d", "timeline", "heatmap", "dashboard"


class VisualizationResponse(BaseModel):
    """Response from visualization generation."""
    visualization_id: str
    exploration_id: str
    visualization_type: str
    data_url: str  # URL to access the visualization


class SearchRequest(BaseModel):
    """Request to search the knowledge graph."""
    query: str
    limit: int = Field(10, ge=1, le=100)
    filters: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Response from search."""
    results: List[ConceptNodeResponse]
    total_results: int
    query: str


class HealthResponse(BaseModel):
    """Response from health check."""
    status: str
    version: str
    timestamp: datetime
