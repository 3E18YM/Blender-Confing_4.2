import bpy
import json

def get_camera_from_center():    
    try:
        with open(bpy.context.window_manager.file_path + 'MA_CameraUpdate.json') as json_file:
            cam_data = json.load(json_file)     
    except:
        return False

    backup_link_data = []  
    backup_parent_data = []     
    for tf_msh in cam_data: #save exist object transformation data   
        if bpy.data.objects.get(tf_msh["cam_name"]) is not None:
            obj_delete = bpy.data.objects[tf_msh["cam_name"]]
            users_colls = obj_delete.users_collection

            if obj_delete.parent: 
                obj_parent = obj_delete.parent.name
            else:
                obj_parent = None
            
            if obj_delete.children:
                obj_child = []
                for ch in obj_delete.children:
                    obj_child.append(ch.name)
                    ch.parent = None 
            else:
                obj_child = None           
           
            exist_transform = obj_delete.matrix_world.copy() 
            backup_parent_data.append({"obj_exist": tf_msh["cam_name"], 
                                            "parent": obj_parent, 
                                            "child": obj_child,
                                            "transform":exist_transform,
                                            "collection":users_colls[0]
                                            })    
           
    for tf_msh in cam_data:        
        if bpy.data.objects.get(tf_msh["cam_name"]) is not None:
            obj_delete = bpy.data.objects[tf_msh["cam_name"]]            
            bpy.data.objects.remove(obj_delete, do_unlink=True)   
    bpy.ops.outliner.orphans_purge()

    try:
        bpy.ops.wm.alembic_import(  filepath=(bpy.context.window_manager.file_path + "MA_CameraTransfer.abc"),
                                    scale = bpy.context.window_manager.Scene_Scale )
    except:
        return False
    
    for re_parent in backup_parent_data:# reparent object
        re_tf_obj  = bpy.data.objects[re_parent["obj_exist"]]     

        re_tf_obj.users_collection[0].objects.unlink(re_tf_obj) 
        if re_parent["collection"].objects.get(re_parent["obj_exist"]) is None: #re link to collection
            re_parent["collection"].objects.link(re_tf_obj)   

        if bpy.context.window_manager.keep_transform:                
            re_tf_obj.matrix_world = re_parent["transform"]        
        if re_parent["parent"]:  
            ob_tf_parent = bpy.data.objects[re_parent["parent"]]      
            re_tf_obj.parent = ob_tf_parent
            re_tf_obj.matrix_parent_inverse = ob_tf_parent.matrix_world.inverted()
        
        if re_parent["child"]:
            for chi in re_parent["child"]:    
                ob_tf_child  = bpy.data.objects[chi]    
                ob_tf_child.parent =  re_tf_obj
                ob_tf_child.matrix_parent_inverse = re_tf_obj.matrix_world.inverted()

    return True