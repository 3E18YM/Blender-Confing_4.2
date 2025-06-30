import bpy

def get_bone_side(bone_name):
    side = ""
    if not "_dupli_" in bone_name:
        side = bone_name[-2:]
    else:
        side = bone_name[-12:]
    return side
    
    
def get_bone_base_name(bone_name):
    base_name = bone_name[:-2]# head.x > head
    if "_dupli_" in bone_name:
        base_name = bone_name[:-12]
    return base_name