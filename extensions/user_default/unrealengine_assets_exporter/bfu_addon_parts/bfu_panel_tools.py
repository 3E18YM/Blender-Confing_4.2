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
from .. import bfu_camera
from .. import bfu_spline
from .. import bfu_collision
from .. import bfu_socket
from .. import bfu_uv_map
from .. import bfu_light_map

class BFU_PT_BlenderForUnrealTool(bpy.types.Panel):
    # Tool panel

    bl_idname = "BFU_PT_BlenderForUnrealTool"
    bl_label = "UE AE Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"

    def draw(self, context: bpy.types.Context):

        layout = self.layout

        # Tools sections
        bfu_camera.bfu_camera_ui_and_props.draw_tools_ui(layout, context)
        bfu_spline.bfu_spline_ui_and_props.draw_tools_ui(layout, context)

        bfu_collision.bfu_collision_ui.draw_tools_ui(layout, context)
        bfu_socket.bfu_socket_ui_and_props.draw_tools_ui(layout, context)

        bfu_uv_map.bfu_uv_map_ui.draw_tools_ui(layout, context)
        bfu_light_map.bfu_light_map_ui.draw_tools_ui(layout, context)


''

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_PT_BlenderForUnrealTool,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
