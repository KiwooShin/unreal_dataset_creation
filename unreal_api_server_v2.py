"""
Unreal Engine HTTP API Server v2
Purpose: Run inside Unreal Editor to receive commands from external Python

IMPROVEMENTS OVER v1:
- Spawn lighting via API
- Material support for colored objects (yellow cube)
- SceneCapture2D for reliable synchronous screenshots
- Better error handling

USAGE:
    In Unreal Editor Python console (one-time):
    exec(open('/Users/kiwooshin/work/unreal_dataset_creation/unreal_api_server_v2.py').read())

    Then control from external Python via HTTP API.
"""

import unreal
import json
import os
import math
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import threading
import queue
import uuid
import time

# Configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 8080
OUTPUT_DIR = '/Users/kiwooshin/work/unreal_dataset_creation/dataset_output'

# Global state
current_actors = []
scene_capture_actor = None
render_target = None
request_queue = queue.Queue()
response_dict = {}
timer_handle = None
tick_paused = False  # Pause tick processing during screenshots

# ============================================================================
# UNREAL ENGINE FUNCTIONS (Main thread only!)
# ============================================================================

def setup_output_directory():
    """Create output directory if needed"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    metadata_dir = os.path.join(OUTPUT_DIR, 'metadata')
    os.makedirs(metadata_dir, exist_ok=True)


def cleanup_scene():
    """Remove all previously spawned actors"""
    global current_actors, scene_capture_actor
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    for actor in current_actors:
        try:
            if actor and actor.is_valid():
                editor_actor_subsystem.destroy_actor(actor)
        except:
            pass

    current_actors = []

    # Also cleanup scene capture
    if scene_capture_actor and scene_capture_actor.is_valid():
        try:
            editor_actor_subsystem.destroy_actor(scene_capture_actor)
        except:
            pass
    scene_capture_actor = None

    unreal.log("Scene cleaned up")


def create_colored_material(color_name, mesh_component=None):
    """
    Create a dynamic material instance with the specified color.

    Args:
        color_name: 'yellow', 'red', 'blue', 'green', 'white', 'gray', 'orange'
        mesh_component: Optional StaticMeshComponent to create dynamic material from

    Returns:
        MaterialInstanceDynamic or None
    """
    # Color definitions (R, G, B, A)
    colors = {
        'yellow': (1.0, 1.0, 0.0, 1.0),
        'red': (1.0, 0.0, 0.0, 1.0),
        'blue': (0.0, 0.0, 1.0, 1.0),
        'green': (0.0, 1.0, 0.0, 1.0),
        'white': (1.0, 1.0, 1.0, 1.0),
        'gray': (0.5, 0.5, 0.5, 1.0),
        'orange': (1.0, 0.5, 0.0, 1.0),
    }

    if color_name not in colors:
        unreal.log_warning(f"Unknown color: {color_name}, using default")
        return None

    r, g, b, a = colors[color_name]
    linear_color = unreal.LinearColor(r, g, b, a)

    # Try to load custom base material with color parameter first
    base_material_path = '/Engine/EngineMaterials/M_ColorBase'
    if unreal.EditorAssetLibrary.does_asset_exist(base_material_path):
        base_material = unreal.EditorAssetLibrary.load_asset(base_material_path)
        if base_material:
            # Create dynamic instance
            mid = unreal.KismetMaterialLibrary.create_dynamic_material_instance(
                unreal.EditorLevelLibrary.get_editor_world(),
                base_material
            )
            if mid:
                mid.set_vector_parameter_value("BaseColor", linear_color)
                unreal.log(f"Created dynamic material with color: {color_name}")
                return mid

    # Fallback: Create dynamic material from mesh component's current material
    if mesh_component:
        try:
            mid = mesh_component.create_dynamic_material_instance(0)
            if mid:
                # Try common parameter names
                for param_name in ["BaseColor", "Color", "Base Color", "Tint"]:
                    try:
                        mid.set_vector_parameter_value(param_name, linear_color)
                        unreal.log(f"Set {param_name} to {color_name}")
                        return mid
                    except:
                        continue
                unreal.log_warning(f"Could not find color parameter in material")
                return mid
        except Exception as e:
            unreal.log_warning(f"Could not create dynamic material: {e}")

    unreal.log_warning(f"Material creation failed for {color_name}. Create /Game/Materials/M_ColorBase with BaseColor parameter.")
    return None


def spawn_object(obj_config):
    """Spawn an object based on configuration"""
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    obj_type = obj_config.get('type', 'cube')
    mesh_path = obj_config.get('mesh', '/Engine/BasicShapes/Cube')
    position = obj_config.get('position', [0, 0, 0])
    rotation = obj_config.get('rotation', [0, 0, 0])
    scale = obj_config.get('scale', [1, 1, 1])
    color = obj_config.get('color', None)
    label = obj_config.get('label', obj_type)

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

    # Apply color/material if specified
    if color:
        material = create_colored_material(color, actor.static_mesh_component)
        if material:
            actor.static_mesh_component.set_material(0, material)

    unreal.log(f"Spawned {obj_type} at {position} with scale {scale}")
    return actor


def spawn_ground(ground_config=None):
    """
    Spawn a ground plane

    Args:
        ground_config: Optional dict with ground settings

    Returns:
        Ground actor
    """
    if ground_config is None:
        ground_config = {}

    position = ground_config.get('position', [0, 0, 0])
    scale = ground_config.get('scale', [50, 50, 1])
    color = ground_config.get('color', 'gray')

    ground = spawn_object({
        'type': 'ground',
        'mesh': '/Engine/BasicShapes/Plane',
        'position': position,
        'rotation': [0, 0, 0],
        'scale': scale,
        'color': color,
        'label': 'GroundPlane'
    })

    return ground


def calculate_look_at_rotation(camera_pos, target_pos):
    """Calculate rotation for camera to look at target"""
    dx = target_pos[0] - camera_pos[0]
    dy = target_pos[1] - camera_pos[1]
    dz = target_pos[2] - camera_pos[2]

    yaw = math.degrees(math.atan2(dy, dx))
    horizontal_dist = math.sqrt(dx*dx + dy*dy)
    pitch = math.degrees(math.atan2(dz, horizontal_dist))

    return [pitch, yaw, 0]


def set_viewport_camera(camera_config):
    """
    Move the viewport camera to specified position

    Args:
        camera_config: Dict with 'position', 'rotation' or 'look_at', 'fov'
    """
    position = camera_config.get('position', [500, 0, 300])

    # Calculate rotation - either from 'rotation' or 'look_at'
    if 'look_at' in camera_config:
        look_at = camera_config['look_at']
        rotation = calculate_look_at_rotation(position, look_at)
        unreal.log(f"Camera look_at calculation: pos={position} -> target={look_at}")
        unreal.log(f"  Calculated rotation: pitch={rotation[0]:.1f}, yaw={rotation[1]:.1f}, roll={rotation[2]:.1f}")
    else:
        rotation = camera_config.get('rotation', [0, 0, 0])

    camera_location = unreal.Vector(position[0], position[1], position[2])
    # Unreal Rotator constructor: (Roll, Pitch, Yaw)
    # rotation = [pitch, yaw, roll] from calculate_look_at_rotation
    camera_rotation = unreal.Rotator(rotation[2], rotation[0], rotation[1])

    try:
        unreal.EditorLevelLibrary.set_level_viewport_camera_info(
            camera_location,
            camera_rotation
        )
        unreal.log(f"Viewport camera SET: location={position}, rotation=Rotator({rotation[0]:.1f}, {rotation[1]:.1f}, {rotation[2]:.1f})")
    except Exception as e:
        unreal.log_warning(f"Could not set viewport camera: {e}")


def take_screenshot_viewport(output_config):
    """
    Take a screenshot using viewport capture

    Args:
        output_config: Dict with 'filename', 'resolution'

    Returns:
        Path to saved image
    """
    global tick_paused

    filename = output_config.get('filename', 'capture.png')
    resolution = output_config.get('resolution', [640, 640])

    full_path = os.path.join(OUTPUT_DIR, filename)

    # Delete old file
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
        except:
            pass

    try:
        # Set to game view for cleaner screenshot
        unreal.EditorLevelLibrary.editor_set_game_view(True)

        # Wait for viewport to stabilize (reduces flickering)
        time.sleep(1.0)

        # Take screenshot
        automation_lib = unreal.AutomationLibrary()
        automation_lib.take_high_res_screenshot(resolution[0], resolution[1], full_path)

        unreal.log(f"Screenshot requested: {full_path}")

        # Wait for file to appear AND stabilize (with timeout)
        max_wait = 60  # seconds
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
                    if stable_count >= 3:  # File size stable for 1.5 seconds
                        unreal.log(f"Screenshot complete: {current_size} bytes")
                        break
                else:
                    stable_count = 0
                last_size = current_size

            time.sleep(0.5)

        if os.path.exists(full_path):
            unreal.log(f"Screenshot saved: {full_path}")

    except Exception as e:
        unreal.log_error(f"Screenshot error: {e}")

    return full_path


def save_metadata(filename, metadata):
    """Save metadata as JSON"""
    metadata_dir = os.path.join(OUTPUT_DIR, 'metadata')
    os.makedirs(metadata_dir, exist_ok=True)
    full_path = os.path.join(metadata_dir, filename)

    with open(full_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    return full_path


# ============================================================================
# REQUEST HANDLERS
# ============================================================================

def handle_status_request():
    """Handle status request"""
    try:
        return {
            'status': 'ok',
            'version': '2.0',
            'unreal_version': unreal.SystemLibrary.get_engine_version(),
            'output_dir': OUTPUT_DIR,
            'active_actors': len(current_actors)
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


def handle_setup_scene_request(config):
    """
    Set up a complete scene with lighting, ground, and objects

    Config:
    {
        "cleanup_before": true,
        "lighting": { "sun_rotation": [-50, -30, 0], "add_skylight": true },
        "ground": { "scale": [50, 50, 1], "color": "gray" },
        "objects": [
            { "type": "cube", "position": [0, 0, 100], "scale": [2, 2, 2], "color": "yellow" }
        ]
    }
    """
    global current_actors

    try:
        if config.get('cleanup_before', True):
            cleanup_scene()

        spawned = []

        # Spawn ground
        if 'ground' in config or config.get('add_ground', True):
            ground_config = config.get('ground', {})
            ground = spawn_ground(ground_config)
            if ground:
                current_actors.append(ground)
                spawned.append("ground plane")

        # Spawn objects
        objects = config.get('objects', [])
        for obj_config in objects:
            actor = spawn_object(obj_config)
            if actor:
                current_actors.append(actor)
        spawned.append(f"{len(objects)} objects")

        return {
            'status': 'success',
            'message': f"Spawned: {', '.join(spawned)}",
            'total_actors': len(current_actors)
        }

    except Exception as e:
        unreal.log_error(f"Error setting up scene: {e}")
        return {'status': 'error', 'error': str(e)}


def handle_capture_request(config):
    """
    Capture a screenshot from specified camera position

    Config:
    {
        "camera": {
            "position": [500, 0, 300],
            "look_at": [0, 0, 100],
            "fov": 90
        },
        "output": {
            "filename": "capture_001.png",
            "resolution": [640, 640]
        },
        "save_metadata": true
    }
    """
    try:
        # Set camera position
        camera_config = config.get('camera', {})
        set_viewport_camera(camera_config)

        # Small delay for viewport to update
        time.sleep(0.5)

        # If position_only, just return without taking screenshot
        if config.get('position_only', False):
            return {
                'status': 'success',
                'message': 'Camera positioned (no screenshot taken)',
                'camera': camera_config
            }

        # Take screenshot
        output_config = config.get('output', {'filename': 'capture.png'})
        image_path = take_screenshot_viewport(output_config)

        # Save metadata
        metadata_path = None
        if config.get('save_metadata', True):
            filename = output_config.get('filename', 'capture.png')
            metadata_filename = filename.replace('.png', '.json')

            metadata = {
                'camera': camera_config,
                'output': output_config,
                'image_path': image_path,
                'timestamp': time.time()
            }
            metadata_path = save_metadata(metadata_filename, metadata)

        return {
            'status': 'success',
            'image_path': image_path,
            'metadata_path': metadata_path
        }

    except Exception as e:
        unreal.log_error(f"Error capturing: {e}")
        return {'status': 'error', 'error': str(e)}


def handle_full_capture_request(config):
    """
    Complete workflow: setup scene + capture from multiple angles

    Config:
    {
        "scene": {
            "objects": [...],
            "lighting": {...},
            "ground": {...}
        },
        "captures": [
            {
                "name": "front",
                "camera": { "position": [500, 0, 300], "look_at": [0, 0, 100] },
                "output": { "filename": "cube_front.png", "resolution": [640, 640] }
            },
            ...
        ]
    }
    """
    try:
        results = []

        # Setup scene
        scene_config = config.get('scene', {})
        scene_config['cleanup_before'] = True
        setup_result = handle_setup_scene_request(scene_config)

        if setup_result['status'] != 'success':
            return setup_result

        # Capture from each angle
        captures = config.get('captures', [])
        for i, capture_config in enumerate(captures):
            name = capture_config.get('name', f'capture_{i}')
            unreal.log(f"Capturing: {name}")

            result = handle_capture_request(capture_config)
            result['name'] = name
            results.append(result)

            # Small delay between captures
            time.sleep(0.5)

        success_count = sum(1 for r in results if r['status'] == 'success')

        return {
            'status': 'success',
            'captures': results,
            'success_count': success_count,
            'total_count': len(captures)
        }

    except Exception as e:
        unreal.log_error(f"Error in full capture: {e}")
        return {'status': 'error', 'error': str(e)}


def handle_cleanup_request():
    """Handle cleanup request"""
    try:
        cleanup_scene()
        return {'status': 'ok', 'message': 'Scene cleaned'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


# ============================================================================
# HTTP SERVER
# ============================================================================

class UnrealAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler"""

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def _send_json(self, data, status=200):
        self._set_headers(status)
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _enqueue_request(self, request_type, data=None):
        """Enqueue request for main thread processing"""
        request_id = str(uuid.uuid4())

        request_queue.put({
            'id': request_id,
            'type': request_type,
            'data': data
        })

        # Wait for response
        timeout = 120  # Increased timeout for screenshot capture
        start_time = time.time()

        while request_id not in response_dict:
            time.sleep(0.1)
            if time.time() - start_time > timeout:
                return {'status': 'error', 'error': 'Request timeout'}

        return response_dict.pop(request_id)

    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/':
            self._send_json({
                'status': 'running',
                'message': 'Unreal Engine API Server v2',
                'endpoints': [
                    'GET  /status',
                    'POST /setup_scene',
                    'POST /capture',
                    'POST /full_capture',
                    'POST /cleanup'
                ]
            })
        elif parsed_path.path == '/status':
            response = self._enqueue_request('status')
            self._send_json(response)
        else:
            self._send_json({'error': 'Not found'}, 404)

    def do_POST(self):
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))

        if content_length > 0:
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self._send_json({'error': 'Invalid JSON'}, 400)
                return
        else:
            data = {}

        endpoint_map = {
            '/setup_scene': 'setup_scene',
            '/capture': 'capture',
            '/full_capture': 'full_capture',
            '/cleanup': 'cleanup'
        }

        if parsed_path.path in endpoint_map:
            response = self._enqueue_request(endpoint_map[parsed_path.path], data)
            self._send_json(response)
        else:
            self._send_json({'error': 'Not found'}, 404)

    def log_message(self, format, *args):
        pass  # Suppress logging


# ============================================================================
# QUEUE PROCESSOR
# ============================================================================

def process_request_queue(delta_time):
    """Process requests from queue on main thread"""
    global tick_paused
    if tick_paused:
        return  # Skip processing when paused (during screenshots)
    try:
        while not request_queue.empty():
            try:
                request = request_queue.get_nowait()
                request_id = request['id']
                request_type = request['type']
                request_data = request.get('data')

                handler_map = {
                    'status': lambda: handle_status_request(),
                    'setup_scene': lambda: handle_setup_scene_request(request_data),
                    'capture': lambda: handle_capture_request(request_data),
                    'full_capture': lambda: handle_full_capture_request(request_data),
                    'cleanup': lambda: handle_cleanup_request()
                }

                if request_type in handler_map:
                    response = handler_map[request_type]()
                else:
                    response = {'status': 'error', 'error': f'Unknown: {request_type}'}

                response_dict[request_id] = response

            except queue.Empty:
                break
            except Exception as e:
                unreal.log_error(f"Error processing request: {str(e)}")

    except Exception as e:
        unreal.log_error(f"Error in queue processor: {str(e)}")


# ============================================================================
# SERVER MANAGEMENT
# ============================================================================

http_server = None
server_thread = None
timer_handle = None

def start_server():
    """Start the HTTP server"""
    global http_server, server_thread, timer_handle

    if http_server is not None:
        unreal.log_warning("Server already running")
        return

    setup_output_directory()

    # Start HTTP server
    http_server = HTTPServer((SERVER_HOST, SERVER_PORT), UnrealAPIHandler)
    server_thread = threading.Thread(target=http_server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Start queue processor
    timer_handle = unreal.register_slate_post_tick_callback(process_request_queue)

    print("=" * 70)
    print("UNREAL ENGINE API SERVER v2 STARTED")
    print("=" * 70)
    print(f"Server: http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"Output: {OUTPUT_DIR}")
    print()
    print("Endpoints:")
    print(f"  GET  /status       - Check server status")
    print(f"  POST /setup_scene  - Spawn lighting, ground, objects")
    print(f"  POST /capture      - Position camera and take screenshot")
    print(f"  POST /full_capture - Complete workflow (scene + captures)")
    print(f"  POST /cleanup      - Remove all spawned actors")
    print()
    print("Test: curl http://localhost:8080/status")
    print("=" * 70)


def stop_server():
    """Stop the HTTP server"""
    global http_server, server_thread, timer_handle

    if timer_handle:
        try:
            unreal.unregister_slate_post_tick_callback(timer_handle)
        except:
            pass
        timer_handle = None

    if http_server is not None:
        try:
            http_server.shutdown()
        except:
            pass
        http_server = None
        server_thread = None

    cleanup_scene()
    print("Server stopped")


def restart_server():
    """Restart the HTTP server"""
    print("Restarting server...")
    stop_server()
    time.sleep(1)  # Wait for port to be released
    start_server()


def is_port_in_use(port):
    """Check if a port is already in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


# Auto-start when script is run
if __name__ == "__main__":
    # Check if server is already running
    if is_port_in_use(SERVER_PORT):
        print(f"Port {SERVER_PORT} already in use.")
        print("Server may already be running. Use restart_server() to restart.")
        print("Or run: stop_server() then start_server()")
    else:
        start_server()
