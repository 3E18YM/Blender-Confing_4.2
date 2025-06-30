import bpy
import os
import json
# from . import rename_for_maya as rn

def update_mesh_to_center(mesh_objs):
    ms_indx = 0
    msh_list = []
    wr_list = [] 
    parent_list = []
    un_parent_wp = {}
    disable_select_backup = []
    visible_select_backup = []

    bpy.ops.object.select_all(action='DESELECT')
    for mesh in mesh_objs:
        if mesh.parent: #Unparent first befor send
            parent_list.append({"obj":mesh.name,"parent":mesh.parent.name })
            parent_wp = mesh.matrix_world.copy()            
            mesh.parent = None
            un_parent_wp[mesh.name] = mesh.matrix_world.copy()   
            mesh.matrix_world = parent_wp
        
        if mesh.hide_select:
            mesh.hide_select = False
            disable_select_backup.append(mesh)

        if not mesh.visible_get():   
            mesh.hide_set(False)
            visible_select_backup.append(mesh)

        mesh.select_set(True)

        sg_list = []
        for m in mesh.material_slots:
                sg_list.append(m.name)   

        uv_set = mesh.data.uv_layers.active
        if uv_set:  
            uv_set_dt = uv_set.name      
        else:
            uv_set_dt = None              

        wr_list.insert(ms_indx,{"mesh_name": mesh.name,
                                "sg_name": sg_list,
                                "uv_set": uv_set_dt}) #do not rename for Maya. UV set can be naming all character !!! 
        ms_indx += 1
    
    try:     
        with open(bpy.context.window_manager.file_path +"BL_MeshUpdate.json", "w") as file:
            json.dump(wr_list,file,indent=2,sort_keys=False) 

        bpy.ops.wm.alembic_export(  filepath=(bpy.context.window_manager.file_path + "BL_MeshTransfer.abc"),
                                            face_sets=True,
                                            selected=True,
                                            global_scale = bpy.context.window_manager.Scene_Scale )
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