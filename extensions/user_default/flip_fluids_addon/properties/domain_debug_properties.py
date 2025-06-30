# -*- coding:utf-8 -*-
from ..iBlender_flip_fluids_addon import _z

# Blender FLIP Fluids Add-on
# Copyright (C) 2024 Ryan L. Guy
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

import bpy, os, sys, platform, traceback
from bpy.props import (
        BoolProperty,
        BoolVectorProperty,
        EnumProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        StringProperty,
        PointerProperty,
        CollectionProperty
        )

# from .custom_properties import (
#         NewMinMaxFloatProperty
#         )

from .. import (
        types,
        bake
        )

from ..operators import draw_grid_operators
from ..operators import draw_particles_operators
from ..operators import draw_force_field_operators
from ..operators import preferences_operators
from ..utils import version_compatibility_utils as vcu
from ..utils import installation_utils
from ..objects import flip_fluid_cache
from .. import bl_info

_LOGGING_DISABLED_MESSAGE = "(Blend file logging disabled in host preferences)"


class VersionHistoryItem(bpy.types.PropertyGroup):
    conv = vcu.convert_attribute_to_28
    blender_version = StringProperty(default="-1"); exec(conv("blender_version"))
    flip_fluids_version = StringProperty(default="-1"); exec(conv("flip_fluids_version"))
    flip_fluids_label = StringProperty(default="-1"); exec(conv("flip_fluids_label"))
    operating_system = StringProperty(default="-1"); exec(conv("operating_system"))


    def get_info_string(self):
        return self.blender_version + "\t" + self.flip_fluids_version + "\t" + self.flip_fluids_label + "\t" + self.operating_system


class DomainDebugProperties(bpy.types.PropertyGroup):
    conv = vcu.convert_attribute_to_28
    
    display_simulation_grid = BoolProperty(
            name=_z("Display Domain Grid"),
            description="Display Domain Grid\nVisualize the domain voxel grid in the 3D viewport."
                " Try scaling different sides of the domain to better understand how the grid works."
                " Try enabling the Lock Cell Size option in the FLIP Fluid Simulation panel and compare"
                " the differences in how the grid changes as the domain is resized",
            default=False,
            update=lambda self, context: self._update_display_simulation_grid(context),
            ); exec(conv("display_simulation_grid"))
    grid_display_mode = EnumProperty(
            name=_z("Grid Display Mode"),
            description="Grid Display Mode\nType of grid debug info to display",
            items=types.grid_display_modes,
            default='GRID_DISPLAY_SIMULATION',
            update=lambda self, context: self._update_debug_grid_geometry(context),
            ); exec(conv("grid_display_mode"))
    grid_display_scale = IntProperty(
            name=_z("Grid Display Scale"),
            description="Grid Display Scale\nNumber of voxels that a single grid spacing in the"
                " viewport represents",
            min = 1, soft_max = 10,
            default=1,
            step=1,
            update=lambda self, context: self._update_debug_grid_geometry(context),
            ); exec(conv("grid_display_scale"))
    enabled_debug_grids = BoolVectorProperty(
            name=_z("Enabled Debug Grids"),
            description="Enabled Debug Grids\nSelect which debug grids are displayed in the viewport",
            default=(True, True, True),
            size=3,
            subtype='XYZ',
            update=lambda self, context: self._update_debug_grid_geometry(context),
            ); exec(conv("enabled_debug_grids"))
    x_grid_color = FloatVectorProperty(  
           name=_z("X Grid Color"),
           subtype='COLOR',
           default=(0.5, 0.0, 0.0),
           min=0.0, max=1.0,
           description="X Grid Color\nX grid display color"
           ); exec(conv("x_grid_color"))
    y_grid_color = FloatVectorProperty(  
           name=_z("Y Grid Color"),
           subtype='COLOR',
           default=(0.0, 0.5, 0.0),
           min=0.0, max=1.0,
           description="Y Grid Color\nY grid display color"
           ); exec(conv("y_grid_color"))
    z_grid_color = FloatVectorProperty(  
           name=_z("Z Grid Color"),
           subtype='COLOR',
           default=(0.0, 0.0, 0.5),
           min=0.0, max=1.0,
           description="Z Grid Color\nZ grid display color"
           ); exec(conv("z_grid_color"))
    debug_grid_offsets = FloatVectorProperty(
            name=_z("Debug Grid Offsets"),
            description="Debug Grid Offsets\nOffset at which an axis' grid is displayed in the viewport",
            min = 0.0, max = 1.0,
            default=(0.0, 0.0, 0.0),
            size=3,
            step=1,
            subtype='XYZ',
            update=lambda self, context: self._update_debug_grid_geometry(context),
            ); exec(conv("debug_grid_offsets"))
    snap_offsets_to_grid = BoolProperty(
            name=_z("Snap Offsets to Grid"),
            description="Snap Offsets to Grid\nAlign debug grids to gridcell locations",
            default=True,
            update=lambda self, context: self._update_debug_grid_geometry(context),
            ); exec(conv("snap_offsets_to_grid"))
    display_domain_bounds = BoolProperty(
            name=_z("Display Bounds"),
            description="Display the true bounds of the domain object." + 
                " The domain boundary contains a thin solid layer. Enabling" + 
                " this visualization will display the actual fluid region of" + 
                " the domain",
            default=False,
            update=lambda self, context: self._update_display_domain_bounds(context),
            ); exec(conv("display_domain_bounds"))
    domain_bounds_color = FloatVectorProperty(  
           name=_z("Domain Bounds Color"),
           subtype='COLOR',
           default=(1.0, 1.0, 0.0),
           min=0.0, max=1.0,
           description="Domain Bounds Color\nColor of the domain bounds visualization",
           update=lambda self, context: self._update_debug_grid_geometry(context),
           ); exec(conv("domain_bounds_color"))

    enable_fluid_particle_debug_output = BoolProperty(
            name=_z("Enable Fluid Particle Debugging"),
            description="Enable Fluid Particle Debugging\nEnable to export simulator fluid particle data and to"
                " visualize and debug problems with fluid behaviour. Enable"
                " this option before baking a simulation to use this feature",
            default=False,
            update=lambda self, context: self._update_enable_fluid_particle_debug_output(context),
            ); exec(conv("enable_fluid_particle_debug_output"))
    fluid_particles_visibility = BoolProperty(
            name=_z("Fluid Particle Visibility"),
            description="Fluid Particle Visibility\nShow fluid particles in the viewport",
            default=True,
            update=lambda self, context: self._update_enable_fluid_particle_debug_output(context),
            ); exec(conv("fluid_particles_visibility"))
    low_speed_particle_color = FloatVectorProperty(  
           name=_z("Low Speed Color"),
           subtype='COLOR',
           default=(0.0, 0.0, 1.0),
           min=0.0, max=1.0,
           description="Low Speed Color\nColor for low velocity fluid particles",
           update=lambda self, context: self._update_debug_particle_geometry(context),
           ); exec(conv("low_speed_particle_color"))
    high_speed_particle_color = FloatVectorProperty(  
           name=_z("High Speed Color"),
           subtype='COLOR',
           default=(1.0, 1.0, 1.0),
           min=0.0, max=1.0,
           description="High Speed Color\nColor for high velocity fluid particles",
           update=lambda self, context: self._update_debug_particle_geometry(context),
           ); exec(conv("high_speed_particle_color"))
    min_gradient_speed = FloatProperty(
            name=_z("Low Color Speed"), 
            description="Low Color Speed\nLow speed value for visualizing fluid particle velocity", 
            min=0,
            default=0.0,
            precision=2,
            update=lambda self, context: self._update_min_gradient_speed(context),
            ); exec(conv("min_gradient_speed"))
    max_gradient_speed = FloatProperty(
            name=_z("High Color Speed"), 
            description="High Color Speed\nHigh speed value for visualizing fluid particle velocity", 
            min=0,
            default=5.0,
            precision=2,
            update=lambda self, context: self._update_max_gradient_speed(context),
            ); exec(conv("max_gradient_speed"))
    fluid_particle_gradient_mode = EnumProperty(
            name=_z("Gradient Mode"),
            description="Gradient Mode\nType of color gradient",
            items=types.gradient_interpolation_modes,
            default='GRADIENT_RGB',
            update=lambda self, context: self._update_max_gradient_speed(context),
            ); exec(conv("fluid_particle_gradient_mode"))
    particle_size = IntProperty(
            name=_z("Particle Size"), 
            description="Particle Size\nSize to draw particles for visualization", 
            min=1, soft_max=10,
            default=1,
            update=lambda self, context: self._update_debug_particle_geometry(context),
            ); exec(conv("particle_size"))
    particle_draw_aabb = PointerProperty(
            name=_z("Visualization Bounds"), 
            description="Visualization Bounds\nIf set, only particles inside the object's axis-aligned"
                " bounding box will be drawn",
            type=bpy.types.Object,
            update=lambda self, context: self._update_debug_particle_geometry(context),
            ); exec(conv("particle_draw_aabb"))

    export_force_field = BoolProperty(
            name=_z("Enable Force Field Debugging"),
            description="Enable Force Field Debugging\nEnable to export simulator force field data and to"
                " visualize force field lines. Enable this option before baking"
                " a simulation to use this feature",
            default=False,
            update=lambda self, context: self._update_export_force_field(context),
            ); exec(conv("export_force_field"))
    force_field_visibility = BoolProperty(
            name=_z("Force Field Visibility"),
            description="Force Field Visibility\nShow force fields in the viewport",
            default=True,
            update=lambda self, context: self._update_export_force_field(context),
            ); exec(conv("force_field_visibility"))
    low_force_field_color = FloatVectorProperty(  
           name=_z("Low Force Color"),
           subtype='COLOR',
           default=(1.0, 1.0, 1.0),
           min=0.0, max=1.0,
           description="Low Force Color\nColor for low strength forces",
           update=lambda self, context: self._update_export_force_field(context),
           ); exec(conv("low_force_field_color"))
    high_force_field_color = FloatVectorProperty(  
           name=_z("High Force Color"),
           subtype='COLOR',
           default=(1.0, 0.0, 0.0),
           min=0.0, max=1.0,
           description="High Force Color\nColor for high strength forces",
           update=lambda self, context: self._update_export_force_field(context),
           ); exec(conv("high_force_field_color"))
    min_gradient_force = FloatProperty(
            name=_z("Low Color Force"), 
            description="Low Color Force\nLow force strength value for visualizing force field lines", 
            min=0,
            default=0.0,
            precision=2,
            update=lambda self, context: self._update_min_gradient_force(context),
            ); exec(conv("min_gradient_force"))
    max_gradient_force = FloatProperty(
            name=_z("High Color Force"), 
            description="High Color Force\nHigh force strength value for visualizing force field lines", 
            min=0,
            default=15.0,
            precision=2,
            update=lambda self, context: self._update_max_gradient_force(context),
            ); exec(conv("max_gradient_force"))
    force_field_gradient_mode = EnumProperty(
            name=_z("Gradient Mode"),
            description="Gradient Mode\nType of color gradient",
            items=types.gradient_interpolation_modes,
            default='GRADIENT_RGB',
            update=lambda self, context: self._update_max_gradient_force(context),
            ); exec(conv("force_field_gradient_mode"))
    force_field_display_amount = IntProperty(
            name=_z("Display Amount"), 
            description="Display Amount\nAmount of force field lines to display in the viewport", 
            min=0, max=100,
            default=25,
            subtype='PERCENTAGE',
            update=lambda self, context: self._update_force_field_geometry(context),
            ); exec(conv("force_field_display_amount"))
    force_field_line_size = IntProperty(
            name=_z("Line Size"), 
            description="Line Size\nLine thickness for force field visualization", 
            min=1, soft_max=10,
            default=2,
            update=lambda self, context: self._update_force_field_geometry(context),
            ); exec(conv("force_field_line_size"))

    export_internal_obstacle_mesh = BoolProperty(
            name=_z("Enable Obstacle Debugging"),
            description="Enable Obstacle Debugging\nEnable to export simulator obstacle data"
                        " and to visualize and debug problems with obstacles."
                        " Enable this setting before baking a simulation to"
                        " use this feature",
            default=False,
            update=lambda self, context: self._update_export_internal_obstacle_mesh(context),
            ); exec(conv("export_internal_obstacle_mesh"))
    internal_obstacle_mesh_visibility = BoolProperty(
            name=_z("Obstacle Debugging Visibility"),
            description="Obstacle Debugging Visibility\nShow obstacle debug mesh in the viewport. If disabled, this prevents debug obstacle"
                " mesh data from being loaded into Blender. Frame must be reloaded after enabling this option for"
                " mesh to reload and become visible",
            default=True,
            update=lambda self, context: self._update_export_internal_obstacle_mesh(context),
            ); exec(conv("internal_obstacle_mesh_visibility"))

    display_console_output = BoolProperty(
            name=_z("Display Console Output"),
            description="Display Console Output\nDisplay simulation info in the Blender system console",
            default=True,
            update=lambda self, context: self._update_display_console_output(context),
            options={'HIDDEN'},
            ); exec(conv("display_console_output"))

    is_draw_debug_grid_operator_running = BoolProperty(default=False); exec(conv("is_draw_debug_grid_operator_running"))
    is_draw_gl_particles_operator_running = BoolProperty(default=False); exec(conv("is_draw_gl_particles_operator_running"))
    is_draw_gl_force_field_operator_running = BoolProperty(default=False); exec(conv("is_draw_gl_force_field_operator_running"))

    grid_display_settings_expanded = BoolProperty(default=True); exec(conv("grid_display_settings_expanded"))
    particle_debug_settings_expanded = BoolProperty(default=False); exec(conv("particle_debug_settings_expanded"))
    force_field_debug_settings_expanded = BoolProperty(default=False); exec(conv("force_field_debug_settings_expanded"))

    version_history = CollectionProperty(type=VersionHistoryItem); exec(conv("version_history"))
    system_info = StringProperty(default=""); exec(conv("system_info"))


    def register_preset_properties(self, registry, path):
        add = registry.add_property
        add(path + ".display_simulation_grid",           _z("Display Domain Grid"),             group_id=0)
        add(path + ".grid_display_mode",                 _z("Grid Display Mode"),               group_id=0)
        add(path + ".grid_display_scale",                _z("Grid Scale"),                      group_id=0)
        add(path + ".enabled_debug_grids",               _z("Draw Grids"),                      group_id=0)
        add(path + ".x_grid_color",                      _z("X Grid Color"),                    group_id=0)
        add(path + ".y_grid_color",                      _z("Y Grid Color"),                    group_id=0)
        add(path + ".z_grid_color",                      _z("Z Grid Color"),                    group_id=0)
        add(path + ".debug_grid_offsets",                _z("Grid Offsets"),                    group_id=0)
        add(path + ".snap_offsets_to_grid",              _z("Snap Offsets to Grid"),            group_id=0)
        add(path + ".enable_fluid_particle_debug_output", _z("Enable Fluid Particle Debugging"), group_id=1)
        add(path + ".fluid_particles_visibility",        _z("Fluid Particle Visibility"),       group_id=1)
        add(path + ".low_speed_particle_color",          _z("Low Velocity Particle Color"),     group_id=1)
        add(path + ".high_speed_particle_color",         _z("High Velocity Particle Color"),    group_id=1)
        add(path + ".min_gradient_speed",                _z("Low-High Particle Velocities"),    group_id=1)
        add(path + ".max_gradient_speed",                _z("Low-High Particle Velocities"),    group_id=1)
        add(path + ".fluid_particle_gradient_mode",      _z("Fluid Speed Gradient Mode"),       group_id=1)
        add(path + ".particle_size",                     _z("Particle Size"),                   group_id=1)
        add(path + ".low_force_field_color",             _z("Low Force Field Color"),           group_id=2)
        add(path + ".high_force_field_color",            _z("High Force Field Color"),          group_id=2)
        add(path + ".min_gradient_force",                _z("Low-High Force Strength"),         group_id=2)
        add(path + ".max_gradient_force",                _z("Low-High Force Strength"),         group_id=2)
        add(path + ".force_field_gradient_mode",         _z("Fluid Speed Gradient Mode"),       group_id=2)
        add(path + ".export_force_field",                _z("Enable Force Field Debugging"),    group_id=2)
        add(path + ".force_field_visibility",            _z("Force Field Visibility"),          group_id=2)
        add(path + ".force_field_line_size",             _z("Line Size"),                       group_id=2)
        add(path + ".export_internal_obstacle_mesh",     _z("Enable Obstacle Debugging"),       group_id=3)
        add(path + ".internal_obstacle_mesh_visibility", _z("Obstacle Debugging Visibility"), group_id=3)
        add(path + ".display_console_output",            _z("Display Console Output"),        group_id=3)


    def load_post(self):
        self.print_system_info()

        self.is_draw_debug_grid_operator_running = False
        self.is_draw_gl_particles_operator_running = False

        # Draw operators should not be run when Blender is launched from the command line
        # in background mode - context will be incorrect.
        if not bpy.app.background:
            if self.enable_fluid_particle_debug_output:
                self._update_debug_particle_geometry(bpy.context)
                bpy.ops.flip_fluid_operators.draw_gl_particles('INVOKE_DEFAULT')
            if self.is_simulation_grid_debugging_enabled():
                self._update_debug_grid_geometry(bpy.context)
                bpy.ops.flip_fluid_operators.draw_debug_grid('INVOKE_DEFAULT')
            if self.export_force_field:
                self._update_force_field_geometry(bpy.context)
                bpy.ops.flip_fluid_operators.draw_force_field('INVOKE_DEFAULT')


    def print_system_and_blend_info(self):
        try:
            preferences = vcu.get_addon_preferences()
            if preferences.enable_support_tools and preferences.enable_blend_file_logging:
                print("*** Developer Tools: FLIP Fluids Version History ***")
                self.print_version_history()
                print()
                print("*** Developer Tools: FLIP Fluids System Info ***")
                self.print_system_info()
        except Exception as e:
            print(e)
            pass


    def scene_update_post(self, scene):
        self._update_debug_grid_geometry(bpy.context)


    def save_pre(self):
        # We don't want a potential error/failure during a save
        try:
            preferences = vcu.get_addon_preferences()
            if preferences.enable_blend_file_logging:
                # Save Version History
                if vcu.is_blender_42():
                    bl_info_dict = bl_info
                else:
                    bl_info_dict = sys.modules[installation_utils.get_module_name()].bl_info

                vdata = self.version_history.add()
                vdata.blender_version = bpy.app.version_string
                vdata.flip_fluids_version = str(bl_info_dict.get('version', (-1, -1, -1)))
                vdata.flip_fluids_label = bl_info_dict.get('description', "-1")
                vdata.operating_system = platform.system()
                if len(self.version_history) > 250:
                    self.version_history.remove(0)

                # Save System and Blend File Info
                self.system_info = preferences_operators.get_system_info_string()
            else:
                global _LOGGING_DISABLED_MESSAGE
                self.version_history.clear()
                self.system_info = "No System and Blend File Info " + _LOGGING_DISABLED_MESSAGE
        except Exception as e:
            print(traceback.format_exc())
            print(e)


    def print_version_history(self):
        if len(self.version_history) == 0:
            global _LOGGING_DISABLED_MESSAGE
            msg = "No version history"
            if _LOGGING_DISABLED_MESSAGE in self.system_info:
                msg += " " + _LOGGING_DISABLED_MESSAGE
            print(msg)
        else:
            for idx,vdata in enumerate(self.version_history):
                print(idx, vdata.get_info_string())


    def print_system_info(self):
        if len(self.system_info) == 0:
            print("No System and Blend File Info")
        else:
            print(self.system_info)


    def get_last_saved_blender_version(self):
        unresolved_version = (-1, -1, -1)
        if len(self.version_history) == 0:
            return unresolved_version

        try:
            valid_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
            bl_version_str = self.version_history[-1].blender_version
            bl_version_str = ''.join([c for c in bl_version_str if c in valid_chars])
            version_numbers = bl_version_str.split('.')
            major = int(version_numbers[0])
            minor = int(version_numbers[1])
            revision = int(version_numbers[2])
            version_tuple = (major, minor, revision)
        except:
            return unresolved_version

        return version_tuple


    def clear_version_history(self):
        self.version_history.clear()


    def clear_system_info(self):
        self.system_info = ""


    def get_particle_draw_aabb_object(self):
        obj = None
        try:
            obj = self.particle_draw_aabb
        except:
            pass
        return obj


    def is_simulation_grid_debugging_enabled(self):
        return self.display_simulation_grid or self.display_domain_bounds


    def _update_enable_fluid_particle_debug_output(self, context):
        dprops = context.scene.flip_fluid.get_domain_properties()
        if dprops is None:
            return

        if self.enable_fluid_particle_debug_output:
            self._update_debug_particle_geometry(context)
            dprops.mesh_cache.gl_particles.enable()
            if not self.is_draw_gl_particles_operator_running:
                bpy.ops.flip_fluid_operators.draw_gl_particles('INVOKE_DEFAULT')
        else:
            dprops.mesh_cache.gl_particles.disable()


    def _update_export_internal_obstacle_mesh(self, context):
        dprops = context.scene.flip_fluid.get_domain_properties()
        if dprops is None:
            return

        if self.export_internal_obstacle_mesh and self.internal_obstacle_mesh_visibility:
            objects_to_initialize = flip_fluid_cache.EnabledMeshCacheObjects()
            objects_to_initialize.debug_obstacle = True
            dprops.mesh_cache.initialize_cache_objects(objects_to_initialize)
        elif self.export_internal_obstacle_mesh and not self.internal_obstacle_mesh_visibility:
            dprops.mesh_cache.obstacle.reset_cache_object()
        else: 
            dprops.mesh_cache.delete_obstacle_cache_object()


    def _update_display_simulation_grid(self, context):
        dprops = context.scene.flip_fluid.get_domain_properties()
        if dprops is None:
            return

        self._update_debug_grid_geometry(context)
        if self.is_simulation_grid_debugging_enabled() and not self.is_draw_debug_grid_operator_running:
            bpy.ops.flip_fluid_operators.draw_debug_grid('INVOKE_DEFAULT')


    def _update_export_force_field(self, context):
        dprops = context.scene.flip_fluid.get_domain_properties()
        if dprops is None:
            return

        if self.export_force_field:
            self._update_force_field_geometry(context)
            dprops.mesh_cache.gl_force_field.enable()
            if not self.is_draw_gl_force_field_operator_running:
                bpy.ops.flip_fluid_operators.draw_force_field('INVOKE_DEFAULT')
        else:
            dprops.mesh_cache.gl_force_field.disable()


    def _update_display_domain_bounds(self, context):
        self._update_display_simulation_grid(context)


    def _update_debug_grid_geometry(self, context):
        draw_grid_operators.update_debug_grid_geometry(context)


    def _update_min_gradient_speed(self, context):
        if self.min_gradient_speed > self.max_gradient_speed:
            self.max_gradient_speed = self.min_gradient_speed
        self._update_debug_particle_geometry(context)


    def _update_max_gradient_speed(self, context):
        if self.max_gradient_speed < self.min_gradient_speed:
            self.min_gradient_speed = self.max_gradient_speed
        self._update_debug_particle_geometry(context)


    def _update_debug_particle_geometry(self, context):
        draw_particles_operators.update_debug_particle_geometry(context)


    def _update_force_field_geometry(self, context):
        draw_force_field_operators.update_debug_force_field_geometry(context)


    def _update_min_gradient_force(self, context):
        if self.min_gradient_force > self.max_gradient_force:
            self.max_gradient_force = self.min_gradient_force
        self._update_force_field_geometry(context)


    def _update_max_gradient_force(self, context):
        if self.max_gradient_force < self.min_gradient_force:
            self.min_gradient_force = self.max_gradient_force
        self._update_force_field_geometry(context)


    def _update_display_console_output(self, context):
        bake.set_console_output(self.display_console_output)


def register():
    bpy.utils.register_class(VersionHistoryItem)
    bpy.utils.register_class(DomainDebugProperties)


def unregister():
    bpy.utils.unregister_class(VersionHistoryItem)
    bpy.utils.unregister_class(DomainDebugProperties)
