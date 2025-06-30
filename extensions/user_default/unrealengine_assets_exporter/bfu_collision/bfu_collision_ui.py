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
from .. import bfu_static_mesh
from .. import bfu_skeletal_mesh


def draw_ui_object(layout: bpy.types.UILayout, obj: bpy.types.Object):
    scene = bpy.context.scene 
    addon_prefs = bfu_basics.GetAddonPrefs()

    # Hide filters
    if obj is None:
        return
    is_static_mesh = bfu_static_mesh.bfu_static_mesh_utils.is_static_mesh(obj)
    is_skeletal_mesh = bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj)
    if addon_prefs.useGeneratedScripts is False:
        return
    if bfu_utils.GetExportAsProxy(obj):
        return
    if obj.bfu_export_type != "export_recursive":
        return
    if is_static_mesh == False and is_skeletal_mesh == False:
        return

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "MISC"):
        scene.bfu_object_collision_properties_expanded.draw(layout)
        if scene.bfu_object_collision_properties_expanded.is_expend():
            # StaticMesh prop
            if is_static_mesh:
                if not obj.bfu_export_as_lod_mesh:
                    auto_generate_collision = layout.row()
                    auto_generate_collision.prop(
                        obj,
                        'bfu_auto_generate_collision'
                        )
                    collision_trace_flag = layout.row()
                    collision_trace_flag.prop(
                        obj,
                        'bfu_collision_trace_flag'
                        )
            # SkeletalMesh prop
            if is_skeletal_mesh:
                if not obj.bfu_export_as_lod_mesh:
                    create_physics_asset = layout.row()
                    create_physics_asset.prop(obj, "bfu_create_physics_asset")
                    enable_skeletal_mesh_per_poly_collision = layout.row()
                    enable_skeletal_mesh_per_poly_collision.prop(obj, 'bfu_enable_skeletal_mesh_per_poly_collision')


def draw_tools_ui(layout: bpy.types.UILayout, context: bpy.types.Context):
    scene = context.scene
    
    scene.bfu_tools_collision_properties_expanded.draw(layout)
    if scene.bfu_tools_collision_properties_expanded.is_expend():

        # Draw user tips and check can use buttons
        ready_for_convert_collider = False
        if not bbpl.utils.active_mode_is("OBJECT"):
            layout.label(text="Switch to Object Mode.", icon='INFO')
        else:
            if bbpl.utils.found_type_in_selection("MESH", False):
                if bbpl.utils.active_type_is_not("ARMATURE") and len(bpy.context.selected_objects) > 1:
                    layout.label(text="Click on button for convert to collider.", icon='INFO')
                    ready_for_convert_collider = True
                else:
                    layout.label(text="Select with [SHIFT] the collider owner.", icon='INFO')
            else:
                layout.label(text="Please select your collider Object(s). Active should be the owner.", icon='INFO')
            
        # Draw buttons
        convertButtons = layout.row().split(factor=0.80)
        convertStaticCollisionButtons = convertButtons.column()
        convertStaticCollisionButtons.enabled = ready_for_convert_collider
        convertStaticCollisionButtons.operator("object.converttoboxcollision", icon='MESH_CUBE')
        convertStaticCollisionButtons.operator("object.converttoconvexcollision", icon='MESH_ICOSPHERE')
        convertStaticCollisionButtons.operator("object.converttocapsulecollision", icon='MESH_CAPSULE')
        convertStaticCollisionButtons.operator("object.converttospherecollision", icon='MESH_UVSPHERE')
        layout.operator("object.toggle_collision_visibility", text="Toggle Collision Visibility", icon='HIDE_OFF')