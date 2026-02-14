"""
Screenshot capture with 3D detection labels.

Captures images from multiple camera positions and generates JSON labels.
"""

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from unreal_dataset.client.api_client import (
    CameraConfig,
    OutputConfig,
    SceneObject,
    UnrealAPIClient,
)
from unreal_dataset.config import get_settings
from unreal_dataset.labeling import generate_labels, save_labels
from unreal_dataset.utils import get_logger
from unreal_dataset.utils.exceptions import CaptureError, TimeoutError

logger = get_logger(__name__)


@dataclass
class CaptureResult:
    """Result of a single capture."""
    name: str
    success: bool
    image_path: Optional[Path] = None
    label_path: Optional[Path] = None
    error: Optional[str] = None


def wait_for_file(
    filepath: Path,
    timeout: int = 60,
    min_size: int = 10000,
) -> bool:
    """
    Wait for a file to exist and reach minimum size.

    Args:
        filepath: Path to the file
        timeout: Maximum wait time in seconds
        min_size: Minimum file size in bytes

    Returns:
        True if file exists and meets size requirement
    """
    start = time.time()
    while time.time() - start < timeout:
        if filepath.exists() and filepath.stat().st_size > min_size:
            return True
        time.sleep(1)
    return False


def capture_with_labels(
    client: UnrealAPIClient,
    camera: CameraConfig,
    output: OutputConfig,
    objects: List[SceneObject],
    scene_name: str,
    output_dir: Path,
) -> CaptureResult:
    """
    Capture a screenshot and generate 3D detection labels.

    Args:
        client: API client
        camera: Camera configuration
        output: Output configuration
        objects: List of scene objects
        scene_name: Name of the scene
        output_dir: Output directory for images and labels

    Returns:
        CaptureResult with paths to image and label files
    """
    capture_name = output.filename.replace(".png", "")

    try:
        # Request capture from server
        result = client.capture(camera, output, position_only=False)
        image_path = Path(result.get("image_path", ""))

        logger.info(f"Screenshot requested: {capture_name}")

        # Wait for file to be written
        settings = get_settings()
        if not wait_for_file(image_path, timeout=settings.capture.screenshot_timeout):
            raise TimeoutError(
                f"Waiting for screenshot {output.filename}",
                settings.capture.screenshot_timeout
            )

        size_kb = image_path.stat().st_size / 1024
        logger.info(f"Image saved: {size_kb:.1f} KB")

        # Generate labels
        objects_dict = [
            {
                "label": obj.label,
                "class_name": obj.class_name,
                "location_world": obj.location_world,
                "rotation_world": obj.rotation_world,
                "scale": obj.scale,
                "dimensions": obj.dimensions,
            }
            for obj in objects
        ]

        labels = generate_labels(
            objects=objects_dict,
            camera_config=camera.to_dict(),
            output_config=output.to_dict(),
            scene_name=scene_name,
        )

        # Save labels
        label_filename = output.filename.replace(".png", ".json")
        label_path = save_labels(labels, output_dir, label_filename)

        logger.info(f"Labels saved: {label_filename} ({len(labels['objects'])} objects)")

        return CaptureResult(
            name=capture_name,
            success=True,
            image_path=image_path,
            label_path=label_path,
        )

    except Exception as e:
        logger.error(f"Capture failed for {capture_name}: {e}")
        return CaptureResult(
            name=capture_name,
            success=False,
            error=str(e),
        )


def capture_multi_view(
    scene_name: str,
    scene_center: List[float],
    camera_positions: List[Dict[str, Any]],
    output_dir: Optional[Path] = None,
    client: Optional[UnrealAPIClient] = None,
) -> List[CaptureResult]:
    """
    Capture screenshots from multiple camera positions.

    Args:
        scene_name: Name of the scene
        scene_center: [X, Y, Z] center point to look at
        camera_positions: List of dicts with 'name' and 'position'
        output_dir: Output directory (uses settings if not provided)
        client: API client (creates one if not provided)

    Returns:
        List of CaptureResult for each camera position
    """
    settings = get_settings()
    output_dir = output_dir or settings.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get or create client
    own_client = client is None
    if own_client:
        client = UnrealAPIClient()

    try:
        # Check connection
        client.check_connection()

        # Get scene objects
        objects = client.get_scene_objects()
        logger.info(f"Found {len(objects)} objects in scene")

        # Capture from each position
        results = []
        for i, cam_config in enumerate(camera_positions):
            name = cam_config.get("name", f"capture_{i}")
            position = cam_config["position"]

            logger.info(f"Capturing {name} from {position}")

            camera = CameraConfig(
                position=position,
                look_at=scene_center,
                fov=settings.capture.fov,
            )
            output = OutputConfig(
                filename=f"{name}.png",
                resolution=list(settings.capture.resolution),
            )

            result = capture_with_labels(
                client=client,
                camera=camera,
                output=output,
                objects=objects,
                scene_name=scene_name,
                output_dir=output_dir,
            )
            results.append(result)

        return results

    finally:
        if own_client:
            client.close()


def main(
    scene_name: str = "house_with_materials",
    scene_center: Optional[List[float]] = None,
    camera_positions: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """
    Main entry point for capture.

    Args:
        scene_name: Name of the scene
        scene_center: Center point to look at
        camera_positions: Camera positions to capture from
    """
    # Default values
    if scene_center is None:
        scene_center = [50, 300, 100]

    if camera_positions is None:
        camera_positions = [
            {"name": "front", "position": [1500, 300, 400]},
            {"name": "top", "position": [50, 300, 2000]},
            {"name": "diagonal", "position": [1200, -400, 800]},
        ]

    settings = get_settings()

    print("=" * 70)
    print("Capture Screenshots with 3D Detection Labels")
    print("=" * 70)
    print(f"Scene: {scene_name}")
    print(f"Center: {scene_center}")
    print(f"Cameras: {len(camera_positions)}")
    print(f"Output: {settings.output_dir}")
    print()

    try:
        results = capture_multi_view(
            scene_name=scene_name,
            scene_center=scene_center,
            camera_positions=camera_positions,
        )

        # Print summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)

        success_count = sum(1 for r in results if r.success)
        print(f"Captured {success_count}/{len(results)} images\n")

        for r in results:
            status = "OK" if r.success else "FAILED"
            if r.success:
                print(f"  [{status}] {r.name}")
                print(f"         Image: {r.image_path}")
                print(f"         Label: {r.label_path}")
            else:
                print(f"  [{status}] {r.name}: {r.error}")

        print("=" * 70)

    except Exception as e:
        print(f"\nERROR: {e}")
        raise


if __name__ == "__main__":
    main()
