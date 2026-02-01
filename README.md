# Unreal Engine Synthetic Dataset Generator

Generate synthetic datasets for deep learning using Unreal Engine 5.6 and Python.

## System Info

- **Unreal Engine:** 5.6.1
- **Python:** 3.11.x (bundled with UE)
- **Platform:** macOS
- **Installation:** `/Users/Shared/Epic Games/UE_5.6/`

---

## Choose Your Approach

### 🔥 Approach 1: ML-Driven Pipeline (Recommended for Production)

**Best for:**
- Running ML models (PyTorch, TensorFlow, object detection)
- Processing real-world images to create digital twins
- Need full Python ecosystem and ML libraries
- Headless/scalable production workflows

**Quick Start:** [QUICK_START.md](QUICK_START.md) (10 minutes)

**Key Features:**
- External Python with full ML support
- HTTP API communication
- Digital twin generation from object detection
- Scalable to headless rendering

**Files:**
- `ml_controller.py` - Main pipeline (runs in terminal)
- `unreal_api_server.py` - API server (runs in Unreal)
- `object_library.py` - Object definitions

**Documentation:**
- [QUICK_START.md](QUICK_START.md) - Get started in 10 minutes
- [ML_DRIVEN_ARCHITECTURE.md](ML_DRIVEN_ARCHITECTURE.md) - Architecture overview
- [HEADLESS_SETUP_GUIDE.md](HEADLESS_SETUP_GUIDE.md) - Complete setup guide

---

### 📦 Approach 2: Simple In-Engine Python (Good for Learning)

**Best for:**
- Learning Unreal Python basics
- Simple cube generation and testing
- No ML models needed
- Quick prototyping

**Quick Start:** [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)

**Key Features:**
- Everything runs inside Unreal's Python
- Simple, straightforward workflow
- Good for understanding the basics

**Files:**
- `basic_cube_screenshot.py` - Single cube test
- `generate_dataset.py` - Basic dataset generator

**Documentation:**
- [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) - Setup guide
- [plan.md](plan.md) - Original planning document

---

## Quick Decision Guide

**Use Approach 1 (ML-Driven) if:**
- ✅ You need to run object detection models
- ✅ You're processing real-world images
- ✅ You need PyTorch/TensorFlow/OpenCV
- ✅ You want to scale to large datasets
- ✅ You need external Python control

**Use Approach 2 (Simple) if:**
- ✅ You're just learning Unreal Python
- ✅ You want something simple to start
- ✅ You don't need ML libraries
- ✅ You're testing basic concepts

## File Structure

```
unreal/
# Start Here
├── README.md                      # This file
├── QUICK_START.md                 # 10-min ML-driven setup ⭐ START HERE

# ML-Driven Approach (Recommended)
├── ML_DRIVEN_ARCHITECTURE.md      # Architecture overview
├── HEADLESS_SETUP_GUIDE.md        # Complete setup guide
├── unreal_api_server.py           # HTTP server (run in Unreal)
├── ml_controller.py               # ML pipeline (run in terminal)
├── object_library.py              # Object definitions
├── requirements.txt               # Python dependencies

# Simple Approach (Learning)
├── SETUP_INSTRUCTIONS.md          # Simple setup guide
├── basic_cube_screenshot.py       # Basic test script
├── generate_dataset.py            # Basic dataset generator

# Planning & Documentation
├── plan.md                        # Original planning document
├── HEADLESS_RENDERING.md          # Headless options explained

# Output Directories
├── ml_env/                        # Python virtual environment
├── renders/                       # ML pipeline output
├── output/                        # Simple approach output
└── dataset/                       # Dataset output
    ├── images/                    # Generated images
    └── metadata/                  # JSON annotations
```

## Key Scripts Overview

### ML-Driven Approach

**unreal_api_server.py** (runs in Unreal Editor)
- HTTP server listening on port 8080
- Receives scene descriptions via REST API
- Creates objects and renders scenes
- Returns image paths and metadata

**ml_controller.py** (runs in terminal with your Python)
- Loads real-world images
- Runs object detection (PyTorch/TensorFlow)
- Converts detections to scene descriptions
- Sends to Unreal via HTTP API
- Generates variations with randomization

**object_library.py** (configuration)
- Maps detected objects to Unreal meshes
- Defines object properties (scale, materials, colors)
- Customizable for your object types

### Simple Approach

**basic_cube_screenshot.py**
- Single cube demonstration
- Good for testing setup
- Run in Unreal Python console

**generate_dataset.py**
- Randomized cube generation
- Configurable parameters
- Run in Unreal Python console

## Metadata Format

Each image has a corresponding JSON file with:

```json
{
  "index": 0,
  "image_filename": "cube_0000.png",
  "cube": {
    "position": {"x": 123.4, "y": -56.7, "z": 189.0},
    "rotation": {"pitch": 45.2, "yaw": 180.5, "roll": 0.0},
    "scale": {"x": 2.5, "y": 2.5, "z": 2.5}
  },
  "camera": {
    "position": {"x": 456.7, "y": 123.4, "z": 300.0},
    "rotation": {"pitch": -15.3, "yaw": 90.0, "roll": 0.0}
  },
  "image_dimensions": {
    "width": 1920,
    "height": 1080
  }
}
```

## Tips for Better Results

### 1. Add Lighting
Before running scripts, add to your level:
- Directional Light (sun)
- Sky Light (ambient)
- Post Process Volume (effects)

### 2. Add Background
- Sky Sphere
- Environment assets
- HDRI backdrop

### 3. Camera Setup
- Set `use_camera: True` in CONFIG for better framing
- Adjust `camera_distance_range` to control view distance

### 4. Materials & Textures
Modify the scripts to:
- Load different materials
- Apply textures to cubes
- Randomize colors

### 5. Multiple Objects
Extend the script to spawn multiple cubes per scene for more complex datasets.

## Troubleshooting

### Script runs but no images appear
- Check the output directory path
- Ensure viewport is visible
- Add lighting to your scene

### Images are black
- Add lights to your scene
- Move cube to visible position
- Check camera is pointing at cube

### Performance is slow
- Reduce image resolution
- Disable real-time rendering
- Use simpler materials

### Can't find output files
- Check the absolute path in CONFIG
- Verify write permissions
- Look for error messages in console

## Next Steps

1. **Test basic script** to verify setup
2. **Run dataset generator** with small num_images (e.g., 5)
3. **Review output** images and metadata
4. **Customize CONFIG** for your needs
5. **Scale up** to full dataset size
6. **Extend scripts** with:
   - Multiple object types
   - Different backgrounds
   - Varied lighting conditions
   - Segmentation masks
   - Bounding boxes

## Resources

- [plan.md](plan.md) - Comprehensive planning document
- [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) - Setup guide
- [UE Python API Docs](https://docs.unrealengine.com/5.6/en-US/PythonAPI/)
- [Scripting Guide](https://docs.unrealengine.com/5.6/en-US/scripting-the-unreal-editor-using-python/)

## Resources & Documentation

### ML-Driven Pipeline
- [QUICK_START.md](QUICK_START.md) - **Start here!** (10 minutes)
- [ML_DRIVEN_ARCHITECTURE.md](ML_DRIVEN_ARCHITECTURE.md) - Architecture details
- [HEADLESS_SETUP_GUIDE.md](HEADLESS_SETUP_GUIDE.md) - Complete setup
- [HEADLESS_RENDERING.md](HEADLESS_RENDERING.md) - Headless options

### Simple Approach
- [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) - Simple setup guide
- [plan.md](plan.md) - Original planning document

### External Resources
- [UE Python API Docs](https://docs.unrealengine.com/5.6/en-US/PythonAPI/)
- [Scripting Guide](https://docs.unrealengine.com/5.6/en-US/scripting-the-unreal-editor-using-python/)

---

## 🚀 Ready to Start?

### For ML-Driven Pipeline (Recommended)
**Open [QUICK_START.md](QUICK_START.md) and follow the 10-minute setup!**

### For Simple Approach
**Open [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)**

---

## Your Use Case

Based on your requirements:
- ✅ Real-world image processing
- ✅ Object detection → Digital twin generation
- ✅ Run 3D detection models
- ✅ Randomize properties for synthetic data

**→ Use the ML-Driven Pipeline (Approach 1)**

Start with [QUICK_START.md](QUICK_START.md)!
