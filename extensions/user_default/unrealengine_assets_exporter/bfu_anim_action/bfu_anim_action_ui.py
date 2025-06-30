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
from .. import bfu_skeletal_mesh
from .. import bfu_alembic_animation
from .. import bfu_camera


def draw_ui(layout: bpy.types.UILayout, obj: bpy.types.Object):

    scene = bpy.context.scene 
    addon_prefs = bfu_basics.GetAddonPrefs()

    # Hide filters
    if obj is None:
        return
    if obj.bfu_export_type != "export_recursive":
        return
    is_skeletal_mesh = bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj)
    is_camera = bfu_camera.bfu_camera_utils.is_camera(obj)
    is_alembic_animation = bfu_alembic_animation.bfu_alembic_animation_utils.is_alembic_animation(obj)
    if True not in [is_skeletal_mesh, is_camera, is_alembic_animation]:
        return

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "ANIM"):
        scene.bfu_animation_action_properties_expanded.draw(layout)
        if scene.bfu_animation_action_properties_expanded.is_expend():
            if is_skeletal_mesh:
                # Action list
                ActionListProperty = layout.column()
                ActionListProperty.prop(obj, 'bfu_anim_action_export_enum')
                if obj.bfu_anim_action_export_enum == "export_specific_list":
                    ActionListProperty.template_list(
                        # type and unique id
                        "BFU_UL_ActionExportTarget", "",
                        # pointer to the CollectionProperty
                        obj, "bfu_action_asset_list",
                        # pointer to the active identifier
                        obj, "bfu_active_action_asset_list",
                        maxrows=5,
                        rows=5
                    )
                    ActionListProperty.operator(
                        "object.updateobjactionlist",
                        icon='RECOVER_LAST')
                if obj.bfu_anim_action_export_enum == "export_specific_prefix":
                    ActionListProperty.prop(obj, 'bfu_prefix_name_to_export')

            # Action Time
            if obj.type != "CAMERA" and obj.bfu_skeleton_export_procedure != "auto-rig-pro":
                ActionTimeProperty = layout.column()
                ActionTimeProperty.enabled = obj.bfu_anim_action_export_enum != 'dont_export'
                ActionTimeProperty.prop(obj, 'bfu_anim_action_start_end_time_enum')
                if obj.bfu_anim_action_start_end_time_enum == "with_customframes":
                    OfsetTime = ActionTimeProperty.row()
                    OfsetTime.prop(obj, 'bfu_anim_action_custom_start_frame')
                    OfsetTime.prop(obj, 'bfu_anim_action_custom_end_frame')
                if obj.bfu_anim_action_start_end_time_enum != "with_customframes":
                    OfsetTime = ActionTimeProperty.row()
                    OfsetTime.prop(obj, 'bfu_anim_action_start_frame_offset')
                    OfsetTime.prop(obj, 'bfu_anim_action_end_frame_offset')

            else:
                layout.label(
                    text=(
                        "Note: animation start/end use scene frames" +
                        " with the camera for the sequencer.")
                    )

            # Nomenclature
            if is_skeletal_mesh:
                export_anim_naming = layout.column()
                export_anim_naming.enabled = obj.bfu_anim_action_export_enum != 'dont_export'
                export_anim_naming.prop(obj, 'bfu_anim_naming_type')
                if obj.bfu_anim_naming_type == "include_custom_name":
                    export_anim_naming_text = export_anim_naming.column()
                    export_anim_naming_text.prop(obj, 'bfu_anim_naming_custom')