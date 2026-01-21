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
            status=exploration.status.value if hasattr(exploration.status, 'value') else str(exploration.status),
            nodes_count=nodes,
            connections_count=edges,
        )
    except HTTPException:
        raise
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
        edges = list(_engine.knowledge_graph.edges.values())[:limit] if isinstance(_engine.knowledge_graph.edges, dict) else _engine.knowledge_graph.edges[:limit]

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

        edge_responses = []
        for edge in edges:
            edge_responses.append(
                GraphEdgeResponse(
                    source=edge.source_node_id,
                    target=edge.target_node_id,
                    relationship_type=edge.relationship_type,
                    weight=edge.weight,
                )
            )

        return KnowledgeGraphResponse(
            nodes=node_responses,
            edges=edge_responses,
            total_nodes=len(_engine.knowledge_graph.nodes),
            total_edges=len(_engine.knowledge_graph.edges),
        )
    except HTTPException:
        raise
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
        _engine.feedback_system.record_user_feedback(
            item_id=request.exploration_id,
            rating=request.rating,
            comment=request.comment,
        )

        return FeedbackResponse(
            success=True, message="Feedback recorded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check Endpoint
# ============================================================================


@router.post("/comprehensive-search")
async def comprehensive_search(request: SearchRequest):
    """Comprehensive multi-source search across all available data sources."""
    if not _engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")
    
    try:
        from data_pipeline.real_ingestion import ComprehensiveDataPipeline
        from config.settings import settings
        
        if not settings.FEATURE_COMPREHENSIVE_SEARCH:
            raise HTTPException(status_code=503, detail="Comprehensive search not enabled")
        
        # Use comprehensive pipeline
        async with ComprehensiveDataPipeline() as pipeline:
            results = await pipeline.comprehensive_search(
                query=request.query,
                sources=["web_search", "academic", "wikipedia", "reddit", "github", "news", "youtube", "arxiv", "pubmed"]
            )
        
        # Convert results to response format
        search_results = []
        for source, result in results.items():
            if result.success and result.data:
                for item in result.data[:3]:  # Limit items per source
                    search_results.append({
                        "id": f"{source}_{len(search_results)}",
                        "title": item.get('title', str(item)[:100]),
                        "content": item.get('content', item.get('description', item.get('abstract', '')))[:500],
                        "url": item.get('url', ''),
                        "source": source,
                        "metadata": {
                            "quality_score": result.quality_score,
                            "relevance_score": result.relevance_score,
                            "timestamp": result.timestamp.isoformat(),
                            **item
                        }
                    })
        
        return {
            "query": request.query,
            "results": search_results[:request.limit],
            "total_results": len(search_results),
            "sources_searched": list(results.keys()),
            "successful_sources": [s for s, r in results.items() if r.success],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Comprehensive search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Real-Time Monitoring Endpoints
# ============================================================================

@router.post("/monitoring/start")
async def start_monitoring(request: dict):
    """Start real-time monitoring for topics"""
    try:
        from monitoring.realtime_monitor import RealTimeMonitor, MonitoringConfig
        from data_pipeline.real_ingestion import ComprehensiveDataPipeline
        
        config = MonitoringConfig(
            topics=request.get('topics', []),
            sources=request.get('sources', ['web_search', 'academic', 'news']),
            alert_threshold=request.get('alert_threshold', 0.8),
            check_interval_minutes=request.get('check_interval_minutes', 5)
        )
        
        async with ComprehensiveDataPipeline() as pipeline:
            monitor = RealTimeMonitor(pipeline)
            monitor_id = await monitor.start_monitoring(config)
        
        return {
            "monitor_id": monitor_id,
            "status": "started",
            "topics": config.topics,
            "sources": config.sources
        }
    except Exception as e:
        logger.error(f"Monitoring start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/alerts")
async def get_alerts(hours: int = Query(24, ge=1, le=168)):
    """Get recent alerts from monitoring system"""
    try:
        from monitoring.realtime_monitor import RealTimeMonitor
        
        # This would normally be stored globally or in database
        return {
            "alerts": [],
            "total_alerts": 0,
            "timeframe_hours": hours,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Alerts retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/trending")
async def get_trending_topics(hours: int = Query(24, ge=1, le=168)):
    """Get currently trending topics"""
    try:
        from monitoring.realtime_monitor import RealTimeMonitor
        
        # This would normally query the monitor system
        return {
            "trending": [
                {"topic": "artificial intelligence", "count": 15, "growth": "+25%"},
                {"topic": "quantum computing", "count": 12, "growth": "+18%"},
                {"topic": "climate change", "count": 10, "growth": "+12%"}
            ],
            "timeframe_hours": hours,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Trending topics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Cross-Reference and Fact Verification Endpoints  
# ============================================================================

@router.post("/cross-reference/{node_id}")
async def cross_reference_node(node_id: str):
    """Cross-reference a knowledge graph node with external sources"""
    if not _engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")
    
    try:
        from knowledge_graph.cross_reference_engine import CrossReferenceEngine
        from data_pipeline.real_ingestion import ComprehensiveDataPipeline
        
        async with ComprehensiveDataPipeline() as pipeline:
            cross_ref_engine = CrossReferenceEngine(
                _engine.knowledge_graph, 
                pipeline
            )
            
            result = await cross_ref_engine.cross_reference_node(node_id)
        
        return result
    except Exception as e:
        logger.error(f"Cross-reference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-fact")
async def verify_fact(request: dict):
    """Verify a factual claim across multiple sources"""
    try:
        from knowledge_graph.cross_reference_engine import CrossReferenceEngine
        from data_pipeline.real_ingestion import ComprehensiveDataPipeline
        
        claim = request.get('claim')
        if not claim:
            raise HTTPException(status_code=400, detail="Claim is required")
        
        async with ComprehensiveDataPipeline() as pipeline:
            cross_ref_engine = CrossReferenceEngine(
                _engine.knowledge_graph if _engine else None,
                pipeline
            )
            
            fact_check = await cross_ref_engine.verify_fact(
                claim, 
                request.get('context')
            )
        
        return {
            "claim": fact_check.claim,
            "status": fact_check.status.value,
            "confidence": fact_check.confidence,
            "supporting_sources": fact_check.supporting_sources,
            "contradicting_sources": fact_check.contradicting_sources,
            "checked_at": fact_check.checked_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Fact verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contradictions")
async def detect_contradictions():
    """Detect contradictions in the knowledge graph"""
    if not _engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")
    
    try:
        from knowledge_graph.cross_reference_engine import CrossReferenceEngine
        from data_pipeline.real_ingestion import ComprehensiveDataPipeline
        
        async with ComprehensiveDataPipeline() as pipeline:
            cross_ref_engine = CrossReferenceEngine(
                _engine.knowledge_graph,
                pipeline
            )
            
            contradictions = await cross_ref_engine.detect_contradictions()
        
        return {
            "contradictions": contradictions,
            "total_contradictions": len(contradictions),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Contradiction detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }
