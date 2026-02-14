"""Label generation modules for 3D object detection."""

from unreal_dataset.labeling.class_definitions import (
    CLASS_DEFINITIONS,
    ClassInfo,
    get_class_info,
    register_class,
)
from unreal_dataset.labeling.generator import (
    generate_labels,
    load_labels,
    save_labels,
)
from unreal_dataset.labeling.transforms import (
    R_CONV,
    compute_intrinsics,
    compute_rotation_y,
    compute_world_to_camera_transform,
    project_point_to_image,
    transform_point_to_camera,
)

__all__ = [
    # Class definitions
    "CLASS_DEFINITIONS",
    "ClassInfo",
    "get_class_info",
    "register_class",
    # Generator
    "generate_labels",
    "load_labels",
    "save_labels",
    # Transforms
    "R_CONV",
    "compute_intrinsics",
    "compute_rotation_y",
    "compute_world_to_camera_transform",
    "project_point_to_image",
    "transform_point_to_camera",
]
