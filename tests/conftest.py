"""Pytest fixtures for Unreal Dataset tests."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_camera_config():
    """Sample camera configuration for testing."""
    return {
        "position": [1500, 300, 800],
        "look_at": [50, 300, 100],
        "fov": 90.0,
    }


@pytest.fixture
def sample_object_info():
    """Sample object info as returned by the API."""
    return {
        "label": "Table",
        "class_name": "table",
        "location_world": [650, 300, 60],
        "rotation_world": [0, 0, 0],
        "scale": [1.0, 1.0, 1.0],
        "dimensions": [120, 120, 80],
        "bounds_center": [650, 300, 60],
        "bounds_extent": [60, 60, 40],
    }


@pytest.fixture
def sample_scene_config():
    """Sample scene configuration for testing."""
    return {
        "name": "test_scene",
        "objects": [
            {
                "type": "table",
                "class_name": "round_table",
                "mesh": "/Game/StarterContent/Props/SM_TableRound",
                "position": [650, 300, 20],
                "scale": [1.0, 1.0, 1.0],
                "is_orientation_agnostic": True,
            },
            {
                "type": "chair",
                "class_name": "chair",
                "mesh": "/Game/StarterContent/Props/SM_Chair",
                "position": [650, 450, 20],
                "rotation": [0, 0, 180],
                "scale": [1.0, 1.0, 1.0],
                "is_orientation_agnostic": False,
            },
        ],
        "camera": {
            "target": [50, 300, 100],
            "position": [1500, 300, 800],
            "fov": 90.0,
        },
    }


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary output directory for testing."""
    output_dir = tmp_path / "dataset_output"
    output_dir.mkdir()
    (output_dir / "labels").mkdir()
    return output_dir
