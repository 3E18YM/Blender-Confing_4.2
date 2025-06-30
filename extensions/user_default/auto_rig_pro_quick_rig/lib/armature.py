import bpy

def sort_armature_collections(armature, only_collection=None):
    order = {'Main':0, 'Secondary':1, 'Orphan Bones':2, 'Deform':3, 'Reference':4}
    
    def get_col_idx(name):
        for i, coll in enumerate(armature.data.collections):          
            if coll.name == col_name:
                return i
        
    for col_name in order:
        if only_collection:
            if only_collection != col_name:
                continue
                
        col = armature.data.collections.get(col_name)  
        cur_idx = get_col_idx(col_name)
        to_idx = order[col_name]       
        armature.data.collections.move(cur_idx, to_idx)
        

def is_bone_in_layer(bone_name, layer_type, idx=None):
    if bpy.app.version >= (4,0,0):
        if bpy.context.mode == 'EDIT_ARMATURE':# # in Edit mode, access edit bones only. Prone to error otherwise (bone data not up to date)
            in_collection = [ebone.name for ebone in bpy.context.active_object.data.edit_bones if layer_type in ebone.collections]
            return bone_name in in_collection
        else:
            return layer_type in bpy.context.active_object.data.bones.get(bone_name).collections
    else:      
        if bpy.context.mode == 'EDIT_ARMATURE':# in Edit mode, access edit bones only. Prone to error otherwise (bone data not up to date)
            return bpy.context.active_object.data.edit_bones.get(bone_name).layers[idx]
        else:
            return bpy.context.active_object.data.bones.get(bone_name).layers[idx]


def enable_layer(layer_type, idx=None):
    if bpy.app.version >= (4,0,0):
        col = bpy.context.active_object.data.collections.get(layer_type)
        col.is_visible = True
    else:
        bpy.context.active_object.data.layers[idx] = True
        
        
def hide_layer(layer_type, idx=None):
    if bpy.app.version >= (4,0,0):
        col = bpy.context.active_object.data.collections.get(layer_type)
        col.is_visible = False
    else:     
        bpy.context.active_object.data.layers[idx] = False


def set_bone_layer(bone, layer_type, idx=None, multi=False):
    if bpy.app.version >= (4,0,0):
        arma = bpy.context.active_object
        col = arma.data.collections.get(layer_type)
        if col == None:# create the collection if necessary
            col = arma.data.collections.new(layer_type)
            col.is_visible = False
            
        if bpy.context.mode == 'EDIT_ARMATURE':
            col.assign(bone)
        else:
            col.assign(arma.data.bones[bone.name])
        
        if multi:
            return
            
        for col in arma.data.collections:
            if col.name != layer_type:
                if bpy.context.mode == 'EDIT_ARMATURE':
                    col.unassign(bone)
                else:
                    col.unassign(arma.data.bones[bone.name])
        
    else:
        bone.layers[idx] = True
        
        if multi:
            return
            
        for i, lay in enumerate(bone.layers):
            if i != idx:
                bone.layers[i] = False