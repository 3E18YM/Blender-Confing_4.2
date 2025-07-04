import os

import blf
import bpy
import gpu

from .. import image_utils, ui_bgl
from .bl_ui_widget import BL_UI_Widget


class BL_UI_Button(BL_UI_Widget):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._text_color = (1.0, 1.0, 1.0, 1.0)
        self._hover_bg_color = (0.5, 0.5, 0.5, 1.0)
        self._select_bg_color = (0.7, 0.7, 0.7, 1.0)

        self._text = "Button"
        self._text_size = 16
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
        if value != self._text_color:
            bpy.context.region.tag_redraw()
        self._text_color = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if value != self._text:
            bpy.context.region.tag_redraw()
        self._text = value

    @property
    def text_size(self):
        return self._text_size

    @text_size.setter
    def text_size(self, value):
        if value != self._text_size:
            bpy.context.region.tag_redraw()
        self._text_size = value

    @property
    def hover_bg_color(self):
        return self._hover_bg_color

    @hover_bg_color.setter
    def hover_bg_color(self, value):
        if value != self._hover_bg_color:
            bpy.context.region.tag_redraw()
        self._hover_bg_color = value

    @property
    def select_bg_color(self):
        return self._select_bg_color

    @select_bg_color.setter
    def select_bg_color(self, value):
        if value != self._select_bg_color:
            bpy.context.region.tag_redraw()
        self._select_bg_color = value

    def set_image_size(self, image_size):
        self.__image_size = image_size

    def set_image_position(self, image_position):
        self.__image_position = image_position

    def check_image_exists(self):
        # it's possible image was removed and doesn't exist.
        try:
            self.__image
            self.__image.filepath
            # self.__image.pixels
        except Exception as e:
            self.__image = None

    def set_image_colorspace(self, colorspace):
        image_utils.set_colorspace(self.__image, colorspace)

    def set_image(self, rel_filepath):
        # first try to access the image, for cases where it can get removed
        self.check_image_exists()
        try:
            if self.__image is None or self.__image.filepath != rel_filepath:
                imgname = f".{os.path.basename(rel_filepath)}"
                img = bpy.data.images.get(imgname)
                if img is not None:
                    self.__image = img
                else:
                    self.__image = bpy.data.images.load(
                        rel_filepath, check_existing=True
                    )
                    self.__image.name = imgname

                self.__image.gl_load()

            if self.__image and len(self.__image.pixels) == 0:
                self.__image.reload()
                self.__image.gl_load()
        except Exception as e:
            print(f"BL_UI_BUTTON set_image() error: {e}")
            self.__image = None

    def get_image_path(self):
        self.check_image_exists()
        if self.__image is None:
            return None
        return self.__image.filepath

    def update(self, x, y):
        super().update(x, y)
        self._textpos = [x, y]

    def draw(self):
        if not self._is_visible:
            return
        area_height = self.get_area_height()

        gpu.state.blend_set("ALPHA")

        self.shader.bind()

        self.set_colors()

        self.batch_panel.draw(self.shader)

        self.draw_image()

        # Draw text
        self.draw_text(area_height)

    def set_colors(self):
        color = self._bg_color

        # pressed
        if self.__state == 1:
            color = self._select_bg_color

        # hover
        elif self.__state == 2:
            color = self._hover_bg_color

        self.shader.uniform_float("color", color)

    def draw_text(self, area_height):
        font_id = 1
        if bpy.app.version < (3, 1, 0):
            # Blender 3.0 requires size:int https://docs.blender.org/api/3.0/blf.html#blf.size
            # but assetBar's search tab text is float - needs conversion in here
            blf.size(font_id, int(self._text_size), 72)
        elif bpy.app.version < (4, 0, 0):
            blf.size(font_id, self._text_size, 72)
        else:
            blf.size(font_id, self._text_size)

        size = blf.dimensions(font_id, self._text)

        textpos_y = area_height - self._textpos[1] - (self.height + size[1]) / 2.0
        blf.position(
            font_id, self._textpos[0] + (self.width - size[0]) / 2.0, textpos_y + 1, 0
        )

        r, g, b, a = self._text_color
        blf.color(font_id, r, g, b, a)

        blf.draw(font_id, self._text)

    def draw_image(self):
        if self.__image is not None:
            y_screen_flip = self.get_area_height() - self.y_screen
            off_x, off_y = self.__image_position
            sx, sy = self.__image_size
            ui_bgl.draw_image(
                self.x_screen + off_x,
                y_screen_flip - off_y - sy,
                sx,
                sy,
                self.__image,
                1.0,
                crop=(0, 0, 1, 1),
                batch=None,
            )
            return True
        return False

    def set_mouse_down(self, mouse_down_func):
        self.mouse_down_func = mouse_down_func

    def mouse_down(self, x, y):
        if self.is_in_rect(x, y):
            self.__state = 1
            try:
                self.mouse_down_func(self)
            except Exception as e:
                import traceback

                traceback.print_exc()

            return True

        return False

    def mouse_move(self, x, y):
        if self.is_in_rect(x, y):
            if self.__state != 1:
                # hover state
                self.__state = 2
        else:
            self.__state = 0

    def mouse_up(self, x, y):
        if self.is_in_rect(x, y):
            self.__state = 2
        else:
            self.__state = 0
