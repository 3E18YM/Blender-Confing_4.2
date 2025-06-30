import bpy
from math import *
from mathutils import *
from .maths_geo import *


def get_bone_children(bname, single_child_only=False):
    children_list = []
    children_list = get_bone_children_recursive(bname, list=children_list, single=single_child_only)
    return children_list
    
    
def get_bone_children_recursive(bname, list=None, single=False):
    _b = bpy.context.active_object.data.bones.get(bname)
    if _b.children:
        for _bi, child in enumerate(_b.children):
            if single:
                if _bi > 0:
                    break
            list.append(child.name)
            get_bone_children_recursive(child.name, list=list, single=single)

    return list


def get_edit_bone(name):
    if name == None:
        return None
    return bpy.context.object.data.edit_bones.get(name)
    
    
def align_bone_x_axis(edit_bone, new_x_axis):
    new_x_axis = new_x_axis.cross(edit_bone.y_axis)
    new_x_axis.normalize()
    dot = max(-1.0, min(1.0, edit_bone.z_axis.dot(new_x_axis)))
    angle = acos(dot)
    edit_bone.roll += angle
    dot1 = edit_bone.z_axis.dot(new_x_axis)
    edit_bone.roll -= angle * 2.0
    dot2 = edit_bone.z_axis.dot(new_x_axis)
    if dot1 > dot2:
        edit_bone.roll += angle * 2.0
        
        
def align_bone_z_axis(edit_bone, new_z_axis):
    new_z_axis = -(new_z_axis.cross(edit_bone.y_axis))
    new_z_axis.normalize()
    dot = max(-1.0, min(1.0, edit_bone.x_axis.dot(new_z_axis)))
    angle = acos(dot)
    edit_bone.roll += angle
    dot1 = edit_bone.x_axis.dot(new_z_axis)
    edit_bone.roll -= angle * 2.0
    dot2 = edit_bone.x_axis.dot(new_z_axis)
    if dot1 > dot2:
        edit_bone.roll += angle * 2.0