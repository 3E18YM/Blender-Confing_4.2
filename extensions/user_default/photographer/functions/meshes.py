import bpy, os

from ..constants import photographer_folder

def append_mesh(mesh_name, obj_name, keep_dimensions=True):
    object = None
    path = "blends/meshes.blend/Mesh/"

    dir = os.path.join(photographer_folder,path)

    # Normalize slashes for Windows // linux
    dir = os.path.normpath(dir)

    # mesh = bpy.data.meshes.get(mesh_name)
    # if mesh:
    #     # mesh = meshes[0]
    #     # object = [o for o in bpy.data.objects if o.data is mesh]
    #     # if object:
    #     #     object = object[0]
    #     # else:
    #     # Duplicate mesh data to allow edits to the mesh
    #     mesh = mesh.copy()

    #     object = bpy.data.objects.new(obj_name, mesh)
    #     object.scale /= bpy.context.scene.unit_settings.scale_length
    #     bpy.context.collection.objects.link(object)

    # # Append mesh if it doesn't already exist
    # else:
    bpy.ops.wm.append(filename=mesh_name, directory=dir)
    new_mesh = [m for m in bpy.data.meshes if m.name == mesh_name][0]
    new_mesh.name = obj_name
    
    object = [o for o in bpy.data.objects if o.data is new_mesh][0]
    if keep_dimensions:
        object.scale /= bpy.context.scene.unit_settings.scale_length
    object.name = obj_name
    
    return new_mesh, object