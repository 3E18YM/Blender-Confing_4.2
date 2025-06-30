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
from .. import bfu_skeletal_mesh
from .. import bfu_alembic_animation
from .. import bfu_cached_asset_list


def draw_ui(layout: bpy.types.UILayout, obj: bpy.types.Object):
    
    scene = bpy.context.scene 
    addon_prefs = bfu_basics.GetAddonPrefs()

    # Hide filters
    if obj is None:
        return
    if obj.bfu_export_type != "export_recursive":
        return
    
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "ANIM"):
        scene.bfu_animation_advanced_properties_expanded.draw(layout)
        if scene.bfu_animation_advanced_properties_expanded.is_expend():
            # Animation fbx properties
            if bfu_alembic_animation.bfu_alembic_animation_utils.is_not_alembic_animation(obj):
                propsFbx = layout.row()
                if obj.bfu_skeleton_export_procedure != "auto-rig-pro":
                    propsFbx.prop(obj, 'bfu_sample_anim_for_export')
                propsFbx.prop(obj, 'bfu_simplify_anim_for_export')
            propsScaleAnimation = layout.row()
            propsScaleAnimation.prop(obj, "bfu_disable_free_scale_animation")

def draw_animation_tab_foot_ui(layout: bpy.types.UILayout, obj: bpy.types.Object):

    scene = bpy.context.scene 
    addon_prefs = bfu_basics.GetAddonPrefs()

    # Hide filters
    if obj is None:
        return
    if bfu_utils.GetExportAsProxy(obj):
        return
    if obj.bfu_export_type != "export_recursive":
        return
    if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_not_skeletal_mesh(obj):
        return
    
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "ANIM"):
        # Armature export action list feedback
        layout.label(
            text='Note: The Action with only one' +
            ' frame are exported like Pose.')
        ArmaturePropertyInfo = (
            layout.row().box().split(factor=0.75)
            )
        animation_asset_cache = bfu_cached_asset_list.GetAnimationAssetCache(obj)
        animation_to_export = animation_asset_cache.GetAnimationAssetList()
        ActionNum = len(animation_to_export)
        if obj.bfu_anim_nla_use:
            ActionNum += 1
        actionFeedback = (
            str(ActionNum) +
            " Animation(s) will be exported with this object.")
        ArmaturePropertyInfo.label(
            text=actionFeedback,
            icon='INFO')
        ArmaturePropertyInfo.operator("object.showobjaction")
