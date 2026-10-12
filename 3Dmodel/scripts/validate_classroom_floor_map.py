import bpy, json
from pathlib import Path
from mathutils import Vector

scene=bpy.context.scene
rooms=[o for o in scene.objects if o.get('room_id')]
assert len(rooms)==10,len(rooms)
assert len([o for o in scene.objects if o.name.startswith('StudentDesk_Row')])==10
assert all(bpy.data.objects.get(n) for n in ('IT_HeadDesk','IT_PlayerDesk','IT_SpareDesk','TeacherDesk','TeacherComputerSet_Root','Door_Leaf_Open_63deg','Corridor_North_End_End','Corridor_South_End_End'))
assert len([o for o in scene.objects if o.name.startswith('Door_') and o.name.endswith('_Hinge')])==7
assert len([o for o in scene.objects if o.name.startswith('Key_') and o.type=='MESH'])==104
assert len([o for o in scene.objects if o.name.startswith('Socket_')])==18
assert len([o for o in scene.objects if o.name.startswith('Stair_UP_Step_')])==20
assert len([o for o in scene.objects if o.name.startswith('Stair_DOWN_Step_')])==20
assert len(bpy.data.libraries)==0,'Unexpected linked library'
missing=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
assert not missing,missing
ceil=bpy.data.collections['07 | Ceilings - toggle for interior']
assert bpy.data.objects['Ceiling_Slab_150mm'] in list(ceil.objects)
assert ceil.hide_render and ceil.hide_viewport
assert not bpy.data.collections.get('STUDIO | render only')
deps=bpy.context.evaluated_depsgraph_get()
corridor=next(o for o in rooms if o['room_id']=='Corridor')
x0,x1,y0,y1=corridor['bounds_m']
xc=(x0+x1)/2
hit=scene.ray_cast(deps,Vector((xc,y0+.25,1.0)),Vector((0,1,0)),distance=y1-y0-.5)
assert not hit[0],('Corridor center blocked',hit[4])
for i in range(1,20):
    y=y0+(y1-y0)*i/20
    hit=scene.ray_cast(deps,Vector((xc,y,.12)),Vector((0,0,-1)),distance=.2)
    assert hit[0] and abs(hit[1].z)<.04,('Corridor floor gap',y)
report={'valid':True,'file':bpy.data.filepath,'room_and_circulation_regions':len(rooms),'doorways_including_existing_classroom':8,'corridor_center_clear':True,'corridor_floor_continuous':True,'student_desks':10,'IT_desks':3,'computer_keys':104,'computer_sockets':18,'stairs_each_direction':20,'ceiling_present_hidden_for_review':True,'missing_external_images':missing,'linked_libraries':len(bpy.data.libraries),'objects':len(scene.objects)}
print(json.dumps(report,indent=2),flush=True)
