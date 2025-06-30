bl_info = {
    "name": "Synced Modifiers",
    "author": "Amandeep",
    "description": "Add modifiers to multiple objects and sync them using Drivers",
    "blender": (2, 91, 0),
    "version": (2, 2, 0),
    "location": "N-Panel > Item > Synced Modifiers",
    "warning": "",
    "category": "Object",
}

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import os
import inspect
import re as regex
from .properties_data_modifiers import *
def get_collection(name):
    if name not in bpy.data.collections:
        bpy.data.collections.new(name)
        col = bpy.data.collections[name]
        bpy.context.scene.collection.children.link(col)
        return col
    return bpy.data.collections[name]
def link_to_collection(obj, col):
    
        if isinstance(col, str):
            if col in bpy.data.collections:
                bpy.data.collections[col].objects.link(obj)
        else:
            if col.name in bpy.data.collections:
                col.objects.link(obj)
def move_to_collection(obj, col):
    if col not in bpy.data.collections:
        bpy.data.collections.new(col)
        col = bpy.data.collections[col]
        bpy.context.scene.collection.children.link(col)
    else:
        col=bpy.data.collections[col]

    cols = obj.users_collection
    for c in cols:
        c.objects.unlink(obj)
    link_to_collection(obj, col)
def deselect_all():
    if bpy.context.mode=='OBJECT':
        bpy.ops.object.select_all( action='DESELECT')
    elif 'EDIT' in bpy.context.mode:
        bpy.ops.mesh.select_all( action='DESELECT')
def delete_object_with_data(obj):
    if obj and obj.name in bpy.data.objects:
        data=obj.data
        isMesh=obj.type=='MESH'
        bpy.data.objects.remove(obj, do_unlink=True)
        if isMesh:
            bpy.data.meshes.remove(data)
def delete_collection(col, delete_objects = False):
    colref = None
    if isinstance(col, str):
            colref = get_collection(col)
    else:
        colref = col

    if delete_objects:
        deselect_all()
        if len(colref.objects) > 0:
            for co in colref.objects:
                delete_object_with_data(co)
                #co.select_set(True)
            #delete_selected_objects()
    else:
        deselect_all()
        if len(colref.objects) > 0:
            for co in colref.objects:
                bpy.context.scene.collection.objects.link(co)

    bpy.data.collections.remove(colref)
def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found
def select(obj,active=True):
    try:
        if obj:
            obj.select_set(True)
            if active:
                bpy.context.view_layer.objects.active = obj
    except:
        pass
def preferences():
    return bpy.context.preferences.addons[__package__].preferences
def sync_modifiers(modifiers,active):
    mod=modifiers[len(modifiers)-1][1]
    if mod.name not in active.SyncedModifierInfo:
        t=active.SyncedModifierInfo.add()
        t.name=mod.name
        active.SyncedModifierIndex=len(active.SyncedModifierInfo)-1
    for obj,o_mod in modifiers[:-1]:
        if o_mod:
                        desyncmodifiers(obj,o_mod)
                        props=[ key for key, value in inspect.getmembers(o_mod) if key not in requiresObject and key not in {'name','is_active','vertex_group','filepath','driver','end_cap','start_cap','collection','armature','rim_vertex_group','shell_vertex_group','grid_name','execution_time',
                                "execution_time","is_cached",
                                "is_bound",
                                "is_bind",
                                "vertex_indices",
                                "vertex_indices_set",
                                "matrix_inverse",
                                "falloff_curve",
                                "vertex_velocities",
                                "read_velocity",
                                "has_velocity",
                                "map_curve",
                                "projectors",
                                "__doc__",
                                "__module__",
                                "__slotnames__",
                                "__slots__",
                                "bl_rna",
                                "rna_type",
                                "debug_options",
                                "type",
                                "object",
                                "delimit",
                                "custom_profile",
                                "face_count",
                                "is_external","cache_file","object_path","mask_tex_map_bone","mask_tex_map_object","mask_tex_uv_layer","mask_texture","mask_vertex_group","vertex_group_a","vertex_group_b","use_bone_envelopes","use_vertex_groups",
                                "total_levels",'texture','texture_coords_bone','texture_coords_object','uv_layer','auxiliary_target','origin','bone_from','bone_to','object_from','object_to','start_position_object',
                                "subtarget",'is_override_data'
                            }]
                            
                        props=do_props(props,o_mod.type)
                        #print(props)
                        add_driver(props,o_mod,mod,active)
                        t=obj.SyncedModifierInfo.add()
                        t.name=o_mod.name
                        obj.SyncedModifierIndex=len(obj.SyncedModifierInfo)-1
mod_object_field={
    'MIRROR':'mirror_object',
    'ARRAY':'offset_object',
    'CURVE':'object',
    'BOOLEAN':'object',
    'SCREW':'object',
    'CAST':'object',
    'HOOK':'object',
    'LATTICE':'object',
    'SHRINKWRAP':'target',
    'SIMPLE_DEFORM':'origin',
    'SURFACE_DEFORM':'origin',
    'DATA_TRANSFER':'object',
    'NORMAL_EDIT':'target',
    'VERTEX_WEIGHT_PROXIMITY':'target',
    

}
icons={'MULTIRES': 'MOD_MULTIRES',
'ARRAY': 'MOD_ARRAY',
'BEVEL': 'MOD_BEVEL',
'BOOLEAN': 'MOD_BOOLEAN',
'BUILD': 'MOD_BUILD',
'DECIMATE': 'MOD_DECIM',
'EDGE_SPLIT': 'MOD_EDGESPLIT',
'NODES': 'MOD_NODES',
'MASK': 'MOD_MASK',
'MIRROR': 'MOD_MIRROR',
'REMESH': 'MOD_REMESH',
'SCREW': 'MOD_SCREW',
'SKIN': 'MOD_SKIN',
'SOLIDIFY': 'MOD_SOLIDIFY',
'SUBSURF': 'MOD_SUBSURF',
'TRIANGULATE': 'MOD_TRIANGULATE',
'VOLUME_TO_MESH': 'VOLUME_DATA',
'WELD': 'AUTOMERGE_ON',
'WIREFRAME': 'MOD_WIREFRAME',
'ARMATURE': 'MOD_ARMATURE',
'CAST': 'MOD_CAST',
'CURVE': 'MOD_CURVE',
'DISPLACE': 'MOD_DISPLACE',
'HOOK': 'HOOK',
'LAPLACIANDEFORM': 'MOD_MESHDEFORM',
'LATTICE': 'MOD_LATTICE',
'MESH_DEFORM': 'MOD_MESHDEFORM',
'SHRINKWRAP': 'MOD_SHRINKWRAP',
'SIMPLE_DEFORM': 'MOD_SIMPLEDEFORM',
'SMOOTH': 'MOD_SMOOTH',
'CORRECTIVE_SMOOTH': 'MOD_SMOOTH',
'LAPLACIANSMOOTH': 'MOD_SMOOTH',
'SURFACE_DEFORM': 'MOD_MESHDEFORM',
'WARP': 'MOD_WARP',
'WAVE': 'MOD_WAVE',
'DATA_TRANSFER': 'MOD_DATA_TRANSFER',
'MESH_CACHE': 'MOD_MESHDEFORM',
'MESH_SEQUENCE_CACHE': 'MOD_MESHDEFORM',
'NORMAL_EDIT': 'MOD_NORMALEDIT',
'WEIGHTED_NORMAL': 'MOD_NORMALEDIT',
'UV_PROJECT': 'MOD_UVPROJECT',
'UV_WARP': 'MOD_UVPROJECT',
'VERTEX_WEIGHT_EDIT': 'MOD_VERTEX_WEIGHT',
'VERTEX_WEIGHT_MIX': 'MOD_VERTEX_WEIGHT',
'VERTEX_WEIGHT_PROXIMITY': 'MOD_VERTEX_WEIGHT',
'OCEAN':'MOD_OCEAN',
'EXPLODE': 'MOD_EXPLODE'}
requiresObject = ["curve", "object", "offset_object", "mirror_object", "target"]
array_props={'MIRROR_use_axis':3,'MIRROR_use_bisect_axis':3,'MIRROR_use_bisect_flip_axis':3,'ARRAY_constant_offset_displace':3,'ARRAY_relative_offset_displace':3,'SIMPLE_DEFORM_limits':2,'NORMAL_EDIT_offset':3,'UV_WARP_center':2,'UV_WARP_offset':2,'UV_WARP_scale':2,'HOOK_center':2}
def do_props(props,mod_type):
    props_present=[prop for prop in [a.replace(mod_type+"_","") for a in array_props.keys()] if prop in props]
    array=props
    for p in props_present:
        pos = array.index(p)
        array=props[:pos]
        rem_array=props[pos+1:]
        for i in range(0,array_props[mod_type+"_"+p]):
            array.append(f'{p}[{i}]')  
        array = array + rem_array
        props=array
    return array
def Diff(li1, li2):
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))
def add_driver(target_properties,target_modifier,source_modifier,source_object):
    #print(target_modifier.name)
    for target_property in target_properties:
        #print(target_property)
        if "[" in target_property:
            index=regex.search(r"\[(.*)\]",target_property)
            if index:
                index=index[1]
                tp=target_property[:target_property.rindex("[")]
                driver=target_modifier.driver_add(tp,eval(index))
        else:
            tp=target_property
            driver=target_modifier.driver_add(target_property)
        var = driver.driver.variables.new()
        var.name = tp
        var.targets[0].data_path = f'modifiers["{source_modifier.name}"].{target_property}'
        var.targets[0].id_type='OBJECT'
        var.targets[0].id = source_object
        driver.driver.expression = f"{tp}"
        driver.driver.expression += " "
        driver.driver.expression = driver.driver.expression[:-1]
modify_mods= ['DATA_TRANSFER', 'MESH_CACHE', 'MESH_SEQUENCE_CACHE', 'NORMAL_EDIT', 'WEIGHTED_NORMAL', 'UV_PROJECT', 'UV_WARP', 'VERTEX_WEIGHT_EDIT', 'VERTEX_WEIGHT_MIX', 'VERTEX_WEIGHT_PROXIMITY']
generate_mods=['ARRAY', 'BEVEL', 'BOOLEAN', 'BUILD', 'DECIMATE', 'EDGE_SPLIT', 'MASK', 'MIRROR', 'REMESH', 'SCREW', 'SKIN', 'SOLIDIFY', 'SUBSURF', 'TRIANGULATE', 'VOLUME_TO_MESH', 'WELD', 'WIREFRAME']
deform_mods=['ARMATURE', 'CAST', 'CURVE', 'DISPLACE', 'HOOK', 'LAPLACIANDEFORM', 'LATTICE', 'MESH_DEFORM', 'SHRINKWRAP', 'SIMPLE_DEFORM', 'SMOOTH', 'CORRECTIVE_SMOOTH', 'LAPLACIANSMOOTH', 'SURFACE_DEFORM', 'WARP', 'WAVE',]
physics_mods=[ 'CLOTH', 'COLLISION', 'DYNAMIC_PAINT', 'EXPLODE', 'FLUID', 'OCEAN', 'PARTICLE_INSTANCE', 'PARTICLE_SYSTEM', 'SOFT_BODY', 'SURFACE']
class RTOOLS_UL_Synced_Mods_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        
        rs = item
        if rs and rs.name in [m.name for m in data.modifiers]:
            row=layout.row()
            row.label(text=rs.name)
            #row.prop(rs, "name", text="", emboss=False)
class RTOOLS_OT_SyncedPanel(bpy.types.Operator):
    bl_idname = "rtools.synced_modifiers_panel"
    bl_label = "Synced Modifiers Panel"
    bl_description = "Synced Modifiers Panel"
    bl_options = {'REGISTER', 'UNDO'}
    def draw(self,context):
        layout= self.layout
        layout.menu("RTOOLS_MT_Synced_Mods_Add_Menu",icon="MODIFIER")
        layout.operator("rtools.syncexistingmodifiers")
        column=layout
        ob=context.active_object
        
        
        if ob:
            
            column=column.split(factor=0.88)
            column.template_list("RTOOLS_UL_Synced_Mods_List", "", ob, "SyncedModifierInfo",ob, "SyncedModifierIndex",item_dyntip_propname='name',sort_reverse=False)
            column=column.column(align=True)
            column.label(text="")
            column.operator("rtools.refreshsyncedmodifiers",text="",icon="FILE_REFRESH")
            column.operator("rtools.desyncmodifiers",text="",icon="REMOVE")
            column.separator()
            column.operator("rtools.clearunuseddrivers",text="",icon="TRASH")
            if ob.SyncedModifierIndex>=0 and ob.SyncedModifierIndex<len(ob.SyncedModifierInfo) and ob.SyncedModifierInfo[ob.SyncedModifierIndex].name in [mod.name for mod in ob.modifiers]:
                m=ob.modifiers[ob.SyncedModifierInfo[ob.SyncedModifierIndex].name]
                m2=m.name
                ob2=ob
                if ob.animation_data and ob.animation_data.drivers:
                    for driver in ob.animation_data.drivers:
                        
                        if f'modifiers["{m.name}"]' in  driver.data_path:
                            #print(f'modifiers["{m.name}"]',driver.data_path)
                            path=driver.driver.variables[0].targets[0].data_path
                            ob2=driver.driver.variables[0].targets[0].id
                            m2=path[path.index("[")+2:path.index("]")-1]
                            #print(m2,ob2)
                            break
                
                if ob2 and m2 in [t.name for t in ob2.modifiers]:
                    layout.separator(factor=0)
                    box=layout.box()
                    row=box.row(align=True)
                    row=row.split(factor=0.6)
                    row.label(text=m.name)
                    row.prop(ob2.modifiers[m2],'show_viewport',text="",icon="RESTRICT_VIEW_ON")
                    row.prop(ob2.modifiers[m2],'show_render',text="",icon="RESTRICT_RENDER_ON")
                    eval(f'{m.type}(self,box,ob2,ob2.modifiers["{m2}"])')
    def invoke(self, context,event):
        return context.window_manager.invoke_popup(self)
    def execute(self, context):
        return {'FINISHED'}
class RTOOLS_PT_SM_Addon(bpy.types.Panel):
    bl_label = "Synced Modifiers"
    bl_idname = "OBJECT_PT_SYNCED_MODS"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    
    def draw(self, context):
        layout= self.layout
        layout.menu("RTOOLS_MT_Synced_Mods_Add_Menu",icon="MODIFIER")
        layout.operator("rtools.syncexistingmodifiers")
        column=layout
        ob=context.active_object
        
        
        if ob:
            
            column=column.split(factor=0.88)
            column.template_list("RTOOLS_UL_Synced_Mods_List", "", ob, "SyncedModifierInfo",ob, "SyncedModifierIndex",item_dyntip_propname='name',sort_reverse=False)
            column=column.column(align=True)
            column.label(text="")
            column.operator("rtools.refreshsyncedmodifiers",text="",icon="FILE_REFRESH")
            column.operator("rtools.desyncmodifiers",text="",icon="REMOVE")
            column.separator()
            column.operator("rtools.clearunuseddrivers",text="",icon="TRASH")
            
            if ob.SyncedModifierIndex>=0 and ob.SyncedModifierIndex<len(ob.SyncedModifierInfo) and ob.SyncedModifierInfo[ob.SyncedModifierIndex].name in [mod.name for mod in ob.modifiers]:
                m=ob.modifiers[ob.SyncedModifierInfo[ob.SyncedModifierIndex].name]
                m2=m.name
                ob2=ob
                if ob.animation_data and ob.animation_data.drivers:
                    for driver in ob.animation_data.drivers:
                        
                        if f'modifiers["{m.name}"]' in  driver.data_path:
                            #print(f'modifiers["{m.name}"]',driver.data_path)
                            path=driver.driver.variables[0].targets[0].data_path
                            ob2=driver.driver.variables[0].targets[0].id
                            m2=path[path.index("[")+2:path.index("]")-1]
                            #print(m2,ob2)
                            break
                
                if ob2 and m2 in [t.name for t in ob2.modifiers]:
                    layout.separator(factor=0)
                    box=layout.box()
                    row=box.row(align=True)
                    row=row.split(factor=0.6)
                    row.label(text=m.name)
                    row.prop(ob2.modifiers[m2],'show_viewport',text="",icon="RESTRICT_VIEW_ON")
                    row.prop(ob2.modifiers[m2],'show_render',text="",icon="RESTRICT_RENDER_ON")
                    eval(f'{m.type}(self,box,ob2,ob2.modifiers["{m2}"])')
class RTOOLS_MT_Synced_Mods_Modify_Menu(bpy.types.Menu):
    bl_label = "Modify Modifiers"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"        
        for a in modify_mods:
            layout.operator("rtools.addsyncedmodifiers",text=a.replace("_", " ").capitalize(),icon=icons[a]).type=a
class RTOOLS_MT_Synced_Mods_Generate_Menu(bpy.types.Menu):
    bl_label = "Generate Modifiers"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"        
        for a in generate_mods:
            layout.operator("rtools.addsyncedmodifiers",text=a.replace("_", " ").capitalize(),icon=icons[a]).type=a
class RTOOLS_MT_Synced_Mods_Deform_Menu(bpy.types.Menu):
    bl_label = "Deform Modifiers"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"        
        for a in deform_mods:
            layout.operator("rtools.addsyncedmodifiers",text=a.replace("_", " ").capitalize(),icon=icons[a]).type=a
class RTOOLS_MT_Synced_Mods_Add_Menu(bpy.types.Menu):
    bl_label = "Add Modifiers"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.menu("RTOOLS_MT_Synced_Mods_Modify_Menu", icon="MESH_DATA")
        layout.menu("RTOOLS_MT_Synced_Mods_Generate_Menu", icon="MOD_TRIANGULATE")
        layout.menu("RTOOLS_MT_Synced_Mods_Deform_Menu",icon="MOD_MESHDEFORM")
def desyncmodifiers(ob,m):
    if m.name in [mod.name for mod in ob.modifiers]:
            if ob.animation_data and ob.animation_data.drivers:
                    for driver in ob.animation_data.drivers:
                        
                        if f'modifiers["{m.name}"]' in  driver.data_path:
                            ob.animation_data.drivers.remove(driver)
                            ob.SyncedModifierInfo.remove(ob.SyncedModifierInfo.find(m.name))
                            if ob.SyncedModifierIndex>=len(ob.SyncedModifierInfo):
                                ob.SyncedModifierIndex=len(ob.SyncedModifierInfo)-1
class RTOOLS_OT_Desync_Modifiers(bpy.types.Operator):
    bl_idname = "rtools.desyncmodifiers"
    bl_label = "Desync Modifiers"
    bl_description = "Remove Drivers from this modifier"
    bl_options = {"REGISTER","UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object
    def execute(self,context):
        #for a in modify_mods+deform_mods+generate_mods:
        #    bpy.ops.rtools.addsyncedmodifiers('INVOKE_DEFAULT',type=a)
        ob=context.active_object
        if ob.SyncedModifierInfo[ob.SyncedModifierIndex].name in [mod.name for mod in ob.modifiers]:
            m=ob.modifiers[ob.SyncedModifierInfo[ob.SyncedModifierIndex].name]
            if ob.animation_data and ob.animation_data.drivers:
                    for driver in ob.animation_data.drivers:
                        
                        if f'modifiers["{m.name}"]' in  driver.data_path:
                            ob.animation_data.drivers.remove(driver)
                            ob.SyncedModifierInfo.remove(ob.SyncedModifierInfo.find(m.name))
                            if ob.SyncedModifierIndex>=len(ob.SyncedModifierInfo):
                                ob.SyncedModifierIndex=len(ob.SyncedModifierInfo)-1
        return {'FINISHED'}
class RTOOLS_OT_Refresh_Synced_Modifiers(bpy.types.Operator):
    bl_idname = "rtools.refreshsyncedmodifiers"
    bl_label = "Refresh Synced Modifiers"
    bl_description = "Refresh the synced modifiers list after manually deleting a modifier"
    bl_options = {"REGISTER","UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object
    def execute(self,context):
        active=context.active_object
        for active in context.scene.objects:
            synced_mods=[a.name for a in active.SyncedModifierInfo]
            active.SyncedModifierInfo.clear()
            for a in synced_mods:
                if a in [mod.name for mod in active.modifiers]:
                    t=active.SyncedModifierInfo.add()
                    t.name=a
            if len(active.SyncedModifierInfo)>0:
                active.SyncedModifierIndex=0
        return {'FINISHED'}
class RTOOLS_OT_Clear_Unused_Drivers(bpy.types.Operator):
    bl_idname = "rtools.clearunuseddrivers"
    bl_label = "Clear Unused Drivers"
    bl_description = "Remove all unused modifier drivers"
    bl_options = {"REGISTER","UNDO"}
    @classmethod
    def poll(cls, context):
        return context.active_object
    def execute(self,context):
        ob=context.active_object
        bpy.ops.rtools.refreshsyncedmodifiers('INVOKE_DEFAULT')
        if ob and ob.animation_data:
            for driver in ob.animation_data.drivers:
                if f'modifiers[' in  driver.data_path:
                    path=driver.data_path
                    m2=path[path.index("[")+2:path.index("]")-1]
                    if m2 not in [mod.name for mod in ob.modifiers]:
                        ob.animation_data.drivers.remove(driver)
        return {'FINISHED'}
class RTOOLS_OT_Add_Modifiers(bpy.types.Operator):
    bl_idname = "rtools.addsyncedmodifiers"
    bl_label = "Sync Modifiers"
    bl_description = "Add this modifier to the selected objects"
    bl_options = {"REGISTER","UNDO"}
    type:bpy.props.StringProperty(default="None",options={'HIDDEN'})
    @classmethod
    def poll(cls, context):
        return context.active_object and len(context.selected_objects)>1
    def execute(self,context):
        #print(self.type)
        active=context.active_object
        selected=context.selected_objects
        bpy.ops.rtools.refreshsyncedmodifiers('INVOKE_DEFAULT')
        if self.type!='None':
            name=self.type.replace("_"," ").capitalize()
            ogname=name
            if active.animation_data and active.animation_data.drivers:
                for driver in active.animation_data.drivers:
                    i=1
                    while( f'modifiers["{name}"]' in  driver.data_path):
                        name=ogname+f"_{i}"
                        i=i+1
            
            mod=active.modifiers.new(type=self.type,name=name+"(Source)")
            if mod:
                t=active.SyncedModifierInfo.add()
                
                t.name=mod.name
                active.SyncedModifierIndex=len(active.SyncedModifierInfo)-1
                for o in [a for a in selected if a!=active]:
                    o_mod=o.modifiers.new(type=self.type,name=name)
                    if o_mod:
                        props=[ key for key, value in inspect.getmembers(o_mod) if key not in requiresObject and key not in {'name','is_active','vertex_group','filepath','driver','end_cap','start_cap','collection','armature','rim_vertex_group','shell_vertex_group','grid_name','execution_time',
                                "execution_time","is_cached",
                                "is_bound",
                                "is_bind",
                                "vertex_indices",
                                "vertex_indices_set",
                                "matrix_inverse",
                                "falloff_curve",
                                "vertex_velocities",
                                "read_velocity",
                                "has_velocity",
                                "map_curve",
                                "projectors",
                                "__doc__",
                                "__module__",
                                "__slotnames__",
                                "__slots__",
                                "bl_rna",
                                "rna_type",
                                "debug_options",
                                "type",
                                "object",
                                "delimit",
                                "custom_profile",
                                "face_count",
                                "is_external","cache_file","object_path","mask_tex_map_bone","mask_tex_map_object","mask_tex_uv_layer","mask_texture","mask_vertex_group","vertex_group_a","vertex_group_b","use_bone_envelopes","use_vertex_groups",
                                "total_levels",'texture','texture_coords_bone','texture_coords_object','uv_layer','auxiliary_target','origin','bone_from','bone_to','object_from','object_to','start_position_object',
                                "subtarget",'is_override_data'
                            }]
                            
                        props=do_props(props,o_mod.type)
                        #print(props)
                        add_driver(props,o_mod,mod,active)
                        t=o.SyncedModifierInfo.add()
                        t.name=o_mod.name
                        o.SyncedModifierIndex=len(o.SyncedModifierInfo)-1
            else:
                self.report({'WARNING'},"Object doesn't support this modifier!")
        return {'FINISHED'}
def active_object_modifiers(self, context):
    obj=context.active_object
    mods=[(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods]
    return mods if mods else [("None","None","None"),]
def selected_object_modifiers(self, context):
    if len(context.selected_objects)>1:
        obj=Diff(context.selected_objects,[context.active_object,])[0]
        if self.mod_1 and self.mod_1!="None" and [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]:
            return [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]
    return [("None","None","None"),]
def selected_object_modifiers_1(self, context):
    if len(context.selected_objects)>2:
        obj=Diff(context.selected_objects,[context.active_object,])[1]
        if self.mod_1 and self.mod_1!="None" and [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]:
            return [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]
    return [("None","None","None"),]
def selected_object_modifiers_2(self, context):
    if len(context.selected_objects)>3:
        obj=Diff(context.selected_objects,[context.active_object,])[2]
        if self.mod_1 and self.mod_1!="None" and [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]:
            return [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]
    return [("None","None","None"),]
def selected_object_modifiers_3(self, context):
    if len(context.selected_objects)>4:
        obj=Diff(context.selected_objects,[context.active_object,])[3]
        if self.mod_1 and self.mod_1!="None" and [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]:
            return [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]
    return [("None","None","None"),]
def selected_object_modifiers_4(self, context):
    if len(context.selected_objects)>5:
        obj=Diff(context.selected_objects,[context.active_object,])[4]
        if self.mod_1 and self.mod_1!="None" and [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]:
            return [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]
    return [("None","None","None"),]
def selected_object_modifiers_5(self, context):
    if len(context.selected_objects)>6:
        obj=Diff(context.selected_objects,[context.active_object,])[5]
        if self.mod_1 and self.mod_1!="None" and [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]:
            return [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]
    return [("None","None","None"),]
def selected_object_modifiers_6(self, context):
    if len(context.selected_objects)>7:
        obj=Diff(context.selected_objects,[context.active_object,])[6]
        if self.mod_1 and self.mod_1!="None" and [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]:
            return [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]
    return [("None","None","None"),]
def selected_object_modifiers_7(self, context):
    if len(context.selected_objects)>8:
        obj=Diff(context.selected_objects,[context.active_object,])[7]
        if self.mod_1 and self.mod_1!="None" and [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]:
            return [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]
    return [("None","None","None"),]
def selected_object_modifiers_8(self, context):
    if len(context.selected_objects)>9:
        obj=Diff(context.selected_objects,[context.active_object,])[8]
        if self.mod_1 and self.mod_1!="None" and [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]:
            return [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]
    return [("None","None","None"),]
def selected_object_modifiers_9(self, context):
    if len(context.selected_objects)>10:
        obj=Diff(context.selected_objects,[context.active_object,])[9]
        if self.mod_1 and self.mod_1!="None" and [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]:
            return [(a.name,a.name,a.name) for a in obj.modifiers if a.type in modify_mods+deform_mods+generate_mods and a.type == context.active_object.modifiers[self.mod_1].type]            
    return [("None","None","None"),]
class RTOOLS_OT_Sync_Existing_Modifiers(bpy.types.Operator):
    bl_idname = "rtools.syncexistingmodifiers"
    bl_label = "Sync Modifiers"
    bl_description = ""
    bl_options = {"REGISTER","UNDO"}
    mod_1:bpy.props.EnumProperty(items=active_object_modifiers,name="Source Modifier")
    add_new:bpy.props.BoolProperty(default=False,name="Add New Modifier",options={'SKIP_SAVE'})
    mod_2:bpy.props.EnumProperty(items=selected_object_modifiers,name="Target Modifier (Object 1)")
    mod_3:bpy.props.EnumProperty(items=selected_object_modifiers_1,name="Target Modifier (Object 2)")
    mod_4:bpy.props.EnumProperty(items=selected_object_modifiers_2,name="Target Modifier (Object 3)")
    mod_5:bpy.props.EnumProperty(items=selected_object_modifiers_3,name="Target Modifier (Object 4)")
    mod_6:bpy.props.EnumProperty(items=selected_object_modifiers_4,name="Target Modifier (Object 5)")
    mod_7:bpy.props.EnumProperty(items=selected_object_modifiers_5,name="Target Modifier (Object 6)")
    mod_8:bpy.props.EnumProperty(items=selected_object_modifiers_6,name="Target Modifier (Object 7)")
    mod_9:bpy.props.EnumProperty(items=selected_object_modifiers_7,name="Target Modifier (Object 8)")
    mod_10:bpy.props.EnumProperty(items=selected_object_modifiers_8,name="Target Modifier (Object 9)")
    mod_11:bpy.props.EnumProperty(items=selected_object_modifiers_9,name="Target Modifier (Object 10)")
    object_1_name:bpy.props.StringProperty(default="Object 1")
    object_2_name:bpy.props.StringProperty(default="Object 2")
    object_3_name:bpy.props.StringProperty(default="Object 3")
    object_4_name:bpy.props.StringProperty(default="Object 4")
    object_5_name:bpy.props.StringProperty(default="Object 5")
    object_6_name:bpy.props.StringProperty(default="Object 6")
    object_7_name:bpy.props.StringProperty(default="Object 7")
    object_8_name:bpy.props.StringProperty(default="Object 8")
    object_9_name:bpy.props.StringProperty(default="Object 9")
    object_10_name:bpy.props.StringProperty(default="Object 10")
    
    
    @classmethod
    def poll(cls, context):
        return context.active_object and len(context.selected_objects)>1
    def draw(self, context):
        layout = self.layout
        layout.prop(self,"mod_1")
        #if len(context.selected_objects)==2:
        layout.prop(self,"add_new")
        if not self.add_new:
            layout.prop(self,"mod_2",text=self.object_1_name)
            if len(context.selected_objects)>2:
                layout.prop(self,"mod_3",text=self.object_2_name)
            if len(context.selected_objects)>3:
                layout.prop(self,"mod_4",text=self.object_3_name)
            if len(context.selected_objects)>4:
                layout.prop(self,"mod_5",text=self.object_4_name)
            if len(context.selected_objects)>5:
                layout.prop(self,"mod_6",text=self.object_5_name)
            if len(context.selected_objects)>6:
                layout.prop(self,"mod_7",text=self.object_6_name)
            if len(context.selected_objects)>7:
                layout.prop(self,"mod_8",text=self.object_7_name)
            if len(context.selected_objects)>8:
                layout.prop(self,"mod_9",text=self.object_8_name)
            if len(context.selected_objects)>9:
                layout.prop(self,"mod_10",text=self.object_9_name)
            if len(context.selected_objects)>10:
                layout.prop(self,"mod_11",text=self.object_10_name)
    def execute(self,context):
        #print(self.type)
        if self.mod_1 and self.mod_1!="None":
            active=context.active_object
            selected=Diff(context.selected_objects,[active,])[0]
            mod_new=None
            active_mod=active.modifiers[self.mod_1]
            mods_to_sync=[]
            if self.add_new:
                for obj in Diff(context.selected_objects,[active,]):
                    mod_new=obj.modifiers.new(type=active.modifiers[self.mod_1].type,name=self.mod_1)
                    mods_to_sync.append((obj,mod_new))
            else:
                if self.mod_2 and self.mod_2!="None" and  self.mod_2 in [a.name for a in selected.modifiers]:
                    mod_new=selected.modifiers[self.mod_2]
                    mods_to_sync.append((selected,mod_new))
                if self.mod_3 and self.mod_3!="None" and  self.mod_3 in [a.name for a in Diff(context.selected_objects,[active,])[1].modifiers]:
                    mod_new=Diff(context.selected_objects,[active,])[1].modifiers[self.mod_3]
                    mods_to_sync.append((Diff(context.selected_objects,[active,])[1],mod_new))
                if self.mod_4 and self.mod_4!="None" and  self.mod_4 in [a.name for a in Diff(context.selected_objects,[active,])[2].modifiers]:
                    mod_new=Diff(context.selected_objects,[active,])[2].modifiers[self.mod_4]
                    mods_to_sync.append((Diff(context.selected_objects,[active,])[2],mod_new))
                if self.mod_5 and self.mod_5!="None" and  self.mod_5 in [a.name for a in Diff(context.selected_objects,[active,])[3].modifiers]:
                    mod_new=Diff(context.selected_objects,[active,])[3].modifiers[self.mod_5]
                    mods_to_sync.append((Diff(context.selected_objects,[active,])[3],mod_new))
                if self.mod_6 and self.mod_6!="None" and  self.mod_6 in [a.name for a in Diff(context.selected_objects,[active,])[4].modifiers]:
                    mod_new=Diff(context.selected_objects,[active,])[4].modifiers[self.mod_6]
                    mods_to_sync.append((Diff(context.selected_objects,[active,])[4],mod_new))
                if self.mod_7 and self.mod_7!="None" and  self.mod_7 in [a.name for a in Diff(context.selected_objects,[active,])[5].modifiers]:
                    mod_new=Diff(context.selected_objects,[active,])[5].modifiers[self.mod_7]
                    mods_to_sync.append((Diff(context.selected_objects,[active,])[5],mod_new))
                if self.mod_8 and self.mod_8!="None" and  self.mod_8 in [a.name for a in Diff(context.selected_objects,[active,])[6].modifiers]:
                    mod_new=Diff(context.selected_objects,[active,])[6].modifiers[self.mod_8]
                    mods_to_sync.append((Diff(context.selected_objects,[active,])[6],mod_new))
                if self.mod_9 and self.mod_9!="None" and self.mod_2!="None" and  self.mod_9 in [a.name for a in Diff(context.selected_objects,[active,])[7].modifiers]:
                    mod_new=Diff(context.selected_objects,[active,])[7].modifiers[self.mod_9]
                    mods_to_sync.append((Diff(context.selected_objects,[active,])[7],mod_new))
                if self.mod_10 and self.mod_10!="None" and  self.mod_10 in [a.name for a in Diff(context.selected_objects,[active,])[8].modifiers]:
                    mod_new=Diff(context.selected_objects,[active,])[8].modifiers[self.mod_10]
                    mods_to_sync.append((Diff(context.selected_objects,[active,])[8],mod_new))
                if self.mod_11 and self.mod_11!="None" and  self.mod_11 in [a.name for a in Diff(context.selected_objects,[active,])[9].modifiers]:
                    mod_new=Diff(context.selected_objects,[active,])[9].modifiers[self.mod_11]
                    mods_to_sync.append((Diff(context.selected_objects,[active,])[9],mod_new))
            if active.animation_data and active.animation_data.drivers:
                        for driver in active.animation_data.drivers:
                            
                            if f'modifiers["{active_mod.name}"]' in  driver.data_path:
                                #print(f'modifiers["{m.name}"]',driver.data_path)
                                path=driver.driver.variables[0].targets[0].data_path
                                if "modifiers" in  path:
                                    ob2=driver.driver.variables[0].targets[0].id
                                    m2=path[path.index("[")+2:path.index("]")-1]
                                    #print(m2,ob2)
                                    if m2 in [a.name for a in ob2.modifiers]:
                                        active=ob2
                                        active_mod=ob2.modifiers[m2]
                                    break
            mods_to_sync.append((active,active.modifiers[self.mod_1]))
            if self.mod_1 and mod_new:
                sync_modifiers(mods_to_sync,active)
        else:
            self.report({'WARNING'},"No Source Modifier")
        return {'FINISHED'}
    def invoke(self, context,event):
        if len(context.selected_objects)>2:
            self.add_new=True
        if  len(context.selected_objects)>1:
            self.object_1_name=Diff(context.selected_objects,[context.active_object,])[0].name
        if  len(context.selected_objects)>2:
            self.object_2_name=Diff(context.selected_objects,[context.active_object,])[1].name
        if  len(context.selected_objects)>3:
            self.object_3_name=Diff(context.selected_objects,[context.active_object,])[2].name
        if  len(context.selected_objects)>4:
            self.object_4_name=Diff(context.selected_objects,[context.active_object,])[3].name
        if  len(context.selected_objects)>5:
            self.object_5_name=Diff(context.selected_objects,[context.active_object,])[4].name
        if  len(context.selected_objects)>6:
            self.object_6_name=Diff(context.selected_objects,[context.active_object,])[5].name
        if  len(context.selected_objects)>7:
            self.object_7_name=Diff(context.selected_objects,[context.active_object,])[6].name
        if  len(context.selected_objects)>8:
            self.object_8_name=Diff(context.selected_objects,[context.active_object,])[7].name
        if  len(context.selected_objects)>9:
            self.object_9_name=Diff(context.selected_objects,[context.active_object,])[8].name
        if  len(context.selected_objects)>10:
            self.object_10_name=Diff(context.selected_objects,[context.active_object,])[9].name
        return self.execute(context)
class RTOOLS_OT_Sync_Modifier_Object(bpy.types.Operator):
    bl_idname = "rtools.sync_object"
    bl_label = "Sync"
    bl_description = "Sync Object Fields"
    bl_options = {"REGISTER","UNDO"}
    mod: bpy.props.StringProperty(options={'SKIP_SAVE'})
    object:bpy.props.StringProperty(options={'SKIP_SAVE'})
    @classmethod
    def poll(cls, context):
        return context.active_object
    def execute(self,context):
        og_mod=bpy.data.objects[self.object].modifiers[self.mod]
        mod_type=bpy.data.objects[self.object].modifiers[self.mod].type
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                if mod.type==mod_type and mod.name in obj.SyncedModifierInfo:
                    setattr(mod,mod_object_field[mod.type],getattr(og_mod,mod_object_field[mod.type]))
            
        return {'FINISHED'}
def drawIntoAddMenu(self, context):
    layout= self.layout
    layout.menu("RTOOLS_MT_Synced_Mods_Add_Menu")
class ModifierInfo(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
classes = (
    RTOOLS_OT_Add_Modifiers,
    RTOOLS_PT_SM_Addon,
    RTOOLS_MT_Synced_Mods_Add_Menu,
    RTOOLS_MT_Synced_Mods_Deform_Menu,
    RTOOLS_MT_Synced_Mods_Generate_Menu,
    RTOOLS_MT_Synced_Mods_Modify_Menu,
    ModifierInfo,
    RTOOLS_UL_Synced_Mods_List,
    RTOOLS_OT_Refresh_Synced_Modifiers,
    RTOOLS_OT_Desync_Modifiers,
    RTOOLS_OT_SyncedPanel,
    RTOOLS_OT_Clear_Unused_Drivers,
    RTOOLS_OT_Sync_Modifier_Object,
    RTOOLS_OT_Sync_Existing_Modifiers
)

icon_collection={}
addon_keymaps = []

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    kmaps = [
        ("rtools.synced_modifiers_panel","J","ALT"),
    ]

    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
    if kc:
        for (op, k, sp) in kmaps:

            kmi = km.keymap_items.new(
                op,
                type=k,
                value="PRESS",
                alt="alt" in sp,
                shift="shift" in sp,
                ctrl="ctrl" in sp,
            )
            addon_keymaps.append((km, kmi))
    bpy.types.VIEW3D_MT_add.append(drawIntoAddMenu)
    bpy.types.Object.SyncedModifierInfo=bpy.props.CollectionProperty(type=ModifierInfo)
    bpy.types.Object.SyncedModifierIndex=bpy.props.IntProperty(name="Modifier")
def unregister():

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    for (km, kmi) in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.types.VIEW3D_MT_add.remove(drawIntoAddMenu)
if __name__ == "__main__":
    register()

