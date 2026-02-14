"""
Label generation for 3D object detection datasets.

Generates JSON labels containing:
- Camera intrinsics and extrinsics
- Object locations in world and camera coordinates
- Object dimensions and orientations
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from unreal_dataset.labeling.class_definitions import get_class_info
from unreal_dataset.labeling.transforms import (
    compute_intrinsics,
    compute_rotation_y,
    compute_world_to_camera_transform,
    transform_point_to_camera,
)


def generate_labels(
    objects: List[Dict[str, Any]],
    camera_config: Dict[str, Any],
    output_config: Dict[str, Any],
    scene_name: str = "scene"
) -> Dict[str, Any]:
    """
    Generate complete 3D detection labels for a capture.

    Args:
        objects: List of object info dicts from /get_scene_objects API
        camera_config: Camera configuration with position, look_at, fov
        output_config: Output configuration with filename, resolution
        scene_name: Name of the scene

    Returns:
        Complete label dictionary with metadata, camera info, and object labels
    """
    # Extract camera parameters
    camera_position = camera_config.get("position", [0, 0, 0])
    look_at = camera_config.get("look_at", [0, 0, 0])
    fov = camera_config.get("fov", 90.0)
    resolution = output_config.get("resolution", [640, 640])
    width, height = resolution[0], resolution[1]
    filename = output_config.get("filename", "capture.png")

    # Compute camera matrices
    T_camera_world, R, t = compute_world_to_camera_transform(camera_position, look_at)
    K, fx, fy, cx, cy = compute_intrinsics(fov, width, height)

    # Generate object labels
    object_labels = []
    for obj in objects:
        class_name = obj.get("class_name", "unknown")
        class_info = get_class_info(class_name)

        # Transform location to camera coordinates
        location_world = obj.get("location_world", [0, 0, 0])
        location_camera = transform_point_to_camera(location_world, T_camera_world)

        # Get rotation in camera frame
        rotation_world = obj.get("rotation_world", [0, 0, 0])
        rotation_y = compute_rotation_y(
            rotation_world,
            R,
            class_info.orientation_agnostic
        )

        # Get dimensions
        dimensions = obj.get("dimensions", [100, 100, 100])

        label = {
            "instance_id": len(object_labels),
            "class_name": class_name,
            "class_id": class_info.id,
            "location_world": location_world,
            "location_camera": location_camera.tolist(),
            "dimensions": {
                "length": dimensions[0],  # X extent
                "width": dimensions[1],   # Y extent
                "height": dimensions[2]   # Z extent
            },
            "rotation_world": {
                "pitch": rotation_world[0],
                "yaw": rotation_world[1],
                "roll": rotation_world[2]
            },
            "rotation_y_camera": rotation_y,
            "is_orientation_agnostic": class_info.orientation_agnostic
        }

        object_labels.append(label)

    # Build complete label structure
    labels = {
        "metadata": {
            "scene_name": scene_name,
            "capture_name": filename.replace(".png", ""),
            "image_file": filename,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        },
        "camera": {
            "intrinsics": {
                "fx": float(fx),
                "fy": float(fy),
                "cx": float(cx),
                "cy": float(cy),
                "width": width,
                "height": height,
                "K": K.tolist()
            },
            "extrinsics": {
                "position_world": camera_position,
                "look_at_world": look_at,
                "rotation_matrix": R.tolist(),
                "translation": t.tolist(),
                "T_camera_world": T_camera_world.tolist()
            },
            "fov_degrees": fov
        },
        "objects": object_labels
    }

    return labels


def save_labels(labels: Dict[str, Any], output_dir: str | Path, filename: str) -> Path:
    """
    Save labels to a JSON file.

    Args:
        labels: Label dictionary
        output_dir: Output directory path
        filename: Output filename (should end with .json)

    Returns:
        Path to saved file
    """
    output_dir = Path(output_dir)
    labels_dir = output_dir / "labels"
    labels_dir.mkdir(parents=True, exist_ok=True)

    filepath = labels_dir / filename
    with open(filepath, "w") as f:
        json.dump(labels, f, indent=2)

    return filepath


def load_labels(filepath: str | Path) -> Dict[str, Any]:
    """
    Load labels from a JSON file.

    Args:
        filepath: Path to the label file

    Returns:
        Label dictionary
    """
    with open(filepath, "r") as f:
        return json.load(f)
