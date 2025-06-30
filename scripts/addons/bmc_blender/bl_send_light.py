import bpy
import os
import json
import math
# from . import rename_for_maya as rn

def update_light_to_center(light_objs):
    l_indx = 0
    wr_list = [] 
    parent_list = []
    un_parent_wp = {}
    disable_select_backup = []
    visible_select_backup = []

    App_info = bpy.context.window_manager

    for lgh in light_objs:
        wr_list.insert(l_indx,{"light_name": lgh.name})
        wr_list[l_indx]["type"] = lgh.data.type #store light type SUN/AREA/SPOT/POINT
        wr_list[l_indx]["intensity"] = lgh.data.energy

        wr_list[l_indx]["color"] = {"r":lgh.data.color.r ,
                                    "g":lgh.data.color.g ,
                                    "b":lgh.data.color.b}      
        
        if lgh.data.type == "AREA":
            if lgh.data.shape=="SQUARE":
                wr_list[l_indx]["shape"] = lgh.data.shape  
                wr_list[l_indx]["size"] = {"x":lgh.data.size,"y":lgh.data.size}
            elif lgh.data.shape=="RECTANGLE":
                wr_list[l_indx]["shape"] = lgh.data.shape  
                wr_list[l_indx]["size"] = {"x":lgh.data.size,"y":lgh.data.size_y}
            elif lgh.data.shape=="DISK":
                wr_list[l_indx]["shape"] = lgh.data.shape  
                wr_list[l_indx]["size"] = {"x":lgh.data.size,"y":lgh.data.size}
            else:
                wr_list[l_indx]["shape"] = lgh.data.shape  
                wr_list[l_indx]["size"] = {"x":lgh.data.size,"y":lgh.data.size_y}
        elif lgh.data.type == "SPOT":
            wr_list[l_indx]["shadowSoft"] = lgh.data.shadow_soft_size  
            wr_list[l_indx]["coneSize"] = math.degrees(lgh.data.spot_size)
        elif lgh.data.type == "POINT":
            wr_list[l_indx]["redius"] = lgh.data.shadow_soft_size 

        l_indx += 1
    try:    
        with open(bpy.context.window_manager.file_path +"BL_LightUpdate.json", "w") as file:
            json.dump(wr_list,file,indent=2,sort_keys=False)   
    except:
        return False

    bpy.ops.object.select_all(action='DESELECT')

    for lgh_ob in light_objs:
        if lgh_ob.parent: #Unparent first befor send
            parent_list.append({"obj":lgh_ob.name,"parent":lgh_ob.parent.name })
            parent_wp = lgh_ob.matrix_world.copy()            
            lgh_ob.parent = None
            un_parent_wp[lgh_ob.name] = lgh_ob.matrix_world.copy()   
            lgh_ob.matrix_world = parent_wp

        if lgh_ob.hide_select:
            lgh_ob.hide_select = False
            disable_select_backup.append(lgh_ob)

        if not lgh_ob.visible_get():   
            lgh_ob.hide_set(False)
            visible_select_backup.append(lgh_ob)

        lgh_ob.select_set(True)
    try:
        bpy.ops.wm.alembic_export(  filepath=(bpy.context.window_manager.file_path+"BL_LightTransfer.abc"),
                                            face_sets = True,
                                            selected = True,
                                            global_scale  = bpy.context.window_manager.Scene_Scale )
    except:
        return False
    
    objects = bpy.data.objects
    for pr_dat in parent_list: #Reparent
        
        obj_c = objects[pr_dat["obj"]]
        obj_p = objects[pr_dat["parent"]]   
        
        obj_c.parent = obj_p
        obj_c.matrix_world = un_parent_wp[obj_c.name] 
    
    for re_disable_select in disable_select_backup:
        print("re_disable_select")
        re_disable_select.hide_select = True

    for re_visible in visible_select_backup:
        re_visible.hide_set(True)
    
    return True