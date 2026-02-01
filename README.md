# Unreal Engine Dataset Creator

Python-based tool for capturing multi-angle screenshots from Unreal Engine 5 via HTTP API.

## Overview

This tool allows you to:
- Control Unreal Engine scenes via HTTP API
- Set up objects (cubes) with configurable positions and colors
- Capture screenshots from multiple camera angles (front, top, diagonal)
- Use `look_at` to automatically point camera at objects

## Requirements

- Unreal Engine 5.6+
- Python 3.x (for running client scripts)

## Files

| File | Description |
|------|-------------|
| `unreal_api_server_v2.py` | HTTP API server (runs inside Unreal) |
| `step1_setup_scene.py` | Sets up scene with cube and ground |
| `step2_take_screenshot.py` | Captures screenshots from 3 angles |
| `get_cube_location.py` | Utility: get current cube position |
| `get_viewport_camera.py` | Utility: get current camera position |

## Setup

### 1. Create Unreal Project

1. Open Unreal Engine 5.6+
2. Create a new **Blank** project
3. Add basic lighting to the level:
   - Directional Light (for sun)
   - Sky Light (for ambient)
   - Sky Atmosphere (optional, for sky)

### 2. Enable Python in Unreal

1. Go to **Edit > Plugins**
2. Search for "Python"
3. Enable **Python Editor Script Plugin**
4. Restart Unreal Editor

### 3. Open Python Console

1. Go to **Window > Developer Tools > Output Log**
2. At the bottom, there's a command input field
3. Change dropdown from "Cmd" to "Python"

## Usage

### Step 1: Start the API Server

In Unreal's Python console, run:

```python
exec(open('/Users/kiwooshin/work/unreal_dataset_creation/unreal_api_server_v2.py').read())
```

You should see: `API server started on port 8080`

### Step 2: Setup the Scene

In your terminal, run:

```bash
cd /Users/kiwooshin/work/unreal_dataset_creation
python step1_setup_scene.py
```

This spawns:
- A ground plane
- A yellow cube at position `[0, 0, 100]`

### Step 3: Capture Screenshots

In your terminal, run:

```bash
python step2_take_screenshot.py
```

This captures 3 screenshots from different angles:
- `cube_front.png` - Front view
- `cube_top.png` - Top-down view
- `cube_diagonal.png` - 45° diagonal view

Output is saved to `dataset_output/` directory.

## Utility Scripts

### Get Cube Location

If you manually move the cube in Unreal, get its new position:

```python
exec(open('/Users/kiwooshin/work/unreal_dataset_creation/get_cube_location.py').read())
```

### Get Viewport Camera

Get current viewport camera position and rotation:

```python
exec(open('/Users/kiwooshin/work/unreal_dataset_creation/get_viewport_camera.py').read())
```

## Configuration

### Modifying Camera Positions

Edit `step2_take_screenshot.py`:

```python
CUBE_POSITION = [50, -500, 100]  # Look-at target

CAMERA_CONFIGS = [
    {"name": "front", "position": [550, -500, 100], "filename": "cube_front.png"},
    {"name": "top", "position": [50, -500, 600], "filename": "cube_top.png"},
    {"name": "diagonal", "position": [300, -250, 454], "filename": "cube_diagonal.png"},
]
```

### Modifying Scene Setup

Edit `step1_setup_scene.py`:

```python
CUBE_POSITION = [0, 0, 100]
CUBE_SCALE = [2, 2, 2]
CUBE_COLOR = "yellow"
```

## API Endpoints

The server exposes these HTTP endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | Check server status |
| `/setup_scene` | POST | Set up scene with objects |
| `/capture` | POST | Capture screenshot |
| `/cleanup` | POST | Remove spawned objects |

### Capture with look_at

```python
{
    "camera": {
        "position": [500, 0, 100],
        "look_at": [0, 0, 100],  # Auto-calculates rotation
        "fov": 90.0
    },
    "output": {
        "filename": "screenshot.png",
        "resolution": [640, 640]
    }
}
```

## Troubleshooting

### "Cannot connect to API server"
- Make sure you ran the server in Unreal's Python console
- Check that port 8080 is not blocked

### Black screenshots
- Add lighting to your Unreal level (Directional Light + Sky Light)
- Ensure the cube is within camera view

### Cube not centered in frame
- Run `get_cube_location.py` to get actual cube position
- Update `CUBE_POSITION` in `step2_take_screenshot.py`

## License

MIT
