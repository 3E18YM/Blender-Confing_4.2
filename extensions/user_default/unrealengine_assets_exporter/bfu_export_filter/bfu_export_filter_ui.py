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
    
    scene.bfu_export_filter_properties_expanded.draw(layout)
    if scene.bfu_export_filter_properties_expanded.is_expend():

        # Assets
        row = layout.row()
        AssetsCol = row.column()
        AssetsCol.label(text="Asset types to export", icon='PACKAGE')
        AssetsCol.prop(scene, 'bfu_use_static_export')
        AssetsCol.prop(scene, 'bfu_use_static_collection_export')
        AssetsCol.prop(scene, 'bfu_use_skeletal_export')
        AssetsCol.prop(scene, 'bfu_use_anin_export')
        AssetsCol.prop(scene, 'bfu_use_alembic_export')
        AssetsCol.prop(scene, 'bfu_use_groom_simulation_export')
        AssetsCol.prop(scene, 'bfu_use_camera_export')
        AssetsCol.prop(scene, 'bfu_use_spline_export')
        layout.separator()

        # Additional file
        FileCol = row.column()
        FileCol.label(text="Additional file", icon='PACKAGE')
        FileCol.prop(scene, 'bfu_use_text_export_log')
        FileCol.prop(scene, 'bfu_use_text_import_asset_script')
        FileCol.prop(scene, 'bfu_use_text_import_sequence_script')
        if addon_prefs.useGeneratedScripts:
            FileCol.prop(scene, 'bfu_use_text_additional_data')

        # exportProperty
        export_by_select = layout.row()
        export_by_select.prop(scene, 'bfu_export_selection_filter')