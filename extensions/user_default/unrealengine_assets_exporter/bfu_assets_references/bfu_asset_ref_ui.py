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
from .. import bbpl
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bfu_skeletal_mesh


def draw_ui(layout: bpy.types.UILayout, obj: bpy.types.Object):
    
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
    is_skeletal_mesh = bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj)
    if is_skeletal_mesh is False:
        return
    
    # Draw UI
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):   
        scene.bfu_engine_ref_properties_expanded.draw(layout)
        if scene.bfu_engine_ref_properties_expanded.is_expend():

            # SkeletalMesh prop
            if is_skeletal_mesh:
                if not obj.bfu_export_as_lod_mesh:
                    unreal_engine_refs = layout.column()
                    draw_skeleton_prop(unreal_engine_refs, obj)
                    draw_skeletal_mesh_prop(unreal_engine_refs, obj)


def draw_skeleton_prop(layout: bpy.types.UILayout, obj: bpy.types.Object):
    layout.prop(obj, "bfu_engine_ref_skeleton_search_mode")
    if obj.bfu_engine_ref_skeleton_search_mode == "auto":
        pass
    if obj.bfu_engine_ref_skeleton_search_mode == "custom_name":
        layout.prop(obj, "bfu_engine_ref_skeleton_custom_name")
    if obj.bfu_engine_ref_skeleton_search_mode == "custom_path_name":
        layout.prop(obj, "bfu_engine_ref_skeleton_custom_path")
        layout.prop(obj, "bfu_engine_ref_skeleton_custom_name")
    if obj.bfu_engine_ref_skeleton_search_mode == "custom_reference":
        layout.prop(obj, "bfu_engine_ref_skeleton_custom_ref")

def draw_skeletal_mesh_prop(layout: bpy.types.UILayout, obj: bpy.types.Object):
    layout.prop(obj, "bfu_engine_ref_skeletal_mesh_search_mode")
    if obj.bfu_engine_ref_skeletal_mesh_search_mode == "auto":
        pass
    if obj.bfu_engine_ref_skeletal_mesh_search_mode == "custom_name":
        layout.prop(obj, "bfu_engine_ref_skeletal_mesh_custom_name")
    if obj.bfu_engine_ref_skeletal_mesh_search_mode == "custom_path_name":
        layout.prop(obj, "bfu_engine_ref_skeletal_mesh_custom_path")
        layout.prop(obj, "bfu_engine_ref_skeletal_mesh_custom_name")
    if obj.bfu_engine_ref_skeletal_mesh_search_mode == "custom_reference":
        layout.prop(obj, "bfu_engine_ref_skeletal_mesh_custom_ref")