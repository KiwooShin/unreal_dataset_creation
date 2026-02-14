"""Unit tests for coordinate transforms."""

import math

import numpy as np
import pytest

from unreal_dataset.labeling.transforms import (
    R_CONV,
    compute_intrinsics,
    compute_rotation_y,
    compute_world_to_camera_transform,
    project_point_to_image,
    transform_point_to_camera,
)


class TestComputeIntrinsics:
    """Tests for compute_intrinsics function."""

    def test_90_degree_fov_square(self):
        """Test with 90 degree FOV and square resolution."""
        K, fx, fy, cx, cy = compute_intrinsics(90.0, 640, 640)

        # For 90 degree FOV: fx = (width/2) / tan(45) = 320 / 1 = 320
        assert pytest.approx(fx, rel=1e-5) == 320.0
        assert pytest.approx(fy, rel=1e-5) == 320.0
        assert pytest.approx(cx, rel=1e-5) == 320.0
        assert pytest.approx(cy, rel=1e-5) == 320.0

        # Check K matrix structure
        assert K.shape == (3, 3)
        assert K[0, 0] == fx
        assert K[1, 1] == fy
        assert K[0, 2] == cx
        assert K[1, 2] == cy
        assert K[2, 2] == 1.0

    def test_60_degree_fov(self):
        """Test with 60 degree FOV."""
        K, fx, fy, cx, cy = compute_intrinsics(60.0, 640, 480)

        # For 60 degree FOV: fx = (width/2) / tan(30) = 320 / 0.577 ≈ 554.3
        expected_fx = 320 / math.tan(math.radians(30))
        assert pytest.approx(fx, rel=1e-5) == expected_fx
        assert pytest.approx(cx, rel=1e-5) == 320.0
        assert pytest.approx(cy, rel=1e-5) == 240.0


class TestComputeWorldToCameraTransform:
    """Tests for SE3 transformation computation."""

    def test_camera_looking_forward(self):
        """Test camera at origin looking along X axis."""
        camera_pos = [0, 0, 0]
        look_at = [100, 0, 0]

        T, R, t = compute_world_to_camera_transform(camera_pos, look_at)

        # Check matrix dimensions
        assert T.shape == (4, 4)
        assert R.shape == (3, 3)
        assert t.shape == (3,)

        # Camera at origin, so translation should be zero
        assert np.allclose(t, [0, 0, 0], atol=1e-10)

        # Check T is valid SE3 (last row is [0, 0, 0, 1])
        assert np.allclose(T[3, :], [0, 0, 0, 1])

    def test_camera_offset(self):
        """Test camera at offset position."""
        camera_pos = [1000, 500, 200]
        look_at = [0, 0, 0]

        T, R, t = compute_world_to_camera_transform(camera_pos, look_at)

        # Transform camera position - should give origin in camera frame
        cam_in_camera = transform_point_to_camera(camera_pos, T)
        assert np.allclose(cam_in_camera, [0, 0, 0], atol=1e-10)

    def test_rotation_is_orthonormal(self):
        """Test that rotation matrix is orthonormal."""
        camera_pos = [500, 300, 200]
        look_at = [0, 100, 50]

        T, R, t = compute_world_to_camera_transform(camera_pos, look_at)

        # R @ R.T should be identity
        assert np.allclose(R @ R.T, np.eye(3), atol=1e-10)

        # det(R) should be 1 (proper rotation)
        assert pytest.approx(np.linalg.det(R), abs=1e-10) == 1.0


class TestTransformPointToCamera:
    """Tests for point transformation."""

    def test_origin_transforms_to_camera_translation(self):
        """Test that world origin transforms to -t in camera frame."""
        camera_pos = [100, 50, 25]
        look_at = [0, 0, 0]

        T, R, t = compute_world_to_camera_transform(camera_pos, look_at)
        origin_in_camera = transform_point_to_camera([0, 0, 0], T)

        # World origin should be at translation in camera coordinates
        assert np.allclose(origin_in_camera, t, atol=1e-10)

    def test_camera_position_at_origin(self):
        """Test that camera position transforms to origin."""
        camera_pos = [500, 200, 100]
        look_at = [0, 0, 0]

        T, R, t = compute_world_to_camera_transform(camera_pos, look_at)
        cam_in_camera = transform_point_to_camera(camera_pos, T)

        assert np.allclose(cam_in_camera, [0, 0, 0], atol=1e-10)


class TestComputeRotationY:
    """Tests for yaw angle computation."""

    def test_orientation_agnostic_returns_zero(self):
        """Test that orientation-agnostic objects return 0."""
        R = np.eye(3)
        rotation_world = [0, 45, 0]  # 45 degree yaw

        rot_y = compute_rotation_y(rotation_world, R, is_orientation_agnostic=True)
        assert rot_y == 0.0

    def test_zero_yaw(self):
        """Test object with zero yaw."""
        # Simple camera looking along world X
        camera_pos = [0, 0, 0]
        look_at = [100, 0, 0]
        T, R, t = compute_world_to_camera_transform(camera_pos, look_at)

        rotation_world = [0, 0, 0]  # No rotation
        rot_y = compute_rotation_y(rotation_world, R, is_orientation_agnostic=False)

        # Should be close to 0 (object facing same direction as camera)
        assert abs(rot_y) < 0.1


class TestProjectPointToImage:
    """Tests for 3D to 2D projection."""

    def test_point_at_center(self):
        """Test that point on optical axis projects to center."""
        K, fx, fy, cx, cy = compute_intrinsics(90.0, 640, 480)

        # Point directly in front of camera (on optical axis)
        point = np.array([0, 0, 100])
        u, v = project_point_to_image(point, K)

        assert pytest.approx(u, rel=1e-5) == cx
        assert pytest.approx(v, rel=1e-5) == cy

    def test_point_behind_camera(self):
        """Test that point behind camera returns NaN."""
        K, fx, fy, cx, cy = compute_intrinsics(90.0, 640, 480)

        # Point behind camera (negative Z)
        point = np.array([0, 0, -100])
        u, v = project_point_to_image(point, K)

        assert math.isnan(u)
        assert math.isnan(v)


class TestRConvMatrix:
    """Tests for the coordinate conversion matrix."""

    def test_r_conv_shape(self):
        """Test R_CONV has correct shape."""
        assert R_CONV.shape == (3, 3)

    def test_r_conv_axes_mapping(self):
        """Test that R_CONV correctly maps Unreal to camera axes."""
        # Unreal X (forward) -> Camera Z
        unreal_x = np.array([1, 0, 0])
        assert np.allclose(R_CONV @ unreal_x, [0, 0, 1])

        # Unreal Y (right) -> Camera X
        unreal_y = np.array([0, 1, 0])
        assert np.allclose(R_CONV @ unreal_y, [1, 0, 0])

        # Unreal Z (up) -> Camera -Y (down)
        unreal_z = np.array([0, 0, 1])
        assert np.allclose(R_CONV @ unreal_z, [0, -1, 0])
