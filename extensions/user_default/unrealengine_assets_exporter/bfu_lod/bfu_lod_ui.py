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
from . import bfu_lod_utils
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl
from .. import bfu_assets_manager
from .. import bfu_static_mesh


def draw_ui(layout: bpy.types.UILayout, obj: bpy.types.Object):

    if obj is None:
        return
    
    scene = bpy.context.scene 
    addon_prefs = bfu_basics.GetAddonPrefs()

    # Hide filters
    if obj is None:
        return
    if bfu_utils.GetExportAsProxy(obj):
        return
    if addon_prefs.useGeneratedScripts is False:
        return
    if obj.bfu_export_type != "export_recursive":
        return
    
    # Draw UI
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "MISC"):        
        scene.bfu_lod_properties_expanded.draw(layout)
        if scene.bfu_lod_properties_expanded.is_expend():

            # Unreal python no longer support Skeletal mesh LODS import.
            asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_asset_class(obj)
            if asset_class and asset_class.use_lods == True:
                LodProp = layout.column()
                LodProp.prop(obj, 'bfu_export_as_lod_mesh')

            #Static only because Unreal python not support Skeletal mesh LODS import.
            if (bfu_static_mesh.bfu_static_mesh_utils.is_static_mesh(obj)):

                # Lod Groups
                bfu_static_mesh_lod_group = layout.row()
                bfu_static_mesh_lod_group.prop(obj, 'bfu_use_static_mesh_lod_group', text="")
                SMLODGroupChild = bfu_static_mesh_lod_group.column()
                SMLODGroupChild.enabled = obj.bfu_use_static_mesh_lod_group
                SMLODGroupChild.prop(obj, 'bfu_static_mesh_lod_group')
                bfu_static_mesh_lod_group.enabled = obj.bfu_export_as_lod_mesh is False

                # Lod Slots 
                LodList = layout.column()
                LodList.prop(obj, 'bfu_lod_target1')
                LodList.prop(obj, 'bfu_lod_target2')
                LodList.prop(obj, 'bfu_lod_target3')
                LodList.prop(obj, 'bfu_lod_target4')
                LodList.prop(obj, 'bfu_lod_target5')
                LodList.enabled = obj.bfu_export_as_lod_mesh is False and obj.bfu_use_static_mesh_lod_group is False

