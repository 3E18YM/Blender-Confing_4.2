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
from .. import bfu_cached_asset_list




def get_preset_values():
    preset_values = [
        'obj.bfu_disable_free_scale_animation',
        'obj.bfu_sample_anim_for_export',
        'obj.bfu_simplify_anim_for_export',
    ]
    return preset_values

class BFU_OT_ShowActionToExport(bpy.types.Operator):
    bl_label = "Show action(s)"
    bl_idname = "object.showobjaction"
    bl_description = (
        "Click to show actions that are" +
        " to be exported with this armature."
        )

    def execute(self, context):
        obj = context.object
        animation_asset_cache = bfu_cached_asset_list.GetAnimationAssetCache(obj)
        animation_asset_cache.UpdateActionCache()
        animation_to_export = animation_asset_cache.GetAnimationAssetList()

        popup_title = "Action list"
        if len(animation_to_export) > 0:
            animationNumber = len(animation_to_export)
            if obj.bfu_anim_nla_use:
                animationNumber += 1
            popup_title = (
                str(animationNumber) +
                ' action(s) found for obj named "'+obj.name+'".'
                )
        else:
            popup_title = (
                'No action found for obj named "' +
                obj.name+'".')

        def draw(self, context: bpy.types.Context):
            col = self.layout.column()

            def addAnimRow(
                    action_name,
                    action_type,
                    frame_start,
                    frame_end):
                row = col.row()
                row.label(
                    text="- ["+action_name +
                    "] Frame "+frame_start+" to "+frame_end +
                    " ("+action_type+")"
                    )

            for action in animation_to_export:
                Frames = bfu_utils.GetDesiredActionStartEndTime(obj, action)
                frame_start = str(Frames[0])
                frame_end = str(Frames[1])
                addAnimRow(action.name, bfu_utils.GetActionType(action), frame_start, frame_end)
            if obj.bfu_anim_nla_use:
                scene = context.scene
                addAnimRow(obj.bfu_anim_nla_export_name, "NlAnim", str(scene.frame_start), str(scene.frame_end))

        bpy.context.window_manager.popup_menu(
            draw,
            title=popup_title,
            icon='ACTION'
            )
        return {'FINISHED'}

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_ShowActionToExport,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_animation_advanced_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Animation Advanced Properties")

    bpy.types.Object.bfu_sample_anim_for_export = bpy.props.FloatProperty(
        name="Sampling Rate",
        description="How often to evaluate animated values (in frames)",
        override={'LIBRARY_OVERRIDABLE'},
        min=0.01, max=100.0,
        soft_min=0.01, soft_max=100.0,
        default=1.0,
        )

    bpy.types.Object.bfu_simplify_anim_for_export = bpy.props.FloatProperty(
        name="Simplify animations",
        description=(
            "How much to simplify baked values" +
            " (0.0 to disable, the higher the more simplified)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        # No simplification to up to 10% of current magnitude tolerance.
        min=0.0, max=100.0,
        soft_min=0.0, soft_max=10.0,
        default=0.0,
        )
    
    bpy.types.Object.bfu_disable_free_scale_animation = bpy.props.BoolProperty(
        name="Disable non-uniform scale animation.",
        description=(
            "If checked, scale animation track's elements always have same value. " + 
            "This applies basic bones only."
        ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_disable_free_scale_animation
    del bpy.types.Object.bfu_simplify_anim_for_export
    del bpy.types.Object.bfu_sample_anim_for_export
    del bpy.types.Scene.bfu_animation_advanced_properties_expanded