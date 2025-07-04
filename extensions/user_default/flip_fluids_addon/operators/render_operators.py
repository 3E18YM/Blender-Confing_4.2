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

import bpy

from .. import render
from ..utils import ui_utils

class FlipFluidQuickViewportDisplayFinal(bpy.types.Operator):
    bl_idname = "flip_fluid_operators.quick_viewport_display_final"
    bl_label = _z("Final")
    bl_description = "Final\nDisplay final mesh quality in the viewport"


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        domain_object = context.scene.flip_fluid.get_domain_object()
        if domain_object is None:
            return {'CANCELLED'}

        rprops = domain_object.flip_fluid.domain.render
        rprops.viewport_display = 'DISPLAY_FINAL'
        rprops.whitewater_viewport_display = 'DISPLAY_FINAL'
        ui_utils.force_ui_redraw()
        return {'FINISHED'}


class FlipFluidQuickViewportDisplayPreview(bpy.types.Operator):
    bl_idname = "flip_fluid_operators.quick_viewport_display_preview"
    bl_label = _z("Preview")
    bl_description = "Preview\nDisplay preview mesh quality in the viewport"


    @classmethod
    def poll(cls, context):
        return True


    def execute(self, context):
        domain_object = context.scene.flip_fluid.get_domain_object()
        if domain_object is None:
            return {'CANCELLED'}

        rprops = domain_object.flip_fluid.domain.render
        rprops.viewport_display = 'DISPLAY_PREVIEW'
        rprops.whitewater_viewport_display = 'DISPLAY_PREVIEW'
        ui_utils.force_ui_redraw()
        return {'FINISHED'}


class FlipFluidQuickViewportDisplayNone(bpy.types.Operator):
    bl_idname = "flip_fluid_operators.quick_viewport_display_none"
    bl_label = _z("None")
    bl_description = "None\nDo not display meshes in the viewport"


    @classmethod
    def poll(cls, context):
        return True


    def execute(self, context):
        domain_object = context.scene.flip_fluid.get_domain_object()
        if domain_object is None:
            return {'CANCELLED'}

        rprops = domain_object.flip_fluid.domain.render
        rprops.viewport_display = 'DISPLAY_NONE'
        rprops.whitewater_viewport_display = 'DISPLAY_NONE'
        ui_utils.force_ui_redraw()
        return {'FINISHED'}


class FlipFluidReloadFrame(bpy.types.Operator):
    bl_idname = "flip_fluid_operators.reload_frame"
    bl_label = _z("Reload Frame")
    bl_description = "Reload Frame\nReload the current frame"


    @classmethod
    def poll(cls, context):
        return True


    def execute(self, context):
        domain_object = context.scene.flip_fluid.get_domain_object()
        if domain_object is None:
            return {'CANCELLED'}

        frameno = render.get_current_simulation_frame()
        render.reload_frame(frameno)
        
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FlipFluidQuickViewportDisplayFinal)
    bpy.utils.register_class(FlipFluidQuickViewportDisplayPreview)
    bpy.utils.register_class(FlipFluidQuickViewportDisplayNone)
    bpy.utils.register_class(FlipFluidReloadFrame)


def unregister():
    bpy.utils.unregister_class(FlipFluidQuickViewportDisplayFinal)
    bpy.utils.unregister_class(FlipFluidQuickViewportDisplayPreview)
    bpy.utils.unregister_class(FlipFluidQuickViewportDisplayNone)
    bpy.utils.unregister_class(FlipFluidReloadFrame)
