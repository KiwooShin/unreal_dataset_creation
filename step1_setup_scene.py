#!/usr/bin/env python
"""
Step 1: Setup scene and position camera
Run this first to verify the cube is visible in the viewport.
"""

import requests
import json

API_URL = "http://localhost:8080"

# Scene configuration
CUBE_POSITION = [0, 0, 100]
CUBE_SCALE = [2, 2, 2]
CUBE_COLOR = "yellow"

# Camera position - we'll get working values from user
CAMERA_POSITION = [259.01, 130.09, 713.33]
CAMERA_ROTATION = [-90.0, -120.59, -7.14]  # [Pitch, Yaw, Roll]

def main():
    print("=" * 60)
    print("STEP 1: Setup Scene and Position Camera")
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

    # Setup scene (spawn ground and cube, no lighting)
    print("\nSetting up scene...")
    scene_config = {
        "cleanup_before": True,
        # "add_ground": False,
        # "ground": {
        #     "position": [0, 0, 0],
        #     "scale": [50, 50, 1],
        #     "color": "gray"
        # },
        "objects": [
            {
                "type": "cube",
                "mesh": "/Engine/BasicShapes/Cube",
                "position": CUBE_POSITION,
                "rotation": [0, 0, 0],
                "scale": CUBE_SCALE,
                "color": CUBE_COLOR,
                "label": "YellowCube"
            }
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
    print(f"  Rotation: Pitch={CAMERA_ROTATION[0]}, Yaw={CAMERA_ROTATION[1]}, Roll={CAMERA_ROTATION[2]}")

    # Use the capture endpoint but without actually saving - just to position camera
    capture_config = {
        "name": "position_only",
        "camera": {
            "position": CAMERA_POSITION,
            "rotation": CAMERA_ROTATION,
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
    print("Can you see the yellow cube?")
    print("=" * 60)
    print("\nIf you can see the cube, run get_viewport_camera.py")
    print("to capture the exact camera values, then we'll take screenshots.")

if __name__ == "__main__":
    main()
