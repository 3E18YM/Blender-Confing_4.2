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



def draw_ui(layout: bpy.types.UILayout, obj: bpy.types.Object):

    scene = bpy.context.scene 
    addon_prefs = bfu_basics.GetAddonPrefs()


    # Hide filters
    if obj is None:
        return
    if obj.bfu_export_type != "export_recursive":
        return
    is_skeletal_mesh = bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj)
    
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "ANIM"):
        scene.bfu_animation_nla_properties_expanded.draw(layout)
        if scene.bfu_animation_nla_properties_expanded.is_expend():
            # NLA
            if is_skeletal_mesh:
                NLAAnim = layout.row()
                NLAAnim.prop(obj, 'bfu_anim_nla_use')
                NLAAnimChild = NLAAnim.column()
                NLAAnimChild.enabled = obj.bfu_anim_nla_use
                NLAAnimChild.prop(obj, 'bfu_anim_nla_export_name')
                if obj.bfu_skeleton_export_procedure == "auto-rig-pro":
                    NLAAnim.enabled = False
                    NLAAnimChild.enabled = False

            # NLA Time
            if obj.type != "CAMERA" and obj.bfu_skeleton_export_procedure != "auto-rig-pro":
                NLATimeProperty = layout.column()
                NLATimeProperty.enabled = obj.bfu_anim_nla_use
                NLATimeProperty.prop(obj, 'bfu_anim_nla_start_end_time_enum')
                if obj.bfu_anim_nla_start_end_time_enum == "with_customframes":
                    OfsetTime = NLATimeProperty.row()
                    OfsetTime.prop(obj, 'bfu_anim_nla_custom_start_frame')
                    OfsetTime.prop(obj, 'bfu_anim_nla_custom_end_frame')
                if obj.bfu_anim_nla_start_end_time_enum != "with_customframes":
                    OfsetTime = NLATimeProperty.row()
                    OfsetTime.prop(obj, 'bfu_anim_nla_start_frame_offset')
                    OfsetTime.prop(obj, 'bfu_anim_nla_end_frame_offset')