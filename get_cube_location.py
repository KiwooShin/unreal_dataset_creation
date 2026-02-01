"""
Get current cube/actor locations in the scene
Run this in Unreal Python console
"""

import unreal

print("=" * 70)
print("SCENE ACTOR LOCATIONS")
print("=" * 70)

# Get all actors in the level
editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
all_actors = editor_actor_subsystem.get_all_level_actors()

# Find static mesh actors (cubes, etc.)
print("\nStatic Mesh Actors:")
print("-" * 70)

for actor in all_actors:
    actor_class = actor.get_class().get_name()

    if 'StaticMeshActor' in actor_class:
        name = actor.get_name()
        label = actor.get_actor_label()
        loc = actor.get_actor_location()
        rot = actor.get_actor_rotation()
        scale = actor.get_actor_scale3d()

        print(f"\n  Name: {name}")
        print(f"  Label: {label}")
        print(f"  Position: [{loc.x:.2f}, {loc.y:.2f}, {loc.z:.2f}]")
        print(f"  Rotation: [Pitch={rot.pitch:.2f}, Yaw={rot.yaw:.2f}, Roll={rot.roll:.2f}]")
        print(f"  Scale: [{scale.x:.2f}, {scale.y:.2f}, {scale.z:.2f}]")

print("\n" + "=" * 70)
print("COPY-PASTE VALUES:")
print("=" * 70)

# Print the first cube/mesh found for easy copying
for actor in all_actors:
    if 'StaticMeshActor' in actor.get_class().get_name():
        label = actor.get_actor_label()
        if 'Cube' in label or 'cube' in label.lower():
            loc = actor.get_actor_location()
            print(f"CUBE_POSITION = [{loc.x:.2f}, {loc.y:.2f}, {loc.z:.2f}]")
            break
else:
    # If no cube found, print first mesh actor
    for actor in all_actors:
        if 'StaticMeshActor' in actor.get_class().get_name():
            loc = actor.get_actor_location()
            print(f"OBJECT_POSITION = [{loc.x:.2f}, {loc.y:.2f}, {loc.z:.2f}]")
            break

print("=" * 70)
