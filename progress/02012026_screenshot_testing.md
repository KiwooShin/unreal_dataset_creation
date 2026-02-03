# Progress Report: February 1, 2026

## Summary
Resumed Unreal Engine dataset creation work. Tested screenshot capture with different objects, colors, and camera angles. Cleaned up codebase and pushed to GitHub.

## Completed Tasks

### 1. Screenshot Capture Testing
- Ran step1 (scene setup) and step2 (screenshot capture)
- Captured 3 photos from different angles:
  - Front view
  - Top view
  - Diagonal view (45°/45° spherical)
- Used `look_at` feature for automatic camera rotation

### 2. Camera Position Calculation
- Fixed mismatch between step1 and step2 cube/object positions
- Synced OBJECT_POSITION to `[50, -500, 100]`
- Camera positions calculated relative to object center

### 3. Object Variations Tested
- Changed object type: cube → sphere
- Changed color: yellow → green
- Mesh path: `/Engine/BasicShapes/Sphere`

### 4. Image Settings
- Resolution changed: 640x640 → 128x128 (for faster testing)

### 5. Codebase Cleanup
- Reduced from ~70 files to 7 core files
- Removed old server versions, test scripts, outdated docs
- Renamed folder: `unreal` → `unreal_dataset_creation`
- Updated all hardcoded paths in scripts

### 6. GitHub Repository
- Pushed to: https://github.com/KiwooShin/unreal_dataset_creation
- Created `plans/` folder for documentation
- Created `results/` folder for outputs
- Updated README with practical setup guide

### 7. Code Improvements
- step1: Uses configurable OBJECT_TYPE, OBJECT_MESH, OBJECT_COLOR
- step2: Uses OBJECT_POSITION with look_at
- Dynamic labels: `{color}{type}` (e.g., "GreenSphere")

## Current File Structure

```
unreal_dataset_creation/
├── plans/
│   ├── plan_01312026.md    # Future dataset generation plan
│   └── plan_02012026.md    # This file
├── results/
├── README.md
├── requirements.txt
├── unreal_api_server_v2.py
├── step1_setup_scene.py
├── step2_take_screenshot.py
├── get_cube_location.py
└── get_viewport_camera.py
```

## Current Configuration

**step1_setup_scene.py:**
```python
OBJECT_TYPE = "sphere"
OBJECT_MESH = "/Engine/BasicShapes/Sphere"
OBJECT_POSITION = [50, -500, 100]
OBJECT_SCALE = [2, 2, 2]
OBJECT_COLOR = "green"
```

**step2_take_screenshot.py:**
```python
OBJECT_POSITION = [50, -500, 100]
resolution = [128, 128]
```

## Next Steps
See `plan_01312026.md` for the comprehensive dataset generation plan:
- Generate 10+ images with varying objects, colors, angles
- Multiple object types (cube, sphere, cylinder, cone)
- Camera orbiting using spherical coordinates
- Metadata JSON for each image
