#!/usr/bin/env python
"""
Step 2: Take 3 screenshots from different angles
"""

import requests
import os
import time

API_URL = "http://localhost:8080"
OUTPUT_DIR = "/Users/kiwooshin/work/unreal_dataset_creation/dataset_output"

CUBE_POSITION = [50, -500, 100]

CAMERA_CONFIGS = [
    {"name": "front", "position": [550, -500, 100], "filename": "cube_front.png"},
    {"name": "top", "position": [50, -500, 600], "filename": "cube_top.png"},
    {"name": "diagonal", "position": [300, -250, 454], "filename": "cube_diagonal.png"},
]

def take_screenshot(camera_config):
    """Take a single screenshot with given camera config"""
    capture_config = {
        "name": camera_config["name"],
        "camera": {
            "position": camera_config["position"],
            "look_at": CUBE_POSITION,
            "fov": 90.0
        },
        "output": {
            "filename": camera_config["filename"],
            "resolution": [640, 640]
        },
        "save_metadata": False
    }

    response = requests.post(f"{API_URL}/capture", json=capture_config, timeout=120)
    result = response.json()

    if result.get('status') == 'success':
        image_path = result.get('image_path', '')
        print(f"    Server returned success")

        # Wait for file
        max_wait = 60
        start = time.time()
        while time.time() - start < max_wait:
            if os.path.exists(image_path) and os.path.getsize(image_path) > 10000:
                size_kb = os.path.getsize(image_path) / 1024
                print(f"    File saved: {size_kb:.1f} KB")
                return True
            time.sleep(1)
        print("    WARNING: File not found after waiting")
        return False
    else:
        print(f"    ERROR: {result.get('error', 'Unknown')}")
        return False

def main():
    print("=" * 60)
    print("STEP 2: Take 3 Screenshots from Different Angles")
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
        return

    print(f"\nCube center: {CUBE_POSITION}")
    print(f"Taking {len(CAMERA_CONFIGS)} screenshots...\n")

    results = []
    for i, config in enumerate(CAMERA_CONFIGS, 1):
        print(f"[{i}/{len(CAMERA_CONFIGS)}] {config['name'].upper()} view")
        print(f"    Position: {config['position']}")
        print(f"    Filename: {config['filename']}")
        success = take_screenshot(config)
        results.append((config['filename'], success))
        print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for filename, success in results:
        status = "OK" if success else "FAILED"
        print(f"  [{status}] {OUTPUT_DIR}/{filename}")
    print("=" * 60)

if __name__ == "__main__":
    main()
