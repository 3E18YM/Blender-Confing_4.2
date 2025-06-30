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


def draw_ui(layout: bpy.types.UILayout, context: bpy.types.Context):
    scene = context.scene
    addon_prefs = bfu_basics.GetAddonPrefs()

    scene.bfu_export_process_properties_expanded.draw(layout)
    if scene.bfu_export_process_properties_expanded.is_expend():

        # Feedback info :
        final_asset_cache = bfu_cached_asset_list.GetfinalAssetCache()
        final_asset_list_to_export = final_asset_cache.GetFinalAssetList()
        AssetNum = len(final_asset_list_to_export)
        AssetInfo = layout.row().box().split(factor=0.75)
        AssetFeedback = str(AssetNum) + " Asset(s) will be exported."
        AssetInfo.label(text=AssetFeedback, icon='INFO')
        AssetInfo.operator("object.showasset")

        # Export button :
        checkButton = layout.row(align=True)
        checkButton.operator("object.checkpotentialerror", icon='FILE_TICK')
        checkButton.operator("object.openpotentialerror", icon='LOOP_BACK', text="")

        exportButton = layout.row()
        exportButton.scale_y = 2.0
        exportButton.operator("object.exportforunreal", icon='EXPORT')

    scene.bfu_script_tool_expanded.draw(layout)
    if scene.bfu_script_tool_expanded.is_expend():
        if addon_prefs.useGeneratedScripts:
            copyButton = layout.row()
            copyButton.operator("object.copy_importassetscript_command")
            copyButton.operator("object.copy_importsequencerscript_command")
            layout.label(text="Click on one of the buttons to copy the import command.", icon='INFO')
            layout.label(text="Then paste it into the cmd console of unreal.")
            layout.label(text="You need activate python plugins in Unreal Engine.")

        else:
            layout.label(text='(Generated scripts are deactivated.)')