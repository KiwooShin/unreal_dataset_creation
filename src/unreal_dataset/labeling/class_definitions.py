"""
Class definitions for 3D object detection.

Defines class IDs and properties for objects in the dataset.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ClassInfo:
    """Information about an object class."""
    id: int
    orientation_agnostic: bool

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {"id": self.id, "orientation_agnostic": self.orientation_agnostic}


# Class definitions for 3D detection
CLASS_DEFINITIONS: Dict[str, ClassInfo] = {
    "floor": ClassInfo(id=0, orientation_agnostic=True),
    "wall": ClassInfo(id=1, orientation_agnostic=False),
    "table": ClassInfo(id=2, orientation_agnostic=False),
    "round_table": ClassInfo(id=3, orientation_agnostic=True),
    "chair": ClassInfo(id=4, orientation_agnostic=False),
    "door": ClassInfo(id=5, orientation_agnostic=False),
    "window": ClassInfo(id=6, orientation_agnostic=False),
    "cabinet": ClassInfo(id=7, orientation_agnostic=False),
    "sofa": ClassInfo(id=8, orientation_agnostic=False),
    "lamp": ClassInfo(id=9, orientation_agnostic=True),
    "sphere": ClassInfo(id=10, orientation_agnostic=True),
    "cube": ClassInfo(id=11, orientation_agnostic=False),
}


def get_class_info(class_name: str) -> ClassInfo:
    """
    Get class information for a class name.

    Supports fuzzy matching for common variations (e.g., "round_table" matches "table").

    Args:
        class_name: Object class name (e.g., "table", "chair")

    Returns:
        ClassInfo with id and orientation_agnostic flag
    """
    class_name_lower = class_name.lower()

    # Direct lookup
    if class_name_lower in CLASS_DEFINITIONS:
        return CLASS_DEFINITIONS[class_name_lower]

    # Fuzzy matching for common variations
    if "table" in class_name_lower:
        if "round" in class_name_lower:
            return CLASS_DEFINITIONS["round_table"]
        return CLASS_DEFINITIONS["table"]
    if "chair" in class_name_lower:
        return CLASS_DEFINITIONS["chair"]
    if "wall" in class_name_lower:
        return CLASS_DEFINITIONS["wall"]
    if "floor" in class_name_lower:
        return CLASS_DEFINITIONS["floor"]

    # Default: unknown class
    return ClassInfo(id=-1, orientation_agnostic=False)


def register_class(name: str, class_id: int, orientation_agnostic: bool = False) -> None:
    """
    Register a new class definition.

    Args:
        name: Class name (lowercase)
        class_id: Unique integer ID
        orientation_agnostic: Whether orientation matters for this class
    """
    CLASS_DEFINITIONS[name.lower()] = ClassInfo(
        id=class_id, orientation_agnostic=orientation_agnostic
    )
