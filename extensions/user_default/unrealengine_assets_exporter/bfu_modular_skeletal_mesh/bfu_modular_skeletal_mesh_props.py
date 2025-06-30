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

def get_preset_values():
    preset_values = [
        'obj.bfu_modular_skeletal_mesh_mode',
        'obj.bfu_modular_skeletal_mesh_every_meshs_separate',
        'obj.bfu_modular_skeletal_specified_parts_meshs_template'
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

    bpy.types.Scene.bfu_modular_skeletal_mesh_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Modular Skeletal Mesh")

    bpy.types.Object.bfu_modular_skeletal_mesh_mode = bpy.props.EnumProperty(
        name="Modular Skeletal Mesh Mode",
        description='Modular skeletal mesh mode',
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("all_in_one",
                "All In One",
                "Export all child meshs  of the armature as one skeletal mesh.",
                1),
            ("every_meshs",
                "Every Meshs",
                "Export one skeletal mesh for every child meshs of the armature.",
                2),
            ("specified_parts",
                "Specified Parts",
                "Export specified mesh parts.",
                3)
            ]
        )
    
    bpy.types.Object.bfu_modular_skeletal_mesh_every_meshs_separate = bpy.props.StringProperty(
        name="Separate string",
        description="String between armature name and mesh name",
        override={'LIBRARY_OVERRIDABLE'},
        default="_"
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bfu_modular_skeletal_mesh_properties_expanded
    del bpy.types.Object.bfu_modular_skeletal_mesh_every_meshs_separate
    del bpy.types.Object.bfu_modular_skeletal_mesh_mode