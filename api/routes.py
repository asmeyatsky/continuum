"""
API routes for the Continuum application.
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from api.models import (
    ConceptInputRequest,
    ConceptExpansionResponse,
    KnowledgeGraphResponse,
    FeedbackRequest,
    FeedbackResponse,
    ContentGenerationRequest,
    ContentGenerationResponse,
    VisualizationRequest,
    VisualizationResponse,
    SearchRequest,
    SearchResponse,
    ConceptNodeResponse,
    GraphEdgeResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["continuum"])

# Global engine reference (will be set at startup)
_engine = None


def set_engine(engine):
    """Set the engine instance for use in routes."""
    global _engine
    _engine = engine


# ============================================================================
# Concept Expansion Endpoints
# ============================================================================


@router.post("/concepts/expand", response_model=ConceptExpansionResponse)
async def submit_concept(request: ConceptInputRequest):
    """
    Submit a concept for expansion.

    The system will autonomously explore the concept and build a knowledge graph.
    """
    if not _engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")

    try:
        exploration_id = _engine.submit_concept(request.concept)

        # Get initial stats
        nodes = len(_engine.knowledge_graph.nodes)
        edges = len(_engine.knowledge_graph.edges)

        return ConceptExpansionResponse(
            exploration_id=exploration_id,
            concept=request.concept,
            status="processing",
            nodes_count=nodes,
            connections_count=edges,
        )
    except Exception as e:
        logger.error(f"Error submitting concept: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/concepts/{exploration_id}", response_model=ConceptExpansionResponse)
async def get_exploration_status(exploration_id: str):
    """Get the status of a concept exploration."""
    if not _engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")

    try:
        # Get exploration status
        exploration = _engine.orchestrator.explorations.get(exploration_id)
        if not exploration:
            raise HTTPException(status_code=404, detail="Exploration not found")

        nodes = len(_engine.knowledge_graph.nodes)
        edges = len(_engine.knowledge_graph.edges)

        return ConceptExpansionResponse(
            exploration_id=exploration_id,
            concept=exploration.concept,
            status=exploration.status,
            nodes_count=nodes,
            connections_count=edges,
        )
    except Exception as e:
        logger.error(f"Error getting exploration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Knowledge Graph Endpoints
# ============================================================================


@router.get("/graph", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph(limit: int = Query(100, ge=1, le=1000)):
    """Get the entire knowledge graph or a limited subset."""
    if not _engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")

    try:
        nodes = list(_engine.knowledge_graph.nodes.values())[:limit]
        edges = _engine.knowledge_graph.edges[:limit]

        node_responses = [
            ConceptNodeResponse(
                id=node.id,
                concept=node.concept,
                content=node.content,
                metadata=node.metadata,
                created_at=node.created_at,
                connections=node.connections,
            )
            for node in nodes
        ]

        edge_responses = [
            GraphEdgeResponse(
                source=edge.source,
                target=edge.target,
                relationship_type=edge.relationship_type,
                weight=edge.weight,
            )
            for edge in edges
        ]

        return KnowledgeGraphResponse(
            nodes=node_responses,
            edges=edge_responses,
            total_nodes=len(_engine.knowledge_graph.nodes),
            total_edges=len(_engine.knowledge_graph.edges),
        )
    except Exception as e:
        logger.error(f"Error retrieving knowledge graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodes/{node_id}", response_model=ConceptNodeResponse)
async def get_node(node_id: str):
    """Get a specific node from the knowledge graph."""
    if not _engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")

    try:
        node = _engine.knowledge_graph.nodes.get(node_id)
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")

        return ConceptNodeResponse(
            id=node.id,
            concept=node.concept,
            content=node.content,
            metadata=node.metadata,
            created_at=node.created_at,
            connections=node.connections,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving node: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Search Endpoints
# ============================================================================


@router.post("/search", response_model=SearchResponse)
async def search_graph(request: SearchRequest):
    """Search the knowledge graph for concepts."""
    if not _engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")

    try:
        # Perform text search on concept names and content
        query_lower = request.query.lower()
        results = []

        for node in _engine.knowledge_graph.nodes.values():
            if (
                query_lower in node.concept.lower()
                or (node.content and query_lower in node.content.lower())
            ):
                results.append(node)

            if len(results) >= request.limit:
                break

        node_responses = [
            ConceptNodeResponse(
                id=node.id,
                concept=node.concept,
                content=node.content,
                metadata=node.metadata,
                created_at=node.created_at,
                connections=node.connections,
            )
            for node in results
        ]

        return SearchResponse(
            results=node_responses,
            total_results=len(results),
            query=request.query,
        )
    except Exception as e:
        logger.error(f"Error searching graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Feedback Endpoints
# ============================================================================


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback on an exploration."""
    if not _engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")

    try:
        _engine.feedback_system.record_feedback(
            exploration_id=request.exploration_id,
            feedback_type=request.feedback_type,
            rating=request.rating,
            comment=request.comment,
        )

        return FeedbackResponse(
            success=True, message="Feedback recorded successfully"
        )
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check Endpoint
# ============================================================================


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }
