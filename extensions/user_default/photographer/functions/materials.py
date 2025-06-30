import bpy

def list_objects_with_material(material):
    objects_with_material = []
    for obj in bpy.context.scene.objects:
        if obj.type in {'MESH','CURVE'}:
            for slot in obj.material_slots:
                if slot.material and slot.material == material:
                    objects_with_material.append(obj)
                    break  # Break the inner loop as the object already has the material

    return objects_with_material