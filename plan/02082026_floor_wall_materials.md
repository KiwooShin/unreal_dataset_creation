# Plan: Floor and Wall Material Changes

**Date:** February 8, 2026
**Status:** Planned

## Goal
Apply realistic materials (textures) to floor and wall meshes instead of solid colors.

## Current State
- Floor and walls use `M_ColorBase` with solid colors (white, red, blue, green)
- No texture/material variety for realistic indoor scenes

## Approach

### Option A: Use StarterContent Materials (Recommended)
Unreal's StarterContent includes ready-to-use materials:

**Floor Materials:**
- `/Game/StarterContent/Materials/M_Wood_Floor_Walnut_Polished`
- `/Game/StarterContent/Materials/M_Wood_Floor_Walnut_Worn`
- `/Game/StarterContent/Materials/M_Tile_Hexagon`
- `/Game/StarterContent/Materials/M_Concrete_Tiles`
- `/Game/StarterContent/Materials/M_CobbleStone_Rough`

**Wall Materials:**
- `/Game/StarterContent/Materials/M_Brick_Clay_New`
- `/Game/StarterContent/Materials/M_Brick_Clay_Old`
- `/Game/StarterContent/Materials/M_Concrete_Poured`
- `/Game/StarterContent/Materials/M_Metal_Burnished_Steel`

### Option B: Create Custom Parameterized Material
Create `M_TextureBase` with switchable texture parameter (more complex).

## Implementation Steps

### 1. Update JSON Config Schema
Add `material` field to object definitions:

```json
{
  "type": "floor",
  "mesh": "/Game/StarterContent/Architecture/Floor_400x400",
  "position": [50, -500, 20],
  "scale": [3.0, 4.0, 1.0],
  "material": "/Game/StarterContent/Materials/M_Wood_Floor_Walnut_Polished"
}
```

### 2. Update unreal_api_server_v2.py
Modify `spawn_static_mesh()` to handle material paths:

```python
def apply_material(material_path, mesh_component):
    """Apply a material from path to mesh component."""
    if unreal.EditorAssetLibrary.does_asset_exist(material_path):
        material = unreal.EditorAssetLibrary.load_asset(material_path)
        mesh_component.set_material(0, material)
        return True
    return False
```

### 3. Update spawn_static_mesh()
- Check if `material` key exists in object config
- If `material` is a path (starts with `/Game/`), use `apply_material()`
- If `material` is a color name, use existing `apply_colored_material()`
- Fallback: keep existing color-based approach

### 4. Create Test Configurations
Create `assets/house_with_materials.json`:

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
  ]
}
```

### 5. Verify StarterContent Materials
Run a test to list available materials in StarterContent:

```python
# In Unreal Python console
import unreal
assets = unreal.EditorAssetLibrary.list_assets('/Game/StarterContent/Materials/')
for a in assets:
    print(a)
```

## Testing Checklist
- [ ] Verify StarterContent materials exist in project
- [ ] Test applying material path to floor mesh
- [ ] Test applying material path to wall mesh
- [ ] Capture screenshots with textured floor/walls
- [ ] Compare visual quality with solid colors

## Fallback Plan
If StarterContent materials are not available:
1. Import free material packs from Quixel Bridge
2. Or continue with solid colors and add material support later

## Expected Output
- Updated `unreal_api_server_v2.py` with material path support
- New `assets/house_with_materials.json` config
- Screenshots in `results/02082026/` showing textured floor and walls
