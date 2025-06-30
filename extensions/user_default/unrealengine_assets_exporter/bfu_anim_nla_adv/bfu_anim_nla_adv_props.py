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
        'obj.bfu_move_nla_to_center_for_export',
        'obj.bfu_rotate_nla_to_zero_for_export',
    ]
    return preset_values

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_animation_nla_advanced_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="NLA Advanced Properties")

    bpy.types.Object.bfu_move_nla_to_center_for_export = bpy.props.BoolProperty(
        name="Move NLA to center",
        description=(
            "(Non linear animation only) If true use object origin else use scene origin." +
            " | If true the mesh will be moved to the center" +
            " of the scene for export." +
            " (This is used so that the origin of the fbx file" +
            " is the same as the mesh in blender)" +
            " Note: Unreal Engine ignore the position of the skeleton at the import."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_rotate_nla_to_zero_for_export = bpy.props.BoolProperty(
        name="Rotate NLA to zero",
        description=(
            "(Non linear animation only) If true use object rotation else use scene rotation." +
            " | If true the mesh will use zero rotation for export."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_rotate_nla_to_zero_for_export
    del bpy.types.Object.bfu_move_nla_to_center_for_export

    del bpy.types.Scene.bfu_animation_nla_advanced_properties_expanded