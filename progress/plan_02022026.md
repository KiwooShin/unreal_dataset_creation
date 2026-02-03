# Progress Report: February 2, 2026

## Summary
Investigated and fixed the color/material issue in Unreal Engine dataset creation. Created a custom base material (`M_ColorBase`) that allows dynamic color assignment to spawned objects.

## Completed Tasks

### 1. Color Issue Investigation
- Identified root cause: `create_colored_material()` was trying to load pre-made materials that didn't exist
- The function returned `None` when materials weren't found, causing objects to use default gray color

### 2. Dynamic Material Instance Implementation
- Updated `create_colored_material()` in `unreal_api_server_v2.py` to:
  - Load a base material with exposed color parameter
  - Create `MaterialInstanceDynamic` at runtime
  - Set color via `set_vector_parameter_value("BaseColor", color)`

### 3. Created M_ColorBase Material in Unreal
Created a custom base material that exposes a color parameter for dynamic modification.

**Steps to create M_ColorBase:**
1. Open Unreal Editor
2. Go to **Content Browser** (Window → Content Browser or Ctrl+Space)
3. Navigate to or create `Content/Materials/` folder
4. Right-click → **Material** → name it `M_ColorBase`
5. Double-click to open Material Editor
6. Right-click in graph → search **"Vector Parameter"** → add it
7. In Details panel, set **Parameter Name** to `BaseColor`
8. **Connect** the Vector Parameter output to **Base Color** input on main material node
9. Click **Apply** and **Save**

### 4. Screenshot Testing
- Captured test images with different colors (blue, red)
- Images saved to `results/02022026/`

## Current File Structure

```
unreal_dataset_creation/
├── plans/
│   ├── plan_01312026.md
│   ├── plan_02012026.md
│   └── plan_02022026.md    # This file
├── results/
│   ├── 02022026/
│   │   ├── sphere_front.png
│   │   ├── sphere_top.png
│   │   └── sphere_diagonal.png
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
OBJECT_COLOR = "red"  # Now working with M_ColorBase!
```

**unreal_api_server_v2.py - create_colored_material():**
- Loads `/Game/Materials/M_ColorBase`
- Creates dynamic material instance
- Sets color via `set_vector_parameter_value("BaseColor", linear_color)`
- Supported colors: yellow, red, blue, green, white, gray, orange

## Key Learning: Unreal Material System

To dynamically change object colors in Unreal Engine via Python:

1. **Cannot set colors directly** on basic shape materials - they have no exposed parameters
2. **Must create a base material** with a Vector Parameter for color
3. **Create MaterialInstanceDynamic** from the base material at runtime
4. **Set the parameter value** using `set_vector_parameter_value()`

## Next Steps
- Test all colors work correctly
- Proceed with extensive dataset generation (see plan_01312026.md)
- Generate 10+ images with varying objects, colors, and camera angles
