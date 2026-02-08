# Unreal Engine Dataset Creator

Python-based tool for generating synthetic image datasets from Unreal Engine 5 scenes via HTTP API.

## Overview

This tool allows you to:
- Control Unreal Engine scenes via HTTP API
- Set up complex scenes with floors, walls, and objects
- Apply materials (textures) or solid colors to meshes
- Capture screenshots from multiple camera angles
- Generate datasets for machine learning and computer vision

## Requirements

- Unreal Engine 5.6+
- Python 3.x
- StarterContent (for architecture meshes and materials)

## Project Structure

```
unreal_dataset_creation/
├── assets/                    # Scene configuration files
│   ├── simple_house.json      # Basic house with solid colors
│   └── house_with_materials.json  # House with textures
├── dataset_output/            # Temporary output (moved to results/)
├── plan/                      # Daily planning documents
├── progress/                  # Daily progress reports
├── results/                   # Organized output by date
│   └── MMDDYYYY/             # Screenshots for each session
├── skills/                    # Automation scripts
├── unreal_api_server_v2.py   # HTTP API server (runs in Unreal)
├── step1_setup_scene.py      # Scene setup script
├── step2_take_screenshot.py  # Screenshot capture script
├── get_cube_location.py      # Utility: get object position
└── get_viewport_camera.py    # Utility: get camera position
```

## Setup

### 1. Create Unreal Project with StarterContent

1. Open Unreal Engine 5.6+
2. Create a new **Blank** project
3. Add StarterContent: Content Browser > Add > Add Feature or Content Pack > Starter Content
4. Add basic lighting to the level (Directional Light + Sky Light)

### 2. Enable Python in Unreal

1. Go to **Edit > Plugins**
2. Search for "Python"
3. Enable **Python Editor Script Plugin**
4. Restart Unreal Editor

### 3. Open Python Console

1. Go to **Window > Developer Tools > Output Log**
2. At the bottom, change dropdown from "Cmd" to "Python"

## Usage

### Step 1: Start the API Server

In Unreal's Python console:

```python
exec(open('/Users/kiwooshin/work/unreal_dataset_creation/unreal_api_server_v2.py').read())
```

You should see: `UNREAL ENGINE API SERVER v2 STARTED`

### Step 2: Setup the Scene

In your terminal:

```bash
cd /Users/kiwooshin/work/unreal_dataset_creation
python step1_setup_scene.py
```

This spawns the scene defined in `assets/house_with_materials.json`:
- Ground plane
- Floor with wood texture
- 3 walls with brick/concrete textures

### Step 3: Capture Screenshots

```bash
python step2_take_screenshot.py
```

Captures 3 screenshots:
- `multi_front.png` - Front view
- `multi_top.png` - Top-down view
- `multi_diagonal.png` - Diagonal view

Output saved to `dataset_output/` directory.

## Scene Configuration

Scene configurations are JSON files in the `assets/` folder.

### Example: House with Materials

```json
{
    "name": "house_with_materials",
    "objects": [
        {
            "type": "floor",
            "mesh": "/Game/StarterContent/Architecture/Floor_400x400",
            "position": [50, -500, 20],
            "scale": [3.0, 4.0, 1.0],
            "material": "/Game/StarterContent/Materials/M_Wood_Floor_Walnut_Polished"
        },
        {
            "type": "wall",
            "mesh": "/Game/StarterContent/Architecture/Wall_400x300",
            "position": [50, -500, 20],
            "scale": [3.0, 1.0, 1.0],
            "material": "/Game/StarterContent/Materials/M_Brick_Clay_New"
        }
    ],
    "camera": {
        "target": [50, 300, 100],
        "position": [1500, 300, 800]
    }
}
```

### Object Properties

| Property | Description | Example |
|----------|-------------|---------|
| `type` | Object identifier | `"floor"`, `"wall"` |
| `mesh` | Unreal mesh asset path | `"/Game/StarterContent/Architecture/Floor_400x400"` |
| `position` | [X, Y, Z] coordinates | `[50, -500, 20]` |
| `rotation` | [Pitch, Yaw, Roll] | `[0, 0, -90]` |
| `scale` | [X, Y, Z] scale factors | `[3.0, 4.0, 1.0]` |
| `material` | Material asset path (optional) | `"/Game/StarterContent/Materials/M_Wood_Floor_Walnut_Polished"` |
| `color` | Solid color fallback (optional) | `"blue"`, `"red"`, `"white"` |

### Available Colors

`yellow`, `red`, `blue`, `green`, `white`, `gray`, `orange`

### Available StarterContent Materials

**Floor:**
- `M_Wood_Floor_Walnut_Polished`
- `M_Wood_Floor_Walnut_Worn`
- `M_Concrete_Tiles`
- `M_CobbleStone_Rough`

**Wall:**
- `M_Brick_Clay_New`
- `M_Brick_Clay_Old`
- `M_Concrete_Poured`
- `M_Basic_Wall`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | Check server status |
| `/setup_scene` | POST | Set up scene with objects |
| `/capture` | POST | Capture screenshot |
| `/full_capture` | POST | Setup + capture in one call |
| `/cleanup` | POST | Remove spawned objects |

### Capture Request

```json
{
    "camera": {
        "position": [1500, 300, 400],
        "look_at": [50, 300, 100],
        "fov": 90.0
    },
    "output": {
        "filename": "screenshot.png",
        "resolution": [640, 640]
    }
}
```

## Server Management

In Unreal Python console:

```python
# Stop server
stop_server()

# Restart server (reload code changes)
stop_server()
exec(open('/path/to/unreal_api_server_v2.py').read())

# Check server status
# curl http://localhost:8080/status
```

## Troubleshooting

### "Cannot connect to API server"
- Ensure server is running in Unreal Python console
- Check port 8080 is not blocked

### Materials not applying
- Reload server after code changes: `stop_server()` then re-run `exec()`
- Verify materials exist: run material check in Unreal Python console
- Check Output Log for "Applied material to X slot(s)" messages

### Black screenshots
- Add lighting to your Unreal level
- Ensure objects are within camera view

### Objects not visible
- Adjust camera position farther back
- Check object positions in scene config

## Workflow

1. **Plan**: Create/edit scene config in `assets/`
2. **Setup**: Run `step1_setup_scene.py`
3. **Verify**: Check Unreal viewport
4. **Capture**: Run `step2_take_screenshot.py`
5. **Wrap up**: Use `/wrap_up` to organize outputs and commit

## License

MIT
