"""
Unreal Dataset - Synthetic 3D object detection dataset generation from Unreal Engine.

This package provides tools to:
- Control Unreal Engine scenes via HTTP API
- Capture screenshots with configurable camera positions
- Generate 3D detection labels with camera intrinsics/extrinsics
- Transform coordinates between world and camera frames
"""

__version__ = "2.0.0"
__author__ = "Kiwoo Shin"

from unreal_dataset.config.settings import get_settings

__all__ = ["__version__", "get_settings"]
