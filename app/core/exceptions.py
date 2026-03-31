class ExternalServiceError(Exception):
    """Raised when an external provider fails."""


class RetrievalError(Exception):
    """Raised when retrieval pipeline fails."""


class GenerationError(Exception):
    """Raised when generation pipeline fails."""
