# -*- coding:utf-8 -*-
from ..iBlender_flip_fluids_addon import _z

# Blender FLIP Fluids Add-on
# Copyright (C) 2022 Ryan L. Guy
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bpy, os, platform, math, mathutils
from bpy.props import (
        IntProperty,
        FloatProperty,
        StringProperty,
        BoolProperty,
        PointerProperty,
        EnumProperty
        )

from .custom_properties import (
        NewMinMaxIntProperty,
        )

from . import preset_properties
from .. import types
from ..operators import helper_operators
from ..utils import version_compatibility_utils as vcu

DISABLE_FRAME_CHANGE_POST_HANDLER = False

def _update_render_passes_camera_screen(self, context):
    hprops = context.scene.flip_fluid_helper
    override_preferences = False # Feature enable override for development purposes
    if hprops.display_compositing_tools_in_ui or override_preferences:

        print("Update render passes camera screen called.")
        bl_camera_screen = bpy.data.objects.get("ff_camera_screen")
        if bl_camera_screen is None:
            print("Camera screen not found.")
            return

        bl_camera = bpy.data.objects.get(hprops.render_passes_cameraselection)
        if bl_camera is None:
            print("Camera not found.")
            return

        print(f"Updating camera screen scale with distance: {hprops.render_passes_camerascreen_distance}")
        helper_operators.update_camera_screen_scale(bl_camera_screen, bl_camera)


class FlipFluidHelperPropertiesRenderPassesCatcher(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name=_z("Name"), description="Name")
    catcher: bpy.props.BoolProperty(
        name=_z("Catcher"),
        description="Catcher\nObject will be used as catcher for shadows and reflections",
        default=False
    )


class FlipFluidHelperProperties(bpy.types.PropertyGroup):
    conv = vcu.convert_attribute_to_28

    enable_auto_frame_load = BoolProperty(
            name=_z("Auto-Load Baked Frames"),
            description="Auto-Load Baked Frames\nAutomatically load frames as they finish baking",
            default=False,
            update=lambda self, context: self._update_enable_auto_frame_load_cmd(context),
            ); exec(conv("enable_auto_frame_load"))
    enable_auto_frame_load_cmd = BoolProperty(
            name=_z("Sync With CMD Bake"),
            description="Sync With CMD Bake\nAutomatically load frames as they finish baking when running a command"
                " line bake. Note: this feature may decrease Blender performance and responsiveness"
                " when a CMD bake is not running. If this is an issue, it is recommended to disable"
                " this option when a CMD bake is not running",
            default=False,
            update=lambda self, context: self._update_enable_auto_frame_load_cmd(context),
            ); exec(conv("enable_auto_frame_load_cmd"))
    playback_frame_offset = IntProperty(
            name=_z("Frame Offset"),
            description="Frame Offset\nFrame offset for simulation playback",
            default=0,
            options={'HIDDEN'},
            ); exec(conv("playback_frame_offset"))

    cmd_bake_and_render = BoolProperty(
            name=_z("Bake and Render"),
            description="Bake and Render\nEnable both baking and rendering in the command line process",
            default=False,
            ); exec(conv("cmd_bake_and_render"))
    cmd_bake_and_render_mode = EnumProperty(
            name=_z("CMD Bake and Render Mode"),
            description="CMD Bake and Render Mode\nHow to bake and render the simulation",
            items=types.cmd_bake_and_render_mode,
            default='CMD_BAKE_AND_RENDER_MODE_SEQUENCE',
            options={'HIDDEN'},
            ); exec(conv("cmd_bake_and_render_mode"))
    cmd_launch_render_after_bake_mode = EnumProperty(
            name=_z("CMD Render After Bake Mode"),
            description="CMD Render After Bake Mode\nHow to render the simulation after the baking process finishes",
            items=types.cmd_render_after_bake_mode,
            default='CMD_RENDER_MODE_NORMAL',
            options={'HIDDEN'},
            ); exec(conv("cmd_launch_render_after_bake_mode"))
    cmd_bake_and_render_interleaved_instances = IntProperty(
            name=_z("Render Instances"),
            description="Render Instances\nMaximum number of render instances to run simultaneously. This number is how many frames"
                " are allowed to be rendered at the same time. More render instances maximizes system resource usage"
                " if the simulation is running faster than the render but will require more RAM and also VRAM if"
                " rendering on the GPU",
            default=1,
            min=1,
            soft_max=8,
            options={'HIDDEN'},
            ); exec(conv("cmd_bake_and_render_interleaved_instances"))
    cmd_bake_and_render_interleaved_no_overwrite = BoolProperty(
            name=_z("Continue render from last rendered frame"),
            description="Continue render from last rendered frame\nIf enabled, already rendered frames will not be overwritten and the render will begin"
                " after the last rendered frame. If disabled, frames will be overwritten and rendering will begin from"
                " the first frame",
            default=False,
            ); exec(conv("cmd_bake_and_render_interleaved_no_overwrite"))
    cmd_open_image_after_render = BoolProperty(
            name=_z("Open Image After Render"),
            description="Open Image After Render\nAfter the command line render process is finished, open the image in your default OS image program",
            default=True,
            ); exec(conv("cmd_open_image_after_render"))
    cmd_close_window_after_render = BoolProperty(
            name=_z("Close CMD Window After Render"),
            description="Close CMD Window After Render\nAfter the command line render process is finished, open the image in your default OS image program",
            default=False,
            ); exec(conv("cmd_close_window_after_render"))
            

    ### NEW RENDER PASSES ###

    # Disabled by default for the release of FLIP Fluids 1.8.0
    display_compositing_tools_in_ui = BoolProperty(default=False); exec(conv("display_compositing_tools_in_ui"))
   
    render_passes = BoolProperty(
            name=_z("Activate Passes Rendering"),
            description="Activate Passes Rendering\nActivate rendering of selected passes",
            default=False
            ); exec(conv("render_passes"))
 
    #render_passes_objectlist = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup); exec(conv("render_passes_objectlist"))
    #render_passes_objectlist_index = bpy.props.IntProperty(); exec(conv("render_passes_objectlist_index"))
    
    render_passes_objectlist: bpy.props.CollectionProperty(type=FlipFluidHelperPropertiesRenderPassesCatcher)
    render_passes_catcherlist: bpy.props.CollectionProperty(type=FlipFluidHelperPropertiesRenderPassesCatcher)
    render_passes_objectlist_index: bpy.props.IntProperty()
    render_passes_catcherlist_index: bpy.props.IntProperty()
    
    def get_camera_items(self, context):
        return [(cam.name, cam.name, "") for cam in bpy.data.objects if cam.type == 'CAMERA']

    render_passes_cameraselection: bpy.props.EnumProperty(
        items=get_camera_items,
        name=_z("Camera Selection"),
        description="Camera Selection\nSelect a camera for rendering"
    )
    
    render_passes_camerascreen_distance: bpy.props.FloatProperty(
        name=_z("CameraScreen Distance"),
        description="CameraScreen Distance\nControls the distance to the selected camera",
        default=10.0,
        min=0.0,
        max=10000.0,
        update=_update_render_passes_camera_screen
    )
       
    render_passes_fluid_only: bpy.props.BoolProperty(
        name=_z("Fluid Surface"),
        description="Fluid Surface\nOnly the fluid_surface with reflections from the background only",
        default=False
    )
    
    render_passes_fluidparticles_only: bpy.props.BoolProperty(
        name=_z("Fluid Particles"),
        description="Fluid Particles\nOnly the fluidparticles with reflections from the background only",
        default=False
    )

    render_passes_fluid_shadows_only: bpy.props.BoolProperty(
        name=_z("Fluid Surface Shadows"),
        description="Fluid Surface Shadows\nOnly the Shadow of the fluid_surface",
        default=False
    )    

    render_passes_reflr_only: bpy.props.BoolProperty(
        name=_z("Reflections & Refractions"),
        description="Reflections & Refractions\nOnly reflections and refractions (except the background)",
        default=False
    )

    render_passes_objects_only: bpy.props.BoolProperty(
        name=_z("Objects"),
        description="Objects\nOnly visible objects",
        default=False
    )
    
    render_passes_catchers_only: bpy.props.BoolProperty(
        name=_z("Catchers"),
        description="Only catcher objects",
        default=False
    )

    render_passes_object_shadows_only: bpy.props.BoolProperty(
        name=_z("Object Shadows"),
        description="Object Shadows\nOnly the shadows of visible objects",
        default=False
    )       
 
    render_passes_bubblesanddust_only: bpy.props.BoolProperty(
        name=_z("Bubbles & Dust"),
        description="Bubbles And Dust",
        default=False
    )    
 

    render_passes_foamandspray_only: bpy.props.BoolProperty(
        name=_z("Foam & Spray"),
        description="Foam And Spray",
        default=False
    )    
 
    ### END OF PASSES ###

    alembic_export_surface = BoolProperty(
            name=_z("Surface"),
            description="Surface\nInclude fluid surface mesh in the Alembic export",
            default=True,
            ); exec(conv("alembic_export_surface"))
    alembic_export_fluid_particles = BoolProperty(
            name=_z("Fluid Particles"),
            description="Fluid Particles\nInclude fluid particles in the Alembic export",
            default=False,
            ); exec(conv("alembic_export_fluid_particles"))
    alembic_export_foam = BoolProperty(
            name=_z("Foam"),
            description="Foam\nInclude whitewater foam mesh in the Alembic export if applicable. This mesh will be exported as a vertex-only mesh",
            default=True,
            ); exec(conv("alembic_export_foam"))
    alembic_export_bubble = BoolProperty(
            name=_z("Bubble"),
            description="Bubble\nInclude whitewater bubble mesh in the Alembic export if applicable. This mesh will be exported as a vertex-only mesh",
            default=True,
            ); exec(conv("alembic_export_bubble"))
    alembic_export_spray = BoolProperty(
            name=_z("Spray"),
            description="Spray\nInclude whitewater spray mesh in the Alembic export if applicable. This mesh will be exported as a vertex-only mesh",
            default=True,
            ); exec(conv("alembic_export_spray"))
    alembic_export_dust = BoolProperty(
            name=_z("Dust"),
            description="Dust\nInclude whitewater dust mesh in the Alembic export if applicable. This mesh will be exported as a vertex-only mesh",
            default=True,
            ); exec(conv("alembic_export_dust"))
    alembic_export_velocity = BoolProperty(
            name=_z("Export Velocity"),
            description="Export Velocity\nInclude velocity data in the Alembic export. This data will be available"
                " under the 'velocity' attribute of the Alembic export and can be used for motion"
                " blur rendering. Velocity attributes for the surface, fluid particles, and/or whitewater are required to"
                " be baked before export",
            default=False,
            ); exec(conv("alembic_export_velocity"))
    alembic_global_scale = FloatProperty(
            name=_z("Scale"), 
            description="Scale\nScale value by which to enlarge or shrink the simulation meshes with respect to the world's origin", 
            min=0.0001,
            max=1000.0,
            default=1.0,
            precision=3,
            ); exec(conv("alembic_global_scale"))
    alembic_frame_range_mode = EnumProperty(
            name=_z("Frame Range Mode"),
            description="Frame Range Mode\nFrame range to use for Alembic Export",
            items=types.frame_range_modes,
            default='FRAME_RANGE_TIMELINE',
            options={'HIDDEN'},
            ); exec(conv("alembic_frame_range_mode"))
    alembic_frame_range_custom = NewMinMaxIntProperty(
            name_min="Start Frame", 
            description_min="First frame of the Alembic export", 
            min_min=0,
            default_min=1,
            options_min={'HIDDEN'},

            name_max="End Frame", 
            description_max="Final frame of the Alembic export", 
            min_max=0,
            default_max=250,
            options_max={'HIDDEN'},
            ); exec(conv("alembic_frame_range_custom"))
    alembic_output_filepath = StringProperty(
            name="",
            description="Alembic export will be saved to this filepath. Remember to save the Blend file before"
                " starting the Alembic export",
            default="//untitled.abc", 
            subtype='FILE_PATH',
            update=lambda self, context: self._update_alembic_output_filepath(context),
            ); exec(conv("alembic_output_filepath"))
    is_alembic_output_filepath_set = BoolProperty(default=False); exec(conv("is_alembic_output_filepath_set"))

    unsaved_blend_file_tooltip = BoolProperty(
            name=_z("Unsaved Blend File Tooltip"), 
            description="Unsaved Blend File Tooltip\nThis is currently an unsaved .blend file. We recommend saving your file before baking a"
                " simulation so you do not accidentally lose your simulation progress or settings", 
            default=True,
            ); exec(conv("unsaved_blend_file_tooltip"))

    turbo_tools_render_tooltip = BoolProperty(
            name=_z("Turbo Tools command line rendering support"), 
            description="Turbo Tools command line rendering support\nAn installation of the Turbo Tools addon has been detected. Use these operators to launch"
                " a Turbo Tools render process or copy the render command. Refer to the Turbo Tools documentation for more info"
                " on command line rendering", 
            default=True,
            ); exec(conv("turbo_tools_render_tooltip"))

    flip_fluids_remesh_skip_hide_render_objects = BoolProperty(
            name=_z("Skip Hidden Render Objects"),
            description="Skip Hidden Render Objects\nSkip remeshing objects in the collection that are hidden from render (outliner camera icon)",
            default=False,
            ); exec(conv("flip_fluids_remesh_skip_hide_render_objects"))
    flip_fluids_remesh_apply_object_modifiers = BoolProperty(
            name=_z("Apply Object Modifiers"),
            description="Apply Object Modifiers\nAutomatically apply modifiers to objects in collection. If disabled, objects with modifiers will"
                " need to have modifiers applied manually or excluded from the viewport (disable outliner monitor icon)"
                " before proceeding with the remesh process. Modifiers may not be applied in the intended order and objects"
                " with complex modifier dependencies may need to be applied manually for accuracy",
            default=True,
            ); exec(conv("flip_fluids_remesh_apply_object_modifiers"))
    flip_fluids_remesh_convert_objects_to_mesh = BoolProperty(
            name=_z("Convert Objects to Mesh"),
            description="Convert Objects to Mesh\nAutomatically convert non-mesh type objects in the collection to a mesh type if applicable. If an object cannot"
                " be converted to a mesh (empties, armatures, etc), the object will be skipped from the remeshing process."
                " If disabled, non-mesh type objects will need to be manually converted to a mesh or excluded from the viewport"
                " (disable outliner monitor icon) before proceeding with the remesh process",
            default=True,
            ); exec(conv("flip_fluids_remesh_convert_objects_to_mesh"))
    update_object_speed_data_on_frame_change = BoolProperty(
            name=_z("Update on frame change"),
            description="Update on frame change\nUpdate the object speed measurement for the active object after changing a frame. Not recommended"
            " to leave this option enabled when not in use as this could slow down Blender when measuring complex or high poly geometry",
            default=False,
            ); exec(conv("update_object_speed_data_on_frame_change"))
    measure_object_speed_units_mode = EnumProperty(
            name=_z("Measurement Units"),
            description="Measurement Units\nDisplay speed in metric or imperial units",
            items=types.measurement_units_mode,
            default='MEASUREMENT_UNITS_MODE_METRIC',
            options={'HIDDEN'},
            ); exec(conv("measure_object_speed_units_mode"))

    disable_addon_in_blend_file = BoolProperty(
            name=_z("Disable Addon in Blend File"),
            description="Disable Addon in Blend File",
            default=False,
            ); exec(conv("disable_addon_in_blend_file"))

    is_auto_frame_load_cmd_operator_running = BoolProperty(default=False); exec(conv("is_auto_frame_load_cmd_operator_running"))

    export_animated_mesh_parent_tooltip = BoolProperty(
            name=_z("Hint: Export Animated Mesh"), 
            description="Hint: Export Animated Mesh\nA parented relation has been detected on this object. If this object"
                " is moving, enabling the 'Export Animated Mesh' option is required to evaluate"
                " parented relationships for the simulator. This option is needed for any object"
                " animation that is more complex than keyframed loc/rot/scale such as parented objects."
                " If the object is static, keep this option disabled", 
            default=True,
            ); exec(conv("export_animated_mesh_parent_tooltip"))

    # Used in Helper Operators > FlipFluidMeasureObjectSpeed operator
    is_translation_data_available = BoolProperty(default=False); exec(conv("is_translation_data_available"))
    min_vertex_translation = FloatProperty(default=0.0); exec(conv("min_vertex_translation"))
    max_vertex_translation = FloatProperty(default=0.0); exec(conv("max_vertex_translation"))
    avg_vertex_translation = FloatProperty(default=0.0); exec(conv("avg_vertex_translation"))
    center_translation = FloatProperty(default=0.0); exec(conv("center_translation"))
    translation_data_object_name = StringProperty(default="Name Not Available"); exec(conv("translation_data_object_name"))
    translation_data_object_vertices = IntProperty(default=-1); exec(conv("translation_data_object_vertices"))
    translation_data_object_frame = IntProperty(default=-1); exec(conv("translation_data_object_frame"))
    translation_data_object_compute_time = IntProperty(default=-1); exec(conv("translation_data_object_compute_time"))

    prepare_geometry_tools_expanded = BoolProperty(default=False); exec(conv("prepare_geometry_tools_expanded"))
    bake_simulation_expanded = BoolProperty(default=True); exec(conv("bake_simulation_expanded"))
    add_remove_objects_expanded = BoolProperty(default=False); exec(conv("add_remove_objects_expanded"))
    outliner_organization_expanded = BoolProperty(default=False); exec(conv("outliner_organization_expanded"))
    quick_select_expanded = BoolProperty(default=False); exec(conv("quick_select_expanded"))

    command_line_tools_expanded = BoolProperty(default=True); exec(conv("command_line_tools_expanded"))
    command_line_bake_expanded = BoolProperty(default=False); exec(conv("command_line_bake_expanded"))
    command_line_render_passes_expanded = BoolProperty(default=False); exec(conv("command_line_render_passes_expanded"))
    command_line_render_expanded = BoolProperty(default=False); exec(conv("command_line_render_expanded"))
    command_line_render_frame_expanded = BoolProperty(default=False); exec(conv("command_line_render_frame_expanded"))
    command_line_render_turbo_tools_expanded  = BoolProperty(default=False); exec(conv("command_line_render_turbo_tools_expanded"))
    command_line_alembic_export_expanded = BoolProperty(default=False); exec(conv("command_line_alembic_export_expanded"))

    geometry_node_tools_expanded = BoolProperty(default=False); exec(conv("geometry_node_tools_expanded"))
    object_speed_measurement_tools_expanded = BoolProperty(default=False); exec(conv("object_speed_measurement_tools_expanded"))
    beginner_tools_expanded = BoolProperty(default=False); exec(conv("beginner_tools_expanded"))
    disable_addon_expanded = BoolProperty(default=False); exec(conv("disable_addon_expanded"))

    quick_viewport_display_expanded = BoolProperty(default=True); exec(conv("quick_viewport_display_expanded"))
    simulation_playback_expanded = BoolProperty(default=False); exec(conv("simulation_playback_expanded"))
    render_tools_expanded = BoolProperty(default=False); exec(conv("render_tools_expanded"))


    @classmethod
    def register(cls):
        bpy.types.Scene.flip_fluid_helper = PointerProperty(
                name=_z("Flip Fluid Helper Properties"),
                description="Flip Fluid Helper Properties",
                type=cls,
                )


    @classmethod
    def unregister(cls):
        del bpy.types.Scene.flip_fluid_helper


    def load_post(self):
        self.is_auto_frame_load_cmd_operator_running = False
        if self.is_auto_frame_load_cmd_enabled():
            bpy.ops.flip_fluid_operators.auto_load_baked_frames_cmd('INVOKE_DEFAULT')

        self.check_alembic_output_filepath()


    def scene_update_post(self, scene):
        _update_render_passes_camera_screen(self, bpy.context)


    def save_post(self):
        self.check_alembic_output_filepath()


    def frame_change_post(self, scene, depsgraph=None):
        if self.update_object_speed_data_on_frame_change:
            try:
                if bpy.ops.flip_fluid_operators.measure_object_speed.poll():
                    print("Measure Object Speed: Update on frame change option is enabled.")
                    bpy.ops.flip_fluid_operators.measure_object_speed('INVOKE_DEFAULT')
                else:
                    bpy.ops.flip_fluid_operators.clear_measure_object_speed('INVOKE_DEFAULT')
            except:
                pass


    def is_addon_disabled_in_blend_file(self):
        is_disabled = False
        for scene in bpy.data.scenes:
            is_disabled = is_disabled or scene.flip_fluid_helper.disable_addon_in_blend_file
        return is_disabled


    def get_addon_preferences(self):
        return vcu.get_addon_preferences()


    def frame_complete_callback(self):
        prefs = self.get_addon_preferences()
        if prefs.enable_helper and self.enable_auto_frame_load:
            bpy.ops.flip_fluid_operators.helper_load_last_frame()


    def is_auto_frame_load_cmd_enabled(self):
        return self.enable_auto_frame_load and self.enable_auto_frame_load_cmd


    def _update_enable_auto_frame_load_cmd(self, context):
        dprops = context.scene.flip_fluid.get_domain_properties()
        if dprops is None:
            return

        is_auto_load_cmd_enabled = self.is_auto_frame_load_cmd_enabled()
        if is_auto_load_cmd_enabled and not self.is_auto_frame_load_cmd_operator_running:
            bpy.ops.flip_fluid_operators.auto_load_baked_frames_cmd('INVOKE_DEFAULT')


    def _update_alembic_output_filepath(self, context):
        self.is_alembic_output_filepath_set = True

        relprefix = "//"
        if self.alembic_output_filepath == "" or self.alembic_output_filepath == relprefix:
            # Don't want the user to set an empty path
            if bpy.data.filepath:
                base = os.path.basename(bpy.data.filepath)
                save_file = os.path.splitext(base)[0]
                output_folder_parent = os.path.dirname(bpy.data.filepath)

                output_filepath = os.path.join(output_folder_parent, save_file + ".abc")
                relpath = os.path.relpath(output_filepath, output_folder_parent)

                default_cache_directory_str = relprefix + relpath
            else:
                temp_directory = vcu.get_blender_preferences_temporary_directory()
                default_cache_directory_str = os.path.join(temp_directory, "untitled.abc")
            self["alembic_output_filepath"] = default_cache_directory_str


    def check_alembic_output_filepath(self):
        if self.is_alembic_output_filepath_set:
            return

        base = os.path.basename(bpy.data.filepath)
        save_file = os.path.splitext(base)[0]
        if not save_file:
            save_file = "untitled"
            self.alembic_output_filepath = save_file + ".abc"
            self.is_alembic_output_filepath_set = False
            return

        alembic_folder_parent = os.path.dirname(bpy.data.filepath)
        alembic_path = os.path.join(alembic_folder_parent, save_file + ".abc")
        relpath = os.path.relpath(alembic_path, alembic_folder_parent)

        relprefix = "//"
        self.alembic_output_filepath = relprefix + relpath
        self.is_alembic_output_filepath_set = True


    def get_alembic_output_abspath(self):
        relprefix = "//"
        path_prop = self.alembic_output_filepath
        path = self.alembic_output_filepath
        if path_prop.startswith(relprefix):
            path_prop = path_prop[len(relprefix):]
            blend_directory = os.path.dirname(bpy.data.filepath)
            path = os.path.join(blend_directory, path_prop)
        path = os.path.abspath(os.path.normpath(path))
        if platform.system() != "Windows":
            # Blend file may have been saved on windows and opened on macOS/Linux. In this case,
            # backslash should be converted to forward slash.
            path = os.path.join(*path.split("\\"))
        return path


def load_post():
    bpy.context.scene.flip_fluid_helper.load_post()


def scene_update_post(scene):
    scene.flip_fluid_helper.scene_update_post(scene)


def frame_change_post(scene, depsgraph=None):
    global DISABLE_FRAME_CHANGE_POST_HANDLER
    if DISABLE_FRAME_CHANGE_POST_HANDLER:
        return
    bpy.context.scene.flip_fluid_helper.frame_change_post(scene, depsgraph)


def save_post():
    bpy.context.scene.flip_fluid_helper.save_post()


def register():
    bpy.utils.register_class(FlipFluidHelperPropertiesRenderPassesCatcher)
    bpy.utils.register_class(FlipFluidHelperProperties)


def unregister():
    bpy.utils.unregister_class(FlipFluidHelperPropertiesRenderPassesCatcher)
    bpy.utils.unregister_class(FlipFluidHelperProperties)
