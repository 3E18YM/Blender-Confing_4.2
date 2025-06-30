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
from .. import bpl
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl
from .. import bfu_alembic_animation
from .. import bfu_camera
from .. import bfu_skeletal_mesh
from .. import bfu_export_procedure
from .. import bfu_custom_property


def draw_ui(layout: bpy.types.UILayout, obj: bpy.types.Object):

    scene = bpy.context.scene 
    addon_prefs = bfu_basics.GetAddonPrefs()

    # Hide filters
    if obj is None:
        return
    if bfu_utils.GetExportAsProxy(obj):
        return
    if obj.bfu_export_type != "export_recursive":
        return
    
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):
        scene.bfu_object_advanced_properties_expanded.draw(layout)
        if scene.bfu_object_advanced_properties_expanded.is_expend():
            transformProp = layout.column()
            is_not_alembic_animation = not bfu_alembic_animation.bfu_alembic_animation_utils.is_alembic_animation(obj)
            is_not_camera = not bfu_camera.bfu_camera_utils.is_camera(obj)
            if is_not_alembic_animation and is_not_camera:
                transformProp.prop(obj, "bfu_move_to_center_for_export")
                transformProp.prop(obj, "bfu_rotate_to_zero_for_export")
                transformProp.prop(obj, "bfu_additional_location_for_export")
                transformProp.prop(obj, "bfu_additional_rotation_for_export")
                
            transformProp.prop(obj, 'bfu_export_global_scale')
            if bfu_camera.bfu_camera_utils.is_camera(obj):
                transformProp.prop(obj, "bfu_additional_location_for_export")

            AxisProperty = layout.column()
            
            AxisProperty.prop(obj, 'bfu_override_procedure_preset')
            if obj.bfu_override_procedure_preset:
                AxisProperty.prop(obj, 'bfu_export_use_space_transform')
                AxisProperty.prop(obj, 'bfu_export_axis_forward')
                AxisProperty.prop(obj, 'bfu_export_axis_up')
                bbpl.blender_layout.layout_doc_button.add_doc_page_operator(AxisProperty, text="About axis Transforms", url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Axis-Transforms")
                if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                    BoneAxisProperty = layout.column()
                    BoneAxisProperty.prop(obj, 'bfu_export_primary_bone_axis')
                    BoneAxisProperty.prop(obj, 'bfu_export_secondary_bone_axis')
            else:
                box = layout.box()
                if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                    preset = bfu_export_procedure.bfu_skeleton_export_procedure.get_obj_skeleton_procedure_preset(obj)
                else:
                    preset = bfu_export_procedure.bfu_static_export_procedure.get_obj_static_procedure_preset(obj)
                var_lines = box.column()
                for key, value in preset.items():
                    display_key = bpl.utils.format_property_name(key)
                    var_lines.label(text=f"{display_key}: {value}\n")
            export_data = layout.column()
            bfu_custom_property.bfu_custom_property_utils.draw_ui_custom_property(export_data, obj)
            export_data.prop(obj, "bfu_export_with_meta_data")