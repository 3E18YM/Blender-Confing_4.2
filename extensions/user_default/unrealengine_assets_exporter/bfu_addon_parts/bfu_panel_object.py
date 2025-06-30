# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================


import os
import bpy
from .. import bbpl
from .. import bfu_basics
from .. import languages
from .. import bfu_custom_property
from .. import bfu_base_object
from .. import bfu_adv_object
from .. import bfu_base_collection
from .. import bfu_material
from .. import bfu_camera
from .. import bfu_spline
from .. import bfu_vertex_color
from .. import bfu_static_mesh
from .. import bfu_skeletal_mesh
from .. import bfu_modular_skeletal_mesh
from .. import bfu_lod
from .. import bfu_alembic_animation
from .. import bfu_anim_base
from .. import bfu_anim_action
from .. import bfu_anim_action_adv
from .. import bfu_anim_nla
from .. import bfu_anim_nla_adv
from .. import bfu_groom
from .. import bfu_uv_map
from .. import bfu_light_map
from .. import bfu_assets_references
from .. import bfu_collision

class BFU_PT_BlenderForUnrealObject(bpy.types.Panel):
    # Unreal engine export panel

    bl_idname = "BFU_PT_BlenderForUnrealObject"
    bl_label = "Unreal Engine Assets Exporter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"


    class BFU_MT_ObjectGlobalPropertiesPresets(bpy.types.Menu):
        bl_label = 'Global Properties Presets'
        preset_subdir = 'blender-for-unrealengine/global-properties-presets'
        preset_operator = 'script.execute_preset'
        draw = bpy.types.Menu.draw_preset

    from bl_operators.presets import AddPresetBase

    class BFU_OT_AddObjectGlobalPropertiesPreset(AddPresetBase, bpy.types.Operator):
        bl_idname = 'object.add_globalproperties_preset'
        bl_label = 'Add or remove a preset for Global properties'
        bl_description = 'Add or remove a preset for Global properties'
        preset_menu = 'BFU_MT_ObjectGlobalPropertiesPresets'

        def get_object_global_preset_propertys():
            preset_values = []
            preset_values += bfu_base_object.bfu_base_obj_props.get_preset_values()
            preset_values += bfu_adv_object.bfu_adv_obj_props.get_preset_values()
            preset_values += bfu_base_collection.bfu_base_col_props.get_preset_values()
            preset_values += bfu_modular_skeletal_mesh.bfu_modular_skeletal_mesh_props.get_preset_values()
            preset_values += bfu_custom_property.bfu_custom_property_props.get_preset_values()
            preset_values += bfu_material.bfu_material_props.get_preset_values()
            preset_values += bfu_camera.bfu_camera_ui_and_props.get_preset_values()
            preset_values += bfu_spline.bfu_spline_ui_and_props.get_preset_values()
            preset_values += bfu_static_mesh.bfu_static_mesh_props.get_preset_values()
            preset_values += bfu_skeletal_mesh.bfu_skeletal_mesh_props.get_preset_values()
            preset_values += bfu_alembic_animation.bfu_alembic_animation_props.get_preset_values()
            preset_values += bfu_anim_base.bfu_anim_base_props.get_preset_values()
            preset_values += bfu_anim_action.bfu_anim_action_props.get_preset_values()
            preset_values += bfu_anim_action_adv.bfu_anim_action_adv_props.get_preset_values()
            preset_values += bfu_anim_nla.bfu_anim_nla_props.get_preset_values()
            preset_values += bfu_anim_nla_adv.bfu_anim_nla_adv_props.get_preset_values()
            preset_values += bfu_vertex_color.bfu_vertex_color_props.get_preset_values()
            preset_values += bfu_lod.bfu_lod_props.get_preset_values()
            preset_values += bfu_uv_map.bfu_uv_map_props.get_preset_values()
            preset_values += bfu_light_map.bfu_light_map_props.get_preset_values()
            preset_values += bfu_assets_references.bfu_asset_ref_props.get_preset_values()
            preset_values += bfu_collision.bfu_collision_props.get_preset_values()
            return preset_values

        # Common variable used for all preset values
        preset_defines = [
                            'obj = bpy.context.object',
                            'col = bpy.context.collection',
                            'scene = bpy.context.scene'
                         ]

        # Properties to store in the preset
        preset_values = get_object_global_preset_propertys()

        # Directory to store the presets
        preset_subdir = 'blender-for-unrealengine/global-properties-presets'


    def draw(self, context: bpy.types.Context):
        
        scene = bpy.context.scene
        obj = bpy.context.object
        addon_prefs = bfu_basics.GetAddonPrefs()
        layout = self.layout
        
        # Extension details
        if bpy.app.version >= (4, 2, 0):
            version_str = 'Version '+ str(bbpl.blender_extension.extension_utils.get_package_version())
        else:
            version_str = 'Version '+ bbpl.blender_addon.addon_utils.get_addon_version_str("Unreal Engine Assets Exporter")

        credit_box = layout.box()
        credit_box.label(text=languages.ti('intro'))
        credit_box.label(text=version_str)
        bbpl.blender_layout.layout_doc_button.functions.add_doc_page_operator(
            layout = layout,
            url = "https://github.com/xavier150/Blender-For-UnrealEngine-Addons",
            text = "Open Github page",
            icon="HELP"
            )

        # Presets
        row = layout.row(align=True)
        row.menu('BFU_MT_ObjectGlobalPropertiesPresets', text='Global Properties Presets')
        row.operator('object.add_globalproperties_preset', text='', icon='ADD')
        row.operator('object.add_globalproperties_preset', text='', icon='REMOVE').remove_active = True

        # Tab Buttions
        layout.row().prop(scene, "bfu_active_tab", expand=True)
        if scene.bfu_active_tab == "OBJECT":
            layout.row().prop(scene, "bfu_active_object_tab", expand=True)
        if scene.bfu_active_tab == "SCENE":
            layout.row().prop(scene, "bfu_active_scene_tab", expand=True)

        # Object
        bfu_base_object.bfu_base_obj_ui.draw_ui(layout, obj)
        bfu_adv_object.bfu_adv_obj_ui.draw_ui(layout, obj)
        bfu_static_mesh.bfu_static_mesh_ui.draw_ui_object(layout, obj)
        bfu_skeletal_mesh.bfu_skeletal_mesh_ui.draw_ui_object(layout, obj)
        bfu_modular_skeletal_mesh.bfu_modular_skeletal_mesh_ui.draw_ui_object(layout, obj)
        bfu_alembic_animation.bfu_alembic_animation_ui.draw_ui_object(layout, obj)
        bfu_groom.bfu_groom_ui.draw_ui_object(layout, obj)
        bfu_camera.bfu_camera_ui_and_props.draw_ui_object_camera(layout, obj)
        bfu_spline.bfu_spline_ui_and_props.draw_ui_object_spline(layout, obj)
        bfu_lod.bfu_lod_ui.draw_ui(layout, obj)
        bfu_collision.bfu_collision_ui.draw_ui_object(layout, obj)
        bfu_uv_map.bfu_uv_map_ui.draw_obj_ui(layout, obj)
        bfu_light_map.bfu_light_map_ui.draw_obj_ui(layout, obj)
        bfu_material.bfu_material_ui.draw_ui_object(layout, obj)
        bfu_vertex_color.bfu_vertex_color_ui.draw_ui_object(layout, obj)
        bfu_assets_references.bfu_asset_ref_ui.draw_ui(layout, obj)

        # Animations
        bfu_anim_action.bfu_anim_action_ui.draw_ui(layout, obj)
        bfu_anim_action_adv.bfu_anim_action_adv_ui.draw_ui(layout, obj)
        bfu_anim_nla.bfu_anim_nla_ui.draw_ui(layout, obj)
        bfu_anim_nla_adv.bfu_anim_nla_adv_ui.draw_ui(layout, obj)
        bfu_anim_base.bfu_anim_base_ui.draw_ui(layout, obj)
        bfu_anim_base.bfu_anim_base_ui.draw_animation_tab_foot_ui(layout, obj)

        # Scene
        bfu_base_collection.bfu_base_col_ui.draw_ui(layout, context)

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_PT_BlenderForUnrealObject,
    BFU_PT_BlenderForUnrealObject.BFU_MT_ObjectGlobalPropertiesPresets,
    BFU_PT_BlenderForUnrealObject.BFU_OT_AddObjectGlobalPropertiesPreset,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
