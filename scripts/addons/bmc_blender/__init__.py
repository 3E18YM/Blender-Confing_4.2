# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#import Placement_object
import bpy
import os
import json

from bpy.props import EnumProperty, FloatProperty, StringProperty, BoolProperty
from bpy.types import  PropertyGroup, WindowManager,  Operator, Panel
from bpy.types import Operator

from . import Action_op 
from . import rename_for_maya as rn

bl_info = {
    "name": "BMC",
    "author": "Nava Selmon",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": 'VIEW_3D',
    "warning": "",
    "category": "Import-Export"
}

class user_setting_bmc(Panel):
    bl_label = "Setting"
    bl_idname = "BMC_PT_Setting"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BMC"

    def draw(self, context):
        layout = self.layout
        App_info = context.window_manager 

        col = layout.column()
        col.scale_y = 1.25
        col.operator("object.save_setting_bmc", icon= "FILE_TICK")
        
       
        row = layout.row(align=True)
        row.prop(App_info, "bmc_userList", text="user")
        row.scale_x = 0.2
        row.operator("object.delete_user_bmc")
        row.operator("object.add_user_bmc")

        col = layout.column()        
        col.prop(App_info, "file_path", text="")   
        col.prop(App_info, "Scene_Scale", text="Scene Scale")

        row = col.row(align=True)   
        row.scale_y = 1.25     
        row.prop(App_info, "type_select_light",text="LIGHT", icon_only=True,icon= "OUTLINER_OB_LIGHT")
        row.prop(App_info, "type_select_camera",text="CAMERA", icon_only=True,icon= "OUTLINER_OB_CAMERA")
        row = col.row(align=True)
        row.scale_y = 1.25
        row.prop(App_info, "type_select_material",text="MATERAIL", icon_only=True,icon= "MATERIAL_DATA")
        row.prop(App_info, "type_select_mesh", text="MESH",icon_only=True,icon= "MESH_CUBE")

class BMC_Action(Panel):
    bl_label = "Action"
    bl_idname = "BMC_PT_from_maya"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BMC"

    def draw(self, context):
        layout = self.layout
        App_info = context.window_manager  

        col = layout.column(align=True)   
        row = col.row(align=True)
        row.scale_y = 1.0
        if App_info.type_only_select:
            os_icon_name = "MOD_BOOLEAN"                        
        else:
            os_icon_name = "IMGDISPLAY"
        row.prop(App_info, "type_only_select",text="SELECT" , icon_only=True,icon= os_icon_name)
        if App_info.send_invisible_obj:
            gi_icon_name = "HIDE_ON"            
        else:
            gi_icon_name = "HIDE_OFF"
        row.prop(App_info, "send_invisible_obj",text="INVISIBLE" ,icon_only=True,icon = gi_icon_name) 
        
        row = col.row(align=True)  
        row.scale_y = 2.5
        row.operator("object.send_to_maya")        

        col = layout.column(align=True)   
        row = col.row(align=True)  
        row.scale_y = 2.5
        row.operator("object.get_from_maya")

        row = col.row(align=True)
        col = row.column(align=True)
        col.scale_y = 1 
        col.prop(App_info, "Light_mult", text="Light_mult")

        col = row.column(align=True)
        col.scale_x = 1.5 
        col.prop(App_info, "keep_transform", icon_only=True,icon = "RESTRICT_INSTANCED_OFF") 

class save_setting_bmc(Operator):
    """Tooltip"""
    bl_idname = "object.save_setting_bmc"
    bl_label = "Save Setting"

    def execute(self, context): 
        try:
            current_folder = os.path.dirname(os.path.abspath(__file__))
            with open(current_folder + "\\bmc_setting.json") as json_file:
                user_data_list = json.load(json_file)    

            count_index = 0
            for user_dt in user_data_list:
                if user_dt["username"] == bpy.context.window_manager.bmc_userList:

                    user_dt["center_path"]  =  bpy.context.window_manager.file_path
                    user_dt["scene_scale"]  =  bpy.context.window_manager.Scene_Scale
                    user_dt["botton_light"]  =  bpy.context.window_manager.type_select_light
                    user_dt["botton_camera"]  =  bpy.context.window_manager.type_select_camera
                    user_dt["botton_material"]  =  bpy.context.window_manager.type_select_material
                    user_dt["botton_mesh"]  =  bpy.context.window_manager.type_select_mesh
                    user_dt["botton_select"]  =  bpy.context.window_manager.type_only_select
                    user_dt["botton_invisible"]  =  bpy.context.window_manager.send_invisible_obj
                    user_dt["Light_mult"]  =  bpy.context.window_manager.Light_mult
                   
                    swap_index = count_index

                count_index += 1
            user_data_list[0],user_data_list[swap_index] = user_data_list[swap_index],user_data_list[0]
        except:
            user_data_list = []
            user_dt = {}

            user_dt["username"] = bpy.context.window_manager.bmc_userList
            user_dt["center_path"]  =  bpy.context.window_manager.file_path
            user_dt["scene_scale"]  =  bpy.context.window_manager.Scene_Scale
            user_dt["botton_light"]  =  bpy.context.window_manager.type_select_light
            user_dt["botton_camera"]  =  bpy.context.window_manager.type_select_camera
            user_dt["botton_material"]  =  bpy.context.window_manager.type_select_material
            user_dt["botton_mesh"]  =  bpy.context.window_manager.type_select_mesh
            user_dt["botton_select"]  =  bpy.context.window_manager.type_only_select
            user_dt["botton_invisible"]  =  bpy.context.window_manager.send_invisible_obj   
            user_dt["Light_mult"]  =  bpy.context.window_manager.Light_mult

            user_data_list.append(user_dt)

        with open(current_folder + "\\bmc_setting.json", "w") as file:
            json.dump(user_data_list, file, indent=2, sort_keys=False)

        bpy.context.window_manager.bmc_userList = bpy.context.window_manager.bmc_userList
        bpy.context.window_manager.file_path = bpy.context.window_manager.file_path
        bpy.context.window_manager.Scene_Scale = bpy.context.window_manager.Scene_Scale
        bpy.context.window_manager.type_select_light = bpy.context.window_manager.type_select_light
        bpy.context.window_manager.type_select_camera = bpy.context.window_manager.type_select_camera
        bpy.context.window_manager.type_select_material = bpy.context.window_manager.type_select_material
        bpy.context.window_manager.type_select_mesh = bpy.context.window_manager.type_select_mesh
        bpy.context.window_manager.type_only_select = bpy.context.window_manager.type_only_select
        bpy.context.window_manager.send_invisible_obj    = bpy.context.window_manager.send_invisible_obj   
        bpy.context.window_manager.Light_mult = bpy.context.window_manager.Light_mult     

        return {'FINISHED'}

class add_user_bmc(Operator):
    """Tooltip"""
    bl_idname = "object.add_user_bmc"
    bl_label = "+"

    new_user : StringProperty(name="user name", default = "")
    def execute(self, context):
        try:
            current_folder = os.path.dirname(os.path.abspath(__file__))
            with open(current_folder + "\\bmc_setting.json") as json_file:
                user_data = json.load(json_file)    
        except:
            user_data = []
        user_name_list = []
        for user_nm in  user_data:
            user_name_list.append(user_nm["username"])
        if self.new_user not in user_name_list and self.new_user !="":
            newuser_setting = {     "username":self.new_user,
                                    # "active":True,
                                    "center_path": bpy.context.window_manager.file_path,
                                    "scene_scale": bpy.context.window_manager.Scene_Scale,
                                    "botton_light": bpy.context.window_manager.type_select_light,
                                    "botton_camera": bpy.context.window_manager.type_select_camera,
                                    "botton_material": bpy.context.window_manager.type_select_material,
                                    "botton_mesh": bpy.context.window_manager.type_select_mesh,
                                    "botton_select": bpy.context.window_manager.type_only_select,
                                    "botton_invisible": bpy.context.window_manager.send_invisible_obj,
                                    "Light_mult": bpy.context.window_manager.Light_mult
                                }
            for user_set in  user_data: 
                user_set["active"] = False
            user_data.append(newuser_setting)   
            with open(current_folder + "\\bmc_setting.json", "w") as file:
                json.dump(user_data, file, indent=2, sort_keys=False)
            bpy.context.window_manager.bmc_userList = self.new_user
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class delete_user_bmc(Operator):
    """Tooltip"""
    bl_idname = "object.delete_user_bmc"
    bl_label = "-"

    def execute(self, context):
        try:
            current_folder = os.path.dirname(os.path.abspath(__file__))
            with open(current_folder + "\\bmc_setting.json") as json_file:
                user_data = json.load(json_file)    
            
            if len(user_data) > 1:
                u_index = 0
                for user_nm in  user_data:
                    if user_nm["username"] == bpy.context.window_manager.bmc_userList:
                        user_data.pop(u_index)
                    u_index += 1
                
                with open(current_folder + "\\bmc_setting.json", "w") as file:
                    json.dump(user_data, file, indent=2, sort_keys=False)
                
                bpy.context.window_manager.bmc_userList = user_data[0]["username"] 
        except:
            print("user not avalable to delete")
        return {'FINISHED'}

def enumlist_user(self, context):
    
    items = []    
    try:
        current_folder = os.path.dirname(os.path.abspath(__file__))
        with open(current_folder + "\\bmc_setting.json") as json_file:
            user_data = json.load(json_file)
        unique_num = 0
        for item in user_data:            
            items.append((item["username"], item["username"], "", "COMMUNITY", unique_num))    
            unique_num += 1
        
    except:
         items.append(("Default", "Default", "", "COMMUNITY", 0 ))
    return items

def updat_user_list(self, context):    
    try:
        current_folder = os.path.dirname(os.path.abspath(__file__))
        with open(current_folder + "\\bmc_setting.json") as json_file:
            user_data = json.load(json_file)

        for user_dt in user_data:
            if user_dt["username"] == bpy.context.window_manager.bmc_userList:
                # user_dt["active"] = True

                bpy.context.window_manager.file_path = user_dt["center_path"] 
                bpy.context.window_manager.Scene_Scale = user_dt["scene_scale"] 
                bpy.context.window_manager.type_select_light = user_dt["botton_light"] 
                bpy.context.window_manager.type_select_camera = user_dt["botton_camera"] 
                bpy.context.window_manager.type_select_material = user_dt["botton_material"] 
                bpy.context.window_manager.type_select_mesh = user_dt["botton_mesh"] 
                bpy.context.window_manager.type_only_select = user_dt["botton_select"] 
                bpy.context.window_manager.send_invisible_obj = user_dt["botton_invisible"]
                bpy.context.window_manager.Light_mult = user_dt["Light_mult"] 
            else:
                user_dt["active"] = False
        
        with open(current_folder + "\\bmc_setting.json", "w") as file:
            json.dump(user_data, file, indent=2, sort_keys=False)
        print("update user list")
    except:
        print("update user list error")

class App_infoProperties(PropertyGroup):   

    try:
        current_folder = os.path.dirname(os.path.abspath(__file__))
        with open(current_folder + "\\bmc_setting.json") as json_file:
            bmc_setting = json.load(json_file)
        
        set_file_path            = bmc_setting[0]["center_path"] 
        set_Scene_Scale          = bmc_setting[0]["scene_scale"]
        set_type_select_light    = bmc_setting[0]["botton_light"]
        set_type_select_camera   = bmc_setting[0]["botton_camera"] 
        set_type_select_material = bmc_setting[0]["botton_material"] 
        set_type_select_mesh     = bmc_setting[0]["botton_mesh"] 
        set_type_only_select     = bmc_setting[0]["botton_select"]
        set_send_invisible_obj   = bmc_setting[0]["botton_invisible"]
        set_Light_mult   = bmc_setting[0]["Light_mult"]
        print("bmc_setting loaded")

    except:
        
        set_file_path            = ""
        set_Scene_Scale          = 1
        set_type_select_light    = True
        set_type_select_camera   = True
        set_type_select_material = True
        set_type_select_mesh     = True
        set_type_only_select     = True
        set_send_invisible_obj   = True
        set_Light_mult           = 1
        
        print("bmc_setting not load")  
    
    WindowManager.bmc_userList =  EnumProperty(
        items = enumlist_user, name = "User", description = "user setting", update = updat_user_list
    )
    WindowManager.Scene_Scale =  FloatProperty(
        name = "SceneScale", min=0.001, default = set_Scene_Scale, description="Set Export,Import Scale"
    )
    WindowManager.Light_mult =  FloatProperty(
        name = "LightMult", min=0.01, default = set_Light_mult, description="Set Export,Import Scale"
    )
    WindowManager.file_path =  StringProperty(
        name = "File",
        default = set_file_path ,
        description = "Wanted File path",
        maxlen = 1024,
        subtype = "DIR_PATH",
    )
    WindowManager.type_select_light =  BoolProperty(default = set_type_select_light)
    WindowManager.type_select_camera =  BoolProperty(default = set_type_select_camera)
    WindowManager.type_select_material =  BoolProperty(default = set_type_select_material)
    WindowManager.type_select_mesh =  BoolProperty(default = set_type_select_mesh)
    WindowManager.type_only_select =  BoolProperty(default = set_type_only_select)
    WindowManager.send_invisible_obj =  BoolProperty(default = set_send_invisible_obj)
    WindowManager.keep_transform = BoolProperty(default = False)

def ShowMessageBox(message="", title="Message Box", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

class bmc_rename_for_maya(Operator):
    """Tooltip"""
    bl_idname = "object.rename_for_maya"
    bl_label = "Rename For Maya"

    def execute(self, context): 
        for ob in bpy.data.objects:
            ob.name = rn.maya_name(ob.name)
        for mat in bpy.data.materials:
            if mat.node_tree:
                print("rename node")
                for node in mat.node_tree.nodes:
                    node.name = rn.maya_name(node.name)
            mat.name = rn.maya_name(mat.name)
        return {'FINISHED'}

classes = [
    user_setting_bmc,
    bmc_rename_for_maya,
    BMC_Action,
    App_infoProperties,
    save_setting_bmc,
    add_user_bmc,
    delete_user_bmc      
]

def register():
    Action_op.register()
    for cls in classes:
        bpy.utils.register_class(cls)    

def unregister():
    Action_op.unregister()
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
    