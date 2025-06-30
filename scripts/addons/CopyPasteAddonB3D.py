#  ##### BEGIN GPL LICENSE BLOCK #####
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

bl_info = {
    "name": "CopyPaste/ExportImport",
    "author": "IgorDmytrenko",
    "version": (1, 0, 8),
    "blender": (2, 93, 2),
    "location": "View3D > Object",
    "description": "import/export object like a copy/paste from dir",
    "warning": "",
    "category": "Object",
}

import bpy
import os
from os.path import join, normpath
import platform

# Get Temp directory --------------------- 
type_os = platform.system()

if type_os == "Windows":
	user_home = os.getenv('userprofile')

else:
	user_home = os.path.expanduser("~")
  
copypaste_dir = normpath(join("/idTools/copypaste/temp"))
dirpath = str(user_home) + copypaste_dir + "/"

if not "idTools" in os.listdir(user_home):  
    os.makedirs(dirpath)
  

#----------------------------------------------

class ExportObject(bpy.types.Operator):
    bl_idname = "object.export_object"
    bl_label = "Copy/Export" 
    bl_options = {'REGISTER', 'UNDO'}

    # >>>>>>>>>>>>>>> Export selected models <<<<<<<<<<<<<<< #

    def execute(self, context):

        sel = bpy.context.selected_objects

        for obj in sel:
            # deselect all meshes
            bpy.ops.object.select_all(action='DESELECT')

            # select the object
            obj.select_set(state = True)

            full_dirpath = normpath(join(dirpath + obj.name + ".obj"))
            # export object
            bpy.ops.export_scene.obj(
                filepath=full_dirpath,
                check_existing=True,
                axis_forward='-Z',
                axis_up='Y',
                filter_glob=".obj;.mtl",
                use_selection=True,
                use_animation=False,
                use_mesh_modifiers=True,
                use_edges=True,
                use_smooth_groups=False,
                use_smooth_groups_bitflags=False,
                use_normals=True,
                use_uvs=True,
                use_materials=True,
                use_triangles=False,
                use_nurbs=False,
                use_vertex_groups=False,
                use_blen_objects=True,
                group_by_object=False,
                group_by_material=False,
                keep_vertex_order=False,
                global_scale=100.0,
                path_mode='AUTO'
                )

        return {"FINISHED"}


class ImportObject(bpy.types.Operator):
    bl_idname = "object.import_object"
    bl_label = "Paste/Import" 
    bl_options = {'REGISTER', 'UNDO'}

    # >>>>>>>>>>>>>>> Import models <<<<<<<<<<<<<<< #

    def execute(self, context):

        files = os.listdir(dirpath)

        imported_list = []

        mats_lib = bpy.data.materials

        if not files:
            self.report({'INFO'}, 'Folder is empty.')

        materials = [ normpath(join(dirpath, file_in)) for file_in in files if file_in.endswith('.mtl')]

        objs = [ normpath(join(dirpath, file_in)) for file_in in files if file_in.endswith('.obj')]

        for obj in objs:
            bpy.ops.import_scene.obj(
                filepath=obj,
                filter_glob="*.obj",
                use_edges=True,
                use_smooth_groups=True,
                use_split_objects=True,
                use_split_groups=True,
                use_groups_as_vgroups=True,
                use_image_search=True,
                split_mode='ON',
                global_clamp_size=0.0,
                axis_forward='-Z',
                axis_up='Y'
                )
            os.remove(obj)
            
            sel = bpy.context.selected_objects
            
            for obj in sel:
                bpy.ops.object.select_all(action='DESELECT')

                # select the object
                obj.select_set(state = True)
                
                # create list for imported objects
                imported_list.append(obj.name)                   

        for mt in materials:
            os.remove(mt)
            
        for obj in imported_list:
            # select object by name
            sel = bpy.data.objects.get(obj)
            # deselect inside loop                      
            bpy.ops.object.select_all(action='DESELECT')     
            # select object inside loop
            sel.select_set(state=True)
            # convert scale to m
            sel.scale = (0.01, 0.01, 0.01)
            # apply transfoem
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                               
            # get material name for selected object
            mats = sel.material_slots[0]
            #print(mats)
            
            if mats.material.name[-3:].isnumeric():
                print(mats.material.name[-3:])
                material_origin = mats.name.rpartition('.')
                
                if material_origin[0] in mats_lib: 
                    mats.material = mats_lib.get(material_origin[0])
                    
            bpy.context.view_layer.objects.active = sel
            sel.active_material.blend_method = 'OPAQUE'

        return {"FINISHED"}


class Import_Export(bpy.types.Menu):
    # Define the " Copy Paste" menu
    bl_idname = "Import_Export"
    bl_label = "Copy Paste"
       
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.operator("object.export_object", text = "Copy/Export")        
        layout.operator("object.import_object", text = "Paste/Import")

# Register all operators and panels

# Define "Extras" menu
def menu_func(self, context):
    lay_out = self.layout
    lay_out.operator_context = 'INVOKE_REGION_WIN'
    lay_out.separator()
    lay_out.menu("Import_Export", text = "Copy Paste")


# Register
classes = [ 
    ExportObject,
    ImportObject,
    Import_Export,
]

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # Add "Extras" menu to the "Object" menu
    bpy.types.VIEW3D_MT_object.append(menu_func)
        

def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()