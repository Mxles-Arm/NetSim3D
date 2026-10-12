import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

blend_path = Path(bpy.data.filepath)
report_path = blend_path.parent / "validation_report.json"

required_roots = ["01_Case", "02_Monitor", "03_Keyboard", "04_Mouse"]
roots = {name: bpy.data.objects.get(name) for name in required_roots}
keys = [obj for obj in bpy.data.objects if obj.name.startswith("Key_") and obj.type == "MESH"]
sockets = [obj for obj in bpy.data.objects if obj.name.startswith("Socket_") and obj.type == "EMPTY"]
required_sockets = {
    "Socket_LAN_RJ45": ("RJ45", 8),
    "Socket_Rear_HDMI": ("HDMI", 19),
    "Socket_Rear_DisplayPort": ("DP", 20),
    "Socket_Rear_USB_A1": ("USB_A_3", None),
    "Socket_Front_USB_C": ("USB_C", 24),
    "Socket_AC_Power_Inlet": ("C14", 3),
    "Socket_Monitor_HDMI": ("HDMI", 19),
    "Socket_Monitor_DP": ("DP", 20),
    "Socket_Keyboard_USB_C": ("USB_C", 24),
    "Socket_Mouse_USB_C": ("USB_C", 24),
}

def descendants(parent):
    result = []
    for obj in bpy.data.objects:
        cursor = obj
        while cursor is not None:
            if cursor == parent:
                result.append(obj)
                break
            cursor = cursor.parent
    return result

def world_min_z(parent):
    values = []
    for obj in descendants(parent):
        if obj.type != "MESH":
            continue
        values.extend((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)
    return min(values) if values else None

errors = []
for name, obj in roots.items():
    if obj is None or obj.type != "EMPTY":
        errors.append(f"missing component root: {name}")

if len(keys) != 104:
    errors.append(f"keyboard key count is {len(keys)}, expected 104")

for name, (kind, contacts) in required_sockets.items():
    obj = bpy.data.objects.get(name)
    if obj is None:
        errors.append(f"missing socket marker: {name}")
        continue
    if obj.get("connector_type") != kind:
        errors.append(f"{name} connector type mismatch")
    if contacts is not None and obj.get("contact_count") != contacts:
        errors.append(f"{name} contact count mismatch")
    if obj.get("insertion_axis") != "-Z":
        errors.append(f"{name} insertion axis is not -Z")

external_images = [img.filepath for img in bpy.data.images if img.source == "FILE" and img.filepath]
if external_images:
    errors.append("external image dependencies detected")

triangle_count = 0
for obj in bpy.data.objects:
    if obj.type == "MESH" and obj.name != "Studio_Backdrop":
        obj.data.calc_loop_triangles()
        triangle_count += len(obj.data.loop_triangles)

root_min_z = {name: world_min_z(obj) if obj else None for name, obj in roots.items()}
for name, value in root_min_z.items():
    if value is None or value < -0.0015 or value > 0.003:
        errors.append(f"{name} tabletop minimum Z is {value}")

report = {
    "blend": str(blend_path),
    "valid": not errors,
    "errors": errors,
    "component_roots": required_roots,
    "key_count": len(keys),
    "socket_count": len(sockets),
    "triangle_count_without_studio_backdrop": triangle_count,
    "component_world_min_z_m": root_min_z,
    "external_images": external_images,
    "studio_collection_present": bpy.data.collections.get("STUDIO | render only") is not None,
    "asset_collection_present": bpy.data.collections.get("ASSET | NetCare Desktop v2") is not None,
}
if not report["studio_collection_present"]:
    errors.append("render-only studio collection is missing")
if not report["asset_collection_present"]:
    errors.append("asset collection is missing")
report["valid"] = not errors
report["errors"] = errors
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2), flush=True)
if errors:
    sys.exit(1)
