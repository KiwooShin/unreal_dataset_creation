# Plan: Extensive Dataset Generation Testing

**Date:** January 31, 2026
**Status:** Ready for implementation

## Goal
Create a comprehensive test script that captures many photos with varying:
- Camera positions and angles (orbiting around objects)
- Object properties (color, size, surface/material)
- Multiple object types (cube, sphere, cylinder, cone)
- Multiple objects in a single scene

## Current Capabilities (from exploration)

| Feature | Status | Details |
|---------|--------|---------|
| Colors | Supported | yellow, red, blue, green, white, gray, orange |
| Scale | Supported | [x, y, z] scaling |
| Meshes | Supported | Any path, e.g., `/Engine/BasicShapes/Cube` |
| Multiple objects | Supported | Via `objects` array in setup_scene |
| Camera look_at | Supported | Auto-calculates rotation |
| Materials | Limited | Attempts to load from /Game/Materials/ |

## Available Basic Shapes in Unreal

```
/Engine/BasicShapes/Cube
/Engine/BasicShapes/Sphere
/Engine/BasicShapes/Cylinder
/Engine/BasicShapes/Cone
/Engine/BasicShapes/Plane
```

## New Script: `generate_dataset.py`

### Features

1. **Configurable parameters at top of file:**
   - Number of images to generate
   - Object types to include
   - Colors to use
   - Scale ranges
   - Camera distance and angle ranges

2. **Camera orbiting:**
   - Generate positions around object using spherical coordinates
   - Vary elevation angle (0° to 80°)
   - Vary horizontal angle (0° to 360°)
   - Consistent distance from object center

3. **Object variations:**
   - Randomize color from available colors
   - Randomize scale within range
   - Randomize object type (cube, sphere, cylinder, cone)

4. **Multi-object scenes:**
   - Option to spawn 1-N objects per scene
   - Random positions within bounds
   - Each object with random properties

5. **Output organization:**
   - Sequential filenames: `img_0001.png`, `img_0002.png`, ...
   - Metadata JSON for each image with object/camera info
   - Summary JSON with generation parameters

### Configuration Structure

```python
CONFIG = {
    "num_images": 10,  # Start with 10 for testing
    "output_dir": "dataset_output",
    "save_metadata": True,  # Save JSON for each image

    # Object settings
    "object_types": ["cube", "sphere", "cylinder", "cone"],
    "colors": ["yellow", "red", "blue", "green", "white", "orange"],
    "scale_range": [1.0, 3.0],
    "objects_per_scene": [1, 3],  # min, max

    # Camera settings
    "camera_distance": 500,
    "elevation_range": [10, 70],  # degrees
    "horizontal_angles": 8,  # number of angles around object

    # Image settings
    "resolution": [640, 640],
    "fov": 90.0,
}
```

### Camera Position Calculation

```python
def calculate_camera_position(target, distance, elevation_deg, azimuth_deg):
    """
    Calculate camera position using spherical coordinates.
    - elevation: angle above horizontal (0=side, 90=top)
    - azimuth: angle around vertical axis (0-360)
    """
    elev_rad = math.radians(elevation_deg)
    azim_rad = math.radians(azimuth_deg)

    x = target[0] + distance * math.cos(elev_rad) * math.cos(azim_rad)
    y = target[1] + distance * math.cos(elev_rad) * math.sin(azim_rad)
    z = target[2] + distance * math.sin(elev_rad)

    return [x, y, z]
```

## Implementation Steps

1. Create `generate_dataset.py` with CONFIG at top
2. Add helper functions for:
   - Camera position calculation (spherical coords)
   - Random object generation
   - Metadata saving
3. Main loop:
   - For each image: setup scene → position camera → capture → save metadata
4. Test with small dataset (10 images)
5. Scale up to larger dataset

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `generate_dataset.py` | Create | Main dataset generation script |
| `README.md` | Update | Document new script |

## Verification

1. Run with `num_images: 10` first
2. Check all images captured correctly
3. Verify metadata JSON files created
4. Check variety in colors, shapes, angles
5. Scale up to 100+ images

---

## How to Resume This Plan

To continue implementing this plan, tell Claude:

```
Read the plan at /Users/kiwooshin/work/unreal_dataset_creation/plan_01312026.md and implement it.
```
