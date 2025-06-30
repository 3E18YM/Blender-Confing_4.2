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
        ]
    return preset_values

class BFU_UL_CollectionExportTarget(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):

        collection_is_valid = False
        if item.name in bpy.data.collections:
            collection_is_valid = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if collection_is_valid:  # If action is valid
                layout.prop(
                    bpy.data.collections[item.name],
                    "name",
                    text="",
                    emboss=False,
                    icon="OUTLINER_COLLECTION")
                layout.prop(item, "use", text="")
            else:
                dataText = (
                    'Collection named "' +
                    item.name +
                    '" Not Found. Please clic on update')
                layout.label(text=dataText, icon="ERROR")
        # Not optimised for 'GRID' layout type.
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class BFU_OT_UpdateCollectionButton(bpy.types.Operator):
    bl_label = "Update collection list"
    bl_idname = "object.updatecollectionlist"
    bl_description = "Update collection list"

    def execute(self, context):
        def UpdateExportCollectionList(scene):
            # Update the provisional collection list known by the object

            def SetUseFromLast(col_list, CollectionName):
                for item in col_list:
                    if item[0] == CollectionName:
                        if item[1]:
                            return True
                return False

            colSave = [["", False]]
            for col in scene.bfu_collection_asset_list:  # CollectionProperty
                name = col.name
                use = col.use
                colSave.append([name, use])
            scene.bfu_collection_asset_list.clear()
            for col in bpy.data.collections:
                scene.bfu_collection_asset_list.add().name = col.name
                useFromLast = SetUseFromLast(colSave, col.name)
                scene.bfu_collection_asset_list[col.name].use = useFromLast
        UpdateExportCollectionList(context.scene)
        return {'FINISHED'}

class BFU_OT_ShowCollectionToExport(bpy.types.Operator):
    bl_label = "Show collection(s)"
    bl_idname = "object.showscenecollection"
    bl_description = "Click to show collections to export"

    def execute(self, context):
        scene = context.scene
        collection_asset_cache = bfu_cached_asset_list.GetCollectionAssetCache()
        collection_export_asset_list = collection_asset_cache.GetCollectionAssetList()
        popup_title = "Collection list"
        if len(collection_export_asset_list) > 0:
            popup_title = (
                str(len(collection_export_asset_list))+' collection(s) to export found.')
        else:
            popup_title = 'No collection to export found.'

        def draw(self, context: bpy.types.Context):
            col = self.layout.column()
            for collection in collection_export_asset_list:
                row = col.row()
                row.label(text="- "+collection.name)
        bpy.context.window_manager.popup_menu(
            draw,
            title=popup_title,
            icon='GROUP')
        return {'FINISHED'}


class BFU_OT_SceneCollectionExport(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="collection data name", default="Unknown", override={'LIBRARY_OVERRIDABLE'})
    use: bpy.props.BoolProperty(name="export this collection", default=False, override={'LIBRARY_OVERRIDABLE'})


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_UL_CollectionExportTarget,
    BFU_OT_UpdateCollectionButton,
    BFU_OT_ShowCollectionToExport,
    BFU_OT_SceneCollectionExport,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_collection_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Collection Properties")

    bpy.types.Scene.bfu_collection_asset_list = bpy.props.CollectionProperty(
        type=BFU_OT_SceneCollectionExport,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'},
        )
    
    bpy.types.Scene.bfu_active_collection_asset_list = bpy.props.IntProperty(
        name="Active Collection",
        description="Index of the currently active collection",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
        )
    
    bpy.types.Collection.bfu_export_folder_name = bpy.props.StringProperty(
        name="Sub folder name",
        description=(
            'The name of sub folder.' +
            ' You can now use ../ for up one directory.'
            ),
        override={'LIBRARY_OVERRIDABLE'},
        maxlen=64,
        default="",
        subtype='FILE_NAME'
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Collection.bfu_export_folder_name

    del bpy.types.Scene.bfu_active_collection_asset_list
    del bpy.types.Scene.bfu_collection_asset_list
    del bpy.types.Scene.bfu_collection_properties_expanded