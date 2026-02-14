"""
Command-line interface for Unreal Dataset.

Usage:
    unreal-dataset setup --config assets/house.json
    unreal-dataset capture --output ./results
    unreal-dataset status
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from unreal_dataset import __version__
from unreal_dataset.config import get_settings
from unreal_dataset.utils import setup_logging


def cmd_setup(args: argparse.Namespace) -> int:
    """Handle the setup command."""
    from unreal_dataset.client.scene_setup import main as setup_main

    config_path = args.config
    if config_path is None:
        settings = get_settings()
        config_path = settings.assets_dir / "house_with_materials.json"

    try:
        setup_main(config_path=str(config_path))
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_capture(args: argparse.Namespace) -> int:
    """Handle the capture command."""
    from unreal_dataset.client.capture import main as capture_main

    # Parse camera positions if provided
    camera_positions = None
    if args.cameras:
        camera_positions = []
        for name in args.cameras.split(","):
            name = name.strip()
            # Default positions for common names
            positions = {
                "front": [1500, 300, 400],
                "top": [50, 300, 2000],
                "diagonal": [1200, -400, 800],
                "side": [50, 1500, 400],
                "back": [-1000, 300, 400],
            }
            if name in positions:
                camera_positions.append({"name": name, "position": positions[name]})
            else:
                print(f"Warning: Unknown camera position '{name}', skipping")

    # Parse scene center
    scene_center = None
    if args.center:
        try:
            scene_center = [float(x) for x in args.center.split(",")]
            if len(scene_center) != 3:
                raise ValueError("Center must have 3 values")
        except ValueError as e:
            print(f"Error parsing center: {e}")
            return 1

    try:
        capture_main(
            scene_name=args.scene or "scene",
            scene_center=scene_center,
            camera_positions=camera_positions,
        )
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_status(args: argparse.Namespace) -> int:
    """Handle the status command."""
    from unreal_dataset.client.api_client import UnrealAPIClient
    from unreal_dataset.utils.exceptions import ConnectionError

    try:
        with UnrealAPIClient() as client:
            status = client.get_status()

            print("Server Status")
            print("=" * 40)
            print(f"Status: {status.get('status', 'unknown')}")
            print(f"Version: {status.get('version', 'unknown')}")
            print(f"Unreal: {status.get('unreal_version', 'unknown')}")
            print(f"Output: {status.get('output_dir', 'unknown')}")
            print(f"Actors: {status.get('active_actors', 0)}")
            return 0

    except ConnectionError as e:
        print(f"Cannot connect to server: {e}")
        print("\nMake sure the Unreal API server is running.")
        print("In Unreal Editor Python console, run:")
        print("  exec(open('scripts/start_server.py').read())")
        return 1


def cmd_cleanup(args: argparse.Namespace) -> int:
    """Handle the cleanup command."""
    from unreal_dataset.client.api_client import UnrealAPIClient
    from unreal_dataset.utils.exceptions import ConnectionError

    try:
        with UnrealAPIClient() as client:
            client.cleanup()
            print("Scene cleaned up")
            return 0
    except ConnectionError as e:
        print(f"Cannot connect to server: {e}")
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="unreal-dataset",
        description="Synthetic 3D object detection dataset generation from Unreal Engine",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        required=True,
    )

    # Setup command
    setup_parser = subparsers.add_parser(
        "setup",
        help="Set up the scene from a configuration file",
    )
    setup_parser.add_argument(
        "-c", "--config",
        type=Path,
        help="Path to scene configuration JSON file",
    )
    setup_parser.set_defaults(func=cmd_setup)

    # Capture command
    capture_parser = subparsers.add_parser(
        "capture",
        help="Capture screenshots with 3D detection labels",
    )
    capture_parser.add_argument(
        "-s", "--scene",
        help="Scene name for labels",
    )
    capture_parser.add_argument(
        "--cameras",
        help="Comma-separated camera names (front,top,diagonal)",
    )
    capture_parser.add_argument(
        "--center",
        help="Scene center as X,Y,Z (e.g., 50,300,100)",
    )
    capture_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output directory",
    )
    capture_parser.set_defaults(func=cmd_capture)

    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Check server status",
    )
    status_parser.set_defaults(func=cmd_status)

    # Cleanup command
    cleanup_parser = subparsers.add_parser(
        "cleanup",
        help="Remove all spawned actors",
    )
    cleanup_parser.set_defaults(func=cmd_cleanup)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level)

    # Run the command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
