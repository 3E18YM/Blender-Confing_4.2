import bpy
import os
import json
# from . import rename_for_maya as rn

def update_cam_to_center(cam_objs):
    cm_indx = 0
    wr_list = [] 
    parent_list = []
    un_parent_wp = {}
    disable_select_backup = []
    visible_select_backup = []

    bpy.ops.object.select_all(action='DESELECT')
    for cam in cam_objs:
        if cam.parent: #Unparent first befor send
            # print(cam.name + " un parent to -- >" +  cam.parent.name )
            parent_list.append({"obj":cam.name,"parent":cam.parent.name })
            parent_wp = cam.matrix_world.copy()            
            cam.parent = None
            un_parent_wp[cam.name] = cam.matrix_world.copy()   
            cam.matrix_world = parent_wp

        if cam.hide_select:
            cam.hide_select = False
            disable_select_backup.append(cam)

        if not cam.visible_get():   
            cam.hide_set(False)
            visible_select_backup.append(cam)

        cam.select_set(True)
        
        wr_list.insert(cm_indx,{"cam_name": cam.name})
        cm_indx += 1
    
    try:
        with open(bpy.context.window_manager.file_path +"BL_CameraUpdate.json", "w") as file:
            json.dump(wr_list,file,indent=2,sort_keys=False)   

        bpy.ops.wm.alembic_export(  filepath=(bpy.context.window_manager.file_path+"BL_CameraTransfer.abc"),
                                            face_sets=True,
                                            selected=True,
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