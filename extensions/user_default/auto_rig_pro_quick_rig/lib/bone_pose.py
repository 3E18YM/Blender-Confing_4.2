import bpy
from .version import blender_version

def get_pose_bone(name):
    return bpy.context.active_object.pose.bones.get(name)
    
    
def get_custom_shape_scale_prop_name():
    if blender_version._float >= 300:
        return 'custom_shape_scale_xyz'
    else:
        return 'custom_shape_scale'
        
    
def set_custom_shape_scale(pbone, scale):	
    if blender_version._float >= 300:
        # uniform scale
        if type(scale) == int or type(scale) == float:
            for i in range(0,3):
                pbone.custom_shape_scale_xyz[i] = scale
        # array scale
        else:
            pbone.custom_shape_scale_xyz = scale
    # pre-Blender 3.0
    else:
        pbone.custom_shape_scale = scale
            

def get_custom_shape_scale(pbone, uniform=True):    
    if blender_version._float >= 300:
        if uniform:       
            # uniform scale
            val = 0
            for i in range(0,3):
                val += pbone.custom_shape_scale_xyz[i]
            return val/3     
        # array scale
        else:
            return pbone.custom_shape_scale_xyz
    # pre-Blender 3.0
    else:        
        return pbone.custom_shape_scale
        
        
def set_bone_color(bone_data, bcolors):
    if type(bcolors) == str:# set the color palette string
        bone_data.color.palette = bcolors
    else:# set the color lists
        col_normal, col_select, col_active = bcolors
        bone_data.color.palette = 'CUSTOM'
        bone_data.color.custom.normal = col_normal
        bone_data.color.custom.select = col_select
        bone_data.color.custom.active = col_active