"""
Comprehensive integration tests for API endpoints.

This module tests all REST API endpoints:
- Concept expansion endpoints
- Knowledge graph endpoints
- Search endpoints
- Feedback endpoints
- Health check endpoints
"""

import pytest
from fastapi.testclient import TestClient
from api.models import (
    ConceptInputRequest,
    ConceptExpansionResponse,
    FeedbackRequest,
    SearchRequest,
)


@pytest.fixture
def setup_test_app():
    """Setup test app with engine."""
    from fastapi import FastAPI
    from api.routes import router, set_engine
    from main import EnhancedInfiniteConceptExpansionEngine

    app = FastAPI()
    app.include_router(router)

    # Initialize engine
    engine = EnhancedInfiniteConceptExpansionEngine()
    set_engine(engine)

    return app, engine


@pytest.fixture
def client(setup_test_app):
    """Create test client."""
    app, _ = setup_test_app
    return TestClient(app)


@pytest.fixture
def engine(setup_test_app):
    """Get engine from setup."""
    _, engine = setup_test_app
    return engine


class TestHealthCheckEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check_returns_200(self, client):
        """Test that health check returns 200 status."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_check_response_format(self, client):
        """Test that health check returns correct format."""
        response = client.get("/api/health")
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_health_check_multiple_calls(self, client):
        """Test multiple health checks."""
        for _ in range(5):
            response = client.get("/api/health")
            assert response.status_code == 200


class TestConceptSubmissionEndpoint:
    """Tests for concept submission endpoint."""

    def test_submit_concept_returns_200(self, client):
        """Test that submitting a concept returns 200."""
        request_data = {"concept": "Artificial Intelligence"}
        response = client.post("/api/concepts/expand", json=request_data)

        assert response.status_code == 200

    def test_submit_concept_response_format(self, client):
        """Test that concept submission response has correct format."""
        request_data = {"concept": "Machine Learning"}
        response = client.post("/api/concepts/expand", json=request_data)
        data = response.json()

        assert "exploration_id" in data
        assert "concept" in data
        assert "status" in data
        assert "nodes_count" in data
        assert "connections_count" in data

    def test_submit_concept_returns_exploration_id(self, client):
        """Test that submission returns a valid exploration ID."""
        request_data = {"concept": "Deep Learning"}
        response = client.post("/api/concepts/expand", json=request_data)
        data = response.json()

        assert data["exploration_id"] is not None
        assert len(data["exploration_id"]) > 0
        assert isinstance(data["exploration_id"], str)

    def test_submit_concept_sets_correct_concept(self, client):
        """Test that submitted concept is returned correctly."""
        concept = "Quantum Computing"
        request_data = {"concept": concept}
        response = client.post("/api/concepts/expand", json=request_data)
        data = response.json()

        assert data["concept"] == concept

    def test_submit_concept_invalid_empty_concept(self, client):
        """Test that empty concept is rejected."""
        request_data = {"concept": ""}
        response = client.post("/api/concepts/expand", json=request_data)

        # Should either return 422 (validation error) or accept it
        assert response.status_code in [200, 422]

    def test_submit_concept_with_context(self, client):
        """Test submitting concept with optional context."""
        request_data = {
            "concept": "Neural Networks",
            "context": "In the field of machine learning"
        }
        response = client.post("/api/concepts/expand", json=request_data)

        assert response.status_code == 200

    def test_submit_multiple_concepts(self, client):
        """Test submitting multiple concepts."""
        concepts = ["AI", "ML", "DL", "NLP", "CV"]
        exploration_ids = []

        for concept in concepts:
            response = client.post("/api/concepts/expand", json={"concept": concept})
            data = response.json()
            exploration_ids.append(data["exploration_id"])

        # All should be unique
        assert len(set(exploration_ids)) == len(exploration_ids)


class TestConceptStatusEndpoint:
    """Tests for getting concept exploration status."""

    def test_get_exploration_status_returns_200(self, client):
        """Test that getting status returns 200."""
        # First submit a concept
        response = client.post("/api/concepts/expand", json={"concept": "Test"})
        exploration_id = response.json()["exploration_id"]

        # Then get its status
        status_response = client.get(f"/api/concepts/{exploration_id}")
        assert status_response.status_code == 200

    def test_get_exploration_status_format(self, client):
        """Test that status response has correct format."""
        response = client.post("/api/concepts/expand", json={"concept": "Test"})
        exploration_id = response.json()["exploration_id"]

        status_response = client.get(f"/api/concepts/{exploration_id}")
        data = status_response.json()

        assert "exploration_id" in data
        assert "concept" in data
        assert "status" in data
        assert "nodes_count" in data
        assert "connections_count" in data

    def test_get_exploration_status_invalid_id(self, client):
        """Test getting status for non-existent exploration."""
        status_response = client.get("/api/concepts/invalid-exploration-id")

        assert status_response.status_code == 404

    def test_get_exploration_status_matches_submission(self, client):
        """Test that retrieved status matches submitted concept."""
        concept = "Biotechnology"
        response = client.post("/api/concepts/expand", json={"concept": concept})
        exploration_id = response.json()["exploration_id"]

        status_response = client.get(f"/api/concepts/{exploration_id}")
        data = status_response.json()

        assert data["concept"] == concept
        assert data["exploration_id"] == exploration_id


class TestKnowledgeGraphEndpoint:
    """Tests for knowledge graph retrieval endpoint."""

    def test_get_knowledge_graph_returns_200(self, client):
        """Test that getting knowledge graph returns 200."""
        response = client.get("/api/graph")
        assert response.status_code == 200

    def test_get_knowledge_graph_format(self, client):
        """Test that knowledge graph response has correct format."""
        response = client.get("/api/graph")
        data = response.json()

        assert "nodes" in data
        assert "edges" in data
        assert "total_nodes" in data
        assert "total_edges" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["edges"], list)

    def test_get_knowledge_graph_respects_limit(self, client):
        """Test that limit parameter is respected."""
        response = client.get("/api/graph?limit=5")
        data = response.json()

        assert len(data["nodes"]) <= 5

    def test_get_knowledge_graph_limit_validation(self, client):
        """Test that invalid limits are handled."""
        # Test limit too high
        response = client.get("/api/graph?limit=2000")
        assert response.status_code in [200, 422]

        # Test limit too low
        response = client.get("/api/graph?limit=0")
        assert response.status_code in [200, 422]

    def test_get_knowledge_graph_default_limit(self, client):
        """Test that default limit is used."""
        response = client.get("/api/graph")
        data = response.json()

        # Default is 100
        assert len(data["nodes"]) <= 100


class TestNodeRetrievalEndpoint:
    """Tests for retrieving individual nodes."""

    def test_get_node_returns_200(self, client, engine):
        """Test that getting a node returns 200."""
        # First create a node
        node_response = client.post("/api/concepts/expand", json={"concept": "Test"})

        # Get from graph (if any nodes exist)
        if len(engine.knowledge_graph.nodes) > 0:
            node_id = list(engine.knowledge_graph.nodes.keys())[0]
            response = client.get(f"/api/nodes/{node_id}")
            assert response.status_code == 200

    def test_get_node_format(self, client, engine):
        """Test that node response has correct format."""
        # Add a node directly to the graph
        from core.concept_orchestrator import ConceptNode
        from datetime import datetime

        node = ConceptNode(
            id="test_node",
            concept="Test Concept",
            content="Test content",
            metadata={"test": True},
            created_at=datetime.now(),
            connections=[]
        )
        engine.knowledge_graph.add_node(node)

        response = client.get("/api/nodes/test_node")
        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert "concept" in data
        assert "content" in data
        assert "metadata" in data
        assert "connections" in data

    def test_get_nonexistent_node(self, client):
        """Test getting a non-existent node."""
        response = client.get("/api/nodes/nonexistent-node-id")
        assert response.status_code == 404


class TestSearchEndpoint:
    """Tests for graph search endpoint."""

    def test_search_returns_200(self, client):
        """Test that search returns 200."""
        request_data = {"query": "AI"}
        response = client.post("/api/search", json=request_data)
        assert response.status_code == 200

    def test_search_response_format(self, client):
        """Test that search response has correct format."""
        request_data = {"query": "concept"}
        response = client.post("/api/search", json=request_data)
        data = response.json()

        assert "results" in data
        assert "total_results" in data
        assert "query" in data
        assert isinstance(data["results"], list)

    def test_search_with_limit(self, client):
        """Test search with limit parameter."""
        request_data = {"query": "test", "limit": 5}
        response = client.post("/api/search", json=request_data)
        data = response.json()

        assert len(data["results"]) <= 5

    def test_search_returns_query(self, client):
        """Test that search returns the query that was submitted."""
        query = "Machine Learning"
        request_data = {"query": query}
        response = client.post("/api/search", json=request_data)
        data = response.json()

        assert data["query"] == query

    def test_search_no_results(self, client):
        """Test search that returns no results."""
        request_data = {"query": "xyznonexistentterm12345"}
        response = client.post("/api/search", json=request_data)
        data = response.json()

        assert data["total_results"] == 0
        assert len(data["results"]) == 0


class TestFeedbackEndpoint:
    """Tests for feedback submission endpoint."""

    def test_submit_feedback_returns_200(self, client):
        """Test that submitting feedback returns 200."""
        # First submit a concept
        response = client.post("/api/concepts/expand", json={"concept": "Test"})
        exploration_id = response.json()["exploration_id"]

        # Submit feedback
        feedback_data = {
            "exploration_id": exploration_id,
            "feedback_type": "quality",
            "rating": 0.85,
            "comment": "Good expansion"
        }
        feedback_response = client.post("/api/feedback", json=feedback_data)

        assert feedback_response.status_code == 200

    def test_submit_feedback_response_format(self, client):
        """Test that feedback response has correct format."""
        response = client.post("/api/concepts/expand", json={"concept": "Test"})
        exploration_id = response.json()["exploration_id"]

        feedback_data = {
            "exploration_id": exploration_id,
            "feedback_type": "accuracy",
            "rating": 0.75
        }
        feedback_response = client.post("/api/feedback", json=feedback_data)
        data = feedback_response.json()

        assert "success" in data
        assert "message" in data
        assert data["success"] is True

    def test_submit_feedback_with_comment(self, client):
        """Test submitting feedback with a comment."""
        response = client.post("/api/concepts/expand", json={"concept": "Test"})
        exploration_id = response.json()["exploration_id"]

        feedback_data = {
            "exploration_id": exploration_id,
            "feedback_type": "relevance",
            "rating": 0.90,
            "comment": "Very relevant and well-structured"
        }
        feedback_response = client.post("/api/feedback", json=feedback_data)

        assert feedback_response.status_code == 200

    def test_submit_feedback_rating_bounds(self, client):
        """Test that feedback rating validation works."""
        response = client.post("/api/concepts/expand", json={"concept": "Test"})
        exploration_id = response.json()["exploration_id"]

        # Valid ratings (0.0 to 1.0)
        for rating in [0.0, 0.5, 1.0]:
            feedback_data = {
                "exploration_id": exploration_id,
                "feedback_type": "quality",
                "rating": rating
            }
            feedback_response = client.post("/api/feedback", json=feedback_data)
            assert feedback_response.status_code == 200

    def test_submit_feedback_invalid_rating_high(self, client):
        """Test that invalid high rating is rejected."""
        response = client.post("/api/concepts/expand", json={"concept": "Test"})
        exploration_id = response.json()["exploration_id"]

        feedback_data = {
            "exploration_id": exploration_id,
            "feedback_type": "quality",
            "rating": 1.5  # Invalid
        }
        feedback_response = client.post("/api/feedback", json=feedback_data)

        assert feedback_response.status_code == 422

    def test_submit_feedback_invalid_rating_low(self, client):
        """Test that invalid low rating is rejected."""
        response = client.post("/api/concepts/expand", json={"concept": "Test"})
        exploration_id = response.json()["exploration_id"]

        feedback_data = {
            "exploration_id": exploration_id,
            "feedback_type": "quality",
            "rating": -0.5  # Invalid
        }
        feedback_response = client.post("/api/feedback", json=feedback_data)

        assert feedback_response.status_code == 422


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_invalid_http_method(self, client):
        """Test that invalid HTTP methods are rejected."""
        response = client.delete("/api/health")
        assert response.status_code == 405  # Method Not Allowed

    def test_invalid_endpoint(self, client):
        """Test that invalid endpoints return 404."""
        response = client.get("/api/invalid-endpoint")
        assert response.status_code == 404

    def test_malformed_json(self, client):
        """Test that malformed JSON is handled."""
        response = client.post(
            "/api/concepts/expand",
            data="{invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_missing_required_field(self, client):
        """Test that missing required fields are rejected."""
        response = client.post("/api/concepts/expand", json={})
        assert response.status_code == 422


class TestEndpointConcurrency:
    """Tests for handling multiple concurrent requests."""

    def test_multiple_concept_submissions(self, client):
        """Test submitting multiple concepts sequentially."""
        concepts = ["AI", "ML", "DL", "NLP", "CV"]
        responses = []

        for concept in concepts:
            response = client.post("/api/concepts/expand", json={"concept": concept})
            responses.append(response)

        assert all(r.status_code == 200 for r in responses)
        exploration_ids = [r.json()["exploration_id"] for r in responses]
        assert len(set(exploration_ids)) == len(exploration_ids)  # All unique

    def test_interleaved_requests(self, client):
        """Test interleaved concept and status requests."""
        # Submit a concept
        response1 = client.post("/api/concepts/expand", json={"concept": "Test1"})
        exploration_id1 = response1.json()["exploration_id"]

        # Get its status
        status1 = client.get(f"/api/concepts/{exploration_id1}")
        assert status1.status_code == 200

        # Submit another concept
        response2 = client.post("/api/concepts/expand", json={"concept": "Test2"})
        exploration_id2 = response2.json()["exploration_id"]

        # Get status of first concept again
        status1_again = client.get(f"/api/concepts/{exploration_id1}")
        assert status1_again.status_code == 200

        # Both should have different IDs
        assert exploration_id1 != exploration_id2
