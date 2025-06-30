import bpy
import json

def get_mesh_from_center():    
    try:
        with open(bpy.context.window_manager.file_path + 'MA_MeshUpdate.json') as json_file:
            mesh_data = json.load(json_file) 
    except:
        return False

    backup_link_data = []  
    backup_parent_data = []     
    for msh in mesh_data: #save exist object transformation data   
        if bpy.data.objects.get(msh["mesh_name"]) is not None:
            obj_delete = bpy.data.objects[msh["mesh_name"]]
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
            backup_parent_data.append({"obj_exist": msh["mesh_name"], 
                                            "parent": obj_parent, 
                                            "child": obj_child,
                                            "transform":exist_transform,
                                            "collection":users_colls[0]
                                            })    
           
    for msh in mesh_data:#delete exist mesh       
        if bpy.data.objects.get(msh["mesh_name"]) is not None:
            obj_delete = bpy.data.objects[msh["mesh_name"]]            
            bpy.data.objects.remove(obj_delete, do_unlink=True)   
    bpy.ops.outliner.orphans_purge()

    try:
        bpy.ops.wm.alembic_import(  filepath=(bpy.context.window_manager.file_path + "MA_MeshTransfer.abc"),
                                    scale = bpy.context.window_manager.Scene_Scale )
    except:
        return False

    for msh in mesh_data:
        print(msh["sg_name"])
        if bpy.data.objects.get(msh["mesh_name"]) is not None:
            msh_sg = bpy.data.objects[msh["mesh_name"]]

            exist_sg_list = []
            for m in msh_sg.material_slots:     
                if m.name not in exist_sg_list:           
                    exist_sg_list.append(m.name)
        
            for sg_dt in msh["sg_name"]:
                if sg_dt not in exist_sg_list :
                    if bpy.data.materials.get(sg_dt):
                        assign_mat = bpy.data.materials[sg_dt]
                    else:
                        assign_mat = bpy.data.materials.new(name = sg_dt)

                    msh_sg.data.materials.append(assign_mat)
    
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