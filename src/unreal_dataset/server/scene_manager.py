"""
Scene state management for the Unreal server.

Encapsulates global state into a singleton class.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

# Conditional import for type hints only
if TYPE_CHECKING:
    import unreal


@dataclass
class ObjectInfo:
    """Information about a spawned object."""
    actor: Any  # unreal.Actor
    config: Dict[str, Any]
    label: str


class SceneManager:
    """
    Manages the scene state including spawned actors.

    This is a singleton class that maintains state across requests.
    """

    _instance: Optional["SceneManager"] = None

    def __new__(cls) -> "SceneManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self._actors: List[Any] = []  # List of unreal.Actor
        self._scene_capture: Optional[Any] = None
        self._render_target: Optional[Any] = None

    @property
    def actors(self) -> List[Any]:
        """Get list of spawned actors."""
        return self._actors

    @property
    def actor_count(self) -> int:
        """Get number of active actors."""
        return len([a for a in self._actors if a and a.is_valid()])

    def add_actor(self, actor: Any) -> None:
        """Add an actor to the managed list."""
        self._actors.append(actor)

    def cleanup(self) -> None:
        """Remove all spawned actors."""
        try:
            import unreal
            editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

            for actor in self._actors:
                try:
                    if actor and actor.is_valid():
                        editor_actor_subsystem.destroy_actor(actor)
                except RuntimeError as e:
                    unreal.log_warning(f"Failed to destroy actor: {e}")

            self._actors.clear()

            # Cleanup scene capture
            if self._scene_capture and self._scene_capture.is_valid():
                try:
                    editor_actor_subsystem.destroy_actor(self._scene_capture)
                except RuntimeError:
                    pass
            self._scene_capture = None

            unreal.log("Scene cleaned up")

        except ImportError:
            # Not running in Unreal
            self._actors.clear()

    def get_objects_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all spawned objects.

        Returns:
            List of dictionaries with object info
        """
        try:
            import unreal
        except ImportError:
            return []

        objects = []

        for actor in self._actors:
            if not actor or not actor.is_valid():
                continue

            # Get actor transform
            transform = actor.get_actor_transform()
            location = transform.translation
            rotation = transform.rotation
            scale = transform.scale3d

            # Get Euler angles
            rotation_euler = [rotation.pitch, rotation.yaw, rotation.roll]

            # Get actor bounds
            origin, extent = actor.get_actor_bounds(only_colliding_components=False)

            # Get label and derive class name
            label = actor.get_actor_label()
            class_name = label.split("_")[0].lower() if "_" in label else label.lower()

            # Skip ground plane
            if class_name in ["groundplane", "ground"]:
                continue

            obj_info = {
                "label": label,
                "class_name": class_name,
                "location_world": [location.x, location.y, location.z],
                "rotation_world": rotation_euler,
                "scale": [scale.x, scale.y, scale.z],
                "bounds_center": [origin.x, origin.y, origin.z],
                "bounds_extent": [extent.x, extent.y, extent.z],
                "dimensions": [extent.x * 2, extent.y * 2, extent.z * 2],
            }

            objects.append(obj_info)

        return objects

    def reset(self) -> None:
        """Reset the singleton instance (for testing)."""
        self.cleanup()
        SceneManager._instance = None


def get_scene_manager() -> SceneManager:
    """Get the singleton scene manager instance."""
    return SceneManager()
