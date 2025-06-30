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
from .. import bfu_export_procedure
from .. import bfu_cached_asset_list


def draw_ui(layout: bpy.types.UILayout, context: bpy.types.Context):

    
    scene = bpy.context.scene 

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("SCENE", "GENERAL"):

        scene.bfu_collection_properties_expanded.draw(layout)
        if scene.bfu_collection_properties_expanded.is_expend():
            collectionListProperty = layout.column()
            collectionListProperty.template_list(
                # type and unique id
                "BFU_UL_CollectionExportTarget", "",
                # pointer to the CollectionProperty
                scene, "bfu_collection_asset_list",
                # pointer to the active identifier
                scene, "bfu_active_collection_asset_list",
                maxrows=5,
                rows=5
            )
            collectionListProperty.operator(
                "object.updatecollectionlist",
                icon='RECOVER_LAST')

            if scene.bfu_active_collection_asset_list < len(scene.bfu_collection_asset_list):
                col_name = scene.bfu_collection_asset_list[scene.bfu_active_collection_asset_list].name
                if col_name in bpy.data.collections:
                    col = bpy.data.collections[col_name]
                    col_prop = layout
                    col_prop.prop(col, 'bfu_export_folder_name', icon='FILE_FOLDER')
                    bfu_export_procedure.bfu_export_procedure_ui.draw_collection_export_procedure(layout, col)

            collectionPropertyInfo = layout.row().box().split(factor=0.75)
            collection_asset_cache = bfu_cached_asset_list.GetCollectionAssetCache()
            collection_export_asset_list = collection_asset_cache.GetCollectionAssetList()
            collectionNum = len(collection_export_asset_list)
            collectionFeedback = (
                str(collectionNum) +
                " Collection(s) will be exported.")
            collectionPropertyInfo.label(text=collectionFeedback, icon='INFO')
            collectionPropertyInfo.operator("object.showscenecollection")
            layout.label(text='Note: The collection are exported like StaticMesh.')