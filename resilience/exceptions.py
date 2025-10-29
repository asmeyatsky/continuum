"""
Custom exceptions for the Continuum application.

Comprehensive exception hierarchy for domain-specific error handling,
detailed logging, and structured API error responses.
"""

from typing import Dict, Optional, Any


class ContinuumException(Exception):
    """
    Base exception for all Continuum errors.

    Provides structured error information with error codes, detailed
    context, and standardized error serialization.
    """

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
        http_status_code: int = 500
    ):
        """
        Initialize exception.

        Args:
            message: Human-readable error message
            code: Machine-readable error code
            details: Additional context/details about the error
            http_status_code: Appropriate HTTP status code for API responses
        """
        self.message = message
        self.code = code
        self.details = details or {}
        self.http_status_code = http_status_code
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API/logging."""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
            "status_code": self.http_status_code
        }

    def __str__(self) -> str:
        """String representation of exception."""
        if self.details:
            return f"{self.code}: {self.message} ({self.details})"
        return f"{self.code}: {self.message}"


# ============================================================================
# Orchestration Errors
# ============================================================================

class OrchestrationError(ContinuumException):
    """Base error for orchestration-related failures."""
    def __init__(self, message: str, code: str = "ORCHESTRATION_ERROR", **kwargs):
        super().__init__(message, code, **kwargs)


class ExplorationNotFoundError(OrchestrationError):
    """Raised when an exploration ID doesn't exist."""

    def __init__(self, exploration_id: str):
        super().__init__(
            message=f"Exploration '{exploration_id}' not found",
            code="EXPLORATION_NOT_FOUND",
            details={"exploration_id": exploration_id},
            http_status_code=404
        )


class InvalidExplorationStateError(OrchestrationError):
    """Raised when an operation is invalid for the current state."""

    def __init__(self, exploration_id: str, current_state: str, operation: str):
        super().__init__(
            message=f"Cannot {operation} exploration in {current_state} state",
            code="INVALID_EXPLORATION_STATE",
            details={
                "exploration_id": exploration_id,
                "current_state": current_state,
                "operation": operation
            },
            http_status_code=409
        )


class TaskExecutionError(OrchestrationError):
    """Raised when a task fails to execute."""

    def __init__(self, task_id: str, reason: str):
        super().__init__(
            message=f"Task '{task_id}' failed: {reason}",
            code="TASK_EXECUTION_FAILED",
            details={"task_id": task_id, "reason": reason},
            http_status_code=500
        )


# ============================================================================
# Knowledge Graph Errors
# ============================================================================

class GraphError(ContinuumException):
    """Base error for knowledge graph operations."""
    def __init__(self, message: str, code: str = "GRAPH_ERROR", **kwargs):
        super().__init__(message, code, **kwargs)


class NodeNotFoundError(GraphError):
    """Raised when a node doesn't exist."""

    def __init__(self, node_id: str):
        super().__init__(
            message=f"Node '{node_id}' not found",
            code="NODE_NOT_FOUND",
            details={"node_id": node_id},
            http_status_code=404
        )


class DuplicateNodeError(GraphError):
    """Raised when attempting to add a duplicate node."""

    def __init__(self, node_id: str):
        super().__init__(
            message=f"Node '{node_id}' already exists",
            code="DUPLICATE_NODE",
            details={"node_id": node_id},
            http_status_code=409
        )


class InvalidNodeError(GraphError):
    """Raised when a node is malformed."""

    def __init__(self, node_id: str, reason: str):
        super().__init__(
            message=f"Invalid node '{node_id}': {reason}",
            code="INVALID_NODE",
            details={"node_id": node_id, "reason": reason},
            http_status_code=400
        )


# ============================================================================
# Agent Errors
# ============================================================================

class AgentError(ContinuumException):
    """Base error for agent-related failures."""
    def __init__(self, message: str, code: str = "AGENT_ERROR", **kwargs):
        super().__init__(message, code, **kwargs)


class AgentNotFoundError(AgentError):
    """Raised when an agent doesn't exist."""

    def __init__(self, agent_name: str):
        super().__init__(
            message=f"Agent '{agent_name}' not found",
            code="AGENT_NOT_FOUND",
            details={"agent_name": agent_name},
            http_status_code=404
        )


class AgentExecutionError(AgentError):
    """Raised when an agent fails to execute."""

    def __init__(self, agent_name: str, task_id: str, reason: str):
        super().__init__(
            message=f"Agent '{agent_name}' failed: {reason}",
            code="AGENT_EXECUTION_FAILED",
            details={
                "agent_name": agent_name,
                "task_id": task_id,
                "reason": reason
            },
            http_status_code=500
        )


# ============================================================================
# Validation Errors
# ============================================================================

class ValidationError(ContinuumException):
    """Raised when validation fails."""

    def __init__(self, message: str, field: str = "unknown"):
        self.field = field
        super().__init__(
            f"Validation Error ({field}): {message}",
            code="VALIDATION_ERROR",
            details={"field": field},
            http_status_code=400
        )


class ConfigurationError(ContinuumException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str):
        super().__init__(
            message,
            code="CONFIGURATION_ERROR",
            http_status_code=500
        )


# ============================================================================
# Content Generation Errors
# ============================================================================

class ContentGenerationError(ContinuumException):
    """Base error for content generation failures."""
    def __init__(self, message: str, code: str = "CONTENT_GENERATION_ERROR", **kwargs):
        super().__init__(message, code, **kwargs)


class ContentQualityError(ContentGenerationError):
    """Raised when content fails quality checks."""

    def __init__(self, reason: str, quality_score: Optional[float] = None):
        super().__init__(
            message=f"Content quality validation failed: {reason}",
            code="CONTENT_QUALITY_FAILED",
            details={
                "reason": reason,
                "quality_score": quality_score
            },
            http_status_code=422
        )


# ============================================================================
# LLM/Embedding Errors
# ============================================================================

class LLMError(ContinuumException):
    """Raised when LLM operations fail."""

    def __init__(self, message: str, provider: str = "unknown"):
        self.provider = provider
        super().__init__(
            f"LLM Error ({provider}): {message}",
            code="LLM_ERROR",
            details={"provider": provider},
            http_status_code=500
        )


class EmbeddingError(ContinuumException):
    """Raised when embedding operations fail."""

    def __init__(self, message: str):
        super().__init__(
            message,
            code="EMBEDDING_ERROR",
            http_status_code=500
        )


class TokenLimitError(LLMError):
    """Raised when token limit is exceeded."""

    def __init__(self, provider: str, tokens_used: int, limit: int):
        super().__init__(
            message=f"Token limit exceeded: {tokens_used}/{limit}",
            provider=provider
        )
        self.code = "TOKEN_LIMIT_EXCEEDED"
        self.details = {"tokens_used": tokens_used, "token_limit": limit}
        self.http_status_code = 429


# ============================================================================
# Data Pipeline Errors
# ============================================================================

class DataPipelineError(ContinuumException):
    """Raised when data pipeline operations fail."""

    def __init__(self, message: str):
        super().__init__(
            message,
            code="PIPELINE_ERROR",
            http_status_code=500
        )


# ============================================================================
# Persistence/Database Errors
# ============================================================================

class PersistenceError(ContinuumException):
    """Base error for persistence-related failures."""
    def __init__(self, message: str, code: str = "PERSISTENCE_ERROR", **kwargs):
        super().__init__(message, code, **kwargs)


class DatabaseError(PersistenceError):
    """Raised when a database operation fails."""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Database {operation} failed: {reason}",
            code="DATABASE_ERROR",
            details={"operation": operation, "reason": reason},
            http_status_code=500
        )


class MigrationError(PersistenceError):
    """Raised when a database migration fails."""

    def __init__(self, migration_name: str, reason: str):
        super().__init__(
            message=f"Migration '{migration_name}' failed: {reason}",
            code="MIGRATION_FAILED",
            details={"migration_name": migration_name, "reason": reason},
            http_status_code=500
        )


# ============================================================================
# Resilience Errors
# ============================================================================

class CircuitBreakerOpenError(ContinuumException):
    """Raised when a circuit breaker is open."""

    def __init__(self, component: str):
        super().__init__(
            message=f"Circuit breaker open for {component}. Service temporarily unavailable.",
            code="CIRCUIT_BREAKER_OPEN",
            details={"component": component},
            http_status_code=503
        )


class RetryExhaustedError(ContinuumException):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, operation: str, attempts: int, last_error: str):
        super().__init__(
            message=f"Operation '{operation}' failed after {attempts} attempts",
            code="RETRY_EXHAUSTED",
            details={
                "operation": operation,
                "attempts": attempts,
                "last_error": last_error
            },
            http_status_code=500
        )


# Backward compatibility aliases
class NotFoundError(ExplorationNotFoundError):
    """Deprecated: Use ExplorationNotFoundError instead."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(resource_id)
        self.message = f"{resource_type} not found: {resource_id}"
        self.code = "NOT_FOUND"


class ConflictError(ContinuumException):
    """Raised when there is a conflict."""

    def __init__(self, message: str):
        super().__init__(
            message,
            code="CONFLICT",
            http_status_code=409
        )
