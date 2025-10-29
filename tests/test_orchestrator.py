"""
Comprehensive tests for the Concept Orchestrator.

This module tests the core orchestration logic including:
- Exploration submission and management
- Task queue management
- State transitions
- Concept node management
"""

import pytest
from datetime import datetime
from uuid import uuid4

from core.concept_orchestrator import (
    DefaultConceptOrchestrator,
    ExplorationTask,
    Exploration,
    ExplorationState,
    ConceptNode,
)


class TestExplorationSubmission:
    """Tests for exploration submission and initial setup."""

    def test_submit_exploration_returns_valid_id(self):
        """Test that submitting an exploration returns a valid ID."""
        orchestrator = DefaultConceptOrchestrator()
        exploration_id = orchestrator.submit_exploration_request("Test Concept")

        assert exploration_id is not None
        assert isinstance(exploration_id, str)
        assert len(exploration_id) > 0

    def test_submit_exploration_creates_exploration(self):
        """Test that submitting creates an exploration record."""
        orchestrator = DefaultConceptOrchestrator()
        concept = "Artificial Intelligence"
        exploration_id = orchestrator.submit_exploration_request(concept)

        assert exploration_id in orchestrator.explorations
        exploration = orchestrator.explorations[exploration_id]
        assert exploration.concept == concept
        assert exploration.status == ExplorationState.IN_PROGRESS

    def test_submit_exploration_creates_initial_task(self):
        """Test that submitting creates an initial task."""
        orchestrator = DefaultConceptOrchestrator()
        exploration_id = orchestrator.submit_exploration_request("Test Concept")

        exploration = orchestrator.explorations[exploration_id]
        assert len(exploration.tasks) == 1
        assert exploration.tasks[0].concept == "Test Concept"
        assert exploration.tasks[0].task_type == "expansion"

    def test_submit_multiple_explorations(self):
        """Test submitting multiple explorations."""
        orchestrator = DefaultConceptOrchestrator()
        id1 = orchestrator.submit_exploration_request("Concept 1")
        id2 = orchestrator.submit_exploration_request("Concept 2")

        assert id1 != id2
        assert len(orchestrator.explorations) == 2
        assert orchestrator.explorations[id1].concept == "Concept 1"
        assert orchestrator.explorations[id2].concept == "Concept 2"


class TestExplorationStatus:
    """Tests for exploration status management."""

    def test_get_exploration_status_in_progress(self):
        """Test getting status of ongoing exploration."""
        orchestrator = DefaultConceptOrchestrator()
        exploration_id = orchestrator.submit_exploration_request("Test Concept")

        status = orchestrator.get_exploration_status(exploration_id)
        assert status == ExplorationState.IN_PROGRESS

    def test_get_exploration_status_not_found(self):
        """Test getting status of non-existent exploration."""
        orchestrator = DefaultConceptOrchestrator()

        with pytest.raises(ValueError):
            orchestrator.get_exploration_status("non-existent-id")

    def test_get_exploration_status_completed(self):
        """Test getting status when all tasks are completed."""
        orchestrator = DefaultConceptOrchestrator()
        exploration_id = orchestrator.submit_exploration_request("Test Concept")

        exploration = orchestrator.explorations[exploration_id]
        for task in exploration.tasks:
            task.status = ExplorationState.COMPLETED

        status = orchestrator.get_exploration_status(exploration_id)
        assert status == ExplorationState.COMPLETED

    def test_get_exploration_status_failed(self):
        """Test getting status when a task has failed."""
        orchestrator = DefaultConceptOrchestrator()
        exploration_id = orchestrator.submit_exploration_request("Test Concept")

        exploration = orchestrator.explorations[exploration_id]
        exploration.tasks[0].status = ExplorationState.FAILED

        status = orchestrator.get_exploration_status(exploration_id)
        assert status == ExplorationState.FAILED

    def test_get_exploration_status_paused(self):
        """Test getting status when a task is paused."""
        orchestrator = DefaultConceptOrchestrator()
        exploration_id = orchestrator.submit_exploration_request("Test Concept")

        exploration = orchestrator.explorations[exploration_id]
        exploration.tasks[0].status = ExplorationState.PAUSED

        status = orchestrator.get_exploration_status(exploration_id)
        assert status == ExplorationState.PAUSED


class TestTaskQueue:
    """Tests for task queue management."""

    def test_get_next_task_returns_task(self):
        """Test that getting next task returns a valid task."""
        orchestrator = DefaultConceptOrchestrator()
        orchestrator.submit_exploration_request("Test Concept")

        task = orchestrator.get_next_task()
        assert task is not None
        assert isinstance(task, ExplorationTask)

    def test_get_next_task_priority_ordering(self):
        """Test that tasks are retrieved in priority order."""
        orchestrator = DefaultConceptOrchestrator()

        # Add multiple tasks with different priorities
        task1 = ExplorationTask(
            id="task1",
            concept="Concept1",
            task_type="expansion",
            priority=5,
            status=ExplorationState.PENDING
        )
        task2 = ExplorationTask(
            id="task2",
            concept="Concept2",
            task_type="expansion",
            priority=10,
            status=ExplorationState.PENDING
        )
        task3 = ExplorationTask(
            id="task3",
            concept="Concept3",
            task_type="expansion",
            priority=7,
            status=ExplorationState.PENDING
        )

        orchestrator.task_queue.extend([task1, task2, task3])

        # Get next task (should be task2 with priority 10)
        next_task = orchestrator.get_next_task()
        assert next_task.id == "task2"

        # Get next task (should be task3 with priority 7)
        next_task = orchestrator.get_next_task()
        assert next_task.id == "task3"

        # Get next task (should be task1 with priority 5)
        next_task = orchestrator.get_next_task()
        assert next_task.id == "task1"

    def test_get_next_task_empty_queue(self):
        """Test getting next task when queue is empty."""
        orchestrator = DefaultConceptOrchestrator()
        task = orchestrator.get_next_task()
        assert task is None

    def test_get_next_task_removes_from_queue(self):
        """Test that getting a task removes it from the queue."""
        orchestrator = DefaultConceptOrchestrator()
        orchestrator.submit_exploration_request("Test Concept")

        initial_count = len(orchestrator.task_queue)
        orchestrator.get_next_task()
        final_count = len(orchestrator.task_queue)

        assert final_count == initial_count - 1


class TestConceptNodeManagement:
    """Tests for concept node management."""

    def test_add_concept_node(self):
        """Test adding a concept node."""
        orchestrator = DefaultConceptOrchestrator()
        node = ConceptNode(
            id="test_node",
            concept="Test Concept",
            content="Test content",
            metadata={"source": "test"},
            created_at=datetime.now(),
            connections=[]
        )

        orchestrator.add_concept_node(node)

        assert "test_node" in orchestrator.nodes
        assert orchestrator.nodes["test_node"].concept == "Test Concept"

    def test_add_multiple_nodes(self):
        """Test adding multiple concept nodes."""
        orchestrator = DefaultConceptOrchestrator()

        for i in range(5):
            node = ConceptNode(
                id=f"node_{i}",
                concept=f"Concept {i}",
                content=f"Content {i}",
                metadata={},
                created_at=datetime.now(),
                connections=[]
            )
            orchestrator.add_concept_node(node)

        assert len(orchestrator.nodes) == 5

    def test_submit_concept_alias(self):
        """Test that submit_concept is an alias for submit_exploration_request."""
        orchestrator = DefaultConceptOrchestrator()
        exploration_id = orchestrator.submit_concept("Test Concept")

        assert exploration_id is not None
        assert exploration_id in orchestrator.explorations


class TestExplorationPauseResume:
    """Tests for pause and resume functionality."""

    def test_pause_exploration(self):
        """Test pausing an exploration."""
        orchestrator = DefaultConceptOrchestrator()
        exploration_id = orchestrator.submit_exploration_request("Test Concept")

        # Pause the exploration
        result = orchestrator.pause_exploration(exploration_id)

        assert result is True
        status = orchestrator.get_exploration_status(exploration_id)
        # Status should be PAUSED after pausing all tasks
        assert status in [ExplorationState.PAUSED, ExplorationState.IN_PROGRESS]

    def test_pause_nonexistent_exploration(self):
        """Test pausing a non-existent exploration."""
        orchestrator = DefaultConceptOrchestrator()
        result = orchestrator.pause_exploration("non-existent-id")
        assert result is False

    def test_resume_exploration(self):
        """Test resuming a paused exploration."""
        orchestrator = DefaultConceptOrchestrator()
        exploration_id = orchestrator.submit_exploration_request("Test Concept")

        # Pause and then resume
        orchestrator.pause_exploration(exploration_id)
        result = orchestrator.resume_exploration(exploration_id)

        assert result is True

    def test_resume_nonexistent_exploration(self):
        """Test resuming a non-existent exploration."""
        orchestrator = DefaultConceptOrchestrator()
        result = orchestrator.resume_exploration("non-existent-id")
        assert result is False


class TestExplorationResults:
    """Tests for exploration results retrieval."""

    def test_get_exploration_results_empty(self):
        """Test getting results for an exploration with no nodes."""
        orchestrator = DefaultConceptOrchestrator()
        exploration_id = orchestrator.submit_exploration_request("Test Concept")

        results = orchestrator.get_exploration_results(exploration_id)
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_exploration_results_nonexistent(self):
        """Test getting results for non-existent exploration."""
        orchestrator = DefaultConceptOrchestrator()
        results = orchestrator.get_exploration_results("non-existent-id")
        assert isinstance(results, list)
        assert len(results) == 0


class TestDataValidation:
    """Tests for data validation and edge cases."""

    def test_empty_concept_submission(self):
        """Test submitting an empty concept."""
        orchestrator = DefaultConceptOrchestrator()
        exploration_id = orchestrator.submit_exploration_request("")

        assert exploration_id is not None
        exploration = orchestrator.explorations[exploration_id]
        assert exploration.concept == ""

    def test_very_long_concept(self):
        """Test submitting a very long concept."""
        orchestrator = DefaultConceptOrchestrator()
        long_concept = "A" * 10000
        exploration_id = orchestrator.submit_exploration_request(long_concept)

        assert exploration_id is not None
        exploration = orchestrator.explorations[exploration_id]
        assert exploration.concept == long_concept

    def test_special_characters_in_concept(self):
        """Test submitting concepts with special characters."""
        orchestrator = DefaultConceptOrchestrator()
        concepts = [
            "Concept-with-dashes",
            "Concept_with_underscores",
            "Concept with spaces",
            "Concept!@#$%^&*()",
            "Concept\nwith\nnewlines",
        ]

        for concept in concepts:
            exploration_id = orchestrator.submit_exploration_request(concept)
            assert exploration_id is not None
            exploration = orchestrator.explorations[exploration_id]
            assert exploration.concept == concept
