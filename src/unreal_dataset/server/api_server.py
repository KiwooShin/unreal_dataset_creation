"""
HTTP API server for Unreal Engine.

This server runs inside the Unreal Editor Python console and provides
HTTP endpoints for controlling the scene and capturing screenshots.
"""

import json
import queue
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from unreal_dataset.server import handlers
from unreal_dataset.server.scene_manager import get_scene_manager

# Try to import unreal
try:
    import unreal
    HAS_UNREAL = True
except ImportError:
    HAS_UNREAL = False
    unreal = None


# Server configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8080
DEFAULT_OUTPUT_DIR = Path.cwd() / "dataset_output"

# Server state
_http_server: Optional[HTTPServer] = None
_server_thread: Optional[threading.Thread] = None
_timer_handle: Optional[Any] = None
_request_queue: queue.Queue = queue.Queue()
_response_dict: Dict[str, Any] = {}


class UnrealAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler."""

    def _set_headers(self, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def _send_json(self, data: Dict[str, Any], status: int = 200) -> None:
        self._set_headers(status)
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _enqueue_request(self, request_type: str, data: Any = None) -> Dict[str, Any]:
        """Enqueue request for main thread processing."""
        request_id = str(uuid.uuid4())

        _request_queue.put({
            "id": request_id,
            "type": request_type,
            "data": data,
        })

        # Wait for response
        timeout = 120
        start_time = time.time()

        while request_id not in _response_dict:
            time.sleep(0.1)
            if time.time() - start_time > timeout:
                return {"status": "error", "error": "Request timeout"}

        return _response_dict.pop(request_id)

    def do_GET(self) -> None:
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/":
            self._send_json({
                "status": "running",
                "message": "Unreal Dataset API Server",
                "endpoints": [
                    "GET  /status",
                    "GET  /get_scene_objects",
                    "POST /setup_scene",
                    "POST /capture",
                    "POST /cleanup",
                ],
            })
        elif parsed_path.path == "/status":
            response = self._enqueue_request("status")
            self._send_json(response)
        elif parsed_path.path == "/get_scene_objects":
            response = self._enqueue_request("get_scene_objects")
            self._send_json(response)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self) -> None:
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))

        if content_length > 0:
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode("utf-8"))
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
                return
        else:
            data = {}

        endpoint_map = {
            "/setup_scene": "setup_scene",
            "/capture": "capture",
            "/cleanup": "cleanup",
        }

        if parsed_path.path in endpoint_map:
            response = self._enqueue_request(endpoint_map[parsed_path.path], data)
            self._send_json(response)
        else:
            self._send_json({"error": "Not found"}, 404)

    def log_message(self, format: str, *args) -> None:
        pass  # Suppress logging


def process_request_queue(delta_time: float) -> None:
    """Process requests from queue on main thread."""
    try:
        while not _request_queue.empty():
            try:
                request = _request_queue.get_nowait()
                request_id = request["id"]
                request_type = request["type"]
                request_data = request.get("data")

                handler_map = {
                    "status": lambda: handlers.handle_status(),
                    "setup_scene": lambda: handlers.handle_setup_scene(request_data),
                    "capture": lambda: handlers.handle_capture(request_data),
                    "get_scene_objects": lambda: handlers.handle_get_scene_objects(),
                    "cleanup": lambda: handlers.handle_cleanup(),
                }

                if request_type in handler_map:
                    response = handler_map[request_type]()
                else:
                    response = {"status": "error", "error": f"Unknown: {request_type}"}

                _response_dict[request_id] = response

            except queue.Empty:
                break
            except Exception as e:
                if HAS_UNREAL:
                    unreal.log_error(f"Error processing request: {e}")

    except Exception as e:
        if HAS_UNREAL:
            unreal.log_error(f"Error in queue processor: {e}")


def start_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> None:
    """
    Start the HTTP server.

    Args:
        host: Server host
        port: Server port
        output_dir: Directory for output files
    """
    global _http_server, _server_thread, _timer_handle

    if _http_server is not None:
        if HAS_UNREAL:
            unreal.log_warning("Server already running")
        return

    # Set up output directory
    handlers.set_output_dir(output_dir)

    # Start HTTP server
    _http_server = HTTPServer((host, port), UnrealAPIHandler)
    _server_thread = threading.Thread(target=_http_server.serve_forever)
    _server_thread.daemon = True
    _server_thread.start()

    # Start queue processor (Unreal main thread callback)
    if HAS_UNREAL:
        _timer_handle = unreal.register_slate_post_tick_callback(process_request_queue)

    print("=" * 70)
    print("UNREAL DATASET API SERVER STARTED")
    print("=" * 70)
    print(f"Server: http://{host}:{port}")
    print(f"Output: {output_dir}")
    print()
    print("Endpoints:")
    print("  GET  /status            - Check server status")
    print("  GET  /get_scene_objects - Get all objects with bounds/transforms")
    print("  POST /setup_scene       - Spawn lighting, ground, objects")
    print("  POST /capture           - Position camera and take screenshot")
    print("  POST /cleanup           - Remove all spawned actors")
    print()
    print(f"Test: curl http://{host}:{port}/status")
    print("=" * 70)


def stop_server() -> None:
    """Stop the HTTP server."""
    global _http_server, _server_thread, _timer_handle

    if _timer_handle and HAS_UNREAL:
        try:
            unreal.unregister_slate_post_tick_callback(_timer_handle)
        except Exception:
            pass
        _timer_handle = None

    if _http_server is not None:
        try:
            _http_server.shutdown()
        except Exception:
            pass
        _http_server = None
        _server_thread = None

    get_scene_manager().cleanup()
    print("Server stopped")


def restart_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> None:
    """Restart the HTTP server."""
    print("Restarting server...")
    stop_server()
    time.sleep(1)
    start_server(host, port, output_dir)


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0
