"""
Simple loader script for starting the API server in Unreal Editor.

Usage in Unreal Python console:
    exec(open('/path/to/unreal_dataset_creation/scripts/start_server.py').read())

Or with custom settings:
    exec(open('/path/to/scripts/start_server.py').read())
    start_server(port=9000)
"""

import sys
from pathlib import Path

# Add the src directory to Python path
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
SRC_DIR = PROJECT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import server functions
from unreal_dataset.server import start_server, stop_server, restart_server, is_port_in_use

# Default configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8080
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "dataset_output"


def main():
    """Start the server with default configuration."""
    if is_port_in_use(DEFAULT_PORT):
        print(f"Port {DEFAULT_PORT} already in use.")
        print("Server may already be running. Use restart_server() to restart.")
        print("Or run: stop_server() then start_server()")
    else:
        start_server(
            host=DEFAULT_HOST,
            port=DEFAULT_PORT,
            output_dir=DEFAULT_OUTPUT_DIR,
        )


# Auto-start when script is executed
if __name__ == "__main__":
    main()
else:
    # When exec() is used, __name__ is not "__main__"
    # Still auto-start in this case
    main()
