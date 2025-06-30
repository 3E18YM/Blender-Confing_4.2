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
from . import bfu_skeletal_mesh_utils
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl


def get_preset_values():
    preset_values = [
        'obj.bfu_export_deform_only',
        'obj.bfu_export_skeletal_mesh_as_static_mesh',
        'obj.bfu_create_sub_folder_with_skeletal_mesh_name',
        'obj.bfu_export_animation_without_mesh',
        'obj.bfu_mirror_symmetry_right_side_bones',
        'obj.bfu_use_ue_mannequin_bone_alignment',
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

    bpy.types.Scene.bfu_skeleton_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Skeleton")

    bpy.types.Object.bfu_export_deform_only = bpy.props.BoolProperty(
        name="Export only deform bones",
        description=(
            "Only write deforming bones" +
            " (and non-deforming ones when they have deforming children)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_export_skeletal_mesh_as_static_mesh = bpy.props.BoolProperty(
        name="Export as Static Mesh",
        description="If true this mesh will be exported as a Static Mesh",
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )
    
    bpy.types.Object.bfu_create_sub_folder_with_skeletal_mesh_name = bpy.props.BoolProperty(
        name="Create SK Sub Folder",
        description="Create a subfolder with the armature name to avoid asset conflicts during the export. (Recommended)",
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_export_animation_without_mesh = bpy.props.BoolProperty(
        name="Export animation without mesh",
        description=(
            "If checked, When exporting animation, do not include mesh data in the FBX file."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_mirror_symmetry_right_side_bones = bpy.props.BoolProperty(
        name="Revert direction of symmetry right side bones",
        description=(
            "If checked, The right-side bones will be mirrored for mirroring physic object in UE PhysicAsset Editor."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_use_ue_mannequin_bone_alignment = bpy.props.BoolProperty(
        name="Apply bone alignments similar to UE Mannequin.",
        description=(
            "If checked, similar to the UE Mannequin, the leg bones will be oriented upwards, and the pelvis and feet bone will be aligned facing upwards during export."
        ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
    )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_use_ue_mannequin_bone_alignment
    del bpy.types.Object.bfu_mirror_symmetry_right_side_bones
    del bpy.types.Object.bfu_export_animation_without_mesh
    
    del bpy.types.Object.bfu_create_sub_folder_with_skeletal_mesh_name
    del bpy.types.Object.bfu_export_skeletal_mesh_as_static_mesh

    del bpy.types.Object.bfu_export_deform_only

    del bpy.types.Scene.bfu_skeleton_properties_expanded