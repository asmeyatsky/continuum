"""
Comprehensive tests for the Agent system.

This module tests all agents:
- ResearchAgent
- ConnectionAgent
- ContentGenerationAgent
- VisualAgent
- MultimediaAgent
- ValidationAgent
- AgentManager
"""

import pytest
from agents.base import (
    ResearchAgent,
    ConnectionAgent,
    ContentGenerationAgent,
    VisualAgent,
    MultimediaAgent,
    ValidationAgent,
    AgentManager,
    AgentResponse,
)
from core.concept_orchestrator import ExplorationTask, ExplorationState


class TestBaseAgentInterface:
    """Tests for basic agent interface compliance."""

    def test_research_agent_implements_interface(self):
        """Test that ResearchAgent implements BaseAgent interface."""
        agent = ResearchAgent()
        assert hasattr(agent, "process_task")
        assert hasattr(agent, "get_agent_name")
        assert callable(agent.process_task)
        assert callable(agent.get_agent_name)

    def test_connection_agent_implements_interface(self):
        """Test that ConnectionAgent implements BaseAgent interface."""
        agent = ConnectionAgent()
        assert hasattr(agent, "process_task")
        assert hasattr(agent, "get_agent_name")

    def test_content_generation_agent_implements_interface(self):
        """Test that ContentGenerationAgent implements BaseAgent interface."""
        agent = ContentGenerationAgent()
        assert hasattr(agent, "process_task")
        assert hasattr(agent, "get_agent_name")

    def test_visual_agent_implements_interface(self):
        """Test that VisualAgent implements BaseAgent interface."""
        agent = VisualAgent()
        assert hasattr(agent, "process_task")
        assert hasattr(agent, "get_agent_name")

    def test_multimedia_agent_implements_interface(self):
        """Test that MultimediaAgent implements BaseAgent interface."""
        agent = MultimediaAgent()
        assert hasattr(agent, "process_task")
        assert hasattr(agent, "get_agent_name")

    def test_validation_agent_implements_interface(self):
        """Test that ValidationAgent implements BaseAgent interface."""
        agent = ValidationAgent()
        assert hasattr(agent, "process_task")
        assert hasattr(agent, "get_agent_name")


class TestResearchAgent:
    """Tests for the ResearchAgent."""

    def test_research_agent_name(self):
        """Test that ResearchAgent returns correct name."""
        agent = ResearchAgent()
        assert agent.get_agent_name() == "ResearchAgent"

    def test_research_agent_process_task(self):
        """Test that ResearchAgent can process a task."""
        agent = ResearchAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Artificial Intelligence",
            task_type="research",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert isinstance(response, AgentResponse)
        assert response.success is True
        assert response.agent_name == "ResearchAgent"
        assert response.data is not None
        assert response.confidence > 0

    def test_research_agent_response_contains_sources(self):
        """Test that ResearchAgent response contains sources."""
        agent = ResearchAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Machine Learning",
            task_type="research",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert "sources" in response.data
        assert isinstance(response.data["sources"], list)

    def test_research_agent_response_contains_summary(self):
        """Test that ResearchAgent response contains a summary."""
        agent = ResearchAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Deep Learning",
            task_type="research",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert "summary" in response.data


class TestConnectionAgent:
    """Tests for the ConnectionAgent."""

    def test_connection_agent_name(self):
        """Test that ConnectionAgent returns correct name."""
        agent = ConnectionAgent()
        assert agent.get_agent_name() == "ConnectionAgent"

    def test_connection_agent_process_task(self):
        """Test that ConnectionAgent can process a task."""
        agent = ConnectionAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Quantum Computing",
            task_type="connection",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert isinstance(response, AgentResponse)
        assert response.success is True
        assert response.agent_name == "ConnectionAgent"
        assert response.data is not None

    def test_connection_agent_finds_analogies(self):
        """Test that ConnectionAgent finds analogies."""
        agent = ConnectionAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Neural Networks",
            task_type="connection",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert "analogies" in response.data
        assert isinstance(response.data["analogies"], list)

    def test_connection_agent_finds_cross_domain_links(self):
        """Test that ConnectionAgent finds cross-domain links."""
        agent = ConnectionAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Photosynthesis",
            task_type="connection",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert "cross_domain_links" in response.data
        assert isinstance(response.data["cross_domain_links"], list)


class TestContentGenerationAgent:
    """Tests for the ContentGenerationAgent."""

    def test_content_generation_agent_name(self):
        """Test that ContentGenerationAgent returns correct name."""
        agent = ContentGenerationAgent()
        assert agent.get_agent_name() == "ContentGenerationAgent"

    def test_content_generation_agent_process_task(self):
        """Test that ContentGenerationAgent can process a task."""
        agent = ContentGenerationAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Climate Change",
            task_type="content_generation",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert isinstance(response, AgentResponse)
        assert response.success is True
        assert response.agent_name == "ContentGenerationAgent"

    def test_content_generation_agent_creates_summary(self):
        """Test that ContentGenerationAgent creates a summary."""
        agent = ContentGenerationAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Renewable Energy",
            task_type="content_generation",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert "summary" in response.data
        assert isinstance(response.data["summary"], str)

    def test_content_generation_agent_creates_explanation(self):
        """Test that ContentGenerationAgent creates an explanation."""
        agent = ContentGenerationAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Blockchain",
            task_type="content_generation",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert "explanation" in response.data


class TestVisualAgent:
    """Tests for the VisualAgent."""

    def test_visual_agent_name(self):
        """Test that VisualAgent returns correct name."""
        agent = VisualAgent()
        assert agent.get_agent_name() == "VisualAgent"

    def test_visual_agent_process_task(self):
        """Test that VisualAgent can process a task."""
        agent = VisualAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Evolution",
            task_type="visual_generation",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert isinstance(response, AgentResponse)
        assert response.success is True
        assert response.agent_name == "VisualAgent"

    def test_visual_agent_generates_diagrams(self):
        """Test that VisualAgent generates diagrams."""
        agent = VisualAgent()
        task = ExplorationTask(
            id="test_task",
            concept="DNA",
            task_type="visual_generation",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert "diagrams" in response.data
        assert isinstance(response.data["diagrams"], list)


class TestMultimediaAgent:
    """Tests for the MultimediaAgent."""

    def test_multimedia_agent_name(self):
        """Test that MultimediaAgent returns correct name."""
        agent = MultimediaAgent()
        assert agent.get_agent_name() == "MultimediaAgent"

    def test_multimedia_agent_process_task(self):
        """Test that MultimediaAgent can process a task."""
        agent = MultimediaAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Music Theory",
            task_type="multimedia_generation",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert isinstance(response, AgentResponse)
        assert response.success is True
        assert response.agent_name == "MultimediaAgent"

    def test_multimedia_agent_provides_audio(self):
        """Test that MultimediaAgent provides audio content."""
        agent = MultimediaAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Acoustics",
            task_type="multimedia_generation",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert "audio" in response.data

    def test_multimedia_agent_provides_video(self):
        """Test that MultimediaAgent provides video content."""
        agent = MultimediaAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Cinematography",
            task_type="multimedia_generation",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert "video" in response.data


class TestValidationAgent:
    """Tests for the ValidationAgent."""

    def test_validation_agent_name(self):
        """Test that ValidationAgent returns correct name."""
        agent = ValidationAgent()
        assert agent.get_agent_name() == "ValidationAgent"

    def test_validation_agent_process_task(self):
        """Test that ValidationAgent can process a task."""
        agent = ValidationAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Scientific Method",
            task_type="validation",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert isinstance(response, AgentResponse)
        assert response.success is True
        assert response.agent_name == "ValidationAgent"

    def test_validation_agent_fact_checks(self):
        """Test that ValidationAgent fact-checks."""
        agent = ValidationAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Earth Science",
            task_type="validation",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert "fact_check_results" in response.data
        assert isinstance(response.data["fact_check_results"], list)

    def test_validation_agent_provides_quality_score(self):
        """Test that ValidationAgent provides a quality score."""
        agent = ValidationAgent()
        task = ExplorationTask(
            id="test_task",
            concept="Chemistry",
            task_type="validation",
            priority=10,
            status=ExplorationState.PENDING
        )

        response = agent.process_task(task)

        assert "quality_score" in response.data
        assert 0 <= response.data["quality_score"] <= 1


class TestAgentManager:
    """Tests for the AgentManager."""

    def test_agent_manager_initialization(self):
        """Test that AgentManager initializes all agents."""
        manager = AgentManager()

        assert len(manager.agents) == 6
        assert "ResearchAgent" in manager.agents
        assert "ConnectionAgent" in manager.agents
        assert "ContentGenerationAgent" in manager.agents
        assert "VisualAgent" in manager.agents
        assert "MultimediaAgent" in manager.agents
        assert "ValidationAgent" in manager.agents

    def test_agent_manager_get_agent(self):
        """Test getting a specific agent by name."""
        manager = AgentManager()
        agent = manager.get_agent("ResearchAgent")

        assert agent is not None
        assert agent.get_agent_name() == "ResearchAgent"

    def test_agent_manager_get_nonexistent_agent(self):
        """Test getting a non-existent agent."""
        manager = AgentManager()
        agent = manager.get_agent("NonExistentAgent")

        assert agent is None

    def test_agent_manager_register_agent(self):
        """Test registering a new agent."""
        manager = AgentManager()
        custom_agent = ResearchAgent()

        # Register another research agent with a different name (not typical but testing functionality)
        manager.register_agent(custom_agent)

        retrieved = manager.get_agent("ResearchAgent")
        assert retrieved is not None

    def test_agent_manager_execute_task(self):
        """Test executing a task across all agents."""
        manager = AgentManager()
        task = ExplorationTask(
            id="test_task",
            concept="Test Concept",
            task_type="expansion",
            priority=10,
            status=ExplorationState.PENDING
        )

        responses = manager.execute_task(task)

        assert isinstance(responses, list)
        assert len(responses) == 6  # Should have response from each agent
        assert all(isinstance(r, AgentResponse) for r in responses)

    def test_agent_manager_all_responses_successful(self):
        """Test that all agent responses are successful."""
        manager = AgentManager()
        task = ExplorationTask(
            id="test_task",
            concept="Test Concept",
            task_type="expansion",
            priority=10,
            status=ExplorationState.PENDING
        )

        responses = manager.execute_task(task)

        assert all(r.success for r in responses)

    def test_agent_manager_responses_have_required_fields(self):
        """Test that all responses have required fields."""
        manager = AgentManager()
        task = ExplorationTask(
            id="test_task",
            concept="Test Concept",
            task_type="expansion",
            priority=10,
            status=ExplorationState.PENDING
        )

        responses = manager.execute_task(task)

        for response in responses:
            assert hasattr(response, "success")
            assert hasattr(response, "data")
            assert hasattr(response, "metadata")
            assert hasattr(response, "agent_name")
            assert hasattr(response, "confidence")

    def test_agent_manager_get_available_agents(self):
        """Test getting list of available agents."""
        manager = AgentManager()
        available = manager.get_available_agents()

        assert isinstance(available, list)
        assert len(available) == 6
        assert "ResearchAgent" in available
        assert "ValidationAgent" in available


class TestAgentResponseStructure:
    """Tests for AgentResponse structure and data integrity."""

    def test_agent_response_creation(self):
        """Test creating an AgentResponse."""
        response = AgentResponse(
            success=True,
            data={"test": "data"},
            metadata={"source": "test"},
            agent_name="TestAgent",
            confidence=0.95
        )

        assert response.success is True
        assert response.data == {"test": "data"}
        assert response.metadata == {"source": "test"}
        assert response.agent_name == "TestAgent"
        assert response.confidence == 0.95

    def test_agent_response_default_confidence(self):
        """Test AgentResponse with default confidence."""
        response = AgentResponse(
            success=True,
            data={"test": "data"},
            metadata={},
            agent_name="TestAgent"
        )

        assert response.confidence == 1.0
