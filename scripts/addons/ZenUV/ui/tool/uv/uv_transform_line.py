# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright 2023, Alex Zhornyak

import bpy
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector

from ZenUV.utils.blender_zen_utils import ZenPolls
from ZenUV.ops.transform_sys.transform_utils.tr_object_data import transform_object_data


if ZenPolls.version_greater_3_2_0:
    vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
    vert_out.smooth('FLOAT', "v_ArcLength")

    shader_info = gpu.types.GPUShaderCreateInfo()
    shader_info.push_constant('MAT4', "ModelViewProjectionMatrix")
    shader_info.push_constant('FLOAT', "u_Scale")
    shader_info.push_constant('VEC4', "color")
    shader_info.vertex_in(0, 'VEC2', "pos")
    shader_info.vertex_in(1, 'FLOAT', "arcLength")
    shader_info.vertex_out(vert_out)
    shader_info.fragment_out(0, 'VEC4', "fragColor")

    shader_info.vertex_source(
        "void main()"
        "{"
        "  v_ArcLength = arcLength;"
        "  gl_Position = ModelViewProjectionMatrix * vec4(pos, 1.0f, 1.0f);"
        "}"
    )

    shader_info.fragment_source(
        "void main()"
        "{"
        "  if (step(sin(v_ArcLength * u_Scale), 0.5) == 1) { fragColor = color; }"
        "  else"
        "  discard;"
        "}"
    )

    shader_line = gpu.shader.create_from_info(shader_info)
    del vert_out
    del shader_info
else:
    shader_line = gpu.shader.from_builtin('2D_UNIFORM_COLOR')


class UV_GT_zenuv_transform_line(bpy.types.Gizmo):
    bl_idname = "UV_GT_zenuv_transform_line"
    bl_target_properties = ()

    __slots__ = (
        "custom_shape",

        "start",
        "end",

        "use_draw_self_line",
        "pivot_line_color",
        "pivot_line_alpha"
    )

    def _do_draw(self, context: bpy.types.Context, select_id=None):
        _, shader = self.custom_shape

        shader.bind()

        region = context.region

        gpu.state.blend_set('ALPHA_PREMULT')

        rgn2d = region.view2d

        v_scale = self.end - self.start

        if ZenPolls.version_greater_3_2_0:
            shader.uniform_float("u_Scale", v_scale.length / 2.0)

        t_data = []

        for _, info in transform_object_data.object_storage.items():
            for pivot in info.loops_data.values():
                x, y = rgn2d.view_to_region(pivot[0], pivot[1], clip=False)
                v_pos = Vector((x, y, 0))

                if self.use_draw_self_line:
                    if (self.start.resized(3) - v_pos).length < 1:
                        continue

                mtx = Matrix.Translation(v_pos) @ Matrix.Diagonal((v_scale.x, v_scale.y, 0)).to_4x4()
                self.draw_custom_shape(self.custom_shape, matrix=mtx, select_id=select_id)

                v_end = mtx @ Vector((1, 1, 0))

                t_data.append((v_end.x, v_end.y))

        # Gizmo Self Line
        if self.use_draw_self_line:
            mtx = Matrix.Translation(self.start.resized(3)) @ Matrix.Diagonal((v_scale.x, v_scale.y, 0)).to_4x4()
            self.draw_custom_shape(self.custom_shape, matrix=mtx, select_id=select_id)

        gpu.state.blend_set('NONE')

        p_font_size = 8
        if bpy.app.version < (3, 1, 0):
            p_font_size = round(p_font_size)
        blf.size(0, p_font_size, bpy.context.preferences.system.dpi)
        blf.color(0, 0, 0, 0, 1)

        for idx, item in enumerate(t_data):
            blf.position(0, item[0] + 3, item[1] + 3, 0)
            blf.draw(0, str(idx + 1))

    def draw(self, context: bpy.types.Context):
        self._do_draw(context)

    def test_select(self, context: bpy.types.Context, location):
        return -1

    def draw_select(self, context: bpy.types.Context, select_id):
        self._do_draw(context, select_id=select_id)

    def setup(self):
        if not hasattr(self, "start"):
            self.start = Vector((0, 0))
            self.end = Vector((0, 0))
            self.custom_shape = [None, shader_line]

            coords = [Vector((0, 0)), Vector((1, 1))]

            if ZenPolls.version_greater_3_2_0:
                arc_lengths = [0]
                for a, b in zip(coords[:-1], coords[1:]):
                    arc_lengths.append(arc_lengths[-1] + (a - b).length)
                self.custom_shape[0] = batch_for_shader(
                    shader_line, 'LINES',
                    {
                        "pos": coords,
                        "arcLength": arc_lengths
                    }
                )
            else:
                self.custom_shape[0] = batch_for_shader(
                    shader_line, 'LINES',
                    {
                        "pos": coords,
                    }
                )
            self.custom_shape[0].program_set(shader_line)
            self.use_draw_self_line = False
            self.pivot_line_color = (0.5, 0.5, 0.5)
            self.pivot_line_alpha = 1.0

    def exit(self, context, cancel):
        context.area.header_text_set(None)
