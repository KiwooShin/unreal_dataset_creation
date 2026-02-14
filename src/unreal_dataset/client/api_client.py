"""
HTTP API client for communicating with the Unreal Engine server.

Provides a typed interface for all server endpoints.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from unreal_dataset.config import get_settings
from unreal_dataset.utils import get_logger
from unreal_dataset.utils.exceptions import (
    CaptureError,
    ConnectionError,
    SceneSetupError,
    ServerError,
    TimeoutError,
)

logger = get_logger(__name__)


@dataclass
class ObjectConfig:
    """Configuration for spawning an object."""
    type: str
    mesh: str
    position: List[float]
    rotation: List[float] = None
    scale: List[float] = None
    color: Optional[str] = None
    material: Optional[str] = None
    label: Optional[str] = None
    class_name: Optional[str] = None
    is_orientation_agnostic: bool = False

    def __post_init__(self):
        if self.rotation is None:
            self.rotation = [0, 0, 0]
        if self.scale is None:
            self.scale = [1, 1, 1]
        if self.label is None:
            self.label = self.type.capitalize()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        return {
            "type": self.type,
            "mesh": self.mesh,
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale,
            "color": self.color,
            "material": self.material,
            "label": self.label,
        }


@dataclass
class CameraConfig:
    """Camera configuration for capture."""
    position: List[float]
    look_at: List[float]
    fov: float = 90.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        return {
            "position": self.position,
            "look_at": self.look_at,
            "fov": self.fov,
        }


@dataclass
class OutputConfig:
    """Output configuration for capture."""
    filename: str
    resolution: List[int] = None

    def __post_init__(self):
        if self.resolution is None:
            self.resolution = [640, 640]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        return {
            "filename": self.filename,
            "resolution": self.resolution,
        }


@dataclass
class SceneObject:
    """Information about an object in the scene."""
    label: str
    class_name: str
    location_world: List[float]
    rotation_world: List[float]
    scale: List[float]
    dimensions: List[float]
    bounds_center: List[float]
    bounds_extent: List[float]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneObject":
        """Create from API response dictionary."""
        return cls(
            label=data["label"],
            class_name=data["class_name"],
            location_world=data["location_world"],
            rotation_world=data["rotation_world"],
            scale=data["scale"],
            dimensions=data["dimensions"],
            bounds_center=data["bounds_center"],
            bounds_extent=data["bounds_extent"],
        )


class UnrealAPIClient:
    """
    HTTP client for the Unreal Engine API server.

    Provides methods for all server endpoints with proper error handling.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize the API client.

        Args:
            base_url: Server URL (defaults to settings)
            timeout: Default request timeout in seconds
        """
        settings = get_settings()
        self.base_url = base_url or settings.api_url
        self.timeout = timeout
        self._session = requests.Session()

    def check_connection(self) -> bool:
        """
        Check if the server is running and accessible.

        Returns:
            True if connected, raises ConnectionError otherwise
        """
        try:
            response = self._session.get(
                f"{self.base_url}/status",
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Connected to API server at {self.base_url}")
                return True
            raise ConnectionError(
                self.base_url,
                f"Status code {response.status_code}"
            )
        except requests.exceptions.RequestException as e:
            raise ConnectionError(self.base_url, str(e))

    def get_status(self) -> Dict[str, Any]:
        """
        Get server status.

        Returns:
            Status dictionary with version, output_dir, active_actors
        """
        try:
            response = self._session.get(
                f"{self.base_url}/status",
                timeout=self.timeout
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(self.base_url, str(e))

    def setup_scene(
        self,
        objects: List[ObjectConfig],
        cleanup_before: bool = True,
    ) -> Dict[str, Any]:
        """
        Set up the scene with objects.

        Args:
            objects: List of object configurations to spawn
            cleanup_before: Whether to remove existing actors first

        Returns:
            Response dictionary with status and message
        """
        config = {
            "cleanup_before": cleanup_before,
            "objects": [obj.to_dict() for obj in objects],
        }

        try:
            response = self._session.post(
                f"{self.base_url}/setup_scene",
                json=config,
                timeout=self.timeout,
            )
            result = response.json()

            if result.get("status") != "success":
                raise SceneSetupError(
                    result.get("error", "Unknown error"),
                    details=result
                )

            logger.info(f"Scene setup: {result.get('message')}")
            return result

        except requests.exceptions.RequestException as e:
            raise SceneSetupError(f"Request failed: {e}")

    def capture(
        self,
        camera: CameraConfig,
        output: OutputConfig,
        position_only: bool = False,
        save_metadata: bool = False,
    ) -> Dict[str, Any]:
        """
        Capture a screenshot.

        Args:
            camera: Camera configuration
            output: Output configuration
            position_only: If True, only position camera without capturing
            save_metadata: Whether to save metadata alongside image

        Returns:
            Response dictionary with image_path and metadata_path
        """
        config = {
            "camera": camera.to_dict(),
            "output": output.to_dict(),
            "position_only": position_only,
            "save_metadata": save_metadata,
        }

        try:
            response = self._session.post(
                f"{self.base_url}/capture",
                json=config,
                timeout=120,  # Screenshots can take longer
            )
            result = response.json()

            if result.get("status") != "success":
                raise CaptureError(
                    result.get("error", "Unknown error"),
                    camera_config=camera.to_dict()
                )

            return result

        except requests.exceptions.Timeout:
            raise TimeoutError("Screenshot capture", 120)
        except requests.exceptions.RequestException as e:
            raise CaptureError(f"Request failed: {e}")

    def get_scene_objects(self) -> List[SceneObject]:
        """
        Get information about all objects in the scene.

        Returns:
            List of SceneObject with positions, dimensions, etc.
        """
        try:
            response = self._session.get(
                f"{self.base_url}/get_scene_objects",
                timeout=self.timeout,
            )
            result = response.json()

            if result.get("status") != "success":
                raise ServerError(
                    "/get_scene_objects",
                    response.status_code,
                    result
                )

            objects = [
                SceneObject.from_dict(obj)
                for obj in result.get("objects", [])
            ]
            logger.info(f"Found {len(objects)} objects in scene")
            return objects

        except requests.exceptions.RequestException as e:
            raise ConnectionError(self.base_url, str(e))

    def cleanup(self) -> None:
        """Remove all spawned actors from the scene."""
        try:
            response = self._session.post(
                f"{self.base_url}/cleanup",
                timeout=self.timeout,
            )
            result = response.json()

            if result.get("status") not in ("ok", "success"):
                raise ServerError("/cleanup", response.status_code, result)

            logger.info("Scene cleaned up")

        except requests.exceptions.RequestException as e:
            raise ConnectionError(self.base_url, str(e))

    def close(self) -> None:
        """Close the HTTP session."""
        self._session.close()

    def __enter__(self) -> "UnrealAPIClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()
