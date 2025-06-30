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

import bpy, os, math
from bpy.props import (
        FloatProperty,
        IntProperty,
        BoolProperty,
        EnumProperty,
        PointerProperty
        )

from .. import types
from ..objects.flip_fluid_aabb import AABB
from ..objects import flip_fluid_cache
from ..utils import version_compatibility_utils as vcu

class DomainSurfaceProperties(bpy.types.PropertyGroup):
    conv = vcu.convert_attribute_to_28
    
    enable_surface_mesh_generation = BoolProperty(
            name=_z("Enable Surface Mesh Generation"),
            description="Enable Surface Mesh Generation\nEnable the generation of the liquid surface mesh. If disabled, "
                "the surface mesh and any surface attributes will not be generated or exported"
                " to the simulation cache",
            default=True,
            update=lambda self, context: self._update_enable_surface_mesh_generation(context),
            ); exec(conv("enable_surface_mesh_generation"))
    subdivisions = IntProperty(
            name=_z("Subdivisions"),
            description="Subdivisions\nThe level of detail of the generated surface mesh."
                " This value is the number of times that the simulation grid"
                " cells are split. A value of 1 is recommended for"
                " most final simulations. A value of 2 or 3 is recommended"
                " to reduce flickering in slow motion simulations."
                " Use a value of 0 to speed up baking during testing",
            min=0,
            soft_max=2,
            default=1,
            ); exec(conv("subdivisions"))
    compute_chunks_auto = IntProperty(
            name=_z("Compute Chunks"),
            description="Compute Chunks\nNumber of chunks to break up mesh into during"
                " computation. Increase to reduce memory usage",
            min=1,
            default=1,
            ); exec(conv("compute_chunks_auto"))
    compute_chunks_fixed = IntProperty(
            name=_z("Compute Chunks"),
            description="Compute Chunks\nNumber of chunks to break up surface into during"
                " mesh generation. Increase to reduce memory usage",
            min=1,
            default=1,
            ); exec(conv("compute_chunks_fixed"))
    compute_chunk_mode = EnumProperty(
            name=_z("Threading Mode"),
            description="Threading Mode\nDetermine the number of compute chunks to use when"
                " generating the surface mesh",
            items=types.surface_compute_chunk_modes,
            default='COMPUTE_CHUNK_MODE_AUTO',
            options={'HIDDEN'},
            ); exec(conv("compute_chunk_mode"))
    meshing_volume_mode = EnumProperty(
            name=_z("Meshing Volume Mode"),
            description="Meshing Volume Mode\nDeterming which parts of the fluid will be meshed",
            items=types.meshing_volume_modes,
            default='MESHING_VOLUME_MODE_DOMAIN',
            options={'HIDDEN'},
            ); exec(conv("meshing_volume_mode"))
    meshing_volume_object = PointerProperty(
            name=_z("Meshing Object"), 
            description="Meshing Object\nOnly fluid that is inside of this object will be meshed",
            type=bpy.types.Object,
            update=lambda self, context: self._update_meshing_volume_object(context),
            poll=lambda self, obj: self._poll_meshing_volume_object(obj),
            ); exec(conv("meshing_volume_object"))
    export_animated_meshing_volume_object = BoolProperty(
            name=_z("Export Animated Mesh"),
            description="Export Animated Mesh\nExport this mesh as an animated one (slower, only use"
                " if really necessary [e.g. armatures or parented objects],"
                " animated pos/rot/scale F-curves do not require it",
            default=False,
            options={'HIDDEN'},
            ); exec(conv("export_animated_meshing_volume_object"))
    enable_meshing_offset = BoolProperty(
            name=_z("Enable"),
            description="Enable\nEnable smooth meshing against obstacles. If disabled,"
                " obstacles will not be considered during meshing and all fluid"
                " particles will be converted to a mesh",
            default=True,
            ); exec(conv("enable_meshing_offset"))
    obstacle_meshing_mode = EnumProperty(
            name=_z("Obstacle Meshing Mode"),
            description="Obstacle Meshing Mode\nHow the fluid surface will be meshed against obstacles",
            items=types.obstacle_meshing_modes,
            default='MESHING_MODE_INSIDE_SURFACE',
            ); exec(conv("obstacle_meshing_mode"))
    remove_mesh_near_domain = BoolProperty(
            name=_z("Remove Mesh Near Boundary"),
            description="Remove Mesh Near Boundary\nRemove parts of the surface mesh that are near the"
                " domain boundary. If a meshing volume object is set, parts"
                " of the mesh that are near the volume object boundary will"
                " also be removed",
            default=False,
            ); exec(conv("remove_mesh_near_domain"))
    remove_mesh_near_domain_distance = IntProperty(
            name=_z("Distance"),
            description="Distance\nDistance from domain boundary to remove mesh parts."
                " This value is in number of voxels. If a meshing volume"
                " object is set, this distance will be limited to 1 voxel",
            min=1,
            default=1,
            ); exec(conv("remove_mesh_near_domain_distance"))
    smoothing_value = FloatProperty(
            name=_z("Factor"), 
            description="Factor\nAmount of surface smoothing. Tip: use a smooth modifier"
                " to increase amount of smoothing", 
            min=0.0, max=1.0,
            default=0.5,
            precision=3,
            subtype='FACTOR',
            ); exec(conv("smoothing_value"))
    smoothing_iterations = IntProperty(
            name=_z("Repeat"),
            description="Repeat\nNumber of smoothing iterations Tip: use a smooth modifier"
                " to increase amount of iterations",
            min=0, max=30,
            default=2,
            ); exec(conv("smoothing_iterations"))
    particle_scale = FloatProperty(
            name=_z("Particle Scale"), 
            description = "Particle Scale\nSize of particles for mesh generation. A value less than 1.0"
                " is not recommended and may result in an incomplete mesh", 
            soft_min=1.0, soft_max=3.0,
            default=1.0,
            precision=2,
            ); exec(conv("particle_scale"))
    invert_contact_normals = BoolProperty(
            name=_z("Invert Fluid-Obstacle Contact Normals"),
            description="Invert Fluid-Obstacle Contact Normals\nInvert surface mesh normals that contact obstacle"
                " surfaces. Enable for correct refraction rendering with"
                " water-glass interfaces. Note: 'Mesh Around Obstacles'"
                " should be enabled when using this feature",
            default=False,
            ); exec(conv("invert_contact_normals"))
    generate_motion_blur_data = BoolProperty(
            name=_z("Generate Motion Blur Vectors"),
            description="Generate Motion Blur Vectors\nGenerate fluid surface speed vectors for motion blur"
                " rendering. See documentation for limitations",
            default=False,
            ); exec(conv("generate_motion_blur_data"))
    enable_velocity_vector_attribute = BoolProperty(
            name=_z("Generate Velocity Attributes"),
            description="Generate Velocity Attributes\nGenerate fluid 3D velocity vector attributes for the fluid surface. After"
                " baking, the velocity vectors (in m/s) can be accessed in a Cycles Attribute"
                " Node or in Geometry Nodes with the name 'flip_velocity' from the Vector output."
                " This attribute is required for motion blur rendering. If the velocity"
                " direction is not needed, use Generate Speed Attributes instead",
            default=False,
            options={'HIDDEN'},
            ); exec(conv("enable_velocity_vector_attribute"))
    enable_velocity_vector_attribute_against_obstacles = BoolProperty(
            name=_z("Generate Against Obstacles"),
            description="Generate Against Obstacles\nGenerate velocity-based attribute data against obstacles."
                " Velocity-based attributes are the velocity/speed/vorticity attributes."
                " If enabled, correct attributes will be generated where liquid and obstacles"
                " meet, but at the cost of simulation performance. If disabled, attributes where"
                " liquids and obstacles meet may be incorrect. This option is only needed if"
                " rendering with velocity-based shaders and/or motion blur where the liquid-obstacle"
                " interface will be visible such as when there are transparent/invisible obstacles"
                " in the render",
            default=True,
            options={'HIDDEN'},
            ); exec(conv("enable_velocity_vector_attribute_against_obstacles"))
    enable_speed_attribute = BoolProperty(
            name=_z("Generate Speed Attributes"),
            description="Generate Speed Attributes\nGenerate fluid speed attributes for the fluid surface. After"
                " baking, the speed values (in m/s) can be accessed in a Cycles Attribute"
                " Node or in Geometry Nodes with the name 'flip_speed' from the Fac output",
            default=False,
            options={'HIDDEN'},
            ); exec(conv("enable_speed_attribute"))
    enable_vorticity_vector_attribute = BoolProperty(
            name=_z("Generate Vorticity Attributes"),
            description="Generate Vorticity Attributes\nGenerate fluid 3D vorticity vector attributes for the fluid surface. After"
                " baking, the vorticity vectors can be accessed in a Cycles Attribute"
                " Node or in Geometry Nodes with the name 'flip_vorticity' from the Vector output",
            default=False,
            options={'HIDDEN'},
            ); exec(conv("enable_vorticity_vector_attribute"))
    enable_age_attribute = BoolProperty(
            name=_z("Generate Age Attributes"),
            description="Generate Age Attributes\nGenerate fluid age attributes for the fluid surface."
                " The age attribute starts at 0.0 when the liquid is spawned and counts up in"
                " seconds. After baking, the age values can be accessed in a Cycles Attribute"
                " Node or in Geometry Nodes with the name 'flip_age' from the Fac output",
            default=False,
            options={'HIDDEN'},
            ); exec(conv("enable_age_attribute"))
    age_attribute_radius = FloatProperty(
            name=_z("Smoothing Radius"), 
            description = "Smoothing Radius\nAmount of smoothing when transferring the age attribute to the surface mesh."
                " Higher values result in smoother attribute transitions at the cost of simulation"
                " performance. Value is the search radius in number of voxels for nearby particles", 
            soft_min=1.0, soft_max=4.0,
            min=0.0,
            default=3.0,
            precision=1,
            ); exec(conv("age_attribute_radius"))
    enable_lifetime_attribute = BoolProperty(
            name=_z("Generate Lifetime Attributes"),
            description="Generate Lifetime Attributes\nGenerate fluid lifetime attributes for the fluid surface. This attribute allows the"
                " fluid to start with a lifetime value that counts down in seconds and once the lifetime reaches 0,"
                " the fluid is removed from the simulation. Each Inflow/Fluid object can be set to assign a"
                " starting lifetime to the generated fluid. After baking, the lifetime remaining values"
                " can be accessed in a Cycles Attribute Node or in Geometry Nodes with the name 'flip_lifetime' from"
                " the Fac output",
            default=False,
            options={'HIDDEN'},
            ); exec(conv("enable_lifetime_attribute"))
    lifetime_attribute_radius = FloatProperty(
            name=_z("Smoothing Radius"), 
            description = "Smoothing Radius\nAmount of smoothing when transferring the lifetime attribute to the surface mesh."
                " Higher values result in smoother attribute transitions at the cost of simulation"
                " performance. Value is the search radius in number of voxels for nearby particles", 
            soft_min=1.0, soft_max=4.0,
            min=0.0,
            default=3.0,
            precision=1,
            ); exec(conv("lifetime_attribute_radius"))
    lifetime_attribute_death_time = FloatProperty(
            name=_z("Base Death Time"), 
            description = "Base Death Time\nBase time in seconds at which fluid is removed from the simulation. At the default of 0.0,"
                " fluid will be removed when their lifetime attribute counts down to 0.0. Increase or decrease this"
                " value to offset the base time of death. Increasing will result in fluid dying earlier."
                " Decreasing will result in fluid dying later", 
            default=0.0,
            precision=2,
            ); exec(conv("lifetime_attribute_death_time"))
    enable_whitewater_proximity_attribute = BoolProperty(
            name=_z("Whitewater Proximity Attributes"),
            description="Whitewater Proximity Attributes\nGenerate whitewater proximity attributes for the fluid surface. The attribute values represent"
                " how many foam, bubble, or spray particles are near the surface mesh and can be used in a material to shade"
                " parts of the surface that are near whitewater particles. After baking, the proximity attribute can be accessed"
                " in a Cycles Attribute Node or in Geometry Nodes with the names 'flip_foam_proximity', 'flip_bubble_proximity',"
                " and 'flip_spray_proximity' from the Fac output",
            default=False,
            options={'HIDDEN'},
            ); exec(conv("enable_whitewater_proximity_attribute"))
    whitewater_proximity_attribute_radius = FloatProperty(
            name=_z("Smoothing Radius"), 
            description = "Smoothing Radius\nAmount of smoothing when transferring the whitewater proximity attribute to the surface mesh."
                " Higher values result in smoother attribute transitions at the cost of simulation"
                " performance. Value is the search radius in number of voxels for nearby particles", 
            soft_min=1.0, soft_max=4.0,
            min=0.0,
            default=2.0,
            precision=1,
            ); exec(conv("whitewater_proximity_attribute_radius"))
    enable_color_attribute = BoolProperty(
            name=_z("Generate Color Attributes"),
            description="Generate Color Attributes\nGenerate fluid color attributes for the fluid surface. Each"
                " Inflow/Fluid object can set to assign color to the generated fluid. After"
                " baking, the color values can be accessed in a Cycles Attribute Node or in Geometry Nodes"
                " with the name 'flip_color' from the Color output. This can be used to create varying color"
                " liquid effects",
            default=False,
            options={'HIDDEN'},
            ); exec(conv("enable_color_attribute"))
    color_attribute_radius = FloatProperty(
            name=_z("Smoothing Radius"), 
            description = "Smoothing Radius\nAmount of smoothing when transferring the color attribute to the surface mesh."
                " Higher values result in smoother attribute transitions at the cost of simulation"
                " performance. Value is the search radius in number of voxels for nearby particles", 
            soft_min=1.0, soft_max=4.0,
            min=0.0,
            default=3.0,
            precision=1,
            ); exec(conv("color_attribute_radius"))
    enable_color_attribute_mixing = BoolProperty(
            name=_z("Enable Mixing"),
            description="Enable Mixing\nSimulate basic color mixing. If enabled, particles will absorb color attributes"
                " from nearby particles. If disabled, particles will hold a static color value",
            default=False,
            ); exec(conv("enable_color_attribute_mixing"))
    color_attribute_mixing_rate = FloatProperty(
            name=_z("Mixing Rate"), 
            description = "Mixing Rate\nControls how quickly particles will absorb color from nearby particles. Higher"
                " values will cause colors to mix and spread more quickly. Lower values will cause colors to"
                " mix and spread more slowly", 
            soft_max=25.0,
            min=0.0,
            default=12,
            precision=2,
            ); exec(conv("color_attribute_mixing_rate"))
    color_attribute_mixing_radius = FloatProperty(
            name=_z("Mixing Radius"), 
            description = "Mixing Radius\nRadius in which a particle can absorb color from nearby particles. Increasing"
                " this value can result in smoother mixing transitions at the cost of simulation performance."
                " This value is the search radius in number of voxels", 
            soft_max=3.0,
            min=0.0,
            default=1.0,
            precision=2,
            ); exec(conv("color_attribute_mixing_radius"))
    color_attribute_mixing_mode = EnumProperty(
            name=_z("Mixing Mode"),
            description="Mixing Mode\nMethod of simulating color attribute mixing",
            items=types.color_mixing_modes,
            default='COLOR_MIXING_MODE_MIXBOX',
            options={'HIDDEN'},
            ); exec(conv("color_attribute_mixing_mode"))
    enable_source_id_attribute = BoolProperty(
            name=_z("Generate Source ID Attributes"),
            description="Generate Source ID Attributes\nGenerate fluid source identifiers for the fluid surface. Each"
                " Inflow/Fluid object can set to assign a source ID to the generated fluid. After"
                " baking, the ID values can be accessed in a Cycles Attribute Node or in Geometry Nodes with the name"
                " 'flip_source_id' from the Fac output. This can be used to identifty fluid from"
                " different sources in a material or geometry node group. Warning: this attribute is"
                " not supported with sheeting effects or resolution upscaling features",
            default=False,
            options={'HIDDEN'},
            ); exec(conv("enable_source_id_attribute"))
    enable_viscosity_attribute = BoolProperty(
            name=_z("Enable Variable Viscosity"),
            description="Enable Variable Viscosity\nEnable the variable viscosity solver for mixed viscosity simulations."
                " After enabling, each Fluid/Inflow object can be set to assign a viscosity value"
                " to the generated fluid. When enabled, viscosity value attributes will also"
                " be generated for the fluid surface. After baking, the viscosity values can"
                " be accessed in a Cycles Attribute Node with the name 'flip_viscosity' from"
                " the Fac output",
            default=False,
            options={'HIDDEN'},
            ); exec(conv("enable_viscosity_attribute"))

    native_particle_scale = FloatProperty(default=3.0); exec(conv("native_particle_scale"))
    default_cells_per_compute_chunk = FloatProperty(default=15.0); exec(conv("default_cells_per_compute_chunk"))   # in millions

    surface_mesh_expanded = BoolProperty(default=True); exec(conv("surface_mesh_expanded"))
    meshing_volume_expanded = BoolProperty(default=False); exec(conv("meshing_volume_expanded"))
    meshing_against_boundary_expanded = BoolProperty(default=False); exec(conv("meshing_against_boundary_expanded"))
    meshing_against_obstacles_expanded = BoolProperty(default=False); exec(conv("meshing_against_obstacles_expanded"))
    surface_display_settings_expanded = BoolProperty(default=False); exec(conv("surface_display_settings_expanded"))
    geometry_attributes_expanded = BoolProperty(default=False); exec(conv("geometry_attributes_expanded"))
    velocity_attributes_expanded = BoolProperty(default=False); exec(conv("velocity_attributes_expanded"))
    color_attributes_expanded = BoolProperty(default=False); exec(conv("color_attributes_expanded"))
    other_attributes_expanded = BoolProperty(default=False); exec(conv("other_attributes_expanded"))

    show_smoothing_radius_in_ui = BoolProperty(default=False); exec(conv("show_smoothing_radius_in_ui"))
    is_smoothing_radius_updated_to_default = BoolProperty(default=False); exec(conv("is_smoothing_radius_updated_to_default"))

    preview_mode_attributes_tooltip = BoolProperty(
            name=_z("Preview Mode Attributes Tooltip"), 
            description="Preview Mode Attributes Tooltip\nThe fluid surface mesh is currently set to Preview Mode within the viewport and attributes"
                " will not be loaded. Attributes will not be displayed correctly in viewport render mode."
                " Surface attributes will only be loaded in Final Mode. The surface mesh display"
                " mode can be set in the 'Domain > Display Settings' panel", 
            default=True,
            ); exec(conv("preview_mode_attributes_tooltip"))


    def register_preset_properties(self, registry, path):
        add = registry.add_property
        add(path + ".enable_surface_mesh_generation",                     _z("Enable Surface Mesh"),                            group_id=0)
        add(path + ".subdivisions",                                   _z("Subdivisions"),                      group_id=0)
        add(path + ".particle_scale",                                 _z("Particle Scale"),                    group_id=0)
        add(path + ".compute_chunk_mode",                             _z("Compute Chunk Mode"),                group_id=0)
        add(path + ".compute_chunks_fixed",                           _z("Num Compute Chunks (fixed)"),        group_id=0)
        add(path + ".meshing_volume_mode",                            _z("Meshing Volume Mode"),               group_id=0)
        add(path + ".export_animated_meshing_volume_object",          _z("Export Animated Mesh"),              group_id=0)
        add(path + ".enable_meshing_offset",                          _z("Enable Obstacle Meshing"),           group_id=0)
        add(path + ".obstacle_meshing_mode",                          _z("Obstacle Meshing Mode"),             group_id=0)
        add(path + ".remove_mesh_near_domain",                        _z("Remove Mesh Near Domain"),           group_id=0)
        add(path + ".remove_mesh_near_domain_distance",               _z("Distance"),                          group_id=0)
        add(path + ".smoothing_value",                                _z("Smoothing Value"),                   group_id=0)
        add(path + ".smoothing_iterations",                           _z("Smoothing Iterations"),              group_id=0)
        add(path + ".invert_contact_normals",                         _z("Invert Contact Normals"),            group_id=0)
        add(path + ".generate_motion_blur_data",                      _z("Generate Motion Blur Data"),         group_id=0)
        add(path + ".enable_velocity_vector_attribute",               _z("Generate Velocity Attributes"),      group_id=0)
        add(path + ".enable_velocity_vector_attribute_against_obstacles",          _z("Generate Velocity Attributes Against Obstacles"), group_id=0)
        add(path + ".enable_speed_attribute",                         _z("Generate Speed Attributes"),                          group_id=0)
        add(path + ".enable_vorticity_vector_attribute",              _z("Generate Vorticity Attributes"),                      group_id=0)
        add(path + ".enable_age_attribute",                           _z("Generate Age Attributes"),                            group_id=0)
        add(path + ".age_attribute_radius",                           _z("Age Attribute Smoothing"),                            group_id=0)
        add(path + ".enable_lifetime_attribute",                          _z("Generate Lifetime Attributes"),                   group_id=0)
        add(path + ".lifetime_attribute_radius",                          _z("Lifetime Attribute Smoothing"),                   group_id=0)
        add(path + ".lifetime_attribute_death_time",                      _z("Death Time"),                                     group_id=0)
        add(path + ".enable_whitewater_proximity_attribute",              _z("Whitewater Proximity"),                           group_id=0)
        add(path + ".whitewater_proximity_attribute_radius",              _z("Whitewater Proximity Attribute Smoothing"),       group_id=0)
        add(path + ".enable_color_attribute",                         _z("Generate Color Attributes"),                          group_id=0)
        add(path + ".color_attribute_radius",                             _z("Color Attribute Smoothing"),                      group_id=0)
        add(path + ".enable_color_attribute_mixing",                      _z("Enable Color Attribute Mixing"),                  group_id=0)
        add(path + ".color_attribute_mixing_rate",                        _z("Color Attribute Mixing Rate"),                    group_id=0)
        add(path + ".color_attribute_mixing_radius",                      _z("Color Attribute Mixing Radius"),                  group_id=0)
        add(path + ".color_attribute_mixing_mode",                        _z("Color Attribute Mixing Mode"),                    group_id=0)
        add(path + ".enable_source_id_attribute",                         _z("Generate Source ID Attributes"),                  group_id=0)
        add(path + ".enable_viscosity_attribute",                         _z("Generate Viscosity Attributes"),                  group_id=0)


    def scene_update_post(self, scene):
        self._update_auto_compute_chunks()


    def load_post(self):
        # In earlier addons versions, the attribute smoothing radius could be set by the user.
        # Now that Blender >= 3.5 has a blur attribute node, this should be used instead for
        # further smoothing.
        #
        # Update Blend files upon the first load by setting the attribute smoothing radii back to
        # the default value of 3.0
        if self.is_smoothing_radius_updated_to_default:
            return
        default_smoothing_radius = 3.0
        self.color_attribute_radius = default_smoothing_radius
        self.age_attribute_radius = default_smoothing_radius
        self.lifetime_attribute_radius = default_smoothing_radius
        self.is_smoothing_radius_updated_to_default = True


    def get_meshing_volume_object(self):
        obj = None
        try:
            all_objects = vcu.get_all_scene_objects()
            obj = self.meshing_volume_object
            obj = all_objects.get(obj.name)
        except:
            pass
        return obj


    def is_meshing_volume_object_valid(self):
        return (self.meshing_volume_mode == 'MESHING_VOLUME_MODE_OBJECT' and 
                self.get_meshing_volume_object() is not None)


    def _update_enable_surface_mesh_generation(self, context):
        dprops = context.scene.flip_fluid.get_domain_properties()
        if dprops is None:
            return

        if self.enable_surface_mesh_generation:
            objects_to_initialize = flip_fluid_cache.EnabledMeshCacheObjects()
            objects_to_initialize.fluid_surface = True

            dprops.mesh_cache.initialize_cache_objects(objects_to_initialize)
            dprops.materials.surface_material = dprops.materials.surface_material
        else:
            dprops.mesh_cache.surface.reset_cache_object()


    def _update_auto_compute_chunks(self):
        domain_object = bpy.context.scene.flip_fluid.get_domain_object()
        if domain_object is None:
            return
        bbox = AABB.from_blender_object(domain_object)
        max_dim = max(bbox.xdim, bbox.ydim, bbox.zdim)

        dprops = bpy.context.scene.flip_fluid.get_domain_properties()
        if dprops.simulation.lock_cell_size:
            unlocked_dx = max_dim / dprops.simulation.resolution
            locked_dx = dprops.simulation.locked_cell_size
            dx = locked_dx
            if abs(locked_dx - unlocked_dx) < 1e-6:
                dx = unlocked_dx
        else:
            dx = max_dim / dprops.simulation.resolution

        subdivisions = self.subdivisions + 1
        max_chunks = subdivisions * subdivisions * subdivisions
        isize = math.ceil(bbox.xdim / dx) * subdivisions
        jsize = math.ceil(bbox.ydim / dx) * subdivisions
        ksize = math.ceil(bbox.zdim / dx) * subdivisions
        total_cells = isize * jsize * ksize
        cells_per_chunk = self.default_cells_per_compute_chunk * 1e6
        num_chunks = math.ceil(total_cells / cells_per_chunk)
        num_chunks = max(min(num_chunks, min(isize, jsize, ksize), max_chunks), 1)
        if self.compute_chunks_auto != num_chunks:
            self.compute_chunks_auto = num_chunks


    def _update_meshing_volume_object(self, context):
        obj = self.get_meshing_volume_object()
        if obj is None:
            return

        obj.hide_render = True
        vcu.set_object_display_type(obj, 'WIRE')
        obj.show_name = True

        try:
            # Cycles may not be enabled in the user's preferences
            if vcu.is_blender_30():
                obj.visible_camera = is_enabled
                obj.visible_diffuse = is_enabled
                obj.visible_glossy = is_enabled
                obj.visible_transmission = is_enabled
                obj.visible_volume_scatter = is_enabled
                obj.visible_shadow = is_enabled
            else:
                obj.cycles_visibility.camera = is_enabled
                obj.cycles_visibility.transmission = is_enabled
                obj.cycles_visibility.diffuse = is_enabled
                obj.cycles_visibility.scatter = is_enabled
                obj.cycles_visibility.glossy = is_enabled
                obj.cycles_visibility.shadow = is_enabled
        except:
            pass


    def _poll_meshing_volume_object(self, obj):
        if obj.type == 'MESH':
            return True
        return False


def register():
    bpy.utils.register_class(DomainSurfaceProperties)


def unregister():
    bpy.utils.unregister_class(DomainSurfaceProperties)