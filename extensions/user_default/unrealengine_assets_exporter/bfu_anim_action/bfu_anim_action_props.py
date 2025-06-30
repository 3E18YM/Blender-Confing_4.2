# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================


import bpy
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl




def get_preset_values():
    preset_values = [
        'obj.bfu_anim_action_export_enum',
        'obj.bfu_prefix_name_to_export',
        'obj.bfu_anim_action_start_end_time_enum',
        'obj.bfu_anim_action_start_frame_offset',
        'obj.bfu_anim_action_end_frame_offset',
        'obj.bfu_anim_action_custom_start_frame',
        'obj.bfu_anim_action_custom_end_frame',
        'obj.bfu_anim_naming_type',
        'obj.bfu_anim_naming_custom',
    ]
    return preset_values

class BFU_UL_ActionExportTarget(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        action_is_valid = False
        if item.name in bpy.data.actions:
            action_is_valid = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if action_is_valid:  # If action is valid
                layout.prop(
                    bpy.data.actions[item.name],
                    "name",
                    text="",
                    emboss=False,
                    icon="ACTION"
                )
                layout.prop(item, "use", text="")
            else:
                dataText = (
                    'Action data named "' + item.name +
                    '" Not Found. Please click on update'
                )
                layout.label(text=dataText, icon="ERROR")
        # Not optimized for 'GRID' layout type.
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class BFU_OT_UpdateObjActionListButton(bpy.types.Operator):
    bl_label = "Update action list"
    bl_idname = "object.updateobjactionlist"
    bl_description = "Update action list"

    def execute(self, context):
        def UpdateExportActionList(obj):
            # Update the provisional action list known by the object

            def SetUseFromLast(anim_list, ActionName):
                for item in anim_list:
                    if item[0] == ActionName:
                        if item[1]:
                            return True
                return False

            animSave = [["", False]]
            for Anim in obj.bfu_action_asset_list:  # CollectionProperty
                name = Anim.name
                use = Anim.use
                animSave.append([name, use])
            obj.bfu_action_asset_list.clear()
            for action in bpy.data.actions:
                obj.bfu_action_asset_list.add().name = action.name
                useFromLast = SetUseFromLast(animSave, action.name)
                obj.bfu_action_asset_list[action.name].use = useFromLast
        UpdateExportActionList(bpy.context.object)
        return {'FINISHED'}

class BFU_OT_ObjExportAction(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Action data name", default="Unknown", override={'LIBRARY_OVERRIDABLE'})
    use: bpy.props.BoolProperty(name="use this action", default=False, override={'LIBRARY_OVERRIDABLE'})


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_UL_ActionExportTarget,
    BFU_OT_UpdateObjActionListButton,
    BFU_OT_ObjExportAction,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_animation_action_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Actions Properties")

    bpy.types.Object.bfu_action_asset_list = bpy.props.CollectionProperty(
        type=BFU_OT_ObjExportAction,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'},
        )

    bpy.types.Object.bfu_active_action_asset_list = bpy.props.IntProperty(
        name="Active Scene Action",
        description="Index of the currently active object action",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
        )
    
    bpy.types.Object.bfu_anim_action_export_enum = bpy.props.EnumProperty(
        name="Action to export",
        description="Export procedure for actions (Animations and poses)",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("export_auto",
                "Export auto",
                "Export all actions connected to the bones names",
                "FILE_SCRIPT",
                1),
            ("export_specific_list",
                "Export specific list",
                "Export only actions that are checked in the list",
                "LINENUMBERS_ON",
                3),
            ("export_specific_prefix",
                "Export specific prefix",
                "Export only actions with a specific prefix" +
                " or the beginning of the actions names",
                "SYNTAX_ON",
                4),
            ("dont_export",
                "Not exported",
                "No action will be exported",
                "MATPLANE",
                5),
            ("export_current",
                "Export Current",
                "Export only the current actions",
                "FILE_SCRIPT",
                6),
            ]
        )
    
    bpy.types.Object.bfu_prefix_name_to_export = bpy.props.StringProperty(
        # properties used with ""export_specific_prefix" on bfu_anim_action_export_enum
        name="Prefix name",
        description="Indicate the prefix of the actions that must be exported",
        override={'LIBRARY_OVERRIDABLE'},
        maxlen=32,
        default="Example_",
        )

    bpy.types.Object.bfu_anim_action_start_end_time_enum = bpy.props.EnumProperty(
        name="Action Start/End Time",
        description="Set when animation starts and end",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("with_keyframes",
                "Auto",
                "The time will be defined according" +
                " to the first and the last frame",
                "KEYTYPE_KEYFRAME_VEC",
                1),
            ("with_sceneframes",
                "Scene time",
                "Time will be equal to the scene time",
                "SCENE_DATA",
                2),
            ("with_customframes",
                "Custom time",
                'The time of all the animations of this object' +
                ' is defined by you.' +
                ' Use "bfu_anim_action_custom_start_frame" and "bfu_anim_action_custom_end_frame"',
                "HAND",
                3),
            ]
        )

    bpy.types.Object.bfu_anim_action_start_frame_offset = bpy.props.IntProperty(
        name="Offset at start frame",
        description="Offset for the start frame.",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
    )

    bpy.types.Object.bfu_anim_action_end_frame_offset = bpy.props.IntProperty(
        name="Offset at end frame",
        description=(
            "Offset for the end frame. +1" +
            " is recommended for the sequences | 0 is recommended" +
            " for UnrealEngine cycles | -1 is recommended for Sketchfab cycles"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=0
    )


    bpy.types.Object.bfu_anim_action_custom_start_frame = bpy.props.IntProperty(
        name="Custom start time",
        description="Set when animation start",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
        )

    bpy.types.Object.bfu_anim_action_custom_end_frame = bpy.props.IntProperty(
        name="Custom end time",
        description="Set when animation end",
        override={'LIBRARY_OVERRIDABLE'},
        default=1
        )
    

    bpy.types.Object.bfu_anim_naming_type = bpy.props.EnumProperty(
        name="Naming type",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ('action_name', "Action name", 'Exemple: "Anim_MyAction"'),
            ('include_armature_name',
                "Include Armature Name",
                'Include armature name in animation export file name.' +
                ' Exemple: "Anim_MyArmature_MyAction"'),
            ('include_custom_name',
                "Include custom name",
                'Include custom name in animation export file name.' +
                ' Exemple: "Anim_MyCustomName_MyAction"'),
            ],
        default='action_name'
        )

    bpy.types.Object.bfu_anim_naming_custom = bpy.props.StringProperty(
        name="Export name",
        override={'LIBRARY_OVERRIDABLE'},
        default='MyCustomName'
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_anim_naming_custom
    del bpy.types.Object.bfu_anim_naming_type

    del bpy.types.Object.bfu_anim_action_custom_end_frame
    del bpy.types.Object.bfu_anim_action_custom_start_frame
    del bpy.types.Object.bfu_anim_action_end_frame_offset
    del bpy.types.Object.bfu_anim_action_start_frame_offset
    del bpy.types.Object.bfu_anim_action_start_end_time_enum

    del bpy.types.Object.bfu_prefix_name_to_export
    del bpy.types.Object.bfu_anim_action_export_enum
    del bpy.types.Object.bfu_active_action_asset_list
    del bpy.types.Object.bfu_action_asset_list
    del bpy.types.Scene.bfu_animation_action_properties_expanded