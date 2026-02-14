"""Client modules for communicating with the Unreal API server."""

from unreal_dataset.client.api_client import (
    CameraConfig,
    ObjectConfig,
    OutputConfig,
    SceneObject,
    UnrealAPIClient,
)
from unreal_dataset.client.capture import (
    CaptureResult,
    capture_multi_view,
    capture_with_labels,
)
from unreal_dataset.client.scene_setup import (
    load_scene_config,
    parse_objects,
    setup_scene,
)

__all__ = [
    # API Client
    "CameraConfig",
    "ObjectConfig",
    "OutputConfig",
    "SceneObject",
    "UnrealAPIClient",
    # Capture
    "CaptureResult",
    "capture_multi_view",
    "capture_with_labels",
    # Scene Setup
    "load_scene_config",
    "parse_objects",
    "setup_scene",
]
