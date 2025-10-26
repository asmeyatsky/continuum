"""
Custom exceptions for the Continuum application.
"""


class ContinuumException(Exception):
    """Base exception for all Continuum errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ConfigurationError(ContinuumException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str):
        super().__init__(message, "CONFIGURATION_ERROR")


class LLMError(ContinuumException):
    """Raised when LLM operations fail."""

    def __init__(self, message: str, provider: str = "unknown"):
        self.provider = provider
        super().__init__(f"LLM Error ({provider}): {message}", "LLM_ERROR")


class EmbeddingError(ContinuumException):
    """Raised when embedding operations fail."""

    def __init__(self, message: str):
        super().__init__(message, "EMBEDDING_ERROR")


class GraphError(ContinuumException):
    """Raised when knowledge graph operations fail."""

    def __init__(self, message: str):
        super().__init__(message, "GRAPH_ERROR")


class DataPipelineError(ContinuumException):
    """Raised when data pipeline operations fail."""

    def __init__(self, message: str):
        super().__init__(message, "PIPELINE_ERROR")


class ValidationError(ContinuumException):
    """Raised when validation fails."""

    def __init__(self, message: str, field: str = "unknown"):
        self.field = field
        super().__init__(f"Validation Error ({field}): {message}", "VALIDATION_ERROR")


class NotFoundError(ContinuumException):
    """Raised when a resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            f"{resource_type} not found: {resource_id}",
            "NOT_FOUND"
        )


class ConflictError(ContinuumException):
    """Raised when there is a conflict."""

    def __init__(self, message: str):
        super().__init__(message, "CONFLICT")
