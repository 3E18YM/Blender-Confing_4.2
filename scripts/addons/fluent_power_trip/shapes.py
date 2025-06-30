import bpy
import blf
import math
import bmesh
import os
from os.path import join, dirname, realpath
import gpu
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils
from mathutils import Vector
from .helpers import *

def drawing_tris(vertices, indices, color):
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.uniform_float("color", color)
    gpu.state.blend_set('ALPHA')
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
    batch.draw(shader)
    gpu.state.blend_set('NONE')

def draw_rectangle(x, y, width, height, color, align = 'CENTER'):
    if align == 'LEFT':
        l = x + width
        h = y - height
        vertices = ((x, y), (l, y), (l, h), (x, h))
    elif align == 'CENTER':
        vertices = ((x-width/2, y+height/2), (x+width/2, y+height/2), (x+width/2, y-height/2), (x-width/2, y-height/2))
    indices = ((0, 1, 2),(0, 2, 3))
    drawing_tris(vertices, indices, color)

def draw_circle(cx, cy, r, color, segments, thickness = 1):
    theta = 2*math.pi/segments
    coords = [(cx+r, cy)]
    for i in range(segments):
        coords.append((math.cos(i*theta)*r+cx , math.sin(i*theta)*r+cy))
        coords.append((math.cos(i*theta)*r+cx , math.sin(i*theta)*r+cy))
    coords.append((cx+r, cy))
    draw_line(coords, 1, color, True)

def draw_circle_full(cx, cy, r, color, segments = 16):
    theta = 2*math.pi/segments
    coords = [(cx,cy)]
    for i in range(segments):
        coords.append((math.cos(i*theta)*r+cx , math.sin(i*theta)*r+cy))
    indices = []
    for i in range(segments-1):
        indices.append((0, i+1, i+2))
    indices.append((0, segments, 1))
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    shader.uniform_float("color", color)
    gpu.state.blend_set('ALPHA')
    batch = batch_for_shader(shader, 'TRIS', {"pos": coords}, indices=indices)
    batch.draw(shader)
    gpu.state.blend_set('NONE')

def draw_line(coords = None, thickness = 1, color = (1, 1, 1, 1), is_2d = False):
    region = bpy.context.region
    rv3d = bpy.context.region_data
    if not is_2d:
        coords_2d = []
        for c in coords:
            coords_2d.append(view3d_utils.location_3d_to_region_2d(region, rv3d, c))
    else:
        coords_2d = coords
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    shader.uniform_float("color", color)
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(thickness)
    try:
        batch = batch_for_shader(shader, 'LINES', {"pos": coords_2d})
    except:
        print('LINE ERROR', coords_2d)
    # try:
    #     import bgl
    #     bgl.glEnable(bgl.GL_BLEND)
    #     bgl.glEnable(bgl.GL_LINE_SMOOTH)
    # except:
    #     pass
    batch.draw(shader)
    gpu.state.blend_set('NONE')
    gpu.state.line_width_set(1)

def draw_text(text = '', text_pos = (0,0), text_size = 16, text_color = (1, 1, 1, 1), align = 'CENTER'):
    blf.size(0, text_size, 72)
    text_dimensions = blf.dimensions(0, text)

    if align == 'CENTER':
        text_pos_x = text_pos[0] - text_dimensions[0] / 2
        text_pos_y = text_pos[1] - text_dimensions[1] / 2
    elif align == 'LEFT':
        text_pos_x = text_pos[0]
        text_pos_y = text_pos[1] + text_dimensions[1] / 2
    elif align == 'RIGHT':
        text_pos_x = text_pos[0] - text_dimensions[0]
        text_pos_y = text_pos[1] + text_dimensions[1] / 2
    blf.position(0, text_pos_x, text_pos_y, 0)

    r, g, b, a = text_color
    blf.color(0, r, g, b, a)

    blf.draw(0, text)

def load_image(image_path):
    my_image = bpy.data.images.load(join(dirname(realpath(__file__)))+'\\'+image_path, check_existing = True)
    my_image.gl_load()
    return my_image

def draw_image(texture, position = [0, 32], size = [32, 32]):
    vertices = (
    (position[0], position[1] + size[1]),
    (position[0], position[1]),
    (position[0] + size[0], position[1]),
    (position[0] + size[0], position[1] + size[1])
    )
    shader = gpu.shader.from_builtin('2D_IMAGE')
    gpu.state.blend_set('ALPHA')
    batch_img = batch_for_shader(shader, 'TRI_FAN', {"pos": vertices, "texCoord": ((0, 1), (0, 0), (1, 0), (1, 1))})
    shader.bind()
    shader.uniform_sampler("image", texture)
    batch_img.draw(shader)
    gpu.state.blend_set('NONE')

def prepare_draw_shape(obj):
    region = bpy.context.region
    rv3d = bpy.context.region_data
    data = obj.data
    if len(data.vertices)<3:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        data = obj_eval.data
    bm = bmesh.new()
    bm.from_mesh(data)
    coords = [(view3d_utils.location_3d_to_region_2d(region, rv3d, obj.matrix_world @ v.co)) for v in bm.verts]
    indices = [[loop.vert.index for loop in looptris] for looptris in bm.calc_loop_triangles()]
    bm.free()
    return [coords, indices]

def draw_edges(obj = None, thickness = 1, color = (1, 1, 1, 1)):
    data = obj.data
    if len(data.vertices)<3:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        data = obj_eval.data
    bm = bmesh.new()
    bm.from_mesh(data)
    coords = []
    for e in bm.edges:
        v = e.verts[0].co
        vv = e.verts[1].co
        global_coord = obj.matrix_world @ v
        global_coord_ = obj.matrix_world @ vv
        coords.append((global_coord.x, global_coord.y, global_coord.z))
        coords.append((global_coord_.x, global_coord_.y, global_coord_.z))
    draw_line(coords, thickness, color, False)

def draw_all_circle_full(center_coord_list, r, color, segments):
    gpu.state.blend_set('ALPHA')
    theta = 2*math.pi/segments
    vertices = []
    indices = []
    center = 0
    for c in center_coord_list:
        cx = c[0]
        cy = c[1]
        vertices.append((cx,cy))
        for i in range(segments):
            vertices.append((math.cos(i*theta)*r+cx , math.sin(i*theta)*r+cy))
        for i in range(segments-1):
            indices.append((center, center+i+1, center+i+2))
        indices.append((center, center+segments, center+1))
        center += segments + 1

    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
    # shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
    gpu.state.blend_set('NONE')

class FLUENT_Draw_Object():

    def __init__(self, obj, color = (0.0, 0.643, 1, 0.05)):
        self.obj = obj
        self.depsgraph = bpy.context.evaluated_depsgraph_get()
        self.obj_evaluated = self.obj.evaluated_get(self.depsgraph)
        self.drawing_data = prepare_draw_shape(self.obj_evaluated)
        self.face_color = (color[0], color[1], color[2], color[3])

    def set_object(self, obj):
        self.obj = obj
        self.refresh_data()

    def get_object(self):
        return self.obj

    def refresh_data(self):
        self.obj_evaluated = self.obj.evaluated_get(self.depsgraph)
        self.drawing_data = prepare_draw_shape(self.obj_evaluated)

    def draw(self, events):
        if not self.obj.hide_viewport:
            self.refresh_data()
            drawing_tris(self.drawing_data[0], self.drawing_data[1], self.face_color)
            draw_edges(self.obj_evaluated, 1, (1, 1, 1, .75))

class FLUENT_Cursor_Infos():
    def __init__(self):
        self.text = [] #chaque élément du tableau est une ligne.
        self.text_size = get_addon_preferences().font_size
        self.text_dimensions = [0, 0]

    def set_text(self, text):
        self.text = text # text doit être un tableau
        blf.size(0, self.text_size, 72)
        try:
            self.text_dimensions = blf.dimensions(0, text[0])
        except:
            pass

    def draw(self, events):
        for index, t in enumerate(self.text):
            draw_text(text = t, text_pos = (events['mouse_x'] + 32, events['mouse_y'] - self.text_dimensions[1] - (index * self.text_dimensions[1] * 2)), text_size = self.text_size, text_color = (1, 1, 1, 1), align = 'LEFT')

class FLUENT_Draw_Dots():
    def __init__(self):
        self.dots = [] #pour chaque point un tableau [pos_x, pos_y, rayon, color]

    def set_dots(self, a):
        self.dots = a

    def get_dots(self):
        return self.dots

    def append_a_dot(self, tab):
        self.dots.append(tab)

    def is_hover(self, events):
        pass

    def get_state(self):
        pass

    def draw(self, events):
        for d in self.dots:
            draw_circle_full(d[0], d[1], d[2], d[3], segments = 8)

class FLUENT_Draw_Lines():
    def __init__(self):
        self.lines = [] #pour chaque point un tableau [coords, thickness, color, is_2d]

    def set_lines(self, a):
        self.lines = a

    def get_lines(self):
        return self.lines

    def append_a_line(self, tab):
        self.lines.append(tab)

    def is_hover(self, events):
        pass

    def get_state(self):
        pass

    def draw(self, events):
        for d in self.lines:
            draw_line(coords = d[0], thickness = d[1], color = d[2], is_2d = d[3])

class FLUENT_Panel_Infos():
        def __init__(self):
            self.text = [[],[]]
            self.text_size = get_addon_preferences().font_size
            self.text_dimensions = [0, 0]
            self.cell_dimensions = [0,0]
            self.origine = [16, 128]

        def reset(self):
            self.text = [[],[]]

        def add_line(self, t1, t2 = '', reset = False):
            if reset:
                self.text = [[],[]]
            self.text[0].append(t1)
            self.text[1].append(t2)
            blf.size(0, self.text_size, 72)
            for i in self.text[0]:
                dim = blf.dimensions(0, i)
                if dim[0] > self.cell_dimensions[0]:
                    self.cell_dimensions[0] = dim[0]
                if dim[1] > self.cell_dimensions[1]:
                    self.cell_dimensions[1] = dim[1]

        def draw(self, events):
            for i, t in enumerate(self.text[0]):
                # première colonne
                pos_x = self.origine[0]
                pos_y = i * (self.cell_dimensions[1]*1.5) + self.origine[1]
                draw_text(text = self.text[0][-i-1], text_pos = (pos_x, pos_y), text_size = self.text_size, text_color = (1, 1, 1, 1), align = 'LEFT')
                # deuxième colonne
                pos_x = self.origine[0] + self.cell_dimensions[0] * 1.1
                draw_text(text = self.text[1][-i-1], text_pos = (pos_x, pos_y), text_size = self.text_size, text_color = get_addon_preferences().hightlight_text, align = 'LEFT')

class GlImageFromPreview:

    __slots__ = ('_bo', 'preview')

    def __init__(self, preview):
        self._bo = None
        self.preview = preview

    def gl_load(self):
        _p = self.preview
        _bo = bgl.Buffer(bgl.GL_INT, [1])
        _pix = _p.image_pixels_float[:]
        w, h = _p.image_size
        buf = bgl.Buffer(bgl.GL_FLOAT, len(_pix), _pix)
        bgl.glGenTextures(2, _bo)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, _bo[-1])
        bgl.glTexImage2D(bgl.GL_TEXTURE_2D, 0, bgl.GL_RGBA, w, h, 0, bgl.GL_RGBA, bgl.GL_FLOAT, buf)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)
        self._bo = _bo

    def gl_free(self):
        if self._bo is not None:
            bgl.glDeleteTextures(2, self._bo)
        self._bo = None

    @property
    def bindcode(self):
        if self._bo is None:
            return 0
        return self._bo[-1]
