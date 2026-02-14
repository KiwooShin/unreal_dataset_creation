"""Custom exceptions for Unreal Dataset."""


class UnrealDatasetError(Exception):
    """Base exception for all Unreal Dataset errors."""

    pass


class ConnectionError(UnrealDatasetError):
    """Failed to connect to the Unreal API server."""

    def __init__(self, url: str, message: str = ""):
        self.url = url
        super().__init__(f"Failed to connect to {url}. {message}".strip())


class SceneSetupError(UnrealDatasetError):
    """Error during scene setup."""

    def __init__(self, message: str, details: dict | None = None):
        self.details = details or {}
        super().__init__(message)


class CaptureError(UnrealDatasetError):
    """Error during screenshot capture."""

    def __init__(self, message: str, camera_config: dict | None = None):
        self.camera_config = camera_config or {}
        super().__init__(message)


class LabelGenerationError(UnrealDatasetError):
    """Error during label generation."""

    def __init__(self, message: str, object_info: dict | None = None):
        self.object_info = object_info or {}
        super().__init__(message)


class ServerError(UnrealDatasetError):
    """Error from the Unreal API server."""

    def __init__(self, endpoint: str, status_code: int | None = None, response: dict | None = None):
        self.endpoint = endpoint
        self.status_code = status_code
        self.response = response or {}
        message = f"Server error at {endpoint}"
        if status_code:
            message += f" (status {status_code})"
        if response and "error" in response:
            message += f": {response['error']}"
        super().__init__(message)


class TimeoutError(UnrealDatasetError):
    """Operation timed out."""

    def __init__(self, operation: str, timeout_seconds: float):
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        super().__init__(f"{operation} timed out after {timeout_seconds} seconds")
