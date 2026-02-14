"""
Coordinate transformations between Unreal Engine and camera coordinates.

Coordinate Systems:
- Unreal World: Left-handed, X-forward, Y-right, Z-up (units: cm)
- Camera: Right-handed, X-right, Y-down, Z-forward (units: cm)
"""

from typing import List, Tuple

import numpy as np


# Coordinate conversion matrix: Unreal -> Camera
# Unreal (X-forward, Y-right, Z-up) -> Camera (X-right, Y-down, Z-forward)
R_CONV = np.array([
    [0, 1, 0],    # Camera X = Unreal Y (right)
    [0, 0, -1],   # Camera Y = -Unreal Z (down)
    [1, 0, 0]     # Camera Z = Unreal X (forward)
])


def compute_intrinsics(
    fov_degrees: float,
    width: int,
    height: int
) -> Tuple[np.ndarray, float, float, float, float]:
    """
    Compute camera intrinsic matrix from FOV and resolution.

    Args:
        fov_degrees: Horizontal field of view in degrees
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Tuple of:
        - K: 3x3 intrinsic matrix
        - fx: Focal length x (pixels)
        - fy: Focal length y (pixels)
        - cx: Principal point x (pixels)
        - cy: Principal point y (pixels)
    """
    fov_rad = np.radians(fov_degrees)

    # Focal length from horizontal FOV: tan(fov/2) = (width/2) / fx
    fx = (width / 2) / np.tan(fov_rad / 2)
    fy = fx  # Square pixels assumption

    # Principal point at image center
    cx = width / 2.0
    cy = height / 2.0

    K = np.array([
        [fx, 0, cx],
        [0, fy, cy],
        [0, 0, 1]
    ])

    return K, fx, fy, cx, cy


def compute_world_to_camera_transform(
    camera_position: List[float],
    look_at_target: List[float],
    up_vector: List[float] | None = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute SE3 transformation from Unreal world to camera coordinates.

    Args:
        camera_position: [X, Y, Z] camera position in Unreal world (cm)
        look_at_target: [X, Y, Z] target point camera is looking at
        up_vector: [X, Y, Z] world up vector (default: Z-up for Unreal)

    Returns:
        Tuple of:
        - T_camera_world: 4x4 transformation matrix
        - R: 3x3 rotation matrix
        - t: 3x1 translation vector
    """
    if up_vector is None:
        up_vector = [0, 0, 1]  # Unreal Z-up

    P_cam = np.array(camera_position)
    P_target = np.array(look_at_target)
    V_up = np.array(up_vector)

    # Compute camera axes in Unreal world coordinates
    forward = P_target - P_cam
    forward = forward / np.linalg.norm(forward)

    right = np.cross(forward, V_up)
    right = right / np.linalg.norm(right)

    up = np.cross(right, forward)
    up = up / np.linalg.norm(up)

    # Rotation matrix from world to Unreal camera frame
    # Each row is a basis vector of the camera frame expressed in world coords
    R_unreal = np.stack([right, up, forward], axis=0)

    # Apply coordinate convention change: Unreal -> standard camera
    R = R_CONV @ R_unreal

    # Translation: camera origin in camera coordinates
    t = -R @ P_cam

    # Build 4x4 transformation matrix
    T_camera_world = np.eye(4)
    T_camera_world[:3, :3] = R
    T_camera_world[:3, 3] = t

    return T_camera_world, R, t


def transform_point_to_camera(
    point_world: List[float],
    T_camera_world: np.ndarray
) -> np.ndarray:
    """
    Transform a point from world to camera coordinates.

    Args:
        point_world: [X, Y, Z] in Unreal world (cm)
        T_camera_world: 4x4 transformation matrix

    Returns:
        point_camera: [X, Y, Z] in camera coordinates (cm)
    """
    p_world = np.array([*point_world, 1.0])
    p_camera = T_camera_world @ p_world
    return p_camera[:3]


def compute_rotation_y(
    rotation_world_deg: List[float],
    R_camera_world: np.ndarray,
    is_orientation_agnostic: bool = False
) -> float:
    """
    Compute object yaw angle in camera coordinates.

    For 3D detection, we need the rotation around the camera Y-axis (pointing down).
    This corresponds to the heading/yaw of the object as seen from the camera.

    Args:
        rotation_world_deg: [Pitch, Yaw, Roll] in degrees (Unreal convention)
        R_camera_world: 3x3 rotation matrix from world to camera
        is_orientation_agnostic: If True, return 0 (for round objects)

    Returns:
        rotation_y: Yaw angle in camera frame (radians), range [-pi, pi]
    """
    if is_orientation_agnostic:
        return 0.0

    # Extract yaw from world rotation (rotation around Z-axis in Unreal)
    yaw_world_deg = rotation_world_deg[1]
    yaw_world_rad = np.radians(yaw_world_deg)

    # Object forward direction in world (Unreal X-axis rotated by yaw around Z)
    forward_world = np.array([
        np.cos(yaw_world_rad),
        np.sin(yaw_world_rad),
        0
    ])

    # Transform to camera coordinates
    forward_camera = R_camera_world @ forward_world

    # Yaw in camera frame: rotation around camera Y-axis
    # Project onto camera XZ plane and compute angle from Z-axis
    rotation_y = np.arctan2(forward_camera[0], forward_camera[2])

    return float(rotation_y)


def project_point_to_image(
    point_camera: np.ndarray,
    K: np.ndarray
) -> Tuple[float, float]:
    """
    Project a 3D point in camera coordinates to 2D image coordinates.

    Args:
        point_camera: [X, Y, Z] in camera coordinates
        K: 3x3 intrinsic matrix

    Returns:
        (u, v): 2D image coordinates in pixels
    """
    # Perspective projection
    x, y, z = point_camera
    if z <= 0:
        return float('nan'), float('nan')

    u = K[0, 0] * x / z + K[0, 2]
    v = K[1, 1] * y / z + K[1, 2]

    return float(u), float(v)
