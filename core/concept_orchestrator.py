"""
Concept Orchestrator - The Brain of the Infinite Concept Expansion Engine

This component serves as the central coordination hub managing the exploration strategy,
task decomposition, resource allocation, and context management for the multi-agent system.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum
import uuid
from datetime import datetime


class ExplorationState(Enum):
    """State of an exploration task"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class Exploration:
    """Represents an exploration with concept and status"""
    id: str
    concept: str
    status: ExplorationState
    created_at: datetime = None
    tasks: List['ExplorationTask'] = None  # List of tasks within this exploration
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.tasks is None:
            self.tasks = []


@dataclass
class ConceptNode:
    """Represents a concept node in the knowledge graph"""
    id: str
    concept: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    connections: List[str]  # List of connected node IDs
    content_type: str = "text"  # text, image, audio, video, etc.


@dataclass
class ExplorationTask:
    """Represents a task for the multi-agent system"""
    id: str
    concept: str
    task_type: str
    priority: int
    status: ExplorationState
    assigned_agent: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class ConceptOrchestrator(ABC):
    """Abstract base class for the concept orchestrator"""
    
    @abstractmethod
    def submit_exploration_request(self, initial_concept: str) -> str:
        """Submit a new exploration request and return exploration ID"""
        pass
    
    @abstractmethod
    def get_exploration_status(self, exploration_id: str) -> ExplorationState:
        """Get the current status of an exploration"""
        pass
    
    @abstractmethod
    def pause_exploration(self, exploration_id: str) -> bool:
        """Pause an ongoing exploration"""
        pass
    
    @abstractmethod
    def resume_exploration(self, exploration_id: str) -> bool:
        """Resume a paused exploration"""
        pass
    
    @abstractmethod
    def get_exploration_results(self, exploration_id: str) -> List[ConceptNode]:
        """Get all results from an exploration"""
        pass


class DefaultConceptOrchestrator(ConceptOrchestrator):
    """Default implementation of the concept orchestrator"""
    
    def __init__(self, knowledge_graph=None):
        self.explorations: Dict[str, List[ExplorationTask]] = {}
        self.nodes: Dict[str, ConceptNode] = {}
        self.task_queue: List[ExplorationTask] = []
        # Add knowledge_graph attribute as expected by the API
        from knowledge_graph.engine import InMemoryKnowledgeGraphEngine
        self.knowledge_graph = knowledge_graph or InMemoryKnowledgeGraphEngine()
        # Add orchestrator attribute for compatibility
        self.orchestrator = self
    
    def submit_exploration_request(self, initial_concept: str) -> str:
        """Submit a new exploration request and return exploration ID"""
        exploration_id = str(uuid.uuid4())
        # Create the initial task to explore the concept
        initial_task = ExplorationTask(
            id=str(uuid.uuid4()),
            concept=initial_concept,
            task_type="expansion",
            priority=10,
            status=ExplorationState.PENDING
        )
        
        # Create an exploration object with the initial concept
        exploration = Exploration(
            id=exploration_id,
            concept=initial_concept,
            status=ExplorationState.IN_PROGRESS,
            tasks=[initial_task]
        )
        
        self.explorations[exploration_id] = exploration
        self.task_queue.append(initial_task)
        
        return exploration_id
    
    def submit_concept(self, initial_concept: str) -> str:
        """Submit a concept for expansion - API compatibility method"""
        return self.submit_exploration_request(initial_concept)
    
    def get_exploration_status(self, exploration_id: str) -> ExplorationState:
        """Get the current status of an exploration"""
        if exploration_id not in self.explorations:
            raise ValueError(f"Exploration {exploration_id} not found")
        
        exploration = self.explorations[exploration_id]
        # Update status based on tasks
        tasks = exploration.tasks
        if all(task.status == ExplorationState.COMPLETED for task in tasks):
            exploration.status = ExplorationState.COMPLETED
        elif any(task.status == ExplorationState.FAILED for task in tasks):
            exploration.status = ExplorationState.FAILED
        elif any(task.status == ExplorationState.PAUSED for task in tasks):
            exploration.status = ExplorationState.PAUSED
        else:
            exploration.status = ExplorationState.IN_PROGRESS
        
        return exploration.status
    
    def __init__(self, knowledge_graph=None):
        self.explorations: Dict[str, Exploration] = {}
        self.nodes: Dict[str, ConceptNode] = {}
        self.task_queue: List[ExplorationTask] = []
        # Add knowledge_graph attribute as expected by the API
        from knowledge_graph.engine import InMemoryKnowledgeGraphEngine
        self.knowledge_graph = knowledge_graph or InMemoryKnowledgeGraphEngine()
        # Add orchestrator attribute for compatibility
        self.orchestrator = self
    
    def pause_exploration(self, exploration_id: str) -> bool:
        """Pause an ongoing exploration"""
        if exploration_id not in self.explorations:
            return False
        
        for task in self.explorations[exploration_id]:
            if task.status == ExplorationState.IN_PROGRESS:
                task.status = ExplorationState.PAUSED
        
        return True
    
    def resume_exploration(self, exploration_id: str) -> bool:
        """Resume a paused exploration"""
        if exploration_id not in self.explorations:
            return False
        
        for task in self.explorations[exploration_id]:
            if task.status == ExplorationState.PAUSED:
                task.status = ExplorationState.PENDING
                self.task_queue.append(task)
        
        return True
    
    def get_exploration_results(self, exploration_id: str) -> List[ConceptNode]:
        """Get all results from an exploration"""
        if exploration_id not in self.explorations:
            return []
        
        # Get all concept nodes created during this exploration
        result_nodes = []
        for task in self.explorations[exploration_id]:
            # This would be populated by agent results in a real system
            pass
        
        return result_nodes
    
    def get_next_task(self) -> Optional[ExplorationTask]:
        """Get the next task from the queue based on priority"""
        if not self.task_queue:
            return None
        
        # Sort by priority (higher priority first)
        self.task_queue.sort(key=lambda x: x.priority, reverse=True)
        return self.task_queue.pop(0)
    
    def add_concept_node(self, node: ConceptNode):
        """Add a concept node to the knowledge graph"""
        self.nodes[node.id] = node