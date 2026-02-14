"""
Request handlers for the Unreal API server.

Each handler processes a specific request type.
"""

import math
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from unreal_dataset.server.scene_manager import get_scene_manager

# Try to import unreal, but allow running without it for testing
try:
    import unreal
    HAS_UNREAL = True
except ImportError:
    HAS_UNREAL = False
    unreal = None


# Output directory - will be set by server
OUTPUT_DIR: Path = Path.cwd() / "dataset_output"


def set_output_dir(path: Path) -> None:
    """Set the output directory."""
    global OUTPUT_DIR
    OUTPUT_DIR = Path(path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "metadata").mkdir(exist_ok=True)


def apply_colored_material(color_name: str, mesh_component: Any) -> Optional[Any]:
    """
    Create and assign a dynamic material instance with the specified color.

    Args:
        color_name: Color name (yellow, red, blue, etc.)
        mesh_component: StaticMeshComponent to apply the material to

    Returns:
        MaterialInstanceDynamic or None
    """
    if not HAS_UNREAL:
        return None

    colors = {
        "yellow": (1.0, 1.0, 0.0, 1.0),
        "red": (1.0, 0.0, 0.0, 1.0),
        "blue": (0.0, 0.0, 1.0, 1.0),
        "green": (0.0, 1.0, 0.0, 1.0),
        "white": (1.0, 1.0, 1.0, 1.0),
        "gray": (0.5, 0.5, 0.5, 1.0),
        "orange": (1.0, 0.5, 0.0, 1.0),
    }

    if color_name not in colors:
        unreal.log_warning(f"Unknown color: {color_name}, using default")
        return None

    r, g, b, a = colors[color_name]
    linear_color = unreal.LinearColor(r, g, b, a)

    # Load base material
    base_material_path = "/Engine/EngineMaterials/M_ColorBase"
    base_material = None
    if unreal.EditorAssetLibrary.does_asset_exist(base_material_path):
        base_material = unreal.EditorAssetLibrary.load_asset(base_material_path)

    # Create dynamic material instance
    mid = mesh_component.create_dynamic_material_instance(0, base_material)
    if mid:
        mid.set_vector_parameter_value("BaseColor", linear_color)
        unreal.log(f"Applied {color_name} material")
        return mid

    unreal.log_warning(f"Material creation failed for {color_name}")
    return None


def apply_material(material_path: str, mesh_component: Any) -> bool:
    """
    Apply a material from asset path to mesh component.

    Args:
        material_path: Full path to material asset
        mesh_component: StaticMeshComponent to apply the material to

    Returns:
        True if successful, False otherwise
    """
    if not HAS_UNREAL:
        return False

    if not unreal.EditorAssetLibrary.does_asset_exist(material_path):
        unreal.log_warning(f"Material not found: {material_path}")
        return False

    material = unreal.EditorAssetLibrary.load_asset(material_path)
    if material:
        material_interface = unreal.MaterialInterface.cast(material)
        if material_interface:
            num_materials = mesh_component.get_num_materials()
            for i in range(num_materials):
                mesh_component.set_material(i, material_interface)
            unreal.log(f"Applied material: {material_path}")
            return True

    unreal.log_warning(f"Failed to load material: {material_path}")
    return False


def spawn_object(obj_config: Dict[str, Any]) -> Optional[Any]:
    """
    Spawn an object based on configuration.

    Args:
        obj_config: Object configuration dictionary

    Returns:
        Spawned actor or None
    """
    if not HAS_UNREAL:
        return None

    scene_manager = get_scene_manager()
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    obj_type = obj_config.get("type", "cube")
    mesh_path = obj_config.get("mesh", "/Engine/BasicShapes/Cube")
    position = obj_config.get("position", [0, 0, 0])
    rotation = obj_config.get("rotation", [0, 0, 0])
    scale = obj_config.get("scale", [1, 1, 1])
    color = obj_config.get("color")
    label = obj_config.get("label", obj_type)

    spawn_location = unreal.Vector(position[0], position[1], position[2])
    spawn_rotation = unreal.Rotator(rotation[0], rotation[1], rotation[2])

    actor = editor_actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor.static_class(),
        spawn_location,
        spawn_rotation
    )

    if not actor:
        unreal.log_error(f"Failed to spawn actor for {obj_type}")
        return None

    # Set mesh
    try:
        static_mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
        if static_mesh:
            actor.static_mesh_component.set_static_mesh(static_mesh)
    except Exception as e:
        unreal.log_warning(f"Could not load mesh {mesh_path}: {e}")

    # Set scale
    actor.set_actor_scale3d(unreal.Vector(scale[0], scale[1], scale[2]))

    # Set label
    actor.set_actor_label(label)

    # Apply material or color
    material_path = obj_config.get("material")
    material_applied = False

    if material_path and (material_path.startswith("/Game/") or material_path.startswith("/Engine/")):
        material_applied = apply_material(material_path, actor.static_mesh_component)

    if not material_applied and color:
        apply_colored_material(color, actor.static_mesh_component)

    unreal.log(f"Spawned {obj_type} at {position}")
    scene_manager.add_actor(actor)
    return actor


def spawn_ground(ground_config: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    """Spawn a ground plane."""
    if ground_config is None:
        ground_config = {}

    position = ground_config.get("position", [0, 0, 0])
    scale = ground_config.get("scale", [50, 50, 1])
    color = ground_config.get("color", "gray")

    return spawn_object({
        "type": "ground",
        "mesh": "/Engine/BasicShapes/Plane",
        "position": position,
        "rotation": [0, 0, 0],
        "scale": scale,
        "color": color,
        "label": "GroundPlane",
    })


def calculate_look_at_rotation(camera_pos: list, target_pos: list) -> list:
    """Calculate rotation for camera to look at target."""
    dx = target_pos[0] - camera_pos[0]
    dy = target_pos[1] - camera_pos[1]
    dz = target_pos[2] - camera_pos[2]

    yaw = math.degrees(math.atan2(dy, dx))
    horizontal_dist = math.sqrt(dx * dx + dy * dy)
    pitch = math.degrees(math.atan2(dz, horizontal_dist))

    return [pitch, yaw, 0]


def set_viewport_camera(camera_config: Dict[str, Any]) -> None:
    """Move the viewport camera to specified position."""
    if not HAS_UNREAL:
        return

    position = camera_config.get("position", [500, 0, 300])

    if "look_at" in camera_config:
        look_at = camera_config["look_at"]
        rotation = calculate_look_at_rotation(position, look_at)
    else:
        rotation = camera_config.get("rotation", [0, 0, 0])

    camera_location = unreal.Vector(position[0], position[1], position[2])
    camera_rotation = unreal.Rotator(rotation[2], rotation[0], rotation[1])

    try:
        unreal.EditorLevelLibrary.set_level_viewport_camera_info(
            camera_location,
            camera_rotation
        )
        unreal.log(f"Camera set: location={position}")
    except Exception as e:
        unreal.log_warning(f"Could not set viewport camera: {e}")


def take_screenshot(output_config: Dict[str, Any]) -> str:
    """
    Take a screenshot using viewport capture.

    Args:
        output_config: Dict with filename and resolution

    Returns:
        Path to saved image
    """
    if not HAS_UNREAL:
        return ""

    filename = output_config.get("filename", "capture.png")
    resolution = output_config.get("resolution", [640, 640])

    full_path = str(OUTPUT_DIR / filename)

    # Delete old file
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
        except OSError:
            pass

    try:
        # Set to game view
        unreal.EditorLevelLibrary.editor_set_game_view(True)
        time.sleep(1.0)

        # Take screenshot
        automation_lib = unreal.AutomationLibrary()
        automation_lib.take_high_res_screenshot(resolution[0], resolution[1], full_path)

        unreal.log(f"Screenshot requested: {full_path}")

        # Wait for file to stabilize
        max_wait = 60
        start_time = time.time()
        last_size = -1
        stable_count = 0

        while True:
            if time.time() - start_time > max_wait:
                unreal.log_warning(f"Screenshot timeout after {max_wait}s")
                break

            if os.path.exists(full_path):
                current_size = os.path.getsize(full_path)
                if current_size > 0 and current_size == last_size:
                    stable_count += 1
                    if stable_count >= 3:
                        unreal.log(f"Screenshot complete: {current_size} bytes")
                        break
                else:
                    stable_count = 0
                last_size = current_size

            time.sleep(0.5)

    except Exception as e:
        unreal.log_error(f"Screenshot error: {e}")

    return full_path


# Request Handlers


def handle_status() -> Dict[str, Any]:
    """Handle status request."""
    scene_manager = get_scene_manager()

    try:
        version = unreal.SystemLibrary.get_engine_version() if HAS_UNREAL else "N/A"
    except Exception:
        version = "N/A"

    return {
        "status": "ok",
        "version": "2.0",
        "unreal_version": version,
        "output_dir": str(OUTPUT_DIR),
        "active_actors": scene_manager.actor_count,
    }


def handle_setup_scene(config: Dict[str, Any]) -> Dict[str, Any]:
    """Handle scene setup request."""
    scene_manager = get_scene_manager()

    try:
        if config.get("cleanup_before", True):
            scene_manager.cleanup()

        spawned = []

        # Spawn ground
        if "ground" in config or config.get("add_ground", True):
            ground_config = config.get("ground", {})
            ground = spawn_ground(ground_config)
            if ground:
                spawned.append("ground plane")

        # Spawn objects
        objects = config.get("objects", [])
        for obj_config in objects:
            spawn_object(obj_config)
        spawned.append(f"{len(objects)} objects")

        return {
            "status": "success",
            "message": f"Spawned: {', '.join(spawned)}",
            "total_actors": scene_manager.actor_count,
        }

    except Exception as e:
        if HAS_UNREAL:
            unreal.log_error(f"Error setting up scene: {e}")
        return {"status": "error", "error": str(e)}


def handle_capture(config: Dict[str, Any]) -> Dict[str, Any]:
    """Handle capture request."""
    try:
        # Set camera position
        camera_config = config.get("camera", {})
        set_viewport_camera(camera_config)

        time.sleep(0.5)

        # Position only mode
        if config.get("position_only", False):
            return {
                "status": "success",
                "message": "Camera positioned (no screenshot taken)",
                "camera": camera_config,
            }

        # Take screenshot
        output_config = config.get("output", {"filename": "capture.png"})
        image_path = take_screenshot(output_config)

        return {
            "status": "success",
            "image_path": image_path,
        }

    except Exception as e:
        if HAS_UNREAL:
            unreal.log_error(f"Error capturing: {e}")
        return {"status": "error", "error": str(e)}


def handle_get_scene_objects() -> Dict[str, Any]:
    """Handle get scene objects request."""
    scene_manager = get_scene_manager()

    try:
        objects = scene_manager.get_objects_info()
        return {
            "status": "success",
            "objects": objects,
            "count": len(objects),
        }
    except Exception as e:
        if HAS_UNREAL:
            unreal.log_error(f"Error getting scene objects: {e}")
        return {"status": "error", "error": str(e)}


def handle_cleanup() -> Dict[str, Any]:
    """Handle cleanup request."""
    scene_manager = get_scene_manager()

    try:
        scene_manager.cleanup()
        return {"status": "ok", "message": "Scene cleaned"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
