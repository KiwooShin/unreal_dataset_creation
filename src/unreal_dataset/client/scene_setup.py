"""
Scene setup functionality.

Loads scene configurations and sets up the Unreal scene.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from unreal_dataset.client.api_client import (
    CameraConfig,
    ObjectConfig,
    OutputConfig,
    UnrealAPIClient,
)
from unreal_dataset.config import get_settings
from unreal_dataset.utils import get_logger
from unreal_dataset.utils.exceptions import SceneSetupError

logger = get_logger(__name__)


def load_scene_config(config_path: str | Path) -> Dict[str, Any]:
    """
    Load scene configuration from a JSON file.

    Args:
        config_path: Path to the scene configuration file

    Returns:
        Scene configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Scene config not found: {config_path}")

    with open(config_path, "r") as f:
        return json.load(f)


def parse_objects(objects_data: List[Dict[str, Any]]) -> List[ObjectConfig]:
    """
    Parse object configurations from scene data.

    Args:
        objects_data: List of object dictionaries from scene config

    Returns:
        List of ObjectConfig instances
    """
    objects = []
    for obj in objects_data:
        config = ObjectConfig(
            type=obj["type"],
            mesh=obj["mesh"],
            position=obj["position"],
            rotation=obj.get("rotation"),
            scale=obj.get("scale"),
            color=obj.get("color"),
            material=obj.get("material"),
            label=obj.get("label"),
            class_name=obj.get("class_name"),
            is_orientation_agnostic=obj.get("is_orientation_agnostic", False),
        )
        objects.append(config)
    return objects


def setup_scene(
    config_path: str | Path,
    client: Optional[UnrealAPIClient] = None,
    position_camera: bool = True,
) -> Dict[str, Any]:
    """
    Set up the scene from a configuration file.

    Args:
        config_path: Path to the scene configuration JSON
        client: Optional API client (creates one if not provided)
        position_camera: Whether to position the camera after setup

    Returns:
        Dictionary with scene info including name and object count
    """
    # Load configuration
    config = load_scene_config(config_path)
    scene_name = config.get("name", "unknown")
    logger.info(f"Loading scene: {scene_name}")

    # Parse objects
    objects = parse_objects(config.get("objects", []))
    logger.info(f"Scene has {len(objects)} objects")

    # Get or create client
    own_client = client is None
    if own_client:
        client = UnrealAPIClient()

    try:
        # Check connection
        client.check_connection()

        # Setup scene
        result = client.setup_scene(objects, cleanup_before=True)

        # Position camera if requested
        if position_camera and "camera" in config:
            camera_data = config["camera"]
            camera = CameraConfig(
                position=camera_data.get("position", [500, 0, 300]),
                look_at=camera_data.get("target", [0, 0, 100]),
                fov=camera_data.get("fov", 90.0),
            )
            output = OutputConfig(filename="temp.png")

            client.capture(camera, output, position_only=True)
            logger.info(f"Camera positioned at {camera.position}")

        return {
            "scene_name": scene_name,
            "object_count": len(objects),
            "objects": objects,
            "camera": config.get("camera"),
            "result": result,
        }

    finally:
        if own_client:
            client.close()


def main(config_path: Optional[str] = None) -> None:
    """
    Main entry point for scene setup.

    Args:
        config_path: Path to scene config (uses default if not provided)
    """
    settings = get_settings()

    if config_path is None:
        config_path = settings.assets_dir / "house_with_materials.json"

    print("=" * 60)
    print("Setting up scene")
    print("=" * 60)

    try:
        result = setup_scene(config_path)

        print(f"\nScene: {result['scene_name']}")
        print(f"Objects spawned: {result['object_count']}")

        if result.get("camera"):
            print(f"Camera position: {result['camera'].get('position')}")
            print(f"Camera target: {result['camera'].get('target')}")

        print("\n" + "=" * 60)
        print("Check the Unreal viewport to verify the scene!")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR: {e}")
        raise


if __name__ == "__main__":
    main()
