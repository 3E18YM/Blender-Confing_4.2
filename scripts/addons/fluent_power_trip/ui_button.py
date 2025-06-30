import bpy
import math

from .helpers import *
from .shapes import *
# from .operators import *
from .constants import *

def make_button(what):
    if what == ('FIRST_SOLIDIFY'):
        button = FLUENT_Ui_Button('FIRST_SOLIDIFY')
        button.set_text('')
        button.set_tool_tip('First solidify (S)')
        button.set_shape('CIRCLE')
        button.set_icon('first_solidify')
        button.set_action(what)
    elif what == ('FIRST_BEVEL'):
        button = FLUENT_Ui_Button('FIRST_BEVEL')
        button.set_text('')
        button.set_tool_tip('First bevel (B)')
        button.set_shape('CIRCLE')
        button.set_icon('first_bevel')
        button.set_action(what)
    elif what == ('SECOND_BEVEL'):
        button = FLUENT_Ui_Button('SECOND_BEVEL')
        button.set_text('')
        button.set_tool_tip('Second bevel')
        button.set_shape('CIRCLE')
        button.set_icon('second_bevel')
        button.set_action(what)
    elif what == ('TAPER'):
        button = FLUENT_Ui_Button('TAPER')
        button.set_text('')
        button.set_tool_tip('Taper')
        button.set_shape('CIRCLE')
        button.set_icon('taper')
        button.set_action(what)
    elif what == ('SECOND_SOLIDIFY'):
        button = FLUENT_Ui_Button('SECOND_SOLIDIFY')
        button.set_text('')
        button.set_tool_tip('Second solidify')
        button.set_shape('CIRCLE')
        button.set_icon('second_solidify')
        button.set_action(what)
    elif what == ('DIMENSIONS'):
        button = FLUENT_Ui_Button('DIMENSIONS')
        button.set_text('')
        button.set_tool_tip('Dimensions')
        button.set_shape('CIRCLE')
        button.set_icon('dimensions')
        button.set_action(what)
    elif what == ('ROTATION'):
        button = FLUENT_Ui_Button('ROTATION')
        button.set_text('')
        button.set_tool_tip('Rotation')
        button.set_shape('CIRCLE')
        button.set_icon('rotation')
        button.set_action(what)
    elif what == ('MIRROR'):
        button = FLUENT_Ui_Button('MIRROR')
        button.set_text('')
        button.set_tool_tip('Mirror (M)')
        button.set_shape('CIRCLE')
        button.set_icon('mirror')
        button.set_action(what)
    elif what == ('ARRAY'):
        button = FLUENT_Ui_Button('ARRAY')
        button.set_text('')
        button.set_tool_tip('Array (A)')
        button.set_shape('CIRCLE')
        button.set_icon('array')
        button.set_action(what)
    elif what == ('CIRCULAR_ARRAY'):
        button = FLUENT_Ui_Button('CIRCULAR_ARRAY')
        button.set_text('')
        button.set_tool_tip('Circular array')
        button.set_shape('CIRCLE')
        button.set_icon('circular_array')
        button.set_action(what)
    elif what == ('RESOLUTION'):
        button = FLUENT_Ui_Button('RESOLUTION')
        button.set_text('')
        button.set_tool_tip('Resolution')
        button.set_shape('CIRCLE')
        button.set_icon('resolution')
        button.set_action(what)
    elif what == ('INSET'):
        button = FLUENT_Ui_Button('INSET')
        button.set_text('')
        button.set_tool_tip('Inset thickness')
        button.set_shape('CIRCLE')
        button.set_icon('first_solidify')
        button.set_action('INSET_THICKNESS')
    elif what == ('RADIUS'):
        button = FLUENT_Ui_Button('RADIUS')
        button.set_text('')
        button.set_tool_tip('Radius')
        button.set_shape('CIRCLE')
        button.set_icon('radius')
        button.set_action(what)
    elif what == ('CURVE'):
        button = FLUENT_Ui_Button('CURVE')
        button.set_text('')
        button.set_tool_tip('Curve')
        button.set_shape('CIRCLE')
        button.set_icon('curve')
        button.set_action(what)
    elif what == ('OUTER_BEVEL'):
        button = FLUENT_Ui_Button('OUTER_BEVEL')
        button.set_text('OB')
        button.set_tool_tip('Outer bevel')
        button.set_shape('CIRCLE')
        # button.set_icon('curve')
        button.set_action(what)
    elif what == ('CANCEL'):
        button = FLUENT_Ui_Button('CANCEL')
        button.set_text('')
        button.set_tool_tip('Cancel (ESC)')
        button.set_shape('CIRCLE')
        button.set_icon('cancel')
        button.set_action('CANCELLED')
        # overlap = bpy.context.preferences.system.use_region_overlap
        t_panel_width = 0
        n_panel_width = 0
        # if overlap:
        for region in bpy.context.area.regions:
            if region.type == 'TOOLS':
                t_panel_width = region.width
            if region.type == 'UI':
                n_panel_width = region.width
        button_dimensions = button.get_dimensions()[0]
        button.set_position((bpy.context.area.width - n_panel_width - t_panel_width - button_dimensions, button_dimensions))
    elif what == ('VALIDATE'):
        button = FLUENT_Ui_Button('VALIDATE')
        button.set_text('')
        button.set_tool_tip('Validate')
        button.set_shape('CIRCLE')
        button.set_action('VALIDATE')
        button.set_icon('validate')
    elif what == ('QUIT'):
        button = FLUENT_Ui_Button('QUIT')
        button.set_text('')
        button.set_tool_tip('Valid and quit (RMB)')
        button.set_shape('CIRCLE')
        button.set_action('FINISHED')
        button.set_icon('quit')
    elif what == ('BACK'):
        button = FLUENT_Ui_Button('BACK')
        button.set_text('')
        button.set_tool_tip('Back')
        button.set_shape('CIRCLE')
        button.set_action('BACK_MENU')
        button.set_icon('back')
    return button

class FLUENT_Ui_Button():
    def __init__(self, name=None):
        self.position = (0, 0)
        self.align = 'CENTER'
        self.dimensions = [100, 100]
        self.margin = 12
        self.default_bg_color = (0.3, 0.3, 0.3, 1)
        self.hover_bg_color = get_addon_preferences().hightlight_text
        self.active_bg_color = (0.4, 0.4, 0.4, 1)
        self.show = True

        self.shape = 'RECTANGLE'

        self.id = name

        self.text = 'Button'
        self.text_size = get_addon_preferences().font_size
        self.text_color = (1.0, 1.0, 1.0, 1.0)
        self.text_position = []

        self.icon = None
        self.icon_size = [int(get_addon_preferences().icon_size), int(get_addon_preferences().icon_size)]

        self.state = 0 # 1→hover 2→press
        self.is_active = False

        self.action = None

        self.tool_tip_text = ''
        self.tool_tip_text_dimensions = 0
        self.display_tool_tip = False

        self.pie_parent = None

    def get_id(self):
        return self.id

    def set_pie_parent(self, a):
        self.pie_parent = a

    def get_pie_parent(self):
        return self.pie_parent

    def set_tool_tip(self, string):
        self.tool_tip_text = string
        blf.size(0, self.text_size, 72)
        self.tool_tip_text_dimensions = blf.dimensions(0, string)

    def get_tool_tip(self):
        return self.tool_tip_text

    def set_default_color(self, color):
        self.default_bg_color = color

    def set_icon(self, image_name):
        icons = load_icons()
        self.icon = icons[image_name]['texture']
        self.refresh_size()

    def set_show(self, bool):
        self.show = bool

    def refresh_size(self):
        if self.text == '' and self.icon:
            self.dimensions = [self.icon_size[0]+self.margin*2, self.icon_size[1]+self.margin*2]
        elif self.text and not self.icon:
            blf.size(0, self.text_size, 72)
            text_dimensions = blf.dimensions(0, self.text)
            self.dimensions = [text_dimensions[0]+self.margin*2, text_dimensions[1]+self.margin*2]
        elif not self.text and not self.icon:
            self.dimensions = [32, 32]

    def set_shape(self, shape):
        self.shape = shape
        if shape == 'CIRCLE':
            self.dimensions[1] = self.dimensions[0]

    def set_action(self, action):
        self.action = action

    def get_action(self):
        return self.action

    def set_text(self, text):
        self.text = text
        self.refresh_size()

    def get_text(self):
        return self.text

    def set_text_position(self, position):
        self.text_position = position

    def set_position(self, pos):
        self.position = pos

    def get_position(self):
        return self.position

    def set_colors(self):
        color = self.default_bg_color
        text_color = self.text_color

        # hover
        if self.state == 1:
            color = self.hover_bg_color

        # press, active
        elif self.state in [2,3] :
            color = self.active_bg_color

        if self.is_active:
            color = self.hover_bg_color

        return color

    def set_state(self, a):
        self.state = a

    def get_state(self):
        return self.state

    def set_active(self, a):
        self.is_active = a

    def get_active(self):
        return self.is_active

    def get_dimensions(self):
        return self.dimensions

    def draw(self, events):
        if self.show:
            self.is_hover(events)
            if self.shape == 'RECTANGLE':
                draw_rectangle(x = self.position[0], y = self.position[1], width = self.dimensions[0], height = self.dimensions[1], color = self.set_colors(), align = self.align)
            elif self.shape == 'CIRCLE':
                draw_circle_full(cx = self.position[0], cy = self.position[1], r = self.dimensions[0]/2, color = self.set_colors(), segments = 64)
                draw_circle(cx = self.position[0], cy = self.position[1], r = self.dimensions[0]/2, color = self.set_colors(), segments = 64)

            draw_text(text = self.text, text_pos = self.position, text_size = self.text_size, text_color = self.text_color, align = 'CENTER')

            # TODO draw image est à uplader
            if self.icon:
                draw_image(texture = self.icon, position = [self.position[0]-self.icon_size[0]/2, self.position[1]-self.icon_size[1]/2], size = self.icon_size)

            if self.display_tool_tip and self.tool_tip_text:
                if not self.text_position:
                    draw_text(text = self.tool_tip_text, text_pos = [self.position[0], self.position[1] + self.dimensions[1]/2 + self.tool_tip_text_dimensions[1]], text_size = self.text_size, text_color = self.text_color, align = 'CENTER')
                else:
                    # draw_rectangle(self.text_position[0], self.text_position[1], self.tool_tip_text_dimensions[0]+8, self.tool_tip_text_dimensions[1]+8, (0, 0, 0, 0.5))
                    draw_text(text=self.tool_tip_text, text_pos=[self.text_position[0], self.text_position[1]], text_size=self.text_size, text_color=self.text_color, align='CENTER')

    def is_hover(self, events):
        if self.show:
            x_min = self.position[0] - self.dimensions[0]/2
            x_max = self.position[0] + self.dimensions[0]/2
            y_min = self.position[1] - self.dimensions[1]/2
            y_max = self.position[1] + self.dimensions[1]/2

            if self.pie_parent:
                pie_center = self.pie_parent.get_pie_center()
                if pie_center == [0, 0]:
                    pie_center = [events['mouse_x'], events['mouse_y']]
                vec = Vector((events['mouse_x'] - pie_center[0], events['mouse_y'] - pie_center[1], 0))
                if vec.length > 32:
                    vec_2 = vec.normalized()
                    vec_2 = vec_2 * self.pie_parent.get_rayon_du_pie()
                    events['mouse_x'] = pie_center[0] + vec_2.x
                    events['mouse_y'] = pie_center[1] + vec_2.y
            if x_min < events['mouse_x'] < x_max and y_min < events['mouse_y'] < y_max:
                self.state = 1
                self.display_tool_tip = True
                if events['value'] == 'RELEASE' and events['type'] == 'LEFTMOUSE' or 'MENU' in self.action:
                    self.state = 2
            else:
                self.display_tool_tip = False
                self.state = 0
        else:
            self.state = 0

class FLUENT_Ui_Layout():
    def __init__(self, id, title='', subtitle=''):
        self.id = id
        self.title = title
        self.subtitle = subtitle
        self.title_dim = blf.dimensions(0, title)
        self.subtitle_dim = blf.dimensions(0, subtitle)
        self.layout = 'ROW'
        self.button_list = []
        self.position = ['BOTTOM', 'CENTER']
        self.margin = 16
        if int(get_addon_preferences().icon_size) == 32:
            self.rayon_du_pie = 150
        else:
            self.rayon_du_pie = 225
        self.nombre_de_partie_du_pie = 1
        self.decalage = 0
        self.pie_center = [0, 0]

        self.obj = None

    def set_pie_center(self, a):
        self.pie_center = a

    def get_pie_center(self):
        return self.pie_center

    def set_decalage(self, a):
        self.decalage = a

    def get_id(self):
        return self.id

    def add_item(self, item):
        if self.layout == 'PIE':
            item.set_pie_parent(self)
        self.button_list.append(item)

    def remove_item(self, item):
        for i, b in enumerate(self.button_list):
            if type(b) is FLUENT_Ui_Button and b.get_id() == item:
                self.button_list.pop(i)
                break

    def get_items(self):
        return [b for b in self.button_list if b != 'SEPARATOR']

    def set_obj(self, obj):
        self.obj = obj

    def get_obj(self):
        return self.obj

    def add_separator(self):
        self.button_list.append('SEPARATOR')

    def set_rayon_du_pie(self, rayon):
        self.rayon_du_pie = rayon

    def get_rayon_du_pie(self):
        return self.rayon_du_pie

    def set_layout(self, layout):
        self.layout = layout

    def get_layout(self):
        return self.layout

    def spread(self, mouse_x=0, mouse_y=0):
        if self.layout == 'ROW':
            largeur_total = 0
            for b in self.button_list:
                largeur_total+=b.get_dimensions()[0]
            largeur_total += self.margin*(len(self.button_list) - 1)
            t_panel_width = 0
            n_panel_width = 0
            # overlap = bpy.context.preferences.system.use_region_overlap
            # if overlap:
            for region in bpy.context.area.regions:
                if region.type == 'TOOLS':
                    t_panel_width = region.width
                if region.type == 'UI':
                    n_panel_width = region.width

            largeur_fenetre = bpy.context.area.width - t_panel_width - n_panel_width
            start_pos_x = (largeur_fenetre - largeur_total) / 2
            pos_x = start_pos_x
            for index,b in enumerate(self.button_list):
                if index == 0:
                    b.set_position([start_pos_x, b.get_dimensions()[1]])
                    pos_x += b.get_dimensions()[0] + self.margin
                else:
                    b.set_position([pos_x, b.get_dimensions()[1]])
                    pos_x += b.get_dimensions()[0] + self.margin
        if self.layout == 'COLUMN_LEFT':
            hauteur_total = 0
            for b in self.button_list:
                hauteur_total+=b.get_dimensions()[1]
            hauteur_total += self.margin*(len(self.button_list) - 1)

            overlap = bpy.context.preferences.system.use_region_overlap
            t_panel_width = 0
            n_panel_width = 0
            # if overlap:
            for region in bpy.context.area.regions:
                if region.type == 'TOOLS':
                    t_panel_width = region.width
                if region.type == 'UI':
                    n_panel_width = region.width

            largeur_fenetre = bpy.context.area.width - t_panel_width - n_panel_width
            hauteur_fenetre = bpy.context.area.height
            if overlap:
                decal = 0
            else:
                decal = 64
            pos_x = (largeur_fenetre - self.button_list[0].get_dimensions()[0] - decal)
            start_pos_y = (hauteur_fenetre + hauteur_total)/2
            pos_y = start_pos_y
            for index,b in enumerate(self.button_list):
                if index == 0:
                    b.set_position([pos_x, start_pos_y])
                    pos_y -= b.get_dimensions()[0] + self.margin
                else:
                    b.set_position([pos_x, pos_y])
                    pos_y -= b.get_dimensions()[0] + self.margin
        elif self.layout == 'PIE':
            nombre_de_boutton = len(self.button_list)
            if nombre_de_boutton:
                angle = math.radians(360/nombre_de_boutton)
            else:
                angle = 0
            for index, b in enumerate(self.button_list):
                try:
                    b.set_position([mouse_x + self.rayon_du_pie * math.cos(angle*index + self.decalage * angle), mouse_y + self.rayon_du_pie * math.sin(angle*index + self.decalage * angle)])
                    b.set_text_position([mouse_x, mouse_y])
                except:pass
            self.pie_center = [mouse_x, mouse_y]
        elif self.layout in ['MIRROR', 'TAPER'] and self.obj:
            if self.layout == 'MIRROR':
                try:
                    location_3d = self.obj.modifiers[fluent_modifiers_name['mirror']].mirror_object.location
                    matrix = self.obj.modifiers[fluent_modifiers_name['mirror']].mirror_object.matrix_world
                except:
                    location_3d = self.obj.location
                    matrix = self.obj.matrix_world
            elif self.layout == 'TAPER':
                location_3d = self.obj.location
                matrix = self.obj.matrix_world

            region = bpy.context.region
            rv3d = bpy.context.region_data

            location_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, location_3d)
            self.pie_center = [location_2d.x, location_2d.y]

            for index, b in enumerate(self.button_list):
                if 'VALIDATE' in b.get_action():
                    b.set_position([location_2d[0], location_2d[1]])

            x_length_x = x_length_y = y_length_x = y_length_y = z_length_x = z_length_y = radius = 0

            while max(x_length_x, x_length_y, y_length_x, y_length_y, z_length_x, z_length_y) < 300:
                radius += 0.05

                x = view3d_utils.location_3d_to_region_2d(region, rv3d, matrix @ mathutils.Vector((radius, 0, 0)))
                xx = view3d_utils.location_3d_to_region_2d(region, rv3d, matrix @ mathutils.Vector((-radius, 0, 0)))
                x_length_x = math.fabs(x.x-xx.x)
                x_length_y = math.fabs(x.y-xx.y)

                y = view3d_utils.location_3d_to_region_2d(region, rv3d, matrix @ mathutils.Vector((0, radius, 0)))
                yy = view3d_utils.location_3d_to_region_2d(region, rv3d, matrix @ mathutils.Vector((0, -radius, 0)))
                y_length_x = math.fabs(y.x-yy.x)
                y_length_y = math.fabs(y.y-yy.y)

                z = view3d_utils.location_3d_to_region_2d(region, rv3d, matrix @ mathutils.Vector((0, 0, radius)))
                zz = view3d_utils.location_3d_to_region_2d(region, rv3d, matrix @ mathutils.Vector((0, 0, -radius)))
                z_length_x = math.fabs(z.x-zz.x)
                z_length_y = math.fabs(z.y-zz.y)

            for index, b in enumerate(self.button_list):
                if '+X' in b.get_action():
                    b.set_position(x)
                elif '-X' in b.get_action():
                    b.set_position(xx)
                elif '+Y' in b.get_action():
                    b.set_position(y)
                elif '-Y' in b.get_action():
                    b.set_position(yy)
                elif '+Z' in b.get_action():
                    b.set_position(z)
                elif '-Z' in b.get_action():
                    b.set_position(zz)

    def draw(self, events):
        if self.layout == 'PIE' and events['mouse_left_click'] and not (bpy.context.active_object and bpy.context.active_object.mode == 'EDIT'):
            vec = Vector((events['mouse_x'] - self.pie_center[0], events['mouse_y'] - self.pie_center[1], 0))
            # if vec.length > self.rayon_du_pie:
            #     vec_2 = vec.normalized()
            #     vec_2 = vec_2 * self.rayon_du_pie
            #     events['mouse_x'] = self.pie_center[0] + vec_2.x
            #     events['mouse_y'] = self.pie_center[1] + vec_2.y
            # vec *= self.rayon_du_pie * 0.1
            coords = [
            (self.pie_center[0] + vec.x, self.pie_center[1]+ vec.y),
            (self.pie_center[0] + vec.x*0.5, self.pie_center[1]+ vec.y*0.5)
            ]
            draw_circle_full(self.pie_center[0], self.pie_center[1], self.rayon_du_pie, (.5, .5, .5, .66), segments=64)
            draw_circle(self.pie_center[0], self.pie_center[1], self.rayon_du_pie, (1, 1, 1, 1), segments=64)
            draw_line(coords=coords, thickness=2, color = (1, 1, 1, .5), is_2d=True)
            # draw_circle_full(self.pie_center[0], self.pie_center[1], 4, (1, 1, 1, .5), segments=32)
            if self.title and not self.subtitle:
                draw_text(text=self.title, text_pos=(self.pie_center[0], self.pie_center[1]), text_size=16, text_color=(1, 1, 1, 1), align='CENTER')
            if self.subtitle and not self.title:
                draw_text(text=self.subtitle, text_pos=(self.pie_center[0], self.pie_center[1]), text_size=16, text_color=(1, 1, 1, 1), align='CENTER')
            if self.subtitle and self.title:
                draw_text(text=self.title, text_pos=(self.pie_center[0], self.pie_center[1]+self.title_dim[1]*2), text_size=16, text_color=(1, 1, 1, 0.5), align='CENTER')
                draw_text(text=self.subtitle, text_pos=(self.pie_center[0], self.pie_center[1]-self.subtitle_dim[1]*2), text_size=16, text_color=(1, 1, 1, 0.5), align='CENTER')
        elif self.layout in ['MIRROR', 'TAPER'] and self.obj:
            self.spread()
            if self.layout == 'MIRROR':
                try:
                    location_3d = self.obj.modifiers[fluent_modifiers_name['mirror']].mirror_object.location
                except:
                    location_3d = self.obj.location
            elif self.layout == 'TAPER':
                location_3d = self.obj.location
            region = bpy.context.region
            rv3d = bpy.context.region_data
            location_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, location_3d)
            for b in self.button_list:
                coords = [
                    location_2d,
                    (b.get_position()[0], b.get_position()[1])
                ]
                if 'X' in b.get_action():
                    color = (.9, 0, 0, 1)
                elif 'Y' in b.get_action():
                    color = (0, .9, 0, 1)
                elif 'Z' in b.get_action():
                    color = (0, 0, .9, 1)
                else:
                    color = (1, 1, 1, 1)
                draw_line(coords = coords, thickness = 2, color = color, is_2d = True)

        if self.layout in ['MIRROR', 'TAPER'] and self.obj or self.layout not in ['MIRROR', 'TAPER'] and not self.obj:
            for b in self.button_list:
                if b != 'SEPARATOR':
                    b.draw(events)