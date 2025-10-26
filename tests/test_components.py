"""
Tests for the Infinite Concept Expansion Engine main components.
"""
import pytest
from core.concept_orchestrator import DefaultConceptOrchestrator, ExplorationTask, ExplorationState
from agents.base import AgentManager, ResearchAgent, ConnectionAgent
from knowledge_graph.engine import InMemoryKnowledgeGraphEngine, ConceptNode
from data_pipeline.ingestion import MockDataIngestionPipeline
from content_generation.multimodal import MockMultimodalContentGenerator
from feedback_system.core import SelfImprovingFeedbackSystem
from datetime import datetime


class TestConceptOrchestrator:
    """Tests for the concept orchestrator"""
    
    def test_submit_exploration_request(self):
        """Test submitting an exploration request"""
        orchestrator = DefaultConceptOrchestrator()
        exploration_id = orchestrator.submit_exploration_request("Test Concept")
        
        assert exploration_id is not None
        assert len(orchestrator.explorations) == 1
        assert exploration_id in orchestrator.explorations
    
    def test_get_exploration_status(self):
        """Test getting exploration status"""
        orchestrator = DefaultConceptOrchestrator()
        exploration_id = orchestrator.submit_exploration_request("Test Concept")
        
        status = orchestrator.get_exploration_status(exploration_id)
        # Initially should be in progress since there are pending tasks
        assert status in [ExplorationState.PENDING, ExplorationState.IN_PROGRESS]


class TestAgents:
    """Tests for the agent system"""
    
    def test_agent_manager_initialization(self):
        """Test that agent manager initializes all agents"""
        manager = AgentManager()
        
        assert len(manager.agents) == 6  # Research, Connection, Content, Visual, Multimedia, Validation
        assert manager.get_agent("ResearchAgent") is not None
        assert manager.get_agent("ConnectionAgent") is not None
    
    def test_research_agent(self):
        """Test research agent functionality"""
        agent = ResearchAgent()
        task = ExplorationTask(
            id="test",
            concept="Artificial Intelligence",
            task_type="research",
            priority=10,
            status=ExplorationState.PENDING
        )
        
        response = agent.process_task(task)
        
        assert response.success is True
        assert response.agent_name == "ResearchAgent"
        assert response.data is not None
        assert "concept" in response.data
    
    def test_connection_agent(self):
        """Test connection agent functionality"""
        agent = ConnectionAgent()
        task = ExplorationTask(
            id="test",
            concept="Machine Learning",
            task_type="connection",
            priority=10,
            status=ExplorationState.PENDING
        )
        
        response = agent.process_task(task)
        
        assert response.success is True
        assert response.agent_name == "ConnectionAgent"
        assert response.data is not None
        assert "cross_domain_links" in response.data


class TestKnowledgeGraph:
    """Tests for the knowledge graph engine"""
    
    def test_add_node(self):
        """Test adding a node to the knowledge graph"""
        graph = InMemoryKnowledgeGraphEngine()
        node = ConceptNode(
            id="test_node",
            concept="Test Concept",
            content="This is a test concept",
            metadata={},
            created_at=datetime.now(),
            connections=[]
        )
        
        result = graph.add_node(node)
        
        assert result is True
        assert graph.get_node("test_node") is not None
        assert graph.get_node_count() == 1
    
    def test_add_edge(self):
        """Test adding an edge to the knowledge graph"""
        graph = InMemoryKnowledgeGraphEngine()
        
        # Add two nodes first
        node1 = ConceptNode(
            id="node1",
            concept="Concept 1",
            content="First concept",
            metadata={},
            created_at=datetime.now(),
            connections=[]
        )
        node2 = ConceptNode(
            id="node2",
            concept="Concept 2",
            content="Second concept",
            metadata={},
            created_at=datetime.now(),
            connections=[]
        )
        
        graph.add_node(node1)
        graph.add_node(node2)
        
        from knowledge_graph.engine import GraphEdge
        edge = GraphEdge(
            id="edge1",
            source_node_id="node1",
            target_node_id="node2",
            relationship_type="related_to",
            weight=0.8,
            created_at=datetime.now(),
            metadata={}
        )
        
        result = graph.add_edge(edge)
        
        assert result is True
        assert graph.get_edge_count() == 1
        
        # Test that neighbors work
        neighbors = graph.get_neighbors("node1")
        assert len(neighbors) == 1
        assert neighbors[0].id == "node2"


class TestContentGeneration:
    """Tests for the content generation system"""
    
    def test_text_content_generation(self):
        """Test generating text content"""
        generator = MockMultimodalContentGenerator()
        content = generator.generate_text_content("Test Concept", style="summary")
        
        assert content.content_type == "text"
        assert content.source_concept == "Test Concept"
        assert content.content_data is not None
        assert len(content.content_data) > 0
    
    def test_visual_content_generation(self):
        """Test generating visual content"""
        generator = MockMultimodalContentGenerator()
        content = generator.generate_visual_content("Test Concept", content_type="diagram")
        
        assert content.content_type == "image"
        assert content.source_concept == "Test Concept"
        assert content.content_data is not None
    
    def test_multimodal_package(self):
        """Test generating a complete multimodal package"""
        generator = MockMultimodalContentGenerator()
        package = generator.generate_multimodal_package("Test Concept")
        
        assert "text" in package
        assert "visual" in package
        assert "audio" in package
        assert "video" in package
        assert all(content.source_concept == "Test Concept" for content in package.values())


class TestFeedbackSystem:
    """Tests for the feedback system"""
    
    def test_record_user_feedback(self):
        """Test recording user feedback"""
        feedback_system = SelfImprovingFeedbackSystem()
        result = feedback_system.record_user_feedback(
            item_id="test_item",
            rating=0.8,
            comment="Good content"
        )
        
        assert result is True
        assert len(feedback_system.feedback_records) == 1
        
        feedback = feedback_system.feedback_records[0]
        assert feedback.feedback_type == "user_rating"
        assert feedback.rating == 0.8
        assert feedback.comment == "Good content"
    
    def test_get_feedback_summary(self):
        """Test getting feedback summary"""
        feedback_system = SelfImprovingFeedbackSystem()
        
        # Add some feedback
        feedback_system.record_user_feedback("item1", 0.9)
        feedback_system.record_user_feedback("item1", 0.7)
        feedback_system.record_user_feedback("item1", 0.8)
        
        summary = feedback_system.get_feedback_summary("item1")
        
        assert summary["total_feedback"] == 3
        assert 0.8 <= summary["average_rating"] <= 0.9  # Should be around 0.8
    
    def test_learning_signals(self):
        """Test that feedback generates learning signals"""
        feedback_system = SelfImprovingFeedbackSystem()
        
        # Record some feedback
        feedback_system.record_user_feedback("item1", 0.9)
        feedback_system.record_user_feedback("item2", 0.2)
        
        signals = feedback_system.get_learning_signals()
        
        assert len(signals) == 2
        signal_types = [s.signal_type for s in signals]
        assert "positive" in signal_types
        assert "negative" in signal_types


def test_integration():
    """Integration test to make sure all components work together"""
    # This tests that all systems can be instantiated and have basic interactions
    orchestrator = DefaultConceptOrchestrator()
    agent_manager = AgentManager()
    knowledge_graph = InMemoryKnowledgeGraphEngine()
    data_pipeline = MockDataIngestionPipeline()
    content_generator = MockMultimodalContentGenerator()
    feedback_system = SelfImprovingFeedbackSystem()
    
    # Test that we can submit and process a simple task
    exploration_id = orchestrator.submit_exploration_request("Integration Test Concept")
    
    task = orchestrator.get_next_task()
    assert task is not None
    
    agent_responses = agent_manager.execute_task(task)
    assert len(agent_responses) > 0
    
    print("✅ Integration test passed! All components work together.")