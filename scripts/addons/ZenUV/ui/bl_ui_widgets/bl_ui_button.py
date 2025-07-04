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

# Copyright: https://github.com/jayanam/bl_ui_widgets

from . bl_ui_widget import BL_UI_Widget

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader


class BL_UI_Button(BL_UI_Widget):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._text_color = (1.0, 1.0, 1.0, 1.0)
        self._hover_bg_color = (0.5, 0.5, 0.5, 1.0)
        self._select_bg_color = (0.7, 0.7, 0.7, 1.0)

        self._text = "Button"
        self._text_size = 16
        self._text_scale = 1.0
        self._textpos = (x, y)

        self.__state = 0
        self.__image = None
        self.__image_size = (24, 24)
        self.__image_position = (4, 2)

    @property
    def text_color(self):
        return self._text_color

    @text_color.setter
    def text_color(self, value):
        self._text_color = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @property
    def text_size(self):
        return self._text_size

    @text_size.setter
    def text_size(self, value):
        self._text_size = value

    @property
    def text_scale(self):
        return self._text_scale

    @text_scale.setter
    def text_scale(self, value):
        self._text_scale = value

    @property
    def hover_bg_color(self):
        return self._hover_bg_color

    @hover_bg_color.setter
    def hover_bg_color(self, value):
        self._hover_bg_color = value

    @property
    def select_bg_color(self):
        return self._select_bg_color

    @select_bg_color.setter
    def select_bg_color(self, value):
        self._select_bg_color = value

    def set_image_size(self, imgage_size):
        self.__image_size = imgage_size

    def set_image_position(self, image_position):
        self.__image_position = image_position

    def set_image(self, rel_filepath):
        try:
            self.__image = bpy.data.images.load(rel_filepath, check_existing=True)
            self.__image.gl_load()
        except Exception:
            pass

    def update(self, x, y):
        super().update(x, y)
        self._textpos = [x, y]

    def draw(self):
        if not self.visible:
            return

        area_height = self.get_area_height()

        self.shader.bind()

        self.set_colors()

        gpu.state.blend_set('ALPHA')

        self.batch_panel.draw(self.shader)

        self.draw_image()

        gpu.state.blend_set('NONE')

        # Draw text
        self.draw_text(area_height)

    def set_colors(self):
        color = self._bg_color
        # text_color = self._text_color ??

        # pressed
        if self.__state == 1:
            color = self._select_bg_color

        # hover
        elif self.__state == 2:
            color = self._hover_bg_color

        self.shader.uniform_float("color", color)

    def draw_text(self, area_height):
        p_font_size = self._text_size * self._text_scale
        if bpy.app.version < (3, 1, 0):
            p_font_size = round(p_font_size)
        blf.size(0, p_font_size, bpy.context.preferences.system.dpi)
        size = blf.dimensions(0, self._text)

        d_height = self._text_size * self._text_scale
        textpos_y = area_height - self._textpos[1] - (self.height + d_height) / 2.0
        blf.position(0, self._textpos[0] + (self.width - size[0]) / 2.0, textpos_y + 1, 0)

        r, g, b, a = self._text_color
        blf.color(0, r, g, b, a)

        blf.draw(0, self._text)

    def draw_image(self):
        if self.__image is not None:
            try:
                y_screen_flip = self.get_area_height() - self.y_screen

                off_x, off_y = self.__image_position
                sx, sy = self.__image_size

                # bottom left, top left, top right, bottom right
                vertices = (
                    (self.x_screen + off_x, y_screen_flip - off_y),
                    (self.x_screen + off_x, y_screen_flip - sy - off_y),
                    (self.x_screen + off_x + sx, y_screen_flip - sy - off_y),
                    (self.x_screen + off_x + sx, y_screen_flip - off_y))

                self.shader_img = gpu.shader.from_builtin('2D_IMAGE')
                self.batch_img = batch_for_shader(
                    self.shader_img, 'TRI_FAN',
                    {
                        "pos": vertices,
                        "texCoord": ((0, 1), (0, 0), (1, 0), (1, 1))
                    },)

                # send image to gpu if it isn't there already
                texture = gpu.texture.from_image(self.__image)

                self.shader_img.bind()
                self.shader_img.uniform_sampler("image", texture)
                self.batch_img.draw(self.shader_img)
                return True
            except Exception:
                pass

        return False

    def set_mouse_down(self, mouse_down_func):
        self.mouse_down_func = mouse_down_func

    def mouse_down(self, x, y):
        if self.is_in_rect(x, y):
            self.__state = 1
            try:
                self.mouse_down_func(self)
            except Exception as e:
                print(e)

            return True

        return False

    def mouse_move(self, x, y):
        if self.is_in_rect(x, y):
            if (self.__state != 1):

                # hover state
                self.__state = 2
        else:
            self.__state = 0

    def mouse_up(self, x, y):
        if self.is_in_rect(x, y):
            self.__state = 2
        else:
            self.__state = 0
