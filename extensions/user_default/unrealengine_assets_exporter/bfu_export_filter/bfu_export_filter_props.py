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
        # Filter Categories
        'scene.bfu_use_static_export',
        'scene.bfu_use_static_collection_export',
        'scene.bfu_use_skeletal_export',
        'scene.bfu_use_anin_export',
        'scene.bfu_use_alembic_export',
        'scene.bfu_use_groom_simulation_export',
        'scene.bfu_use_camera_export',
        'scene.bfu_use_spline_export',

        # Additional Files
        'scene.bfu_use_text_export_log',
        'scene.bfu_use_text_import_asset_script',
        'scene.bfu_use_text_import_sequence_script',
        'scene.bfu_use_text_additional_data',

        # Export Filter
        'scene.bfu_export_selection_filter',
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

    bpy.types.Scene.bfu_export_filter_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Export filters")

    # Filter Categories
    bpy.types.Scene.bfu_use_static_export = bpy.props.BoolProperty(
        name="StaticMesh(s)",
        description="Check mark to export StaticMesh(s)",
        default=True
        )

    bpy.types.Scene.bfu_use_static_collection_export = bpy.props.BoolProperty(
        name="Collection(s) ",
        description="Check mark to export Collection(s)",
        default=True
        )

    bpy.types.Scene.bfu_use_skeletal_export = bpy.props.BoolProperty(
        name="SkeletalMesh(s)",
        description="Check mark to export SkeletalMesh(s)",
        default=True
        )

    bpy.types.Scene.bfu_use_anin_export = bpy.props.BoolProperty(
        name="Animation(s)",
        description="Check mark to export Animation(s)",
        default=True
        )

    bpy.types.Scene.bfu_use_alembic_export = bpy.props.BoolProperty(
        name="Alembic Animation(s)",
        description="Check mark to export Alembic animation(s)",
        default=True
        )
    
    bpy.types.Scene.bfu_use_groom_simulation_export = bpy.props.BoolProperty(
        name="Groom Simulation(s)",
        description="Check mark to export Alembic animation(s)",
        default=True
        )

    bpy.types.Scene.bfu_use_camera_export = bpy.props.BoolProperty(
        name="Camera(s)",
        description="Check mark to export Camera(s)",
        default=True
        )
    
    bpy.types.Scene.bfu_use_spline_export = bpy.props.BoolProperty(
        name="Spline(s)",
        description="Check mark to export Spline(s)",
        default=True
        )
    
    # Additional Files
    bpy.types.Scene.bfu_use_text_export_log = bpy.props.BoolProperty(
        name="Export Log",
        description="Check mark to write export log file",
        default=True
        )

    bpy.types.Scene.bfu_use_text_import_asset_script = bpy.props.BoolProperty(
        name="Import assets script",
        description="Check mark to write import asset script file",
        default=True
        )

    bpy.types.Scene.bfu_use_text_import_sequence_script = bpy.props.BoolProperty(
        name="Import sequence script",
        description="Check mark to write import sequencer script file",
        default=True
        )

    bpy.types.Scene.bfu_use_text_additional_data = bpy.props.BoolProperty(
        name="Additional data",
        description=(
            "Check mark to write additional data" +
            " like parameter or anim tracks"),
        default=True
        )
    
    # Export Filter
    bpy.types.Scene.bfu_export_selection_filter = bpy.props.EnumProperty(
        name="Selection filter",
        items=[
            ('default', "No Filter", "Export as normal all objects with the recursive export option.", 0),
            ('only_object', "Only selected", "Export only the selected and visible object(s)", 1),
            ('only_object_action', "Only selected and active action",
                "Export only the selected and visible object(s) and active action on this object", 2),
            ],
        description=(
            "Choose what need be export from asset list."),
        default="default"
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bfu_export_selection_filter

    del bpy.types.Scene.bfu_use_text_additional_data
    del bpy.types.Scene.bfu_use_text_import_sequence_script
    del bpy.types.Scene.bfu_use_text_import_asset_script
    del bpy.types.Scene.bfu_use_text_export_log

    del bpy.types.Scene.bfu_use_spline_export
    del bpy.types.Scene.bfu_use_camera_export
    del bpy.types.Scene.bfu_use_groom_simulation_export
    del bpy.types.Scene.bfu_use_alembic_export
    del bpy.types.Scene.bfu_use_anin_export
    del bpy.types.Scene.bfu_use_skeletal_export
    del bpy.types.Scene.bfu_use_static_collection_export
    del bpy.types.Scene.bfu_use_static_export

    del bpy.types.Scene.bfu_export_filter_properties_expanded