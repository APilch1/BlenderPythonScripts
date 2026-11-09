import bpy
import re

# Threshold: if a MESH child's local offset from its parent is larger than this,
# the child is assumed to be sitting at Blender world origin instead of the chunk
# position.  800 units = one chunk width; anything beyond half a chunk is wrong.
THRESHOLD = 400.0

# ---------------------------------------------------------------------------
# Identify chunk MESH objects (named chunk_ROW_COL)
# ---------------------------------------------------------------------------
chunk_pattern = re.compile(r'^chunk_\d+_\d+$')

bpy.context.view_layer.update()

reset    = []
skipped  = []
already  = []

for obj in bpy.data.objects:
    # Only look at MESH objects whose name matches chunk_ROW_COL (the terrain mesh)
    if obj.type != 'MESH' or not chunk_pattern.match(obj.name):
        continue

    for child in obj.children:
        if child.type != 'MESH':
            continue

        # Skip navmeshes — parent_navmeshes.py already handles those
        if child.name.endswith('_navmesh'):
            already.append(child.name + ' (navmesh, skipped)')
            continue

        # Measure local offset: how far is this child from its parent's origin?
        local_offset = child.location.length

        if local_offset <= THRESHOLD:
            already.append(f'{child.name}  offset={local_offset:.1f}  (OK)')
            continue

        # Reset local position to (0,0,0) so the child overlays the terrain
        child.location = (0, 0, 0)
        reset.append(f'{child.name}  (was offset={local_offset:.1f} from {obj.name})')

bpy.context.view_layer.update()

print('\n=== fix_mesh_positions.py ===')
print(f'Reset to local (0,0,0): {len(reset)}')
for line in reset:
    print(f'  FIX: {line}')

print(f'\nAlready correct / skipped: {len(already)}')
for line in already:
    print(f'  OK : {line}')

print('\nDone.')
print('Re-export affected chunks, then adjust house positions as needed.')
