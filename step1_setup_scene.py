#!/usr/bin/env python
"""
Step 1: Setup scene and position camera
Run this first to verify the object is visible in the viewport.
"""

import requests
import json
import os

API_URL = "http://localhost:8080"

# Load scene configuration from JSON file
ASSET_FILE = os.path.join(os.path.dirname(__file__), "assets/house_with_materials.json")

with open(ASSET_FILE, 'r') as f:
    config = json.load(f)

OBJECTS = config["objects"]
CAMERA_TARGET = config["camera"]["target"]
CAMERA_POSITION = config["camera"]["position"]

def main():
    print("=" * 60)
    print("STEP 1: Setup Scene and Position Camera")
    print(f"Config: {config.get('name', 'unknown')}")
    print("=" * 60)

    # Check connection
    try:
        response = requests.get(f"{API_URL}/status", timeout=5)
        if response.status_code != 200:
            print("ERROR: Cannot connect to API server")
            return
        print("Connected to API server")
    except:
        print("ERROR: API server not running")
        print("Run in Unreal: exec(open('/Users/kiwooshin/work/unreal_dataset_creation/unreal_api_server_v2.py').read())")
        return

    # Setup scene (spawn objects)
    print(f"\nSetting up scene with {len(OBJECTS)} objects...")
    scene_config = {
        "cleanup_before": True,
        "objects": [
            {
                "type": obj["type"],
                "mesh": obj["mesh"],
                "position": obj["position"],
                "rotation": obj.get("rotation", [0, 0, 0]),
                "scale": obj["scale"],
                "color": obj.get("color"),
                "material": obj.get("material"),  # Pass material path if specified
                "label": obj.get("label", f"{obj.get('type', 'object').capitalize()}")
            }
            for obj in OBJECTS
        ]
    }

    response = requests.post(f"{API_URL}/setup_scene", json=scene_config, timeout=30)
    result = response.json()

    if result.get('status') == 'success':
        print(f"  {result.get('message')}")
    else:
        print(f"  ERROR: {result.get('error')}")
        return

    # Position camera
    print("\nPositioning camera...")
    print(f"  Position: {CAMERA_POSITION}")
    print(f"  Looking at: {CAMERA_TARGET}")

    # Use the capture endpoint but without actually saving - just to position camera
    capture_config = {
        "name": "position_only",
        "camera": {
            "position": CAMERA_POSITION,
            "look_at": CAMERA_TARGET,
            "fov": 90.0
        },
        "output": {
            "filename": "temp_test.png",
            "resolution": [640, 640]
        },
        "position_only": True  # Flag to only position camera, not take screenshot
    }

    response = requests.post(f"{API_URL}/capture", json=capture_config, timeout=30)
    result = response.json()
    print(f"  Camera positioned")

    print("\n" + "=" * 60)
    print("DONE - Check the Unreal viewport!")
    for obj in OBJECTS:
        material_info = obj.get('material', obj.get('color', 'default'))
        print(f"  - {obj['type']} with {material_info} at {obj['position']}")
    print("=" * 60)
    print(f"\nIf you can see all {len(OBJECTS)} objects, run step2_take_screenshot.py to capture images.")

if __name__ == "__main__":
    main()
