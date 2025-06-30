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


def draw_ui(layout: bpy.types.UILayout, context: bpy.types.Context):
    scene = context.scene
    addon_prefs = bfu_basics.GetAddonPrefs()

    scene.bfu_nomenclature_properties_expanded.draw(layout)
    if scene.bfu_nomenclature_properties_expanded.is_expend():

        # Prefix
        propsPrefix = layout.row()
        propsPrefix = propsPrefix.column()
        propsPrefix.prop(scene, 'bfu_static_mesh_prefix_export_name', icon='OBJECT_DATA')
        propsPrefix.prop(scene, 'bfu_skeletal_mesh_prefix_export_name', icon='OBJECT_DATA')
        propsPrefix.prop(scene, 'bfu_skeleton_prefix_export_name', icon='OBJECT_DATA')
        propsPrefix.prop(scene, 'bfu_alembic_animation_prefix_export_name', icon='OBJECT_DATA')
        propsPrefix.prop(scene, 'bfu_groom_simulation_prefix_export_name', icon='OBJECT_DATA')
        propsPrefix.prop(scene, 'bfu_anim_prefix_export_name', icon='OBJECT_DATA')
        propsPrefix.prop(scene, 'bfu_pose_prefix_export_name', icon='OBJECT_DATA')
        propsPrefix.prop(scene, 'bfu_camera_prefix_export_name', icon='OBJECT_DATA')
        propsPrefix.prop(scene, 'bfu_spline_prefix_export_name', icon='OBJECT_DATA')

        # Sub folder
        propsSub = layout.row()
        propsSub = propsSub.column()
        propsSub.prop(scene, 'bfu_anim_subfolder_name', icon='FILE_FOLDER')

        if addon_prefs.useGeneratedScripts:
            bfu_unreal_import_module = propsSub.column()
            bfu_unreal_import_module.prop(
                scene,
                'bfu_unreal_import_module',
                icon='FILE_FOLDER')
            bfu_unreal_import_location = propsSub.column()
            bfu_unreal_import_location.prop(
                scene,
                'bfu_unreal_import_location',
                icon='FILE_FOLDER')

        # File path
        filePath = layout.row()
        filePath = filePath.column()
        filePath.prop(scene, 'bfu_export_static_file_path')
        filePath.prop(scene, 'bfu_export_skeletal_file_path')
        filePath.prop(scene, 'bfu_export_alembic_file_path')
        filePath.prop(scene, 'bfu_export_groom_file_path')
        filePath.prop(scene, 'bfu_export_camera_file_path')
        filePath.prop(scene, 'bfu_export_spline_file_path')
        filePath.prop(scene, 'bfu_export_other_file_path')

        # File name
        fileName = layout.row()
        fileName = fileName.column()
        fileName.prop(scene, 'bfu_file_export_log_name', icon='FILE')
        if addon_prefs.useGeneratedScripts:
            fileName.prop(
                scene,
                'bfu_file_import_asset_script_name',
                icon='FILE')
            fileName.prop(
                scene,
                'bfu_file_import_sequencer_script_name',
                icon='FILE')