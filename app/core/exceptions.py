"""
Exceptions for the application, defining custom exceptions for various error scenarios.
"""
class AppBaseError(Exception):
    """
    A base exception class for the application, providing a structure for error messages,
    error codes, and HTTP status codes.
    """
    def __init__(self, message: str, error_code: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code


class ExternalServiceError(AppBaseError):
    """
    Exception raised when an external service (e.g., language model API, vector database)
    returns an error or is unreachable."""
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            error_code="external_service_error",
            status_code=502,
        )


class RetrievalError(AppBaseError):
    """
    Exception raised when there is an error during the retrieval process, such as issues
    with the vector database or embedding generation.
    """
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            error_code="retrieval_error",
            status_code=500,
        )


class GenerationError(AppBaseError):
    """
    GenerationError is raised when there is an error during the answer generation process, 
    such as issues with the language model API or response generation.
    """
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            error_code="generation_error",
            status_code=500,
        )


class ConfigurationError(AppBaseError):
    """
    ConfigurationError is raised when there is an error in the application's configuration,
    such as missing or invalid environment variables or settings.
    """
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            error_code="configuration_error",
            status_code=500,
        )
