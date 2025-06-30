import bpy
from bpy.types import Operator
from ..independant_helpers import *
from ..helpers import *
from ..viewport_drawing import *
from ..shapes import *
from ..ui_button import *
import time
import math
from bpy.props import StringProperty


def wire_ui():
    pie_menu = FLUENT_Ui_Layout('WIRE',title='Pipe menu', subtitle='Hold shift to lock')
    pie_menu.set_layout('PIE')

    button = make_button('QUIT')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_tool_tip('Radius')
    button.set_text('')
    button.set_shape('CIRCLE')
    button.set_icon('radius')
    button.set_action('RADIUS')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_tool_tip('Bevel')
    button.set_text('')
    button.set_shape('CIRCLE')
    button.set_icon('first_bevel')
    button.set_action('PIPE_BEVEL')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Root strength')
    button.set_shape('CIRCLE')
    button.set_icon('stiffness')
    button.set_action('STIFFNESS')
    pie_menu.add_item(button)
    #
    # button = FLUENT_Ui_Button()
    # button.set_text('')
    # button.set_icon('t1')
    # button.set_tool_tip('Twist 01')
    # button.set_shape('CIRCLE')
    # button.set_action('TILT_01')
    # pie_menu.add_item(button)
    #
    # button = FLUENT_Ui_Button()
    # button.set_text('')
    # button.set_icon('t2')
    # button.set_tool_tip('Twist 02')
    # button.set_shape('CIRCLE')
    # button.set_action('TILT_02')
    # pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Array')
    button.set_icon('array')
    button.set_shape('CIRCLE')
    button.set_action('ARRAY_MENU')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Extra')
    button.set_icon('extra')
    button.set_shape('CIRCLE')
    button.set_action('EXTRA_MENU')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Utilities')
    button.set_icon('tool')
    button.set_shape('CIRCLE')
    button.set_action('UTILITIES_MENU')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Path')
    button.set_shape('CIRCLE')
    button.set_icon('path')
    button.set_action('PATH')
    pie_menu.add_item(button)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def wire_ring_ui():
    pie_menu = FLUENT_Ui_Layout('WIRE_RING_MENU',title='Ring menu', subtitle='Hold shift to lock')
    pie_menu.set_layout('PIE')

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Add')
    button.set_icon('creation')
    button.set_shape('CIRCLE')
    button.set_action('ADD_RING')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Pick')
    button.set_icon('pick')
    button.set_shape('CIRCLE')
    button.set_action('RING_PICK')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Radius')
    button.set_icon('radius')
    button.set_shape('CIRCLE')
    button.set_action('RING_RADIUS')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Move')
    button.set_icon('move')
    button.set_shape('CIRCLE')
    button.set_action('RING_MOVE')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Length')
    button.set_icon('thickness')
    button.set_shape('CIRCLE')
    button.set_action('RING_LENGTH')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Scale')
    button.set_icon('scale')
    button.set_shape('CIRCLE')
    button.set_action('RING_SCALE')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Thickness')
    button.set_icon('first_solidify')
    button.set_shape('CIRCLE')
    button.set_action('RING_THICKNESS')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Bevel')
    button.set_icon('first_bevel')
    button.set_shape('CIRCLE')
    button.set_action('RING_BEVEL')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Array')
    button.set_icon('array')
    button.set_shape('CIRCLE')
    button.set_action('RING_ARRAY_COUNT')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('LR')
    button.set_tool_tip('Length Resolution')
    button.set_shape('CIRCLE')
    button.set_action('RING_L_RESOLUTION')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_icon('resolution')
    button.set_tool_tip('Circle resolution')
    button.set_shape('CIRCLE')
    button.set_action('RING_C_RESOLUTION')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Remove')
    button.set_icon('remove')
    button.set_shape('CIRCLE')
    button.set_action('RING_REMOVE')
    pie_menu.add_item(button)

    button = make_button('BACK')
    pie_menu.add_item(button)

    pie_menu.set_decalage(1)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def wire_array_ui():
    pie_menu = FLUENT_Ui_Layout('ARRAY_MENU',title='Array menu', subtitle='Hold shift to lock')
    pie_menu.set_layout('PIE')

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Radius')
    button.set_icon('radius')
    button.set_shape('CIRCLE')
    button.set_action('RADIUS')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('Count')
    button.set_shape('RECTANGLE')
    button.set_action('ARRAY_COUNT')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('Gap')
    button.set_shape('RECTANGLE')
    button.set_action('ARRAY_GAP')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Linear')
    button.set_icon('array')
    button.set_shape('CIRCLE')
    button.set_action('ARRAY_LINEAR')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Circular')
    button.set_icon('circular_array')
    button.set_shape('CIRCLE')
    button.set_action('ARRAY_CIRCULAR')
    pie_menu.add_item(button)

    button = make_button('BACK')
    pie_menu.add_item(button)

    pie_menu.set_decalage(1)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def wire_extra_ui():
    pie_menu = FLUENT_Ui_Layout('EXTRA_MENU',title='Extra menu', subtitle='Hold shift to lock')
    pie_menu.set_layout('PIE')

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Coil')
    button.set_shape('CIRCLE')
    button.set_icon('coil')
    button.set_action('COIL_MENU')
    pie_menu.add_item(button)

    # button = FLUENT_Ui_Button()
    # button.set_text('')
    # button.set_tool_tip('Protection')
    # button.set_shape('CIRCLE')
    # button.set_icon('protection')
    # button.set_action('PROTECTION_MENU')
    # pie_menu.add_item(button)

    # button = FLUENT_Ui_Button()
    # button.set_text('')
    # button.set_tool_tip('Duct')
    # button.set_icon('duct')
    # button.set_shape('CIRCLE')
    # button.set_action('DUCT_MENU')
    # pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Ring')
    button.set_shape('CIRCLE')
    button.set_icon('ring')
    button.set_action('WIRE_RING_MENU')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_icon('connector')
    button.set_tool_tip('Connector')
    button.set_shape('CIRCLE')
    button.set_action('CONNECTOR_MENU')
    pie_menu.add_item(button)

    button = make_button('BACK')
    pie_menu.add_item(button)

    pie_menu.set_decalage(1)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def wire_coil_ui():
    pie_menu = FLUENT_Ui_Layout('COIL_MENU',title='Coil menu', subtitle='Hold shift to lock')
    pie_menu.set_layout('PIE')

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Add/Remove')
    button.set_icon('on_off')
    button.set_shape('CIRCLE')
    button.set_action('COIL_ADD')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Radius')
    button.set_icon('radius')
    button.set_shape('CIRCLE')
    button.set_action('COIL_RADIUS')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Resolution')
    button.set_icon('resolution')
    button.set_shape('CIRCLE')
    button.set_action('COIL_SPIRAL_RESOLUTION')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('ROT')
    button.set_tool_tip('Rotations count')
    button.set_shape('CIRCLE')
    button.set_action('COIL_ROTATIONS')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Root strength')
    button.set_shape('CIRCLE')
    button.set_icon('stiffness')
    button.set_action('STIFFNESS')
    pie_menu.add_item(button)

    button = make_button('BACK')
    pie_menu.add_item(button)

    pie_menu.set_decalage(1)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def wire_protection_ui():
    pie_menu = FLUENT_Ui_Layout('PROTECTION_MENU',title='Protection menu', subtitle='Hold shift to lock')
    pie_menu.set_layout('PIE')

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Add/Remove')
    button.set_icon('on_off')
    button.set_shape('CIRCLE')
    button.set_action('PROTECTION_ADD')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Spiral radius')
    button.set_icon('radius')
    button.set_shape('CIRCLE')
    button.set_action('PROTECTION_SPIRAL_RADIUS')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Height')
    button.set_icon('height')
    button.set_shape('CIRCLE')
    button.set_action('PROTECTION_HEIGHT')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('ROT')
    button.set_tool_tip('Rotations count')
    button.set_shape('CIRCLE')
    button.set_action('PROTECTION_ROTATIONS')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Thickness')
    button.set_icon('first_solidify')
    button.set_shape('CIRCLE')
    button.set_action('PROTECTION_THICKNESS')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Resolution')
    button.set_icon('resolution')
    button.set_shape('CIRCLE')
    button.set_action('PROTECTION_RESOLUTION')
    pie_menu.add_item(button)

    button = make_button('BACK')
    pie_menu.add_item(button)

    pie_menu.set_decalage(1)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def wire_duct_ui():
    pie_menu = FLUENT_Ui_Layout('DUCT_MENU',title='Duct menu', subtitle='Hold shift to lock')
    pie_menu.set_layout('PIE')

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Add/Remove')
    button.set_icon('on_off')
    button.set_shape('CIRCLE')
    button.set_action('DUCT_ADD')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Radius')
    button.set_icon('radius')
    button.set_shape('CIRCLE')
    button.set_action('DUCT_RADIUS')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('RAT')
    button.set_tool_tip('Ratio')
    button.set_shape('CIRCLE')
    button.set_action('DUCT_RATIO')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Root strength')
    button.set_shape('CIRCLE')
    button.set_icon('stiffness')
    button.set_action('STIFFNESS')
    pie_menu.add_item(button)

    button = make_button('BACK')
    pie_menu.add_item(button)

    pie_menu.set_decalage(1)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def wire_utilities_ui():
    pie_menu = FLUENT_Ui_Layout('UTILITIES_MENU',title='Utilities menu', subtitle='Hold shift to lock')
    pie_menu.set_layout('PIE')

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Circle resolution')
    button.set_shape('CIRCLE')
    button.set_icon('resolution')
    button.set_action('CIRCLE_RESOLUTION')
    pie_menu.add_item(button)

    # button = FLUENT_Ui_Button()
    # button.set_text('')
    # button.set_tool_tip('Curve resolution')
    # button.set_shape('CIRCLE')
    # button.set_icon('curve_resolution')
    # button.set_action('CURVE_RESOLUTION')
    # pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Reuse')
    button.set_icon('reuse')
    button.set_shape('CIRCLE')
    button.set_action('REUSE')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Reset')
    button.set_icon('reset')
    button.set_shape('CIRCLE')
    button.set_action('RESET')
    pie_menu.add_item(button)

    button = make_button('BACK')
    pie_menu.add_item(button)
    pie_menu.set_decalage(1)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def wire_connector_ui():
    pie_menu = FLUENT_Ui_Layout('CONNECTOR_MENU', title='Connector menu', subtitle='Hold shift to lock')
    pie_menu.set_layout('PIE')

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_icon('pick')
    button.set_tool_tip('Pick')
    button.set_shape('CIRCLE')
    button.set_action('CONNECTOR_PICK')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_icon('remove')
    button.set_tool_tip('Remove')
    button.set_shape('CIRCLE')
    button.set_action('CONNECTOR_REMOVE')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_icon('scale')
    button.set_tool_tip('Scale')
    button.set_shape('CIRCLE')
    button.set_action('CONNECTOR_SCALE')
    pie_menu.add_item(button)

    button = make_button('BACK')
    pie_menu.add_item(button)

    pie_menu.set_decalage(1)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def only_validate_menu():
    pie_menu = FLUENT_Ui_Layout('WIRE_RING')
    pie_menu.set_layout('PIE')

    button = make_button('VALIDATE')
    pie_menu.add_item(button)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


class FLUENT_OT_Pipe(Operator):
    """Put a pie"""
    bl_idname = "fluent.pipe"
    bl_label = "Fluent pipe"
    bl_options = {'REGISTER', 'UNDO'}

    operation: StringProperty(
        default='ADD'
    )

    def number_adjustment(self, the_modifier, input, increment, event, type):
        if self.previous_value == None:
            self.previous_value = the_modifier[input]
            self.slider_origin = event.mouse_region_x
            self.pie_menu_history.append(only_validate_menu())
        self.enter_value = enter_value(self.enter_value, self.events)
        if self.events['shift_work']:
            increment = increment*10
        elif self.events['ctrl_work']:
            increment = increment/10
        else:
            increment = increment
        if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or self.events[
            'ctrl_release']:
            self.slider_origin = event.mouse_region_x
            self.previous_value = the_modifier[input]

        value = self.previous_value + ((event.mouse_region_x - self.slider_origin) / increment)
        if enter_value_validation(self.enter_value, event)[0]:
            value = enter_value_validation(self.enter_value, event)[1]
            self.end_of_adjustment()
        if type == 'FLOAT':
            the_modifier[input] = value
        elif type == 'INT':
            the_modifier[input] = int(value)


        the_modifier.show_viewport = False
        the_modifier.show_viewport = True

    def load_geometry_node(self):
        # charge la node
        if not bpy.data.node_groups.get('fluent_pipe'):
            file_path_node_tree = os.path.dirname(realpath(__file__)) + "/wire/wire.blend/NodeTree"
            bpy.ops.wm.append(filename='fluent_pipe', directory=file_path_node_tree)
        # ajoute geometry nodes
        geo_nodes = self.fluent_curve['curve_obj'].modifiers.new(name='.f_geometry_nodes', type='NODES')
        geo_nodes.node_group = bpy.data.node_groups['fluent_pipe']

    def make_pipe(self):

        try:
            x_i = self.fluent_curve['first_point']['hit'].x
            y_i = self.fluent_curve['first_point']['hit'].y
            z_i = self.fluent_curve['first_point']['hit'].z
        except:
            x_i = self.fluent_curve['first_point']['hit'][0]
            y_i = self.fluent_curve['first_point']['hit'][1]
            z_i = self.fluent_curve['first_point']['hit'][2]
        start = Vector((x_i, y_i, z_i))

        try:
            x_f = self.fluent_curve['second_point']['hit'].x
            y_f = self.fluent_curve['second_point']['hit'].y
            z_f = self.fluent_curve['second_point']['hit'].z
        except:
            x_f = self.fluent_curve['second_point']['hit'][0]
            y_f = self.fluent_curve['second_point']['hit'][1]
            z_f = self.fluent_curve['second_point']['hit'][2]
        end = Vector((x_f, y_f, z_f))

        root_length = self.fluent_curve['root_length']
        first_corner = start + (root_length * self.fluent_curve['first_point']['normal'])
        last_corner = end + (root_length * self.fluent_curve['second_point']['normal'])
        if self.fluent_curve['combinaison'] == 1:
            self.fluent_curve['path'] = [
                start,
                first_corner,
                (last_corner.x, first_corner.y, first_corner.z),
                (last_corner.x, last_corner.y, first_corner.z),
                last_corner,
                end
            ]
        elif self.fluent_curve['combinaison'] == 2:
            self.fluent_curve['path'] = [
                start,
                first_corner,
                (last_corner.x, first_corner.y, first_corner.z),
                (last_corner.x, first_corner.y, last_corner.z),
                last_corner,
                end
            ]
        elif self.fluent_curve['combinaison'] == 3:
            self.fluent_curve['path'] = [
                start,
                first_corner,
                (first_corner.x, last_corner.y, first_corner.z),
                (last_corner.x, last_corner.y, first_corner.z),
                last_corner,
                end
            ]
        elif self.fluent_curve['combinaison'] == 4:
            self.fluent_curve['path'] = [
                start,
                first_corner,
                (first_corner.x, last_corner.y, first_corner.z),
                (first_corner.x, last_corner.y, last_corner.z),
                last_corner,
                end
            ]
        elif self.fluent_curve['combinaison'] == 5:
            self.fluent_curve['path'] = [
                start,
                first_corner,
                (first_corner.x, first_corner.y, last_corner.z),
                (last_corner.x, first_corner.y, last_corner.z),
                last_corner,
                end
            ]
        elif self.fluent_curve['combinaison'] == 6:
            self.fluent_curve['path'] = [
                start,
                first_corner,
                (first_corner.x, first_corner.y, last_corner.z),
                (first_corner.x, last_corner.y, last_corner.z),
                last_corner,
                end
            ]

        pipe_verts = []
        for i in self.fluent_curve['path']:
            pipe_verts.append((0, 0, 0))
        edges = []
        for i in range(len(self.fluent_curve['path']) - 1):
            edges.append((i, i + 1))
        faces = []
        mesh_data = bpy.data.meshes.new("pipe_data")
        mesh_data.from_pydata(pipe_verts, edges, faces)
        mesh_data.update()
        pipe = bpy.data.objects.new("pipe", mesh_data)
        self.bool_obj = pipe
        bpy.context.scene.collection.objects.link(pipe)
        active_object('SET', pipe)
        bpy.ops.object.mode_set(mode='OBJECT')

        i = 0
        for v in pipe.data.vertices:
            v.co = self.fluent_curve['path'][i]
            i += 1

        pipe.modifiers.new(name=fluent_modifiers_name['weld'], type='WELD')

        # bpy.ops.object.mode_set(mode='EDIT')
        # bpy.ops.mesh.select_all(action="SELECT")
        # bpy.ops.mesh.dissolve_limited(angle_limit=0.0174533)
        # bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode='OBJECT')
        modif = pipe.modifiers.new(name='BEVEL', type='BEVEL')
        modif.affect = 'VERTICES'
        modif.width = 0.1
        modif.segments = auto_bevel_segments(modif)
        modif.show_expanded = False

        self.fluent_curve['curve_obj'] = pipe
        pipe.data.use_auto_smooth = True

        self.load_geometry_node()

    def align_ending_point(self, axis):
        if axis == 'X' and self.fluent_curve['path'][5].x != self.fluent_curve['path'][0].x:
            self.fluent_curve['path'][5].x = self.fluent_curve['path'][0].x
        elif axis == 'X' and self.fluent_curve['path'][5].x == self.fluent_curve['path'][0].x:
            self.fluent_curve['path'][5].x = self.fluent_curve['second_point']['hit'].x

        if axis == 'Y' and self.fluent_curve['path'][5].y != self.fluent_curve['path'][0].y:
            self.fluent_curve['path'][5].y = self.fluent_curve['path'][0].y
        elif axis == 'Y' and self.fluent_curve['path'][5].y == self.fluent_curve['path'][0].y:
            self.fluent_curve['path'][5].y = self.fluent_curve['second_point']['hit'].y

        if axis == 'Z' and self.fluent_curve['path'][5].z != self.fluent_curve['path'][0].z:
            self.fluent_curve['path'][5].z = self.fluent_curve['path'][0].z
        elif axis == 'Z' and self.fluent_curve['path'][5].z == self.fluent_curve['path'][0].z:
            self.fluent_curve['path'][5].z = self.fluent_curve['second_point']['hit'].z

        self.update_path()

    def update_path(self):
        start = self.fluent_curve['path'][0]
        end = self.fluent_curve['path'][5]

        root_length = self.fluent_curve['root_length']
        first_corner = start + (root_length * self.fluent_curve['first_point']['normal'])
        last_corner = end + (root_length * self.fluent_curve['second_point']['normal'])

        if self.fluent_curve['combinaison'] == 1:
            self.fluent_curve['path'] = [
                start,
                first_corner,
                (last_corner.x, first_corner.y, first_corner.z),
                (last_corner.x, last_corner.y, first_corner.z),
                last_corner,
                end
            ]
        elif self.fluent_curve['combinaison'] == 2:
            self.fluent_curve['path'] = [
                start,
                first_corner,
                (last_corner.x, first_corner.y, first_corner.z),
                (last_corner.x, first_corner.y, last_corner.z),
                last_corner,
                end
            ]
        elif self.fluent_curve['combinaison'] == 3:
            self.fluent_curve['path'] = [
                start,
                first_corner,
                (first_corner.x, last_corner.y, first_corner.z),
                (last_corner.x, last_corner.y, first_corner.z),
                last_corner,
                end
            ]
        elif self.fluent_curve['combinaison'] == 4:
            self.fluent_curve['path'] = [
                start,
                first_corner,
                (first_corner.x, last_corner.y, first_corner.z),
                (first_corner.x, last_corner.y, last_corner.z),
                last_corner,
                end
            ]
        elif self.fluent_curve['combinaison'] == 5:
            self.fluent_curve['path'] = [
                start,
                first_corner,
                (first_corner.x, first_corner.y, last_corner.z),
                (last_corner.x, first_corner.y, last_corner.z),
                last_corner,
                end
            ]
        elif self.fluent_curve['combinaison'] == 6:
            self.fluent_curve['path'] = [
                start,
                first_corner,
                (first_corner.x, first_corner.y, last_corner.z),
                (first_corner.x, last_corner.y, last_corner.z),
                last_corner,
                end
            ]

        for i, v in enumerate(self.fluent_curve['curve_obj'].data.vertices):
            v.co = self.fluent_curve['path'][i]

    def add_ring(self, picked_ring=None):
        if not picked_ring:
            folder = '/wire'
            file_path_wire = os.path.dirname(realpath(__file__)) + folder + "/wire.blend/Object/"
            self.fluent_curve['curve_obj'].select_set(False)
            bpy.ops.wm.append(filename='f_ring_01', directory=file_path_wire)
            ring = bpy.context.selected_objects[0]
            ring['fluent_type'] = 'pipe_ring'
            ring.name = self.fluent_curve['curve_obj'].name + '.Ring'
        else:
            ring = picked_ring

        # mise à jour de geometry nodes
        the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
        tree = the_modifier.node_group
        nodes = tree.nodes
        link = tree.links.new
        node_ring = nodes.new(type='GeometryNodeGroup')
        node_ring.node_tree = bpy.data.node_groups.get('f_add_pipe_ring')
        node_join = None
        node_reroute = None
        for n in nodes:
            if n.name == 'Join rings':
                node_join = n
            if n.name == 'curve_for_extra':
                node_reroute = n
            if node_join and node_reroute:
                break
        link(node_ring.outputs[0], node_join.inputs[0])
        link(node_reroute.outputs[0], node_ring.inputs[0])
        node_ring.inputs[1].default_value = ring

        if not picked_ring:
            the_input = ring.modifiers['Radius']
            the_input.strength = tree.inputs['Radius'].default_value * 2
            node_ring.inputs['X Offset'].default_value = 0
            if self.current_ring_node:
                for i in range(len(ring.modifiers)):
                    ring.modifiers.remove(ring.modifiers[0])
                copy_modifiers_stack(self.current_ring_node.inputs['Object'].default_value, ring, name='')
            ring.hide_set(True)
            ring.hide_render = True
        self.current_ring_node = node_ring
        self.fluent_curve['ring_nodes'].append(node_ring)

    def add_duct(self):
        folder = '/wire'
        file_path_wire = os.path.dirname(realpath(__file__)) + folder + "/wire.blend/Object/"
        self.fluent_curve['curve_obj'].select_set(False)
        bpy.ops.wm.append(filename='f_duct', directory=file_path_wire)
        duct = bpy.context.selected_objects[0]
        duct.hide_set(True)
        duct.hide_render = True
        duct.name = self.fluent_curve['curve_obj'].name + '.Duct'

        # mise à jour de geometry nodes
        node_group = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes'].node_group.nodes['fluent_pipe']
        node_group.inputs['Design'].default_value = duct
        node_group.inputs['Radius'].default_value = 0

        # ajoute un weld modifier juste après geometry node
        weld = self.fluent_curve['curve_obj'].modifiers.new(type='WELD', name=fluent_modifiers_name['weld'])
        active_object('SET', self.fluent_curve['curve_obj'], True)
        bpy.ops.object.modifier_move_to_index(modifier=weld.name, index=1)

    def end_of_adjustment(self):
        if self.action in {'TILT_01', 'TILT_02'} :
            active_object(self.fluent_curve['curve_obj'], 'SET')
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.curve.select_all(action = 'SELECT')
            bpy.ops.curve.smooth_tilt()
            bpy.ops.object.mode_set(mode='OBJECT')
            self.fluent_curve['curve_obj'].select_set(False)

        try:
            modifier_name = self.action.split('#')[1]
            if modifier_name in {'F_Ring_Array'}:
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        except:pass
        self.action = 'NOTHING'
        self.build_step = self.other_adjustment = None
        self.enter_value = 'None'
        self.previous_value = None

    def put_curve(self):
        self.screen_text.append(['Pipe tool',''])
        self.screen_text.append(['Put pipe ends','Left click'])
        self.screen_text.append(['Snap to face center','Hold ctrl'])
        if not self.fluent_curve['added'] and self.fluent_curve['first_point'] and self.fluent_curve['second_point']:
            self.snap_face_center = False
            self.make_pipe()

            self.fluent_curve['added'] = True
            self.draw_dots.set_dots([])
            self.pie_menu_history.append(self.wire_menu)
            self.pie_menu_history[-1].spread(self.events['mouse_x'], self.events['mouse_y'])

        # place le second point
        if self.events['value'] == 'PRESS' and self.events['type'] == 'LEFTMOUSE' and not self.fluent_curve['second_point'] and self.fluent_curve['first_point']:
            obj = click_on(self.events['mouse_x'], self.events['mouse_y'])
            if obj:
                copy = duplicate(obj, '.f_temp')
                apply_modifiers(copy)
                cast = obj_ray_cast(copy, self.events['mouse_x'], self.events['mouse_y'])
                if self.events['ctrl_work']:
                    cast['hit'] = copy.data.polygons[cast['face_index']].center
                local_cast = cast_local2global(cast)
                del local_cast['obj']
                bpy.data.objects.remove(copy, do_unlink=True)
                self.fluent_curve['second_point'] = local_cast.copy()
                co_2d = co3d_to_co2d(local_cast['hit'])
                self.draw_dots.append_a_dot([co_2d.x, co_2d.y, 6, (1, 1, 1, 1)])

        # place le premier point
        if self.events['value'] == 'PRESS' and self.events['type'] == 'LEFTMOUSE' and not self.fluent_curve['first_point']:
            obj = click_on(self.events['mouse_x'], self.events['mouse_y'])
            if obj:
                copy = duplicate(obj, '.f_temp')
                apply_modifiers(copy)
                cast = obj_ray_cast(copy, self.events['mouse_x'], self.events['mouse_y'])
                if self.events['ctrl_work']:
                    cast['hit'] = copy.data.polygons[cast['face_index']].center
                global_cast = cast_local2global(cast)
                del global_cast['obj']
                bpy.data.objects.remove(copy, do_unlink=True)
                self.fluent_curve['first_point'] = global_cast.copy()
                co_2d = co3d_to_co2d(global_cast['hit'])
                self.draw_dots.append_a_dot([co_2d.x, co_2d.y, 6, (1, 1, 1, 1)])

    def modal(self, context, event):
        context.area.tag_redraw()
        self.screen_text = []

        self.ui_items_list = [i for i in self.ui_items_list if
                              not (type(i) is FLUENT_Ui_Layout and i.get_layout() in ['PIE', 'MIRROR', 'TAPER'])]
        if len(self.pie_menu_history):
            self.ui_items_list.append(self.pie_menu_history[-1])

        self.events = event_dico_refresh(self.events, event)

        if pass_through(event) or event.type == 'TAB':
            return {'PASS_THROUGH'}

        try:
            if bpy.context.active_object.mode == 'EDIT' and not self.action:
                return {'PASS_THROUGH'}
        except:pass

        # animation
        if event.type == 'TIMER' and self.value_animation['step'] == 'PROCESS':
            delta = 10*(time.time()-self.value_animation['t0'])
            self.value_animation['input'].default_value = self.value_animation['v0'] + math.sin(delta)*self.value_animation['strength']
            if round(delta, 2) >= round(math.pi*2, 2):
                self.value_animation['input'].default_value = self.value_animation['v0']
                self.value_animation['step'] = 'WAIT'

        # action des bouttons
        action = None
        for b in self.ui_items_list:
            if type(b) is FLUENT_Ui_Button:
                b.is_hover(self.events)
                if b.get_state() == 2:
                    action = b.get_action()
                    b.set_state(0)
                    break
                else:
                    action = None
            elif type(b) is FLUENT_Ui_Layout:
                layout_items_list = b.get_items()
                for i in layout_items_list:
                    i.is_hover(self.events)
                    if i.get_state() == 2:
                        action = i.get_action()
                        i.set_state(0)
                        break
                    else:
                        action = None
                if action:
                    break

        # action du clavier
        if self.fluent_curve['added']:
            if event.type == 'R' and event.value == 'PRESS':
                action = 'SELECT_RING'
            if event.type == 'X' and event.value == 'PRESS':
                action = 'ALIGN_X'
            if event.type == 'Y' and event.value == 'PRESS':
                action = 'ALIGN_Y'
            if event.type == 'Z' and event.value == 'PRESS':
                action = 'ALIGN_Z'
        if event.type == 'ESC' and event.value == 'PRESS' and not self.action:
            action = 'CANCELLED'
        if event.type == 'ESC' and event.value == 'PRESS' and self.action:
            self.action = None

        if action:
            if action == 'VALIDATE':
                del self.pie_menu_history[-1]
                self.end_of_adjustment()
                action = 'NOTHING'
            elif action == 'WIRE_RING_MENU' and not event.shift:
                if not self.delay:
                    self.delay = time.time()
                else:
                    if time.time() - self.delay > 0.5:
                        self.delay = None
                        self.wire_ring_menu.spread(self.wire_menu.get_pie_center()[0],
                                                   self.wire_menu.get_pie_center()[1])
                        self.pie_menu_history.append(self.wire_ring_menu)
            elif action == 'ARRAY_MENU' and not event.shift:
                if not self.delay:
                    self.delay = time.time()
                else:
                    if time.time() - self.delay > 0.5:
                        self.delay = None
                        self.array_menu.spread(self.wire_menu.get_pie_center()[0], self.wire_menu.get_pie_center()[1])
                        self.pie_menu_history.append(self.array_menu)
            elif action == 'EXTRA_MENU' and not event.shift:
                if not self.delay:
                    self.delay = time.time()
                else:
                    if time.time() - self.delay > 0.5:
                        self.delay = None
                        self.extra_menu.spread(self.wire_menu.get_pie_center()[0], self.wire_menu.get_pie_center()[1])
                        self.pie_menu_history.append(self.extra_menu)
            elif action == 'COIL_MENU' and not event.shift:
                if not self.delay:
                    self.delay = time.time()
                else:
                    if time.time() - self.delay > 0.5:
                        self.delay = None
                        self.coil_menu.spread(self.wire_menu.get_pie_center()[0], self.wire_menu.get_pie_center()[1])
                        self.pie_menu_history.append(self.coil_menu)
            elif action == 'PROTECTION_MENU' and not event.shift:
                if not self.delay:
                    self.delay = time.time()
                else:
                    if time.time() - self.delay > 0.5:
                        self.delay = None
                        self.protection_menu.spread(self.wire_menu.get_pie_center()[0],
                                                    self.wire_menu.get_pie_center()[1])
                        self.pie_menu_history.append(self.protection_menu)
            elif action == 'UTILITIES_MENU' and not event.shift:
                if not self.delay:
                    self.delay = time.time()
                else:
                    if time.time() - self.delay > 0.5:
                        self.delay = None
                        self.utilities_menu.spread(self.wire_menu.get_pie_center()[0],
                                                   self.wire_menu.get_pie_center()[1])
                        self.pie_menu_history.append(self.utilities_menu)
            elif action == 'DUCT_MENU' and not event.shift:
                if not self.delay:
                    self.delay = time.time()
                else:
                    if time.time() - self.delay > 0.5:
                        self.delay = None
                        self.duct_menu.spread(self.pie_menu_history[-1].get_pie_center()[0],
                                              self.pie_menu_history[-1].get_pie_center()[1])
                        self.pie_menu_history.append(self.duct_menu)
            elif action == 'CONNECTOR_MENU' and not event.shift:
                if not self.delay:
                    self.delay = time.time()
                else:
                    if time.time() - self.delay > 0.5:
                        self.delay = None
                        self.connector_menu.spread(self.pie_menu_history[-1].get_pie_center()[0],
                                                   self.pie_menu_history[-1].get_pie_center()[1])
                        self.pie_menu_history.append(self.connector_menu)
            elif action == 'BACK_MENU' and not event.shift:
                if not self.delay:
                    self.delay = time.time()
                else:
                    if time.time() - self.delay > 0.5:
                        self.delay = None
                        del self.pie_menu_history[-1]
            self.action = action
        else:
            self.delay = None
        # gestion affichage du pie menu
        if self.fluent_curve['added'] and self.events['mouse_left_click'] and len(self.pie_menu_history):
            for b in self.pie_menu_history[-1].get_items():
                try:
                    b.set_show(True)
                except:
                    print('--- ERROR Impossible to show button')
        else:
            if len(self.pie_menu_history) and self.pie_menu_history[-1].get_layout() not in ['MIRROR', 'TAPER']:
                self.pie_menu_history[-1].spread(self.events['mouse_x'], self.events['mouse_y'])
                for b in self.pie_menu_history[-1].get_items():
                    try:
                        b.set_show(False)
                    except:
                        print('--- ERROR Impossible to hide button')

        # creation de la courbe
        if not self.fluent_curve['added']:
            self.put_curve()

        if action in ['ALIGN_X', 'ALIGN_Y', 'ALIGN_Z']:
            if 'X' in action:
                self.align_ending_point('X')
            elif 'Y' in action:
                self.align_ending_point('Y')
            elif 'Z' in action:
                self.align_ending_point('Z')

        if not self.events['mouse_left_click'] and self.value_animation['step'] == 'WAIT':
            # basic settings ###############################
            if self.action == 'RADIUS':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_6'
                self.number_adjustment(the_modifier, the_input, 400, event, 'FLOAT')
                if self.enter_value != 'None':
                    self.screen_text.append(['Radius', str(self.enter_value)])
                else:
                    self.screen_text.append(['Radius', str(round(the_modifier[the_input], 5))])
                self.screen_text.append(['Gap', 'V'])
                self.screen_text.append(['Count', 'B'])

                if event.type == 'C' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'RADIUS'
                    return {'RUNNING_MODAL'}
                if event.type == 'V' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'ARRAY_GAP'
                    return {'RUNNING_MODAL'}
                if event.type == 'B' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'ARRAY_COUNT'
                    return {'RUNNING_MODAL'}

            if self.action == 'PIPE_BEVEL':
                the_input = self.fluent_curve['curve_obj'].modifiers['BEVEL']
                if self.previous_value == None:
                    self.previous_value = the_input.width
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.enter_value != 'None':
                    self.screen_text.append(['Width', str(self.enter_value)])
                else:
                    self.screen_text.append(['Width', str(round(the_input.width, 5))])
                self.enter_value = enter_value(self.enter_value, self.events)
                self.screen_text.append(['Segments', 'C'])
                self.screen_text.append(['Wireframe', 'W'])
                if self.events['shift_work']:
                    increment = 4000
                elif self.events['ctrl_work']:
                    increment = 40
                else:
                    increment = 400
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or self.events['ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = the_input.width

                the_input.width = self.previous_value + ((event.mouse_region_x - self.slider_origin)/increment)
                if enter_value_validation(self.enter_value, event)[0]:
                    the_input.width = enter_value_validation(self.enter_value, event)[1]
                    self.end_of_adjustment()

                if event.type == 'C' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'PIPE_SEGMENTS'
                    return {'RUNNING_MODAL'}

            if self.action == 'PIPE_SEGMENTS':
                the_input = self.fluent_curve['curve_obj'].modifiers['BEVEL']
                if self.previous_value == None:
                    self.previous_value = the_input.segments
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.enter_value != 'None':
                    self.screen_text.append(['Segments', str(self.enter_value)])
                else:
                    self.screen_text.append(['Segments', str(round(the_input.segments, 5))])
                self.enter_value = enter_value(self.enter_value, self.events)
                self.screen_text.append(['Width', 'C'])
                self.screen_text.append(['Wireframe', 'W'])
                if self.events['shift_work']:
                    increment = 1000
                elif self.events['ctrl_work']:
                    increment = 10
                else:
                    increment = 100
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or self.events['ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = the_input.segments

                the_input.segments = int(self.previous_value + ((event.mouse_region_x - self.slider_origin)/increment))
                if enter_value_validation(self.enter_value, event)[0]:
                    the_input.segments = int(enter_value_validation(self.enter_value, event)[1])
                    self.end_of_adjustment()

                if event.type == 'C' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'PIPE_BEVEL'
                    return {'RUNNING_MODAL'}

            if self.action == 'TILT_01':
                if self.previous_value == None:
                    self.previous_value = self.fluent_curve['curve_obj'].data.splines[0].bezier_points[0].tilt
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.events['shift_work']:
                    increment = 3000
                elif self.events['ctrl_work']:
                    increment = 30
                else:
                    increment = 300
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or self.events['ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = self.fluent_curve['curve_obj'].data.splines[0].bezier_points[0].tilt

                self.fluent_curve['curve_obj'].data.splines[0].bezier_points[0].tilt = self.previous_value - ((event.mouse_region_x - self.slider_origin)/increment)

            if self.action == 'TILT_02':
                spline = self.fluent_curve['curve_obj'].data.splines[0]
                if self.previous_value == None:
                    self.previous_value = self.fluent_curve['curve_obj'].data.splines[0].bezier_points[-1].tilt
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.events['shift_work']:
                    increment = 3000
                elif self.events['ctrl_work']:
                    increment = 30
                else:
                    increment = 300
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or self.events['ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = self.fluent_curve['curve_obj'].data.splines[0].bezier_points[len(spline.bezier_points)-1].tilt

                self.fluent_curve['curve_obj'].data.splines[0].bezier_points[-1].tilt = self.previous_value - ((event.mouse_region_x - self.slider_origin)/increment)

            if self.action == 'STIFFNESS':
                if self.previous_value == None:
                    self.previous_value = self.fluent_curve['root_length']
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.events['shift_work']:
                    increment = 3000
                elif self.events['ctrl_work']:
                    increment = 30
                else:
                    increment = 300
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or self.events['ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = self.fluent_curve['stiffness']

                if event.type =='MOUSEMOVE':
                    self.fluent_curve['root_length'] = self.previous_value + ((event.mouse_region_x - self.slider_origin)/increment)
                    if self.fluent_curve['root_length'] < 0:
                        self.fluent_curve['root_length'] = 0
                    self.update_path()

            if self.action == 'CIRCLE_RESOLUTION':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_27'
                self.number_adjustment(the_modifier, the_input, 10, event, 'INT')
                if self.enter_value != 'None':
                    self.screen_text.append(['Resolution', str(self.enter_value)])
                else:
                    self.screen_text.append(['Resolution', str(round(the_modifier[the_input], 5))])

            if self.action == 'CURVE_RESOLUTION':
                if self.previous_value == None:
                    self.previous_value = self.fluent_curve['curve_obj'].data.resolution_u
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.enter_value != 'None':
                    self.screen_text.append(['RESOLUTION', str(self.enter_value)])
                else:
                    self.screen_text.append(['RESOLUTION', str(self.fluent_curve['curve_obj'].data.resolution_u)])
                self.enter_value = enter_value(self.enter_value, self.events)
                if self.events['shift_work']:
                    increment = 300
                elif self.events['ctrl_work']:
                    increment = 3
                else:
                    increment = 30
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or self.events['ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = self.fluent_curve['curve_obj'].data.bevel_resolution

                self.fluent_curve['curve_obj'].data.resolution_u = self.previous_value + ((event.mouse_region_x - self.slider_origin)/increment)
                if enter_value_validation(self.enter_value, event)[0]:
                    self.do_not = 'QUIT_FLUENT'
                    self.fluent_curve['curve_obj'].data.resolution_u = enter_value_validation(self.enter_value, event)[1]
                    self.end_of_adjustment()

            if self.action == 'CURVE_OFFSET':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_7'
                self.number_adjustment(the_modifier, the_input, 80, event, 'FLOAT')
                if self.enter_value != 'None':
                    self.screen_text.append(['Resolution', str(self.enter_value)])
                else:
                    self.screen_text.append(['Resolution', str(round(the_modifier[the_input], 5))])
                self.enter_value = enter_value(self.enter_value, self.events)

            if self.action == 'PATH':
                if self.previous_value == None:
                    self.previous_value = 0
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())

                increment = 1

                value = self.previous_value + ((event.mouse_region_x - self.slider_origin)/increment)
                value = snap_slider_value(value, 20)

                if round(value) != 0:
                    self.previous_value = 0
                    self.slider_origin = event.mouse_region_x
                    if round(value) > 0:
                        self.fluent_curve['combinaison'] += 1
                        if self.fluent_curve['combinaison'] > 6:
                            self.fluent_curve['combinaison'] = 0
                    else:
                        self.fluent_curve['combinaison'] -= 1
                        if self.fluent_curve['combinaison'] < 0:
                            self.fluent_curve['combinaison'] = 6
                    self.update_path()

                self.screen_text.append(['Path', str(self.fluent_curve['combinaison'])])

            # array ######################################
            if self.action == 'ARRAY_COUNT':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_4'
                if self.enter_value != 'None':
                    self.screen_text.append(['Count', str(self.enter_value)])
                else:
                    self.screen_text.append(['Count', str(round(the_modifier[the_input], 5))])
                self.screen_text.append(['Radius', 'C'])
                self.screen_text.append(['Gap', 'V'])

                self.number_adjustment(the_modifier, the_input, 50, event, 'INT')

                if event.type == 'C' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'RADIUS'
                    return {'RUNNING_MODAL'}
                if event.type == 'V' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'ARRAY_GAP'
                    return {'RUNNING_MODAL'}
                if event.type == 'B' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'ARRAY_COUNT'
                    return {'RUNNING_MODAL'}

            if self.action == 'ARRAY_GAP':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_3'
                if self.enter_value != 'None':
                    self.screen_text.append(['Gap', str(self.enter_value)])
                else:
                    self.screen_text.append(['Gap', str(round(the_modifier[the_input], 5))])
                self.screen_text.append(['Radius', 'C'])
                self.screen_text.append(['Count', 'B'])

                self.number_adjustment(the_modifier, the_input, 200, event, 'FLOAT')

                if event.type == 'C' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'RADIUS'
                    return {'RUNNING_MODAL'}
                if event.type == 'V' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'ARRAY_GAP'
                    return {'RUNNING_MODAL'}
                if event.type == 'B' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'ARRAY_COUNT'
                    return {'RUNNING_MODAL'}

            if self.action == 'ARRAY_LINEAR':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_5'
                the_modifier[the_input] = False
                the_modifier.show_viewport = False
                the_modifier.show_viewport = True
                self.action = None

            if self.action == 'ARRAY_CIRCULAR':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_5'
                the_modifier[the_input] = True
                the_modifier.show_viewport = False
                the_modifier.show_viewport = True
                self.action = None

            # coil #######################################
            if self.action == 'COIL_ADD':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_9'
                the_modifier[the_input] = not the_modifier[the_input]
                the_modifier.show_viewport = False
                the_modifier.show_viewport = True
                self.action = None

            if self.action == 'COIL_RADIUS':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_28'
                if self.enter_value != 'None':
                    self.screen_text.append(['Radius', str(self.enter_value)])
                else:
                    self.screen_text.append(['Radius', str(round(the_modifier[the_input], 5))])
                self.screen_text.append(['Toggle cable/spiral radius', 'C'])

                self.number_adjustment(the_modifier, the_input, 500, event, 'FLOAT')

                if event.type == 'C' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'COIL_SPIRAL_RADIUS'
                    return {'RUNNING_MODAL'}

            if self.action == 'COIL_ROTATIONS':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_13'
                if self.enter_value != 'None':
                    self.screen_text.append(['Count', str(self.enter_value)])
                else:
                    self.screen_text.append(['Count', str(round(the_modifier[the_input], 5))])

                self.number_adjustment(the_modifier, the_input, 100, event, 'FLOAT')

            if self.action == 'COIL_SPIRAL_RADIUS':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_14'
                if self.enter_value != 'None':
                    self.screen_text.append(['Radius', str(self.enter_value)])
                else:
                    self.screen_text.append(['Radius', str(round(the_modifier[the_input], 5))])
                self.screen_text.append(['Toggle cable/spiral radius', 'C'])

                self.number_adjustment(the_modifier, the_input, 100, event, 'FLOAT')

                if event.type == 'C' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'COIL_RADIUS'
                    return {'RUNNING_MODAL'}

            if self.action == 'COIL_SPIRAL_RESOLUTION':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_12'
                if self.enter_value != 'None':
                    self.screen_text.append(['Resolution', str(self.enter_value)])
                else:
                    self.screen_text.append(['Resolution', str(round(the_modifier[the_input], 5))])
                self.number_adjustment(the_modifier, the_input, 100, event, 'INT')

            # protection #################################
            if self.action == 'PROTECTION_ADD':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_17'
                the_modifier[the_input] = not the_modifier[the_input]
                the_modifier.show_viewport = False
                the_modifier.show_viewport = True
                self.action = None

            if self.action == 'PROTECTION_SPIRAL_RADIUS':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_18'
                self.number_adjustment(the_modifier, the_input, 300, event, 'FLOAT')
                if self.enter_value != 'None':
                    self.screen_text.append(['Radius', str(self.enter_value)])
                else:
                    self.screen_text.append(['Radius', str(round(the_modifier[the_input], 5))])
                self.screen_text.append(['Thickness', 'C'])

                if event.type == 'C' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'PROTECTION_THICKNESS'
                    return {'RUNNING_MODAL'}

            if self.action == 'PROTECTION_HEIGHT':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_19'
                self.number_adjustment(the_modifier, the_input, 300, event, 'FLOAT')
                if self.enter_value != 'None':
                    self.screen_text.append(['Height', str(self.enter_value)])
                else:
                    self.screen_text.append(['Height', str(round(the_modifier[the_input], 5))])
                self.screen_text.append(['Rotation', 'C'])

                if event.type == 'C' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'PROTECTION_ROTATIONS'
                    return {'RUNNING_MODAL'}

            if self.action == 'PROTECTION_ROTATIONS':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_20'
                self.number_adjustment(the_modifier, the_input, 100, event, 'FLOAT')
                if self.enter_value != 'None':
                    self.screen_text.append(['Count', str(self.enter_value)])
                else:
                    self.screen_text.append(['Count', str(round(the_modifier[the_input], 5))])
                self.screen_text.append(['Height', 'C'])

                if event.type == 'C' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'PROTECTION_HEIGHT'
                    return {'RUNNING_MODAL'}

            if self.action == 'PROTECTION_THICKNESS':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_21'
                self.number_adjustment(the_modifier, the_input, 500, event, 'FLOAT')
                if self.enter_value != 'None':
                    self.screen_text.append(['Thickness', str(self.enter_value)])
                else:
                    self.screen_text.append(['Thickness', str(round(the_modifier[the_input], 5))])
                self.screen_text.append(['Radius', 'C'])

                if event.type == 'C' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'PROTECTION_SPIRAL_RADIUS'
                    return {'RUNNING_MODAL'}

            if self.action == 'PROTECTION_RESOLUTION':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_22'
                self.number_adjustment(the_modifier, the_input, 10, event, 'INT')
                if self.enter_value != 'None':
                    self.screen_text.append(['Resolution', str(self.enter_value)])
                else:
                    self.screen_text.append(['Resolution', str(round(the_modifier[the_input], 5))])

            # rings ######################################
            if self.action == 'SELECT_RING':
                for i, n in enumerate(self.fluent_curve['ring_nodes']):
                    if n == self.current_ring_node:
                        try:
                            self.current_ring_node = self.fluent_curve['ring_nodes'][i + 1]
                        except:
                            self.current_ring_node = self.fluent_curve['ring_nodes'][0]
                        self.value_animation['input'] = self.current_ring_node.inputs['X Offset']
                        self.value_animation['v0'] = self.current_ring_node.inputs['X Offset'].default_value
                        self.value_animation['t0'] = time.time()
                        self.value_animation['strength'] = 0.02
                        self.value_animation['step'] = 'PROCESS'
                        break
                self.action = None

            if self.action == 'ADD_RING':
                self.add_ring()
                self.action = None

            if self.action == 'RING_MOVE' and self.current_ring_node:
                node = self.current_ring_node
                the_input = node.inputs['X Offset']
                if self.previous_value == None:
                    self.previous_value = the_input.default_value
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.enter_value != 'None':
                    self.screen_text.append(['Offset', str(self.enter_value)])
                else:
                    self.screen_text.append(['Offset', str(round(the_input.default_value, 5))])
                self.enter_value = enter_value(self.enter_value, self.events)
                if self.events['shift_work']:
                    increment = 3000
                elif self.events['ctrl_work']:
                    increment = 30
                else:
                    increment = 300
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or \
                        self.events[
                            'ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = the_input.default_value

                the_input.default_value = self.previous_value + (
                            (event.mouse_region_x - self.slider_origin) / increment)
                if enter_value_validation(self.enter_value, event)[0]:
                    the_input.default_value = enter_value_validation(self.enter_value, event)[1]
                    self.end_of_adjustment()

            if self.action == 'RING_SCALE' and self.current_ring_node and self.current_ring_node.inputs[
                'Object'].default_value.get('fluent_type') != 'pipe_ring':
                node = self.current_ring_node
                the_input = node.inputs['Scale']
                if self.previous_value == None:
                    self.previous_value = the_input.default_value
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.enter_value != 'None':
                    self.screen_text.append(['Scale', str(self.enter_value)])
                else:
                    self.screen_text.append(['Scale', str(round(the_input.default_value, 5))])
                self.enter_value = enter_value(self.enter_value, self.events)
                if self.events['shift_work']:
                    increment = 3000
                elif self.events['ctrl_work']:
                    increment = 30
                else:
                    increment = 300
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or \
                        self.events[
                            'ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = the_input.default_value

                the_input.default_value = self.previous_value + (
                            (event.mouse_region_x - self.slider_origin) / increment)
                if enter_value_validation(self.enter_value, event)[0]:
                    the_input.default_value = enter_value_validation(self.enter_value, event)[1]
                    self.end_of_adjustment()

            if self.action == 'RING_ARRAY_COUNT' and self.current_ring_node:
                node = self.current_ring_node
                the_input = node.inputs['Count']
                if self.previous_value == None:
                    self.previous_value = the_input.default_value
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.enter_value != 'None':
                    self.screen_text.append(['Count', str(self.enter_value)])
                else:
                    self.screen_text.append(['Count', str(round(the_input.default_value, 5))])
                self.enter_value = enter_value(self.enter_value, self.events)
                self.screen_text.append(['Gap', 'C'])
                if self.events['shift_work']:
                    increment = 1000
                elif self.events['ctrl_work']:
                    increment = 10
                else:
                    increment = 100
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or \
                        self.events[
                            'ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = the_input.default_value

                the_input.default_value = int(self.previous_value + ((event.mouse_region_x - self.slider_origin) / increment))
                if enter_value_validation(self.enter_value, event)[0]:
                    the_input.default_value = int(enter_value_validation(self.enter_value, event)[1])
                    self.end_of_adjustment()

                if event.type == 'C' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'RING_ARRAY_GAP'
                    return {'RUNNING_MODAL'}

            if self.action == 'RING_ARRAY_GAP' and self.current_ring_node:
                node = self.current_ring_node
                the_input = node.inputs['Gap']
                if self.previous_value == None:
                    self.previous_value = the_input.default_value
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.enter_value != 'None':
                    self.screen_text.append(['Gap', str(self.enter_value)])
                else:
                    self.screen_text.append(['Gap', str(round(the_input.default_value, 5))])
                self.enter_value = enter_value(self.enter_value, self.events)
                self.screen_text.append(['Count', 'C'])
                if self.events['shift_work']:
                    increment = 1000
                elif self.events['ctrl_work']:
                    increment = 10
                else:
                    increment = 100
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or \
                        self.events[
                            'ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = the_input.default_value

                the_input.default_value = self.previous_value + (
                            (event.mouse_region_x - self.slider_origin) / increment)
                if enter_value_validation(self.enter_value, event)[0]:
                    the_input.default_value = enter_value_validation(self.enter_value, event)[1]
                    self.end_of_adjustment()

                if event.type == 'C' and event.value == 'PRESS':
                    del self.pie_menu_history[-1]
                    self.end_of_adjustment()
                    self.action = 'RING_ARRAY_COUNT'
                    return {'RUNNING_MODAL'}

            if self.action == 'RING_LENGTH' and self.current_ring_node and self.current_ring_node.inputs[
                'Object'].default_value.get('fluent_type') == 'pipe_ring':
                node = self.current_ring_node
                ring_obj = node.inputs['Object'].default_value
                the_input = ring_obj.modifiers['Length']
                if self.previous_value == None:
                    self.previous_value = the_input.screw_offset
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.enter_value != 'None':
                    self.screen_text.append(['Length', str(self.enter_value)])
                else:
                    self.screen_text.append(['Length', str(round(the_input.screw_offset, 5))])
                self.enter_value = enter_value(self.enter_value, self.events)
                if self.events['shift_work']:
                    increment = 3000
                elif self.events['ctrl_work']:
                    increment = 30
                else:
                    increment = 300
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or \
                        self.events[
                            'ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = the_input.screw_offset

                the_input.screw_offset = self.previous_value + ((event.mouse_region_x - self.slider_origin) / increment)
                if enter_value_validation(self.enter_value, event)[0]:
                    the_input.screw_offset = enter_value_validation(self.enter_value, event)[1]
                    self.end_of_adjustment()

            if self.action == 'RING_L_RESOLUTION' and self.current_ring_node and self.current_ring_node.inputs[
                'Object'].default_value.get('fluent_type') == 'pipe_ring':
                node = self.current_ring_node
                ring_obj = node.inputs['Object'].default_value
                the_input = ring_obj.modifiers['Length']
                if self.previous_value == None:
                    self.previous_value = the_input.steps
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.enter_value != 'None':
                    self.screen_text.append(['Length', str(self.enter_value)])
                else:
                    self.screen_text.append(['Length', str(round(the_input.steps, 5))])
                self.enter_value = enter_value(self.enter_value, self.events)
                if self.events['shift_work']:
                    increment = 500
                elif self.events['ctrl_work']:
                    increment = 5
                else:
                    increment = 50
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or \
                        self.events[
                            'ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = the_input.steps

                the_input.steps = the_input.render_steps = int(self.previous_value + ((event.mouse_region_x - self.slider_origin) / increment))
                if enter_value_validation(self.enter_value, event)[0]:
                    the_input.steps = the_input.render_steps = int(enter_value_validation(self.enter_value, event)[1])
                    self.end_of_adjustment()

            if self.action == 'RING_RADIUS' and self.current_ring_node and self.current_ring_node.inputs[
                'Object'].default_value.get('fluent_type') == 'pipe_ring':
                node = self.current_ring_node
                ring_obj = node.inputs['Object'].default_value
                the_input = ring_obj.modifiers['Radius']
                if self.previous_value == None:
                    self.previous_value = the_input.strength
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.enter_value != 'None':
                    self.screen_text.append(['Length', str(self.enter_value)])
                else:
                    self.screen_text.append(['Length', str(round(the_input.strength, 5))])
                self.screen_text.append(['Same as wire', 'C'])
                self.enter_value = enter_value(self.enter_value, self.events)
                if self.events['shift_work']:
                    increment = 500
                elif self.events['ctrl_work']:
                    increment = 5
                else:
                    increment = 50
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or \
                        self.events[
                            'ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = the_input.strength

                the_input.strength = self.previous_value + ((event.mouse_region_x - self.slider_origin) / increment)
                if enter_value_validation(self.enter_value, event)[0]:
                    the_input.strength = enter_value_validation(self.enter_value, event)[1]
                    self.end_of_adjustment()
                if self.events['type'] == 'C' and self.events['value'] == 'PRESS':
                    geo_node = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes'].node_group.nodes['fluent_pipe']
                    the_input.strength = geo_node.inputs['Radius'].default_value * 2
                    self.end_of_adjustment()

            if self.action == 'RING_THICKNESS' and self.current_ring_node and self.current_ring_node.inputs[
                'Object'].default_value.get('fluent_type') == 'pipe_ring':
                node = self.current_ring_node
                ring_obj = node.inputs['Object'].default_value
                the_input = ring_obj.modifiers['Thickness']
                if self.previous_value == None:
                    self.previous_value = the_input.thickness
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.enter_value != 'None':
                    self.screen_text.append(['Length', str(self.enter_value)])
                else:
                    self.screen_text.append(['Length', str(round(the_input.thickness, 5))])
                self.screen_text.append(['Same as wire', 'C'])
                self.enter_value = enter_value(self.enter_value, self.events)
                if self.events['shift_work']:
                    increment = 5000
                elif self.events['ctrl_work']:
                    increment = 50
                else:
                    increment = 500
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or \
                        self.events[
                            'ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = the_input.thickness

                the_input.thickness = self.previous_value + ((event.mouse_region_x - self.slider_origin) / increment)
                if enter_value_validation(self.enter_value, event)[0]:
                    the_input.thickness = enter_value_validation(self.enter_value, event)[1]
                    self.end_of_adjustment()

            if self.action == 'RING_BEVEL' and self.current_ring_node and self.current_ring_node.inputs[
                'Object'].default_value.get('fluent_type') == 'pipe_ring':
                node = self.current_ring_node
                ring_obj = node.inputs['Object'].default_value
                the_input = ring_obj.modifiers['Bevel']
                if self.previous_value == None:
                    self.previous_value = the_input.width
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.enter_value != 'None':
                    self.screen_text.append(['Length', str(self.enter_value)])
                else:
                    self.screen_text.append(['Length', str(round(the_input.width, 5))])
                self.screen_text.append(['Convex/Straigth', 'C'])
                self.enter_value = enter_value(self.enter_value, self.events)
                if self.events['shift_work']:
                    increment = 8000
                elif self.events['ctrl_work']:
                    increment = 80
                else:
                    increment = 800
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or \
                        self.events[
                            'ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = the_input.width

                if event.type == 'C' and event.value == 'PRESS':
                    if the_input.segments == 1:
                        the_input.segments = auto_bevel_segments(the_input)
                    else:
                        the_input.segments = 1
                the_input.width = self.previous_value + ((event.mouse_region_x - self.slider_origin) / increment)
                if enter_value_validation(self.enter_value, event)[0]:
                    the_input.width = enter_value_validation(self.enter_value, event)[1]
                    self.end_of_adjustment()

            if self.action == 'RING_C_RESOLUTION' and self.current_ring_node and self.current_ring_node.inputs[
                'Object'].default_value.get('fluent_type') == 'pipe_ring':
                node = self.current_ring_node
                ring_obj = node.inputs['Object'].default_value
                the_input = ring_obj.modifiers['Screw']
                if self.previous_value == None:
                    self.previous_value = the_input.steps
                    self.slider_origin = event.mouse_region_x
                    self.pie_menu_history.append(only_validate_menu())
                if self.enter_value != 'None':
                    self.screen_text.append(['Length', str(self.enter_value)])
                else:
                    self.screen_text.append(['Length', str(round(the_input.steps, 5))])
                self.enter_value = enter_value(self.enter_value, self.events)
                if self.events['shift_work']:
                    increment = 500
                elif self.events['ctrl_work']:
                    increment = 5
                else:
                    increment = 50
                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or \
                        self.events[
                            'ctrl_release']:
                    self.slider_origin = event.mouse_region_x
                    self.previous_value = the_input.steps

                the_input.steps = the_input.render_steps = int(self.previous_value + ((event.mouse_region_x - self.slider_origin) / increment))
                if enter_value_validation(self.enter_value, event)[0]:
                    the_input.steps = the_input.render_steps = int(enter_value_validation(self.enter_value, event)[1])
                    self.end_of_adjustment()

            if self.action == 'RING_REMOVE' and self.current_ring_node:
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                if self.current_ring_node.inputs['Object'].default_value.get('fluent_type') == 'pipe_ring':
                    bpy.data.objects.remove(self.current_ring_node.inputs['Object'].default_value, do_unlink=True)
                else:
                    original_name = self.current_ring_node.inputs['Object'].default_value.name
                    save = duplicate(self.current_ring_node.inputs['Object'].default_value)
                    bpy.data.objects.remove(self.current_ring_node.inputs['Object'].default_value, do_unlink=True)
                    save.name = original_name
                the_modifier.node_group.nodes.remove(self.current_ring_node)
                self.current_ring_node = None
                self.fluent_curve['ring_nodes'] = []
                for n in the_modifier.node_group.nodes:
                    if n.type == 'GROUP' and n.node_tree.name == 'f_add_pipe_ring' and n.inputs['Object'].default_value:
                        self.fluent_curve['ring_nodes'].append(n)
                if len(self.fluent_curve['ring_nodes']):
                    self.current_ring_node = self.fluent_curve['ring_nodes'][-1]
                self.action = None

            # duct ##########################################################
            if self.action == 'DUCT_ADD':
                the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                the_input = 'Input_25'
                if the_modifier[the_input]:
                    the_modifier[the_input] = None
                    the_modifier['Input_6'] = 0.05
                    self.fluent_curve['curve_obj'].modifiers.remove(
                        self.fluent_curve['curve_obj'].modifiers[fluent_modifiers_name['weld']])
                else:
                    self.add_duct()
                self.action = None

            if self.action == 'DUCT_RATIO':
                duct_obj = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']['Input_25']
                if duct_obj:
                    ratio_modifier = duct_obj.modifiers['ratio']
                    if self.previous_value == None:
                        self.previous_value = ratio_modifier.strength
                        self.slider_origin = event.mouse_region_x
                        self.pie_menu_history.append(only_validate_menu())
                    if self.enter_value != 'None':
                        self.screen_text.append(['Ratio', str(self.enter_value)])
                    else:
                        self.screen_text.append(['Ratio', str(round(ratio_modifier.strength, 5))])
                    self.enter_value = enter_value(self.enter_value, self.events)
                    self.screen_text.append(['Radius', 'C'])
                    if self.events['shift_work']:
                        increment = 3000
                    elif self.events['ctrl_work']:
                        increment = 30
                    else:
                        increment = 300
                    if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or \
                            self.events['ctrl_release']:
                        self.slider_origin = event.mouse_region_x
                        self.previous_value = ratio_modifier.strength

                    ratio_modifier.strength = self.previous_value + (
                                (event.mouse_region_x - self.slider_origin) / increment)
                    if enter_value_validation(self.enter_value, event)[0]:
                        ratio_modifier.strength = enter_value_validation(self.enter_value, event)[1]
                        self.end_of_adjustment()

                    if event.type == 'C' and event.value == 'PRESS':
                        del self.pie_menu_history[-1]
                        self.end_of_adjustment()
                        self.action = 'DUCT_RADIUS'
                        return {'RUNNING_MODAL'}

            if self.action == 'DUCT_RADIUS':
                duct_obj = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']['Input_25']
                if duct_obj:
                    radius_01_modifier = duct_obj.modifiers['radius_01']
                    radius_02_modifier = duct_obj.modifiers['radius_02']
                    if self.previous_value == None:
                        self.adjust_me = radius_01_modifier
                        self.previous_value = self.adjust_me.strength
                        self.slider_origin = event.mouse_region_x
                        self.pie_menu_history.append(only_validate_menu())
                    if self.enter_value != 'None':
                        self.screen_text.append(['Radius', str(self.enter_value)])
                    else:
                        self.screen_text.append(['Radius', str(round(self.adjust_me.strength, 5))])
                    self.screen_text.append(['Other radius', 'C'])
                    self.enter_value = enter_value(self.enter_value, self.events)
                    self.screen_text.append(['Ratio', 'V'])
                    if self.events['shift_work']:
                        increment = 3000
                    elif self.events['ctrl_work']:
                        increment = 30
                    else:
                        increment = 300
                    if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or \
                            self.events['ctrl_release']:
                        self.slider_origin = event.mouse_region_x
                        self.previous_value = self.adjust_me.strength

                    if self.events['type'] == 'C' and self.events['value'] == 'PRESS':
                        if self.adjust_me == radius_01_modifier:
                            self.adjust_me = radius_02_modifier
                        elif self.adjust_me == radius_02_modifier:
                            self.adjust_me = radius_01_modifier
                        self.previous_value = self.adjust_me.strength
                        self.slider_origin = event.mouse_region_x

                    self.adjust_me.strength = self.previous_value + (
                            (event.mouse_region_x - self.slider_origin) / increment)
                    if enter_value_validation(self.enter_value, event)[0]:
                        self.adjust_me.strength = enter_value_validation(self.enter_value, event)[1]
                        self.end_of_adjustment()

                    if event.type == 'V' and event.value == 'PRESS':
                        del self.pie_menu_history[-1]
                        self.end_of_adjustment()
                        self.action = 'DUCT_RATIO'
                        return {'RUNNING_MODAL'}

        # ring #########################################
        if self.action == 'RING_PICK':
            self.screen_text.append(['Pick an object', 'Left click'])
            self.screen_text.append(['Cancel', 'ESC'])
            if event.type == 'ESC' and event.value == 'PRESS':
                self.action = None

        if self.action == 'RING_PICK' and event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            obj = None
            obj = click_on(event.mouse_region_x, event.mouse_region_y)
            if obj:
                self.add_ring(obj)
                self.action = None

        # connector ##################################
        if self.action == 'CONNECTOR_PICK':
            self.screen_text.append(['Pick an object', 'Left click'])
            self.screen_text.append(['Cancel', 'ESC'])
            if event.type == 'ESC' and event.value == 'PRESS':
                self.action = None

        if self.action == 'CONNECTOR_REMOVE':
            the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
            the_modifier['Input_1'] = None
            the_modifier.show_viewport = False
            the_modifier.show_viewport = True
            self.action = None

        if self.action == 'CONNECTOR_SCALE' and not self.events['mouse_left_click']:
            the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
            the_input = 'Input_33'
            if self.enter_value != 'None':
                self.screen_text.append(['Scale', str(self.enter_value)])
            else:
                self.screen_text.append(['Scale', str(round(the_modifier[the_input], 5))])

            self.number_adjustment(the_modifier, the_input, 400, event, 'FLOAT')

        if self.action == 'CONNECTOR_PICK' and event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            obj = None
            obj = click_on(event.mouse_region_x, event.mouse_region_y)
            if obj:
                geo_node = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                geo_node['Input_1'] = obj
                self.action = None
                geo_node.show_viewport = False
                geo_node.show_viewport = True

        # utilities ####################################
        if self.action == 'REUSE':
            self.screen_text.append(['Pick another wire', 'Left click'])
            self.screen_text.append(['Cancel', 'ESC'])
        if self.action == 'REUSE' and event.value == 'PRESS' and event.type == 'LEFTMOUSE':
            obj_source = click_on(event.mouse_region_x, event.mouse_region_y)
            if obj_source and obj_source.get('fluent_type') == 'pipe':
                self.action = None
                the_modifier_source = obj_source.modifiers['.f_geometry_nodes']
                if the_modifier_source:
                    the_modifier = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes']
                    copy_gn_mod_inputs(the_modifier, obj_source)
                    the_modifier.show_viewport = False
                    the_modifier.show_viewport = True
                # recopie les paramètre du bevel
                bevel_source = obj_source.modifiers['BEVEL']
                bevel_data = get_modifier_values(bevel_source)
                set_modifier_value(self.fluent_curve['curve_obj'].modifiers['BEVEL'], bevel_data)

        if self.action == 'RESET':
            bpy.data.objects.remove(self.fluent_curve['curve_obj'], do_unlink=True)
            self.fluent_curve['added'] = False
            self.put_curve()

        # sortie ##############################################
        if self.action == 'CANCELLED':
            if self.operation == 'ADD':
                try:
                    bpy.data.objects.remove(self.fluent_curve['curve_obj'], do_unlink=True)
                except:
                    pass
            context.window_manager.event_timer_remove(self.timer)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        if event.value == 'PRESS' and event.type == 'W':
            if self.fluent_curve['curve_obj'].show_wire:
                self.fluent_curve['curve_obj'].show_wire = False
                try:
                    self.fluent_curve['wire_obj'].show_wire = False
                except:pass
            else:
                self.fluent_curve['curve_obj'].show_wire = True
                try:
                    self.fluent_curve['wire_obj'].show_wire = True
                except:pass

        if event.value == 'PRESS' and event.type == 'RIGHTMOUSE' or self.action == 'FINISHED':
            self.fluent_curve['ring_nodes'] = []
            self.fluent_curve['curve_obj']['fluent_pipe_data'] = self.fluent_curve
            self.fluent_curve['curve_obj']['fluent_type'] = 'pipe'
            try:
                bpy.data.collections['Wire_Objects'].objects.link(self.fluent_curve['curve_obj'])
                bpy.context.scene.collection.objects.unlink(self.fluent_curve['curve_obj'])
            except:pass
            context.window_manager.event_timer_remove(self.timer)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        self.screen_text.append(['Align the ends', 'X/Y/Z'])

        self.side_infos.reset()
        for i, j in enumerate(self.screen_text):
            self.side_infos.add_line(j[0], j[1])

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.fluent_curve = {
            'added': False,
            'curve_obj': None,
            'ring_nodes': [],
            'first_point': None,
            'second_point': None,
            'root_length': 0.2,
            'path': [],
            'combinaison': 2,
        }
        self.adjustment = None

        self.build_step = None

        self.wire_style = None

        self.simulation_data = {
        'bevel_depth':0,
        'bevel_resolution':0
        }

        self.current_ring_node = None

        # affichage
        self.ui_items_list = []
        self.side_infos = FLUENT_Panel_Infos()
        self.screen_text = []
        self.ui_items_list.append(self.side_infos)
        self.draw_dots = FLUENT_Draw_Dots()
        self.ui_items_list.append(self.draw_dots)
        self.pie_menu_history = []
        self.value_animation = {
            'input':None,
            'v0':None,
            't0': None,
            'strength':0.1,
            'step':'WAIT' # WAIT ou RUNNING
        }
        self.delay = None

        self.events = event_dico_builder(event)

        self.display_menu = None
        self.action = None
        self.previous_value = None
        self.adjust_me = None
        self.slider_origin = None
        self.other_adjustment = None
        self.enter_value = 'None'

        self.previous_radius = None

        self.cast = None
        self.snap_face_center = True

        self.wire_menu = wire_ui()
        self.wire_ring_menu = wire_ring_ui()
        self.array_menu = wire_array_ui()
        self.extra_menu = wire_extra_ui()
        self.coil_menu = wire_coil_ui()
        self.utilities_menu = wire_utilities_ui()
        self.duct_menu = wire_duct_ui()
        self.connector_menu = wire_connector_ui()

        button = make_button('CANCEL')
        self.ui_items_list.append(button)

        if self.operation == 'EDIT':
            obj = active_object('GET')
            self.fluent_curve['ring_nodes'] = []
            self.fluent_curve = {
                'added': True,
                'curve_obj': obj,
                'ring_nodes': [],
                'root_length': obj['fluent_pipe_data']['root_length'],
                'path': [
                    Vector((obj['fluent_pipe_data']['path'][0][0], obj['fluent_pipe_data']['path'][0][1], obj['fluent_pipe_data']['path'][0][2])),
                    Vector((obj['fluent_pipe_data']['path'][1][0], obj['fluent_pipe_data']['path'][1][1], obj['fluent_pipe_data']['path'][1][2])),
                    Vector((obj['fluent_pipe_data']['path'][2][0], obj['fluent_pipe_data']['path'][2][1], obj['fluent_pipe_data']['path'][2][2])),
                    Vector((obj['fluent_pipe_data']['path'][3][0], obj['fluent_pipe_data']['path'][3][1], obj['fluent_pipe_data']['path'][3][2])),
                    Vector((obj['fluent_pipe_data']['path'][4][0], obj['fluent_pipe_data']['path'][4][1], obj['fluent_pipe_data']['path'][4][2])),
                    Vector((obj['fluent_pipe_data']['path'][5][0], obj['fluent_pipe_data']['path'][5][1], obj['fluent_pipe_data']['path'][5][2])),
                ],
                'combinaison': obj['fluent_pipe_data']['combinaison'],
                'first_point': {
                    'hit': Vector((obj['fluent_pipe_data']['first_point']['hit'][0], obj['fluent_pipe_data']['first_point']['hit'][1], obj['fluent_pipe_data']['first_point']['hit'][2])),
                    'normal': Vector((obj['fluent_pipe_data']['first_point']['normal'][0], obj['fluent_pipe_data']['first_point']['normal'][1], obj['fluent_pipe_data']['first_point']['normal'][2]))
                },
                'second_point': {
                    'hit': Vector((obj['fluent_pipe_data']['second_point']['hit'][0], obj['fluent_pipe_data']['second_point']['hit'][1], obj['fluent_pipe_data']['second_point']['hit'][2])),
                    'normal': Vector((obj['fluent_pipe_data']['second_point']['normal'][0], obj['fluent_pipe_data']['second_point']['normal'][1], obj['fluent_pipe_data']['second_point']['normal'][2]))
                }
            }
            geo_node = self.fluent_curve['curve_obj'].modifiers['.f_geometry_nodes'].node_group
            for n in geo_node.nodes:
                if n.type == 'GROUP' and n.node_tree.name == 'f_add_pipe_ring' and n.inputs['Object'].default_value:
                    self.fluent_curve['ring_nodes'].append(n)
            if len(self.fluent_curve['ring_nodes']):
                self.current_ring_node = self.fluent_curve['ring_nodes'][-1]
            self.pie_menu_history.append(self.wire_menu)

        if not bpy.data.collections.get('Wire_Objects'):
            coll = bpy.data.collections.new("Wire_Objects")
            bpy.context.scene.collection.children.link(coll)

        active_object(self.fluent_curve['curve_obj'], 'SET', True)

        args = (self, context)
        self.timer = context.window_manager.event_timer_add(0.04, window=context.window)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


classes = [FLUENT_OT_Pipe]