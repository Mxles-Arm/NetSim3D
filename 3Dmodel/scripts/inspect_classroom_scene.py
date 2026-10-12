import bpy, json
from mathutils import Vector
items=[]
for o in bpy.context.scene.objects:
    item={'name':o.name,'type':o.type,'location':list(o.location),'rotation':list(o.rotation_euler),'dimensions':list(o.dimensions),'parent':o.parent.name if o.parent else None,'hidden':o.hide_get(),'hide_render':o.hide_render,'collections':[c.name for c in o.users_collection]}
    if o.type=='MESH':
        corners=[o.matrix_world @ Vector(p) for p in o.bound_box]
        item['bounds']=[[min(v[i] for v in corners) for i in range(3)],[max(v[i] for v in corners) for i in range(3)]]
    items.append(item)
print(json.dumps({'objects':items,'collections':[c.name for c in bpy.data.collections],'materials':[m.name for m in bpy.data.materials],'units':bpy.context.scene.unit_settings.system},indent=2))
