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
from .. import bbpl
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bfu_assets_manager
from .. import bfu_cached_asset_list
from .. import bfu_check_potential_error
from .. import bfu_export
from .. import bfu_write_text


class BFU_OT_ExportForUnrealEngineButton(bpy.types.Operator):
    bl_label = "Export for Unreal Engine"
    bl_idname = "object.exportforunreal"
    bl_description = "Export all assets of this scene."

    def execute(self, context):
        scene = bpy.context.scene

        def isReadyForExport():

            def GetIfOneTypeCheck():
                all_assets = bfu_assets_manager.bfu_asset_manager_utils.get_all_asset_class()
                for assets in all_assets:
                    assets: bfu_assets_manager.bfu_asset_manager_type.BFU_BaseAssetClass
                    if assets.can_export_asset():
                        return True

                if (scene.bfu_use_static_collection_export
                        or scene.bfu_use_anin_export):
                    return True
                else:
                    return False

            if not bfu_basics.CheckPluginIsActivated("io_scene_fbx"):
                self.report(
                    {'WARNING'},
                    'Add-on FBX format is not activated!' +
                    ' Edit > Preferences > Add-ons > And check "FBX format"')
                return False

            if not GetIfOneTypeCheck():
                self.report(
                    {'WARNING'},
                    "No asset type is checked.")
                return False

            final_asset_cache = bfu_cached_asset_list.GetfinalAssetCache()
            final_asset_list_to_export = final_asset_cache.GetFinalAssetList()
            if not len(final_asset_list_to_export) > 0:
                self.report(
                    {'WARNING'},
                    "Not found assets with" +
                    " \"Export recursive\" properties " +
                    "or collection to export.")
                return False

            if not bpy.data.is_saved:
                # Primary check	if file is saved
                # to avoid windows PermissionError
                self.report(
                    {'WARNING'},
                    "Please save this .blend file before export.")
                return False

            if bbpl.scene_utils.is_tweak_mode():
                # Need exit Tweakmode because the Animation data is read only.
                self.report(
                    {'WARNING'},
                    "Exit Tweakmode in NLA Editor. [Tab]")
                return False

            return True

        if not isReadyForExport():
            return {'FINISHED'}

        scene.UnrealExportedAssetsList.clear()
        counter = bpl.utils.CounterTimer()
        bfu_check_potential_error.bfu_check_utils.process_general_fix()
        bfu_export.bfu_export_asset.process_export(self)
        bfu_write_text.WriteAllTextFiles()

        self.report(
            {'INFO'},
            "Export of " + str(len(scene.UnrealExportedAssetsList)) + " asset(s) has been finalized in " + counter.get_str_time() + " Look in console for more info.")
        print(
            "=========================" +
            " Exported asset(s) " +
            "=========================")
        print("")
        lines = bfu_write_text.WriteExportLog().splitlines()
        for line in lines:
            print(line)
        print("")
        print(
            "=========================" +
            " ... " +
            "=========================")

        return {'FINISHED'}

class BFU_OT_CopyImportAssetScriptCommand(bpy.types.Operator):
    bl_label = "Copy import script (Assets)"
    bl_idname = "object.copy_importassetscript_command"
    bl_description = "Copy Import Asset Script command"

    def execute(self, context):
        scene = context.scene
        bfu_basics.setWindowsClipboard(bfu_utils.GetImportAssetScriptCommand())
        self.report(
            {'INFO'},
            "command for "+scene.bfu_file_import_asset_script_name +
            " copied")
        return {'FINISHED'}

class BFU_OT_CopyImportSequencerScriptCommand(bpy.types.Operator):
    bl_label = "Copy import script (Sequencer)"
    bl_idname = "object.copy_importsequencerscript_command"
    bl_description = "Copy Import Sequencer Script command"

    def execute(self, context):
        scene = context.scene
        bfu_basics.setWindowsClipboard(bfu_utils.GetImportSequencerScriptCommand())
        self.report(
            {'INFO'},
            "command for "+scene.bfu_file_import_sequencer_script_name +
            " copied")
        return {'FINISHED'}


def get_preset_values():
    preset_values = [
        ]
    return preset_values

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_ExportForUnrealEngineButton,
    BFU_OT_CopyImportAssetScriptCommand,
    BFU_OT_CopyImportSequencerScriptCommand,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
