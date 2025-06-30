import bpy
import json
from . import warning_info as wr

def get_light_from_center():

    try:
        with open(bpy.context.window_manager.file_path + 'MA_LightUpdate.json') as json_file:
            light_data = json.load(json_file) 
    except:        
        return False

    print("after errror")
    backup_link_data = []  
    backup_parent_data = []     
    for lgh in light_data: #save exist object transformation data   
        if bpy.data.objects.get(lgh["light_name"]) is not None:
            obj_delete = bpy.data.objects[lgh["light_name"]]
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
            backup_parent_data.append({"obj_exist": lgh["light_name"], 
                                            "parent": obj_parent, 
                                            "child": obj_child,
                                            "transform":exist_transform,
                                            "collection":users_colls[0]
                                            })    
           
    for lgh in light_data:        
        if bpy.data.objects.get(lgh["light_name"]) is not None:
            obj_delete = bpy.data.objects[lgh["light_name"]]            
            bpy.data.objects.remove(obj_delete, do_unlink=True)   
    bpy.ops.outliner.orphans_purge()

    try:
        bpy.ops.wm.alembic_import(  filepath=(bpy.context.window_manager.file_path + "MA_LightTransfer.abc"),
                                    scale = bpy.context.window_manager.Scene_Scale )
    except:
        return False

    for lgh in light_data:        
        lgh_empty = bpy.data.objects[lgh["light_name"]]   
        lgh_empty_transform = lgh_empty.matrix_world.copy()  
        bpy.data.objects.remove(lgh_empty, do_unlink=True) #remove import light transform
        light_multiply = bpy.context.window_manager.Light_mult

        if lgh["type"] == "SUN":
            lgh_sun = bpy.data.lights.new(name=lgh["light_name"], type='SUN')
            lgh_sun.color = (lgh["color"]["r"],lgh["color"]["g"],lgh["color"]["b"])
            lgh_sun.energy = lgh["intensity"]*light_multiply

            lgh_sun_tf = bpy.data.objects.new(name=lgh["light_name"], object_data=lgh_sun)
            bpy.context.collection.objects.link(lgh_sun_tf)
            lgh_sun_tf.matrix_world = lgh_empty_transform
        #    lgh_sun.matrix_world = lgh_empty_transform
            
        elif lgh["type"] == "SPOT":
            lgh_spot = bpy.data.lights.new(name=lgh["light_name"], type='SPOT')
            lgh_spot.color = (lgh["color"]["r"],lgh["color"]["g"],lgh["color"]["b"])
            lgh_spot.energy = lgh["intensity"]*light_multiply

            lgh_spot_tf = bpy.data.objects.new(name=lgh["light_name"], object_data=lgh_spot)
            bpy.context.collection.objects.link(lgh_spot_tf)
            lgh_spot_tf.matrix_world = lgh_empty_transform            

        elif lgh["type"] == "AREA":
            lgh_area = bpy.data.lights.new(name=lgh["light_name"], type='AREA')
            lgh_area.color = (lgh["color"]["r"],lgh["color"]["g"],lgh["color"]["b"])
            lgh_area.energy = lgh["intensity"]*light_multiply

            lgh_area_tf = bpy.data.objects.new(name=lgh["light_name"], object_data=lgh_area)
            bpy.context.collection.objects.link(lgh_area_tf)
            lgh_area_tf.matrix_world = lgh_empty_transform           

            if lgh["shape"] == "RECTANGLE":
                lgh_area.size = lgh["size"]["x"] * 2 # multiply 2 for asjust sizing same in Maya
                lgh_area.size_y = lgh["size"]["y"] * 2
                lgh_area.shape = "RECTANGLE" 
            else:
                lgh_area.size = lgh["size"]["x"] * 2 
                lgh_area.size_y = lgh["size"]["y"] * 2
                lgh_area.shape = "ELLIPSE" 
        
        else:
            lgh_point = bpy.data.lights.new(name=lgh["light_name"], type='POINT')
            lgh_point.color = (lgh["color"]["r"],lgh["color"]["g"],lgh["color"]["b"])
            lgh_point.energy = lgh["intensity"]*light_multiply

            lgh_point_tf = bpy.data.objects.new(name=lgh["light_name"], object_data=lgh_point)
            bpy.context.collection.objects.link(lgh_point_tf)
            lgh_point_tf.matrix_world = lgh_empty_transform
            lgh_point.shadow_soft_size = lgh["redius"]

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