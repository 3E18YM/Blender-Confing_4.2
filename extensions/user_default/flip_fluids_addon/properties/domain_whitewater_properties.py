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

import bpy, os
from bpy.props import (
        BoolProperty,
        BoolVectorProperty,
        EnumProperty,
        FloatProperty,
        IntProperty
        )

from .custom_properties import (
        NewMinMaxIntProperty,
        NewMinMaxFloatProperty
        )
from .. import types
from ..utils import version_compatibility_utils as vcu
from ..objects import flip_fluid_cache


class DomainWhitewaterProperties(bpy.types.PropertyGroup):
    conv = vcu.convert_attribute_to_28
    
    whitewater_ui_mode = EnumProperty(
            name=_z("Whitewater UI Mode"),
            description="Whitewater UI Mode\nWhitewater UI mode",
            items=types.whitewater_ui_modes,
            default='WHITEWATER_UI_MODE_BASIC',
            ); exec(conv("whitewater_ui_mode"))
    highlight_advanced_settings = BoolProperty(
            name=_z("Highlight Advanced Settings"),
            description="Highlight Advanced Settings\nHighlight advanced parameters in red",
            default=True,
            ); exec(conv("highlight_advanced_settings"))
    enable_whitewater_simulation = BoolProperty(
            name=_z("Enable Whitewater Simulation"),
            description="Enable Whitewater Simulation\nEnable whitewater foam/bubble/spray particle solver",
            default=False,
            update=lambda self, context: self._update_enable_whitewater_simulation(context),
            options={'HIDDEN'},
            ); exec(conv("enable_whitewater_simulation"))
    enable_foam = BoolProperty(
            name=_z("Foam"),
            description="Foam\nEnable solving for foam particles. Foam particles form"
                " a layer on the fluid surface and are advected with the fluid"
                " velocity. If disabled, any particles that enter the foam layer"
                " will be destroyed",
            default=True,
            ); exec(conv("enable_foam"))
    enable_bubbles = BoolProperty(
            name = _z("Bubbles"),
            description="Bubbles\nEnable solving for bubble particles. Bubble particles"
                " below the foam layer are advected with the fluid velocity and"
                " float towards the foam layer. If disabled, any particles that"
                " move below the foam layer will be destroyed. WARNING: Bubble"
                " particles are a large contributor to the foam layer and"
                " disabling may severely limit the amount of generated foam",
            default=True,
            ); exec(conv("enable_bubbles"))
    enable_spray = BoolProperty(
            name=_z("Spray"),
            description="Spray\nEnable solving for spray particles. Spray particles"
                " above the foam layer are simulated ballistically with"
                " gravity. If disabled, any particles that move above the foam"
                " layer will be destroyed",
            default=True,
            ); exec(conv("enable_spray"))
    enable_dust = BoolProperty(
            name=_z("Dust"),
            description="Dust\nEnable solving for dust particles. Dust particles are"
                " generated near obstacle surfaces and are advected with the"
                " fluid velocity while sinking towards the ground. If disabled,"
                " these particles will not be generated",
            default=False,
            ); exec(conv("enable_dust"))
    generate_whitewater_motion_blur_data = BoolProperty(
            name=_z("Generate Motion Blur Vectors"),
            description="Generate Motion Blur Vectors\nGenerate whitewater speed vectors for motion blur"
                " rendering",
            default=False,
            ); exec(conv("generate_whitewater_motion_blur_data"))
    enable_velocity_vector_attribute = BoolProperty(
            name=_z("Generate Velocity Attributes"),
            description="Generate Velocity Attributes\nGenerate fluid 3D velocity vector attributes for whitewater particles. After"
                " baking, the velocity vectors (in m/s) can be accessed in a Cycles Attribute"
                " Node or in Geometry Nodes with the name 'flip_velocity' from the Vector output. Not supported on"
                " instanced particles, only supported on pointclouds",
            default=False,
            options={'HIDDEN'},
            ); exec(conv("enable_velocity_vector_attribute"))
    enable_id_attribute = BoolProperty(
            name=_z("Generate ID Attributes"),
            description="Generate ID Attributes\nGenerate stable ID attributes for whitewater particles. After"
                " baking, the ID values can be accessed in a Cycles Attribute"
                " Node or in Geometry Nodes with the name 'flip_id'. Use where consistent"
                " particle attributes are needed between frames, such as for varying particle"
                " size or color. Not supported on instanced particles, only supported on pointclouds",
            default=False,
            options={'HIDDEN'},
            ); exec(conv("enable_id_attribute"))
    enable_lifetime_attribute = BoolProperty(
            name=_z("Generate Lifetime Attributes"),
            description="Generate Lifetime Attributes\nGenerate remaining lifetime attributes for whitewater particles. After"
                " baking, the lifetime values can be accessed in a Cycles Attribute Node or in"
                " Geometry Nodes with the name 'flip_lifetime'. When the lifetime of a particle"
                " reaches 0, the particle will despawn. Not supported on instanced particles,"
                " only supported on pointclouds",
            default=False,
            options={'HIDDEN'},
            ); exec(conv("enable_lifetime_attribute"))
    enable_whitewater_emission = bpy.props.BoolProperty(
            name=_z("Enable Whitewater Emission"),
            description="Enable Whitewater Emission\nAllow whitewater emitters to generate new particles",
            default=True,
            ); exec(conv("enable_whitewater_emission"))
    whitewater_emitter_generation_rate = IntProperty(
            name=_z("Emitter Generation Rate (Percent)"), 
            description="Emitter Generation Rate (Percent)\nControls how many whitewater emitters are generated."
                " Emitters are generated at wavecrests and in areas high"
                " turbulence where fluid is likely to be aerated", 
            min=0, max=100,
            default=100,
            ); exec(conv("whitewater_emitter_generation_rate"))
    wavecrest_emission_rate = FloatProperty(
            name=_z("Max Wavecrest Emission Rate"), 
            description="Max Wavecrest Emission Rate\nMaximum number of whitewater particles that a"
                " single wavecrest emitter may generate per simulation second", 
            min=0, soft_max=1000,
            default=175,
            step=30,
            precision=0,
            ); exec(conv("wavecrest_emission_rate"))
    turbulence_emission_rate = FloatProperty(
            name=_z("Max Turbulence Emission Rate"), 
            description="Max Turbulence Emission Rate\nMaximum number of whitewater particles that a"
                " single turbulence emitter may generate per simulation second", 
            min=0, soft_max=1000,
            default=175,
            step=30,
            precision=0,
            ); exec(conv("turbulence_emission_rate"))
    dust_emission_rate = FloatProperty(
            name=_z("Max Dust Emission Rate"), 
            description="Max Dust Emission Rate\nMaximum number of dust particles that a"
                " single dust emitter may generate per simulation second", 
            min=0, soft_max=1000,
            default=175,
            step=30,
            precision=0,
            ); exec(conv("dust_emission_rate"))
    spray_emission_speed = FloatProperty(
            name=_z("Spray Emission Speed"), 
            description="Spray Emission Speed\nSpeed scaling factor for spray particle emission. Increasing"
                " this value will generate more spread out and exaggerated spray effects", 
            min=0.0, soft_min=1.0,
            soft_max=3.0,
            default=1.2,
            ); exec(conv("spray_emission_speed"))
    min_max_whitewater_energy_speed = NewMinMaxFloatProperty(
            name_min="Min Energy Speed", 
            description_min="Fluid with speed less than this value will generate"
                " no whitewater", 
            min_min=0,
            default_min=0.2,
            precision_min=2,

            name_max="Max Energy Speed", 
            description_max="When fluid speed is greater than the min value, and"
                " less than the max value, proportionally increase the amount"
                " of whitewater emitted based on emission rate of the emitter", 
            min_max=0,
            default_max=3.0,
            precision_max=2,
            ); exec(conv("min_max_whitewater_energy_speed"))
    min_max_whitewater_wavecrest_curvature = NewMinMaxFloatProperty(
            name_min="Min Curvature", 
            description_min="Wavecrests with curvature less than this value will"
                " generate no whitewater. This value rarely needs to be changed", 
            min_min=0.0, max_min=5.0,
            default_min=0.4,
            precision_min=2,

            name_max="Max Curvature", 
            description_max="When wavecrest curvature is greater than the min value,"
                " and less than the max value, proportionally increase the amount"
                " of whitewater emitted based on the Wavecrest Emission Rate."
                " This value rarely needs to be changed", 
            min_max=0.0, max_max=5.0,
            default_max=1.0,
            precision_max=2,
            ); exec(conv("min_max_whitewater_wavecrest_curvature"))
    min_max_whitewater_turbulence = NewMinMaxFloatProperty(
            name_min="Min Turbulence", 
            description_min="Fluid with turbulence less than this value will"
                " generate no whitewater. This value rarely needs to be changed", 
            min_min=0,
            default_min=100,
            precision_min=0,

            name_max="Max Turbulence", 
            description_max="When the fluid turbulence is greater than the min value,"
                " and less than the max value, proportionally increase the amount"
                " of whitewater emitted based on the Turbulence Emission Rate."
                " This value rarely needs to be changed", 
            min_max=0,
            default_max=200,
            precision_max=0,
            ); exec(conv("min_max_whitewater_turbulence"))
    max_whitewater_particles = FloatProperty(
            name=_z("Max Particles (in millions)"), 
            description="Max Particles (in millions)\nMaximum number of whitewater particles (in millions)"
                " to simulate. The solver will stop generating new whitewater"
                " particles to prevent exceeding this limit. If set to 0, the"
                " solver will not limit the number of whitewater particles,"
                " however this may require large amounts of storage space depending"
                " on the simulation", 
            min=0, max=2000,
            default=12,
            precision=2,
            ); exec(conv("max_whitewater_particles"))
    enable_whitewater_emission_near_boundary = BoolProperty(
            name=_z("Enable Emission Near Domain Boundary"),
            description="Enable Emission Near Domain Boundary\nAllow whitewater emitters to generate particles at"
                " the domain boundary",
            default=False,
            ); exec(conv("enable_whitewater_emission_near_boundary"))
    enable_dust_emission_near_boundary = BoolProperty(
            name=_z("Enable Dust Emission Near Domain Boundary"),
            description="Enable Dust Emission Near Domain Boundary\nAllow whitewater emitters to generate dust particles near"
                " the domain floor",
            default=False,
            ); exec(conv("enable_dust_emission_near_boundary"))
    min_max_whitewater_lifespan = NewMinMaxFloatProperty(
            name_min="Min Lifespan", 
            description_min="Minimum whitewater particle lifespan in seconds", 
            min_min=0.0,
            default_min=0.5,
            precision_min=2,

            name_max="Max Lifespan", 
            description_max="Maximum whitewater particle lifespan in seconds", 
            min_max=0.0,
            default_max=6.0,
            precision_max=2,
            ); exec(conv("min_max_whitewater_lifespan"))
    whitewater_lifespan_variance = FloatProperty(
            name=_z("Lifespan Variance"), 
            description ="Lifespan Variance\nA random number of seconds in this range will be added"
                " or subtracted from the whitewater particle lifespan", 
            min=0.0,
            default=3.0,
            precision=2,
            ); exec(conv("whitewater_lifespan_variance"))
    foam_lifespan_modifier = FloatProperty(
            name=_z("Foam Lifespan Modifier"), 
            description="Foam Lifespan Modifier\nMultiply the lifespan of a foam particle by this value", 
            min=0.0,
            default=1.0,
            precision=1,
            ); exec(conv("foam_lifespan_modifier"))
    bubble_lifespan_modifier = FloatProperty(
            name=_z("Bubble Lifespan Modifier"), 
            description="Bubble Lifespan Modifier\nMultiply the lifespan of a bubble particle by this value", 
            min=0.0,
            default=4.0,
            precision=1,
            ); exec(conv("bubble_lifespan_modifier"))
    spray_lifespan_modifier = FloatProperty(
            name=_z("Spray Lifespan Modifier"), 
            description="Spray Lifespan Modifier\nMultiply the lifespan of a spray particle by this value", 
            min=0.0,
            default=5.0,
            precision=1,
            ); exec(conv("spray_lifespan_modifier"))
    dust_lifespan_modifier = FloatProperty(
            name=_z("Dust Lifespan Modifier"), 
            description="Dust Lifespan Modifier\nMultiply the lifespan of a dust particle by this value", 
            min=0.0,
            default=2.0,
            precision=1,
            ); exec(conv("dust_lifespan_modifier"))
    foam_advection_strength = FloatProperty(
            name=_z("Foam Advection Strength"), 
            description="Foam Advection Strength\nControls how much the foam moves along with the motion"
                " of the fluid surface. High values cause tighter streaks of"
                " foam that closely follow the fluid motion. Lower values will"
                " cause more diffuse and spread out foam", 
            min=0.0, max=1.0,
            default=1.0,
            precision=2,
            subtype='FACTOR',
            ); exec(conv("foam_advection_strength"))
    foam_layer_depth = FloatProperty(
            name=_z("Foam Layer Depth"), 
            description="Foam Layer Depth\nSet the thickness of the whitewater foam layer", 
            min=0.0,
            max=1.0,
            default=0.4,
            precision=2,
            subtype='FACTOR',
            ); exec(conv("foam_layer_depth"))
    foam_layer_offset = FloatProperty(
            name=_z("Foam Layer Offset"), 
            description="Foam Layer Offset\nSet the offset of the whitewater foam layer above/below"
                " the fluid surface. If set to a value of 1, the foam layer will"
                " rest entirely above the fluid surface. A value of -1 will have"
                " the foam layer rest entirely below the fluid surface", 
            min=-1.0,
            max=1.0,
            default=0.25,
            precision=2,
            subtype='FACTOR',
            ); exec(conv("foam_layer_offset"))
    preserve_foam = BoolProperty(
            name=_z("Preserve Foam"),
            description="Preserve Foam\nIncrease the lifespan of foam particles based on the"
                " local density of foam particles, which can help create clumps"
                " and streaks of foam on the liquid surface over time",
            default=True,
            ); exec(conv("preserve_foam"))
    foam_preservation_rate = FloatProperty(
            name=_z("Foam Preservation Rate"), 
            description="Foam Preservation Rate\nRate to add to the lifetime of preserved foam. This"
                " value is the number of seconds to add per second, so if"
                " greater than one can effectively preserve high density foam"
                " clumps from every being killed", 
            default=0.75,
            precision=2,
            ); exec(conv("foam_preservation_rate"))
    min_max_foam_density = NewMinMaxIntProperty(
            name_min="Min Foam Density", 
            description_min="Foam densities less than this value will not increase"
                " the lifetime of a foam particle. Foam density units are in"
                " number of particles per voxel", 
            min_min=0,
            default_min=20,

            name_max="Max Foam Density", 
            description_max="Foam densities that are greater than the min value,"
                " and less than the max value, proportionally increase the"
                " particle lifetime based on the Foam Preservation Rate. Foam"
                " density units are in number of particles per voxel", 
            min_max=0,
            default_max=45,
            ); exec(conv("min_max_foam_density"))
    bubble_drag_coefficient = FloatProperty(
            name=_z("Bubble Drag Coefficient"), 
            description="Bubble Drag Coefficient\nControls how quickly bubble particles are dragged with"
                " the fluid velocity. If set to 1, bubble particles will be"
                " immediately dragged into the flow direction of the fluid", 
            min=0.0, max=1.0,
            default=0.8,
            precision=2,
            subtype='FACTOR',
            ); exec(conv("bubble_drag_coefficient"))
    bubble_bouyancy_coefficient = FloatProperty(
            name=_z("Bubble Buoyancy Coefficient"), 
            description="Bubble Buoyancy Coefficient\nControls how quickly bubble particles float towards"
                " the fluid surface. If set to a negative value, bubbles will"
                " sink away from the fluid surface", 
            default=2.5,
            precision=2,
            step=0.3,
            ); exec(conv("bubble_bouyancy_coefficient"))
    spray_drag_coefficient = FloatProperty(
            name=_z("Spray Drag Coefficient"), 
            description="Spray Drag Coefficient\nControls amount of air resistance on a spray particle", 
            min=0.0, max=5.0,
            default=3.0,
            precision=2,
            ); exec(conv("spray_drag_coefficient"))
    dust_drag_coefficient = FloatProperty(
            name=_z("Dust Drag Coefficient"), 
            description="Dust Drag Coefficient\nControls how quickly dust particles are dragged with"
                " the fluid velocity. If set to 1, dust particles will be"
                " immediately dragged into the flow direction of the fluid", 
            min=0.0, max=1.0,
            default=0.75,
            precision=2,
            subtype='FACTOR',
            ); exec(conv("dust_drag_coefficient"))
    dust_bouyancy_coefficient = FloatProperty(
            name=_z("Dust Buoyancy Coefficient"), 
            description="Dust Buoyancy Coefficient\nControls how quickly dust particles sink towards"
                " the ground. Decreasing this value will cause particles to sink"
                " more quickly. If set to a positive value, dust will float towards"
                " fluid surface", 
            default=-3.0,
            precision=2,
            step=0.3,
            ); exec(conv("dust_bouyancy_coefficient"))
    foam_boundary_behaviour = EnumProperty(
            name=_z("Foam Behaviour At Limits"),
            description="Foam Behaviour At Limits\nSpecifies the foam particle behavior when hitting the"
                " domain boundary",
            items=types.boundary_behaviours,
            default='BEHAVIOUR_COLLIDE',
            ); exec(conv("foam_boundary_behaviour"))
    bubble_boundary_behaviour = EnumProperty(
            name=_z("Bubble Behaviour At Limits"),
            description="Bubble Behaviour At Limits\nSpecifies the bubble particle behavior when hitting"
                " the domain boundary",
            items=types.boundary_behaviours,
            default='BEHAVIOUR_COLLIDE',
            ); exec(conv("bubble_boundary_behaviour"))
    spray_boundary_behaviour = EnumProperty(
            name=_z("Spray Behaviour At Limits"),
            description="Spray Behaviour At Limits\nSpecifies the spray particle behavior when hitting the"
                " domain boundary",
            items=types.boundary_behaviours,
            default='BEHAVIOUR_COLLIDE',
            ); exec(conv("spray_boundary_behaviour"))
    foam_boundary_active = BoolVectorProperty(
            name="",
            description="Activate behaviour on the corresponding side of the domain",
            default=(True, True, True, True, False, True),
            size=6,
            ); exec(conv("foam_boundary_active"))
    bubble_boundary_active = BoolVectorProperty(
            name="",
            description="Activate behaviour on the corresponding side of the domain",
            default=(True, True, True, True, False, True),
            size=6,
            ); exec(conv("bubble_boundary_active"))
    spray_boundary_active = BoolVectorProperty(
            name="",
            description="Activate behaviour on the corresponding side of the domain",
            default=(True, True, True, True, False, True),
            size=6,
            ); exec(conv("spray_boundary_active"))
    whitewater_boundary_collisions_mode = EnumProperty(
            name=_z("Domain Boundary Collisions Mode"),
            description="Domain Boundary Collisions Mode\nSelect how to set the domain boundary collisions",
            items=types.boundary_collisions_modes,
            default='BOUNDARY_COLLISIONS_MODE_INHERIT',
            options={'HIDDEN'},
            ); exec(conv("whitewater_boundary_collisions_mode"))
    foam_boundary_collisions = BoolVectorProperty(
            name="",
            description="Enable collisions on the corresponding side of the domain for whitewater foam particles."
                " If disabled, this side of the boundary will be open and will act"
                " as an outflow",
            default=(True, True, True, True, True, True),
            size=6,
            ); exec(conv("foam_boundary_collisions"))
    bubble_boundary_collisions = BoolVectorProperty(
            name="",
            description="Enable collisions on the corresponding side of the domain for whitewater bubble particles."
                " If disabled, this side of the boundary will be open and will act"
                " as an outflow",
            default=(True, True, True, True, True, True),
            size=6,
            ); exec(conv("bubble_boundary_collisions"))
    spray_boundary_collisions = BoolVectorProperty(
            name="",
            description="Enable collisions on the corresponding side of the domain for whitewater spray particles."
                " If disabled, this side of the boundary will be open and will act"
                " as an outflow",
            default=(True, True, True, True, True, True),
            size=6,
            ); exec(conv("spray_boundary_collisions"))
    dust_boundary_collisions = BoolVectorProperty(
            name="",
            description="Enable collisions on the corresponding side of the domain for whitewater dust particles."
                " If disabled, this side of the boundary will be open and will act"
                " as an outflow",
            default=(True, True, True, True, True, True),
            size=6,
            ); exec(conv("dust_boundary_collisions"))
    obstacle_influence_base_level = FloatProperty(
            name=_z("Influence Base Level"), 
            description="Influence Base Level\nThe default value of whitewater influence. If a location"
                " is not affected by an obstacle's influence, the amount"
                " of whitewater generated at this location will be scaled by"
                " this value. A value of 1.0 will generate a normal amount"
                " of whitewater, a value greater than 1.0 will generate more,"
                " a value less than 1.0 will generate less",
            min=0.0,
            default=1.0,
            precision=2,
            ); exec(conv("obstacle_influence_base_level"))
    obstacle_influence_decay_rate = FloatProperty(
            name=_z("Influence Decay Rate"), 
            description="Influence Decay Rate\nThe rate at which influence will decay towards the"
                " base level. If a keyframed/animated obstacle leaves an"
                " influence above/below the base level at some location," 
                " the value of influence at this location will adjust towards"
                " the base level value at this rate. This value is in amount" 
                " of influence per second",
            min=0.0,
            default=5.0,
            precision=2,
            ); exec(conv("obstacle_influence_decay_rate"))

    settings_view_mode_expanded = BoolProperty(default=False); exec(conv("settings_view_mode_expanded"))
    whitewater_simulation_particles_expanded = BoolProperty(default=False); exec(conv("whitewater_simulation_particles_expanded"))
    emitter_settings_expanded = BoolProperty(default=True); exec(conv("emitter_settings_expanded"))
    particle_settings_expanded = BoolProperty(default=False); exec(conv("particle_settings_expanded"))
    boundary_behaviour_settings_expanded = BoolProperty(default=False); exec(conv("boundary_behaviour_settings_expanded"))
    obstacle_settings_expanded = BoolProperty(default=False); exec(conv("obstacle_settings_expanded"))
    whitewater_display_settings_expanded = BoolProperty(default=False); exec(conv("whitewater_display_settings_expanded"))
    geometry_attributes_expanded = BoolProperty(default=False); exec(conv("geometry_attributes_expanded"))


    def register_preset_properties(self, registry, path):
        add = registry.add_property
        add(path + ".enable_whitewater_simulation",             _z("Enable Whitewater"),              group_id=0)
        add(path + ".enable_foam",                              _z("Enable Foam"),                    group_id=0)
        add(path + ".enable_bubbles",                           _z("Enable Bubbles"),                 group_id=0)
        add(path + ".enable_spray",                             _z("Enable Spray"),                   group_id=0)
        add(path + ".enable_dust",                              _z("Enable Dust"),                    group_id=0)
        add(path + ".generate_whitewater_motion_blur_data",     _z("Generate Motion Blur Data"),      group_id=0)
        add(path + ".enable_velocity_vector_attribute",         _z("Generate Velocity Attributes"),   group_id=0)
        add(path + ".enable_id_attribute",                      _z("Generate ID Attributes"),         group_id=0)
        add(path + ".enable_lifetime_attribute",                _z("Generate Lifetime Attributes"),   group_id=0)
        add(path + ".enable_whitewater_emission",               _z("Enable Emission"),                group_id=0)
        add(path + ".whitewater_emitter_generation_rate",       _z("Emission Rate"),                  group_id=0)
        add(path + ".wavecrest_emission_rate",                  _z("Wavecrest Emission Rate"),        group_id=0)
        add(path + ".turbulence_emission_rate",                 _z("Turbulence Emission Rate"),       group_id=0)
        add(path + ".dust_emission_rate",                       _z("Dust Emission Rate"),             group_id=0)
        add(path + ".spray_emission_speed",                     _z("Spray Emission Speed"),           group_id=0)
        add(path + ".min_max_whitewater_energy_speed",          _z("Min-Max Energy Speed"),           group_id=0)
        add(path + ".min_max_whitewater_wavecrest_curvature",   _z("Min-Max Curvature"),              group_id=0)
        add(path + ".min_max_whitewater_turbulence",            _z("Min-Max Turbulence"),             group_id=0)
        add(path + ".max_whitewater_particles",                 _z("Max Particles"),                  group_id=0)
        add(path + ".enable_whitewater_emission_near_boundary", _z("Emit Near Boundary"),             group_id=0)
        add(path + ".enable_dust_emission_near_boundary",       _z("Emit Dust Near Boundary"),        group_id=0)
        add(path + ".min_max_whitewater_lifespan",              _z("Min-Max Lifespane"),              group_id=1)
        add(path + ".whitewater_lifespan_variance",             _z("Lifespan Variance"),              group_id=1)
        add(path + ".foam_lifespan_modifier",                   _z("Foam Lifespan Modifier"),         group_id=1)
        add(path + ".bubble_lifespan_modifier",                 _z("Bubble Lifespan Modifier"),       group_id=1)
        add(path + ".spray_lifespan_modifier",                  _z("Spray Lifespan Modifier"),        group_id=1)
        add(path + ".dust_lifespan_modifier",                   _z("Dust Lifespan Modifier"),         group_id=1)
        add(path + ".foam_advection_strength",                  _z("Foam Advection Strength"),        group_id=1)
        add(path + ".foam_layer_depth",                         _z("Foam Depth"),                     group_id=1)
        add(path + ".foam_layer_offset",                        _z("Foam Offset"),                    group_id=1)
        add(path + ".preserve_foam",                            _z("Preserve Foam"),                  group_id=1)
        add(path + ".foam_preservation_rate",                   _z("Preservation Rate"),              group_id=1)
        add(path + ".min_max_foam_density",                     _z("Min-Max Density"),                group_id=1)
        add(path + ".bubble_drag_coefficient",                  _z("Bubble Drag"),                    group_id=2)
        add(path + ".bubble_bouyancy_coefficient",              _z("Bubble Bouyancy"),                group_id=2)
        add(path + ".spray_drag_coefficient",                   _z("Spray Drag"),                     group_id=2)
        add(path + ".dust_drag_coefficient",                    _z("Dust Drag"),                      group_id=2)
        add(path + ".dust_bouyancy_coefficient",                _z("Dust Bouyancy"),                  group_id=2)
        add(path + ".foam_boundary_behaviour",                  _z("Foam Boundary Behaviour"),        group_id=2)
        add(path + ".bubble_boundary_behaviour",                _z("Bubble Boundary Behaviour"),      group_id=2)
        add(path + ".spray_boundary_behaviour",                 _z("Spray Boundary Behaviour"),       group_id=2)
        add(path + ".foam_boundary_active",                     _z("Foam Boundary X–/+ Y–/+ Z–/+"),   group_id=2)
        add(path + ".bubble_boundary_active",                   _z("Bubble Boundary X–/+ Y–/+ Z–/+"), group_id=2)
        add(path + ".spray_boundary_active",                    _z("Spray Boundary X–/+ Y–/+ Z–/+"),  group_id=2)
        add(path + ".whitewater_boundary_collisions_mode",      _z("Boundary Collisions Mode"),       group_id=2)
        add(path + ".foam_boundary_collisions",                 _z("Foam Boundary Collisions"),       group_id=2)
        add(path + ".bubble_boundary_collisions",               _z("Bubble Boundary Collisions"),     group_id=2)
        add(path + ".spray_boundary_collisions",                _z("Spray Boundary Collisions"),      group_id=2)
        add(path + ".dust_boundary_collisions",                 _z("Dust Boundary Collisions"),       group_id=2)
        add(path + ".obstacle_influence_base_level",            _z("Obstacle Influence Base Level"),  group_id=2)
        add(path + ".obstacle_influence_decay_rate",            _z("Obstacle Influence Base Level"),  group_id=2)


    def _update_enable_whitewater_simulation(self, context):
        dprops = context.scene.flip_fluid.get_domain_properties()
        if dprops is None:
            return

        if self.enable_whitewater_simulation:
            objects_to_initialize = flip_fluid_cache.EnabledMeshCacheObjects()
            objects_to_initialize.whitewater_particles = True

            dprops.mesh_cache.initialize_cache_objects(objects_to_initialize)
            dprops.materials.whitewater_foam_material = dprops.materials.whitewater_foam_material
            dprops.materials.whitewater_bubble_material = dprops.materials.whitewater_bubble_material
            dprops.materials.whitewater_spray_material = dprops.materials.whitewater_spray_material
            dprops.materials.whitewater_dust_material = dprops.materials.whitewater_dust_material
        else:
            dprops.mesh_cache.foam.reset_cache_object()
            dprops.mesh_cache.bubble.reset_cache_object()
            dprops.mesh_cache.spray.reset_cache_object()
            dprops.mesh_cache.dust.reset_cache_object()


def register():
    bpy.utils.register_class(DomainWhitewaterProperties)


def unregister():
    bpy.utils.unregister_class(DomainWhitewaterProperties)