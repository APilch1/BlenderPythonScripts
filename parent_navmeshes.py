import bpy

# Flush the dependency graph so matrix_world values are current
bpy.context.view_layer.update()

parented = []
missing = []
skipped = []

for obj in bpy.data.objects:
    if not obj.name.endswith("_navmesh"):
        continue
    parent_name = obj.name[:-8]
    parent = bpy.data.objects.get(parent_name)
    if parent is None:
        missing.append(obj.name)
        continue

    loc = tuple(round(v, 4) for v in obj.location)
    if obj.parent == parent and loc == (0.0, 0.0, 0.0):
        skipped.append(obj.name)
        continue

    obj.parent = parent

    # Reset local position to zero so the navmesh sits exactly at the chunk's
    # world origin. Both the navmesh and terrain mesh have geometry spanning
    # ±400 units around their object origins, so colocating them overlays
    # the navmesh perfectly on the terrain in the exported GLB.
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)

    parented.append(obj.name + " -> " + parent_name)

# Flush again so the scene reflects the new local matrices
bpy.context.view_layer.update()

print("--- Navmesh parenting complete ---")
print("Parented/repositioned: " + str(len(parented)))
for line in parented:
    print("  OK: " + line)
if skipped:
    print("Already correct (skipped): " + str(len(skipped)))
if missing:
    print("Missing parents: " + str(len(missing)))
    for name in missing:
        print("  MISSING: " + name)
