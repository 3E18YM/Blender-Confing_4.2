import bpy
import os
import json
from bpy.props import StringProperty, IntProperty, CollectionProperty, BoolProperty
from bpy.types import  UIList, Operator, PropertyGroup
from . import bl_send_material as um
from . import bl_send_light as ul
from . import bl_send_mesh as ums
from . import bl_send_camera as uc
from . import bl_get_material as gm
from . import bl_get_light as gl
from . import bl_get_mesh as gms
from . import bl_get_camera as gc
from . import warning_info as wr
from . import rename_for_maya as rn

class BMC_send(Operator):
    """Tooltip"""
    bl_idname = "object.send_to_maya"
    bl_label = "SEND"

    def execute(self, context):   
        send = False
        mat_repeat_mane = False
        App_info = context.window_manager  
        
        if App_info.type_only_select:#send only select
            if App_info.send_invisible_obj:
                objs_sl = [ob for ob in bpy.context.selected_objects]             
            else:                
                objs_sl = [ob for ob in bpy.context.selected_objects if ob.visible_get()]
        else:#send all    
            if App_info.send_invisible_obj:
                objs_sl = [ob for ob in bpy.context.view_layer.objects]                   
            else:                
                objs_sl = [ob for ob in bpy.context.view_layer.objects if ob.visible_get()]  

        objs_send =  [ob for ob in objs_sl if ob.type in {"MESH","CAMERA","LIGHT"} ]          

        try:
            current_folder = os.path.dirname(os.path.abspath(__file__))
            with open(current_folder + '\\Material_dict.json') as json_file:
                mat_dict = json.load(json_file)
        except:
            print("Material_dict loading error")
            return {'CANCELLED'}

        mat_list = []
        node_list = []
        context.scene.rename_list.clear()  
        for ob_s in objs_send:#verification name is duplicate
            if ob_s.type == 'MESH':
                for slot in ob_s.material_slots: 
                    mat = slot.material
                    if mat and not mat.name in mat_list:#check for mesh use same material  
                        mat_list.append(mat.name)
                        mat_name_dup_obj = bpy.data.objects.get(mat.name)                   
                        #check material name duplicate with object.
                        if mat_name_dup_obj or not rn.maya_name_check(mat.name):
                            m_item = context.scene.rename_list.add()
                            m_item.name = mat.name
                            m_item.type = "MAT_SG"  

                            if mat_name_dup_obj :                                    
                                m_item.name_duplicate = True
                            if not rn.maya_name_check(mat.name):
                                m_item.name_illegal = True                            
                        else:
                            node_list.append(mat.name)#for verification a node name  not duplicate with material name.

                        for m_node in mat.node_tree.nodes:
                            if m_node.type in mat_dict["blender"]:
                                node_name_dup_obj = bpy.data.objects.get(m_node.name)
                                #check node name in material duplicate with other material.
                                if node_name_dup_obj or  m_node.name in node_list or not rn.maya_name_check(m_node.name):
                                    n_item = context.scene.rename_list.add()
                                    n_item.rt_m_name = mat.name 
                                    n_item.name = m_node.name
                                    n_item.type = "MAT_NODE"

                                    if node_name_dup_obj or  m_node.name in node_list :                                    
                                        n_item.name_duplicate = True
                                    if not rn.maya_name_check(m_node.name):
                                        n_item.name_illegal = True

                                if not m_node.name in node_list :
                                    node_list.append(m_node.name) 
                     

            if not rn.maya_name_check(ob_s.name):
                ob_item = context.scene.rename_list.add()
                ob_item.name = ob_s.name
                ob_item.type = ob_s.type


                   
        if context.scene.rename_list:
            bpy.ops.object.rename_ma()
            return {'CANCELLED'}            
        

        if App_info.type_select_light:
            light_objs = [ob for ob in objs_send if ob.type == 'LIGHT']
            if light_objs:
                if ul.update_light_to_center(light_objs):
                    print("send light")
                    send = True
                
        if App_info.type_select_camera:
            cam_objs = [ob for ob in objs_send if ob.type == 'CAMERA']
            if cam_objs:
                if uc.update_cam_to_center(cam_objs):
                    print("send camera")
                    send = True

        if App_info.type_select_material:
            mesh_objs = [ob for ob in objs_send if ob.type == 'MESH'] #link mesh to materal
            mat_objs = um.get_mat_from_mesh(mesh_objs) #only for check name 
            if mat_objs:                 
                if um.update_mat_to_center(mesh_objs):
                    print("send material")
                    send = True

        if App_info.type_select_mesh:
            mesh_objs = [ob for ob in objs_send if ob.type == 'MESH']
            if mesh_objs:       
                    if ums.update_mesh_to_center(mesh_objs):
                        print("send mesh")
                        send = True

        if send:
            print("......................send comlete......................")  
        else:  
            wr.ShowMessageBox(message="Dont have anythning to send. please check your setting", title="warning", icon='INFO')
        
        return {'FINISHED'}

class BMC_get(Operator):
    """Tooltip"""
    bl_idname = "object.get_from_maya"
    bl_label = "GET"

    def execute(self, context):
        
        App_info = context.window_manager 
        get = False
        if App_info.type_select_light:
            if gl.get_light_from_center():
                print("get light ")
                get = True
        if App_info.type_select_camera:
            if gc.get_camera_from_center():
                print("get camera ")
                get = True        
        if App_info.type_select_mesh:
            if gms.get_mesh_from_center():
                print("get mesh ")
                get = True
        if App_info.type_select_material:
            if gm.get_mat_from_center():
                print("get material ")
                get = True
                
        if get:
            print("......................object has get......................")            
        else:
            wr.ShowMessageBox(message="Dont have anythning to get. please check your setting", title="warning", icon='INFO')

        return {'FINISHED'}

class Rename_maya_popup(Operator):
    bl_idname = "object.rename_ma"
    bl_label = "rename for maya"

    # rename_obj = BoolProperty(default=False)
    # rename_mat = BoolProperty(default=False)

    def execute(self, context):
        wm = context.window_manager
        return wm.invoke_popup(self, width = 300)

    def draw(self, context):
       
        layout = self.layout
        scn = context.scene
        col = layout.column(align=True)  
        col.label(text = "Name is not support to transfer / Name duplicate.", icon = 'ERROR')

        # if self.rename_obj: 
        layout.template_list("MY_UL_List", "", scn,"rename_list", scn, "list_index")                 
        
        col = layout.column(align=True)   
        row = col.row(align=True)  
        row.scale_y = 1
        row.operator("object.rename_maya_op")

class rename_maya_OP(Operator):
    
    bl_idname = "object.rename_maya_op"
    bl_label = "Rename"

    def execute(self, context): 
        for item_rn in context.scene.rename_list:
            if item_rn.type in {"MESH","CAMERA","LIGHT"}:  
                new_name = rn.maya_name(item_rn.name)
                exist_name = bpy.data.objects.get(new_name)  
                cont = 0
                while exist_name: 
                    cont += 1                   
                    exist_name = bpy.data.objects.get(new_name + "_" + str(cont))                   
                if cont != 0 :
                     new_name = new_name + "_" + str(cont)
                bpy.data.objects[item_rn.name].name = new_name

            elif item_rn.type == "MAT_NODE":
                m_node = bpy.data.materials[item_rn.rt_m_name ].node_tree.nodes[item_rn.name]
                if item_rn.name_duplicate:                    
                    m_node.name = rn.maya_name(item_rn.rt_m_name) + "_" + m_node.name
                    # m_node.name = item_rn.rt_m_name + "_" + m_node.name
                if item_rn.name_illegal:                     
                    m_node_new_name = rn.maya_name(m_node.name)                     
                    m_node_exist_name = bpy.data.objects.get(m_node_new_name)  
                    cont = 0
                    while m_node_exist_name: 
                        cont += 1                   
                        m_node_exist_name = bpy.data.objects.get(m_node_new_name + "_" + str(cont))                   
                    if cont != 0 :
                        m_node_new_name = m_node_new_name + "_" + str(cont)
                    m_node.name = m_node_new_name
                
        for item_rn in context.scene.rename_list:    
            if item_rn.type == "MAT_SG":   
                m_sg = bpy.data.materials[item_rn.name]
                if item_rn.name_duplicate:                    
                    m_sg.name = m_sg.name + "_M"     
                if item_rn.name_illegal:
                    m_sg_new_name = rn.maya_name(m_sg.name)   
                    m_sg_exist_name = bpy.data.objects.get(m_sg_new_name)  
                    cont = 0
                    while m_sg_exist_name: 
                        cont += 1                   
                        m_sg_exist_name = bpy.data.objects.get(m_sg_new_name + "_" + str(cont))                   
                    if cont != 0 :
                        m_sg_new_name = m_sg_new_name + "_" + str(cont)
                    m_sg.name = m_sg_new_name
        
        context.scene.rename_list.clear()
        return {'FINISHED'}

class MY_UL_List(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        
        if item.type == "MESH":
            data_icon ='MESH_CUBE'
        elif item.type == "CAMERA":
            data_icon ='VIEW_CAMERA'
        elif item.type == "LIGHT":
            data_icon ='OUTLINER_OB_LIGHT'
        elif item.type == "MAT_SG":
            data_icon ='SHADING_RENDERED'
        elif item.type == "MAT_NODE":
            data_icon ='POINTCLOUD_DATA'
        else:
            data_icon ='OBJECT_DATAMODE'

        status = ""
        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:            
            if item.name_duplicate:
                status = "( d )"
            if item.name_illegal:
                status += "( i )"      

            if item.type == "MAT_NODE":               
                layout.label(text= item.rt_m_name  + " < " + item.name + " >" + status, icon = data_icon)
            else:
                layout.label(text=item.name + status, icon = data_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = data_icon)

class ListItem(PropertyGroup):

    name: StringProperty( description="name for item", default="Untitled")
    rt_m_name: StringProperty( description="name for root material for node ", default="")
    type: StringProperty( description="type of item", default="")
    name_duplicate:BoolProperty( description="name has duplicate", default=False)
    name_illegal:BoolProperty( description="name is not allowed in Maya", default=False)
         
classes = [
    BMC_get,
    BMC_send,
    Rename_maya_popup,  
    rename_maya_OP,    
    ListItem,
    MY_UL_List
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rename_list = CollectionProperty(type = ListItem)
    bpy.types.Scene.list_index = IntProperty(name = "Index for rename_list",default = 0)


def unregister():
    del bpy.types.Scene.rename_list
    del bpy.types.Scene.list_index
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()


 