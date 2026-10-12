import bpy
import json
from mathutils import Vector

o = bpy.data.objects['01_Case_StaticDetails']
pc = bpy.data.objects['01_Case']
to_pc = pc.matrix_world.inverted() @ o.matrix_world
mesh = o.data
neighbors = [[] for _ in mesh.vertices]
for edge in mesh.edges:
    a, b = edge.vertices
    neighbors[a].append(b)
    neighbors[b].append(a)
remaining = set(range(len(mesh.vertices)))
islands = []
while remaining:
    pending = [remaining.pop()]
    island = []
    while pending:
        idx = pending.pop()
        island.append(idx)
        for j in neighbors[idx]:
            if j in remaining:
                remaining.remove(j)
                pending.append(j)
    coordinates = [to_pc @ mesh.vertices[i].co for i in island]
    lo = [min(v[a] for v in coordinates) * 1000 for a in range(3)]
    hi = [max(v[a] for v in coordinates) * 1000 for a in range(3)]
    if len(island) > 20 and hi[1] < -150:
        islands.append({'verts': len(island), 'min_mm': lo, 'max_mm': hi})
print(json.dumps({'file': bpy.data.filepath, 'object': o.name, 'case_matrix': [list(row) for row in pc.matrix_world], 'front_islands': islands, 'materials': [m.name if m else None for m in mesh.materials]}, indent=2))
