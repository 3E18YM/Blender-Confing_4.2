
import bpy
from bpy.types import (PropertyGroup)
from bpy.props import (PointerProperty)
from .operators import (TransferShapeData, TransferShapeKeyData, TransferVertexGroupsData,
                        TransferUVData, TransferShapeKeyDrivers)

bl_info = {
    "name" : "MeshDataTransfer",
    "author" : "Maurizio Memoli",
    "description" : "This add on will transfer geometry data from one mesh to another based on 3 different spaces:"
                    " 'world, object, uv' also will tranfer UVs based on topology",
    "blender" : (2, 80, 0),
    "version" : (1, 4, 2,),
    "location" : "(Object Mode) Mesh > ObjectData > Mesh Data Transfer ",
    "warning" : "",
    "wiki_url": "",
    "category" : "Mesh"
}




def scene_chosenobject_poll(self , object):
    if bpy.context.active_object == object:
        return False
    return object.type in ['MESH']

def pick_armature(self , object):
    if bpy.context.active_object == object:
        return False
    return object.type in ['ARMATURE']

class MeshDataSettings(PropertyGroup):
    mesh_object_space: bpy.props.EnumProperty(
        items=[('WORLD', 'World', '', 1),('LOCAL', 'Local', '', 2), ('UVS', 'Active UV', '', 3), ('TOPOLOGY', 'Topology', '', 4)],
        name="Object Space", default = 'LOCAL')

    gp_object_space: bpy.props.EnumProperty(
        items=[('WORLD', 'World', '', 1),('LOCAL', 'Local', '', 2)],
        name="Object Space", default = 'LOCAL')

    search_method: bpy.props.EnumProperty(
        items=[('CLOSEST', 'Closest', '', 1),('RAYCAST', 'Raycast', '', 2)],
        name="Search method")

    # transfer_shape: bpy.props.BoolProperty()
    #
    # transfer_shapekeys: bpy.props.BoolProperty()
    #
    # transfer_vertex_groups : bpy.props.BoolProperty()
    #
    # transfer_uv_data: bpy.props.BoolProperty ()

    mesh_source: bpy.props.PointerProperty(name="Source mesh", description= "Pick a source mesh for transfer."
                                           ,type=bpy.types.Object, poll=scene_chosenobject_poll)

    arm_source: bpy.props.PointerProperty(name="Source armature", description= "Pick a source mesh for transfer."
                                           ,type=bpy.types.Object, poll=pick_armature)

    arm_target: bpy.props.PointerProperty(name="Target armature", description= "Pick a source mesh for transfer."
                                           ,type=bpy.types.Object, poll=pick_armature)

    vertex_group_filter: bpy.props.StringProperty (name="Vertex Group",
                                                   description="Filter transfer using a vertex group.")
    invert_vertex_group_filter: bpy.props.BoolProperty (name= "Invert vertex group values")

    transfer_shape_as_key : bpy.props.BoolProperty (name="Transfer as shape key",
                                                    description="Transfer vertices position as a shape key.")
    transfer_to_new_uv : bpy.props.BoolProperty()

    transfer_modified_target : bpy.props.BoolProperty ()
    transfer_modified_source : bpy.props.BoolProperty ()

    exclude_muted_shapekeys : bpy.props.BoolProperty (name= "Exclude muted",
                                                      description="Muted shape keys will be not transferred.")

    exclude_locked_groups: bpy.props.BoolProperty (name= "Exclude locked",
                                                   description="Locked vertex groups will be not transferred.")
    snap_to_closest_shape: bpy.props.BoolProperty (name="Snap shape to closest vertex",
                                                   description="Snap transferred vertices to closest vertex on source mesh")
    snap_to_closest_shapekey: bpy.props.BoolProperty (name="Snap shape key to closest vertex",
                                                   description="Snap transferred shape keys vertices to closest vertex on source shape key")

    transfer_shapekeys_drivers: bpy.props.BoolProperty (name="Transfer shape keys drivers",
                                                   description="Transfer the drivers along with the shape keys.")


class MeshDataGlobalSettings(PropertyGroup):
    transfer_modified_target : bpy.props.BoolProperty ()
    transfer_modified_source : bpy.props.BoolProperty ()

# class ShapeKeysProp(bpy.types.PropertyGroup):
#     name : bpy.props.StringProperty()
#     enabled : bpy.props.BoolProperty()

#=========================================UI===============================================================

class DATA_PT_mesh_data_transfer(bpy.types.Panel):
    bl_label = "Mesh Data Transfer"
    bl_idname = "MESH_PT_mesh_data_transfer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        # To reactivate GPencil change the variable to: ['MESH','GPENCIL']
        return context.active_object.type in ['MESH']


    def draw(self, context):
        active = bpy.context.active_object
        ob_prop = context.object.mesh_data_transfer_object
        vg_prop = context.object.mesh_data_transfer_object
        # sc_prop = context.scene.mesh_data_transfer_global
        obj = context.object
        is_gp = active.type == "GPENCIL"

        # mesh_object_space layout
        main_box_layout = self.layout.box()
        sample_main_box = main_box_layout.box()

        option_label = sample_main_box.row()
        option_label.alignment = 'CENTER'
        option_label.label(text="SAMPLE SPACE")
        option_row = sample_main_box.row()
        obj_space_option = "mesh_object_space"
        if is_gp:
            obj_space_option = "gp_object_space"
        option_row.prop(ob_prop,obj_space_option, expand=True, text="Sample space")
        option_row2 = sample_main_box.row()
        option_row2.prop(ob_prop, 'search_method', expand=True, text="Search method")

        #option_row.use_property_split = True
        # sample_target_mod = main_box_layout.row ()
        # sample_target_mod.prop(ob_prop, 'transfer_modified_target', text="Sample Modified Target", icon='MESH_DATA')
        if not is_gp:
            sample_source_mod = main_box_layout.row()
            sample_source_mod.prop(ob_prop, 'transfer_modified_source', text="Sample Modified Source", icon='MESH_DATA')

            if ob_prop.mesh_object_space not in {'WORLD', 'LOCAL', 'UVS'} :
                # sample_target_mod.enabled = False
                sample_source_mod.enabled = False

        #mesh picker layout
        mesh_picker_box_layout = main_box_layout.box()
        mesh_picker_box_layout.prop_search(ob_prop, "mesh_source", context.scene, "objects", text="Source: ")




        #top row
        top_row_layout = main_box_layout.row()
        left_top_row_box_layout = top_row_layout.box ()
        shape_cols_layout = left_top_row_box_layout.row(align=True)
        shape_cols_layout.operator ("object.transfer_shape_data" , text="Transfer Shape" , icon="MOD_DATA_TRANSFER")
        # split = shape_cols_layout.split()
        if not is_gp:
            snap_shape_icon =  "SNAP_OFF"
            if ob_prop.snap_to_closest_shape:
                snap_shape_icon = "SNAP_ON"
            shape_cols_layout.prop (ob_prop , "snap_to_closest_shape" , text="" , toggle=True , icon=snap_shape_icon)

            shape_cols_layout.prop (ob_prop , "transfer_shape_as_key" , text="", toggle=True, icon='SHAPEKEY_DATA')

            left_bottom_row_box_layout = left_top_row_box_layout.row(align=True)
            left_bottom_row_box_layout.operator("object.transfer_shape_key_data" , text="Transfer Shape Keys" ,
                                                    icon="SHAPEKEY_DATA")
            snap_key_icon = "SNAP_OFF"
            if ob_prop.snap_to_closest_shapekey:
                snap_key_icon = "SNAP_ON"
            left_bottom_row_box_layout.prop(ob_prop , "snap_to_closest_shapekey" , text="",
                                             toggle=True, icon=snap_key_icon)
            left_bottom_row_box_layout.prop(ob_prop , "exclude_muted_shapekeys" , text="",
                                             toggle=True, icon='CHECKMARK')
            # left_bottom_row_box_layout.prop(ob_prop , "transfer_shapekeys_drivers" , text="",
            #                                  toggle=True, icon='DRIVER')


        top_row_layout.split()
        right_top_row_box_layout = top_row_layout.box()
        if not is_gp:
            right_top_row_box_layout.operator ("object.transfer_uv_data" , text="Transfer UV" ,
                                             icon="UV_DATA")
        right_bottom_row_box_layout = right_top_row_box_layout.row(align=True)
        right_bottom_row_box_layout.operator("object.transfer_vertex_groups_data" , text="Transfer Vertex Groups" ,
                                                icon="GROUP_VERTEX")
        right_bottom_row_box_layout.prop(ob_prop , "exclude_locked_groups" , text="",
                                         toggle=True, icon='LOCKED')

        vgroup_picker_box_layout = main_box_layout.box()
        vgroup_row = vgroup_picker_box_layout.row(align=True)
        vgroup_row.prop_search(ob_prop, "vertex_group_filter", active, "vertex_groups")
        vgroup_row.prop (ob_prop , "invert_vertex_group_filter" , text="" , toggle=True , icon='ARROW_LEFTRIGHT')

        utility_box_layout = main_box_layout.box()
        utility_label = utility_box_layout.row(align=True)
        utility_label.prop(obj, "expanded",
            icon="TRIA_DOWN" if obj.expanded else "TRIA_RIGHT",
            icon_only=True, emboss=False, expand=False)
        utility_label.label(text="RIGGING HELPERS")
        utility_label.alignment = "LEFT"
        if obj.expanded:
            #armature picker layout
            source_arm_picker_box_layout = utility_box_layout.box()
            source_arm_picker_box_layout.prop_search(ob_prop, "arm_source", context.scene, "objects", text="Source Armature")
            target_arm_picker_box_layout = utility_box_layout.box()
            target_arm_picker_box_layout.prop_search(ob_prop, "arm_target", context.scene, "objects", text="Target Armature")
            transfer_drivers_layout = utility_box_layout.row()
            transfer_drivers_layout.operator("object.transfer_shape_key_drivers", text="Transfer Shape Keys drivers",
                                                icon="DRIVER")


#=================================================================================================================

classes = (DATA_PT_mesh_data_transfer, MeshDataSettings, MeshDataGlobalSettings, TransferShapeData,
           TransferShapeKeyData, TransferVertexGroupsData, TransferUVData, TransferShapeKeyDrivers)

def register():
    global classes
    for cl in classes:
        bpy.utils.register_class(cl)

    bpy.types.Object.mesh_data_transfer_object = PointerProperty (type=MeshDataSettings)
    bpy.types.Object.expanded = bpy.props.BoolProperty(default=False)
    # bpy.types.Scene.mesh_data_transfer_global = PointerProperty (type=MeshDataGlobalSettings)

def unregister():
    global classes
    for cl in classes:
        # print (cl)
        bpy.utils.unregister_class (cl)

    del bpy.types.Object.mesh_data_transfer_object
    del bpy.types.Object.expanded
    # del bpy.types.Scene.mesh_data_transfer_global

if __name__ == "__main__":
    register()
