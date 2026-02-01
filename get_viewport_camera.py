"""
Get current viewport camera position and rotation
Run this in Unreal Python console
"""

import unreal

print("=" * 70)
print("CURRENT VIEWPORT CAMERA INFO")
print("=" * 70)

# Get current viewport camera info
camera_info = unreal.EditorLevelLibrary.get_level_viewport_camera_info()

location = camera_info[0]
rotation = camera_info[1]

print(f"\nLocation: {location}")
print(f"  X: {location.x}")
print(f"  Y: {location.y}")
print(f"  Z: {location.z}")

print(f"\nRotation: {rotation}")
print(f"  Roll: {rotation.roll}")
print(f"  Pitch: {rotation.pitch}")
print(f"  Yaw: {rotation.yaw}")

print("\n" + "=" * 70)
print("COPY THIS FOR YOUR SCRIPT:")
print("=" * 70)
print(f"camera_location = unreal.Vector({location.x}, {location.y}, {location.z})")
print(f"camera_rotation = unreal.Rotator({rotation.roll}, {rotation.pitch}, {rotation.yaw})")
print("=" * 70)
