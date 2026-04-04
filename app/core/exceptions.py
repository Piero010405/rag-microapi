"""
Exceptions for the application, defining custom exceptions for various error scenarios.
"""
class ExternalServiceError(Exception):
    """Exception raised when an external service 
    (e.g., LLM provider, vector database) returns an error.
    """
    pass


class RetrievalError(Exception):
    """Exception raised when retrieval pipeline fails."""
    pass


class GenerationError(Exception):
    """Exception raised when generation pipeline fails."""
    pass


class ConfigurationError(Exception):
    """Exception raised when there is a configuration error."""
    pass
