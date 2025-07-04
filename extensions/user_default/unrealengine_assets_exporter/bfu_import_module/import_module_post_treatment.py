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

import os
from . import import_module_unreal_utils

try:
    import unreal
except ImportError:
    import unreal_engine as unreal


def import_static_lod(asset, asset_options, asset_data, asset_additional_data, lod_name, lod_number):

    print(f"Start Import Lod_{str(lod_number)} ({lod_name})")

    if "LevelOfDetail" in asset_additional_data:
        if lod_name in asset_additional_data["LevelOfDetail"]:
            lodTask = unreal.AssetImportTask()
            lodTask.filename = asset_additional_data["LevelOfDetail"][lod_name]
            destination_path = os.path.normpath(asset_data["full_import_path"]).replace('\\', '/')
            lodTask.destination_path = destination_path
            lodTask.automated = True
            lodTask.replace_existing = True

            if asset_options:
                lodTask.set_editor_property('options', asset_options)
            else:
                # Replicate asset import settings when asset_options is None
                lodTask.set_editor_property('options', asset.get_editor_property('asset_import_data'))


            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([lodTask])
            if len(lodTask.imported_object_paths) > 0:
                lodAsset = import_module_unreal_utils.load_asset(lodTask.imported_object_paths[0])
                slot_replaced = unreal.EditorStaticMeshLibrary.set_lod_from_static_mesh(asset, lod_number, lodAsset, 0, True)
                unreal.EditorAssetLibrary.delete_asset(lodTask.imported_object_paths[0])

def import_skeletal_lod(asset, asset_options, asset_data, asset_additional_data, lod_name, lod_number):
    if "LevelOfDetail" in asset_additional_data:
        if lod_name in asset_additional_data["LevelOfDetail"]:
            # Unreal python no longer support Skeletal mesh LODS import.
            pass

def set_static_mesh_lods(asset, asset_options, asset_data, asset_additional_data):
    # Import the StaticMesh lod(s)
    unreal.EditorStaticMeshLibrary.remove_lods(asset)  
    import_static_lod(asset, asset_options, asset_data, asset_additional_data, "lod_1", 1)
    import_static_lod(asset, asset_options, asset_data, asset_additional_data, "lod_2", 2)
    import_static_lod(asset, asset_options, asset_data, asset_additional_data, "lod_3", 3)
    import_static_lod(asset, asset_options, asset_data, asset_additional_data, "lod_4", 4)
    import_static_lod(asset, asset_options, asset_data, asset_additional_data, "lod_5", 5)


def set_skeletal_mesh_lods(asset, asset_options, asset_data, asset_additional_data):
    # Import the SkeletalMesh lod(s)
    import_skeletal_lod(asset, asset_options, asset_data, asset_additional_data, "lod_1", 1)
    import_skeletal_lod(asset, asset_options, asset_data, asset_additional_data, "lod_2", 2)
    import_skeletal_lod(asset, asset_options, asset_data, asset_additional_data, "lod_3", 3)
    import_skeletal_lod(asset, asset_options, asset_data, asset_additional_data, "lod_4", 4)
    import_skeletal_lod(asset, asset_options, asset_data, asset_additional_data, "lod_5", 5)


def set_sequence_preview_skeletal_mesh(asset: unreal.AnimSequence, origin_skeletal_mesh):
    if origin_skeletal_mesh:
        # @TODO preview_pose_asset doesn’t retarget right now. Need wait update in Unreal Engine Python API.
        asset.get_editor_property('preview_pose_asset')
        pass
        