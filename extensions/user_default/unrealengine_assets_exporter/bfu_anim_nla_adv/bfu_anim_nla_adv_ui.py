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
from .. import bfu_alembic_animation



def draw_ui(layout: bpy.types.UILayout, obj: bpy.types.Object):

    scene = bpy.context.scene 
    addon_prefs = bfu_basics.GetAddonPrefs()

    # Hide filters
    if obj is None:
        return
    if obj.bfu_export_type != "export_recursive":
        return
    if bfu_alembic_animation.bfu_alembic_animation_utils.is_alembic_animation(obj):
        return
    
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "ANIM"):
        scene.bfu_animation_nla_advanced_properties_expanded.draw(layout)
        if scene.bfu_animation_nla_advanced_properties_expanded.is_expend():
            transformProp2 = layout.column()
            transformProp2.enabled = obj.bfu_anim_nla_use
            transformProp2.prop(obj, "bfu_move_nla_to_center_for_export")
            transformProp2.prop(obj, "bfu_rotate_nla_to_zero_for_export")