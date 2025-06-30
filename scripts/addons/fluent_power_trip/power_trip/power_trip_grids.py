import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from ..independant_helpers import *
from ..helpers import *
from ..viewport_drawing import *
from ..ui_button import *


def grid_list_ui():
    # menu box
    pie_menu = FLUENT_Ui_Layout('GRID_LIST')
    pie_menu.set_layout('PIE')

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Square')
    button.set_shape('CIRCLE')
    button.set_icon('square')
    button.set_action('ADD_SQUARE')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Circle')
    button.set_shape('CIRCLE')
    button.set_icon('circle')
    button.set_action('ADD_CIRCLE')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Staggered circle')
    button.set_shape('CIRCLE')
    button.set_icon('circle_staggered')
    button.set_action('ADD_CIRCLE-STAGGERED')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Diamond')
    button.set_shape('CIRCLE')
    button.set_icon('diamond')
    button.set_action('ADD_DIAMOND')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Hexagon')
    button.set_shape('CIRCLE')
    button.set_icon('hexagon')
    button.set_action('ADD_HEXAGON')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Triangle')
    button.set_shape('CIRCLE')
    button.set_icon('triangle')
    button.set_action('ADD_TRIANGLE')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Alpha')
    button.set_shape('CIRCLE')
    button.set_icon('alpha')
    button.set_action('ADD_ALPHA')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Beta')
    button.set_shape('CIRCLE')
    button.set_icon('beta')
    button.set_action('ADD_BETA')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Gamma')
    button.set_shape('CIRCLE')
    button.set_icon('gamma')
    button.set_action('ADD_GAMMA')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Omega')
    button.set_shape('CIRCLE')
    button.set_icon('omega')
    button.set_action('ADD_OMEGA')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Sigma')
    button.set_shape('CIRCLE')
    button.set_icon('sigma')
    button.set_action('ADD_SIGMA')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Epsilon')
    button.set_shape('CIRCLE')
    button.set_icon('epsilon')
    button.set_action('ADD_EPSILON')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Zeta')
    button.set_shape('CIRCLE')
    button.set_icon('zeta')
    button.set_action('ADD_ZETA')
    pie_menu.add_item(button)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def grid_adjust_ui():
    pie_menu = FLUENT_Ui_Layout('ADJUSTMENTS')
    pie_menu.set_layout('PIE')

    button = make_button('QUIT')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Change')
    button.set_shape('CIRCLE')
    button.set_icon('change')
    button.set_action('CHANGE')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Thickness')
    button.set_shape('CIRCLE')
    button.set_icon('first_solidify')
    button.set_action('THICKNESS')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Position')
    button.set_shape('CIRCLE')
    button.set_icon('height')
    button.set_action('DISPLACE')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('Hole size')
    # button.set_tool_tip('Off')
    button.set_shape('RECTANGLE')
    # button.set_icon('thickness')
    button.set_action('HOLE_SIZE')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Scale')
    button.set_shape('CIRCLE')
    button.set_icon('scale')
    button.set_action('SCALE')
    pie_menu.add_item(button)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def solidify_ui():
    pie_menu = FLUENT_Ui_Layout('SOLIDIFY')
    pie_menu.set_layout('PIE')

    button = make_button('VALIDATE')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('Thickness')
    # button.set_tool_tip('Off')
    button.set_shape('RECTANGLE')
    # button.set_icon('thickness')
    button.set_action('THICKNESS')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('Offset')
    # button.set_tool_tip('Off')
    button.set_shape('RECTANGLE')
    # button.set_icon('thickness')
    button.set_action('OFFSET')
    pie_menu.add_item(button)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def displace_ui():
    pie_menu = FLUENT_Ui_Layout('DISPLACE')
    pie_menu.set_layout('PIE')

    button = make_button('VALIDATE')
    pie_menu.add_item(button)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def scale_ui():
    pie_menu = FLUENT_Ui_Layout('SCALE')
    pie_menu.set_layout('PIE')

    button = make_button('VALIDATE')
    pie_menu.add_item(button)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def hole_ui():
    pie_menu = FLUENT_Ui_Layout('HOLE')
    pie_menu.set_layout('PIE')

    button = make_button('VALIDATE')
    pie_menu.add_item(button)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


class FLUENT_OT_Grids(Operator):
    """Place a grid
Select a Fluent boolean before."""
    bl_idname = "fluent.grids"
    bl_label="Place a grid"
    bl_options={'REGISTER','UNDO'}

    operation: StringProperty(
        default=''
    )

    def adjustment(self):
        what = self.statut.split('#')[1]
        if 'SOLIDIFY' in what:
            solidify = self.fluent_grid['grid_obj'].modifiers['Solidify']
            if 'THICKNESS' in what:
                if self.events['shift_work']:
                    increment = 3000
                elif self.events['ctrl_work']:
                    increment = 30
                else:
                    increment = 300

                if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or self.events['ctrl_release']:
                    self.slider_origin_x = self.events['mouse_x']
                    self.previous_value = solidify.thickness

                solidify.thickness = self.previous_value + ((self.events['mouse_x'] - self.slider_origin_x)/increment)
                for c in self.fluent_grid['grid_obj'].children:
                    c.modifiers['Solidify'].thickness = solidify.thickness
        elif 'DISPLACE' in what:
            displace = self.fluent_grid['grid_obj'].modifiers['Displace_Z']
            if self.events['shift_work']:
                increment = 3000
            elif self.events['ctrl_work']:
                increment = 30
            else:
                increment = 300

            if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or self.events['ctrl_release']:
                self.slider_origin_x = self.events['mouse_x']
                self.previous_value = displace.strength

            displace.strength = self.previous_value + ((self.events['mouse_x'] - self.slider_origin_x)/increment)
            for c in self.fluent_grid['grid_obj'].children:
                c.modifiers['Displace_Z'].strength = displace.strength
        elif 'SCALE' in what:
            if self.events['shift_work']:
                increment = 3000
            elif self.events['ctrl_work']:
                increment = 30
            else:
                increment = 300

            if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or self.events['ctrl_release']:
                self.slider_origin_x = self.events['mouse_x']
                self.previous_value = self.fluent_grid['grid_obj'].scale.copy()

            self.fluent_grid['grid_obj'].scale = self.previous_value * (1+(self.events['mouse_x'] - self.slider_origin_x)/increment)
        elif 'HOLE' in what:
            key = self.fluent_grid['grid_obj'].data.shape_keys.key_blocks['HOLE_SIZE']
            if self.events['shift_work']:
                increment = 3000
            elif self.events['ctrl_work']:
                increment = 30
            else:
                increment = 300

            if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or self.events['ctrl_release']:
                self.slider_origin_x = self.events['mouse_x']
                self.previous_value = key.value

            key.value = self.previous_value + ((self.events['mouse_x'] - self.slider_origin_x)/increment)
            for c in self.fluent_grid['grid_obj'].children:
                c.data.shape_keys.key_blocks['HOLE_SIZE'].value = key.value

    def end(self, cancel=False):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        if cancel:
            if self.fluent_grid.get('grid_obj'):
                for c in self.fluent_grid['grid_obj'].children:
                    bpy.data.objects.remove(c, do_unlink=True)
                bpy.data.objects.remove(self.fluent_grid['grid_obj'], do_unlink=True)
                self.fluent_grid['gid_obj'] = None

    def adjust_size(self):
        obj = self.fluent_grid['grid_obj']
        bool = self.fluent_grid['bool_obj']

        obj.modifiers['Array_X'].count = 1
        obj.modifiers['Array_Y'].count = 1

        has_boolean = []
        for m in obj.modifiers:
            if m.type == "BOOLEAN" and m.show_viewport:
                m.show_viewport = m.show_render = False
                has_boolean.append(m)

        # desactive temporairement les mirrors et arrays
        has_mirror = []
        has_array = []
        for m in bool.modifiers:
            if m.type == "MIRROR" and m.show_viewport:
                m.show_viewport = False
                m.show_render = False
                has_mirror.append(m)
            if m.type == "ARRAY" and m.show_viewport:
                m.show_viewport = m.show_render = False
                has_array.append(m)
        for m in obj.modifiers:
            if 'from_bool' in m.name or 'to_center' in m.name:
                m.show_viewport = False
                m.show_render = False

        depsgraph = bpy.context.evaluated_depsgraph_get()
        depsgraph.id_type_updated('OBJECT')
        dim_x = obj.dimensions[0]
        dim_y = obj.dimensions[1]

        for i in range(500):
            obj.modifiers['Array_X'].count += 1
            depsgraph = bpy.context.evaluated_depsgraph_get()
            depsgraph.id_type_updated('OBJECT')
            if obj.dimensions[0] > bool.dimensions[0] * 1.02:
                break

        for i in range(500):
            obj.modifiers['Array_Y'].count += 1
            depsgraph = bpy.context.evaluated_depsgraph_get()
            depsgraph.id_type_updated('OBJECT')
            if obj.dimensions[1] > bool.dimensions[1] * 1.02:
                break

        print('--- 03')
        depsgraph = bpy.context.evaluated_depsgraph_get()
        depsgraph.id_type_updated('OBJECT')
        obj.modifiers['Displace_X'].strength = obj.dimensions[0] / obj.scale[0] * (-1) + dim_x / obj.scale[0]
        obj.modifiers['Displace_Y'].strength = obj.dimensions[1] / obj.scale[1] * (-1) + dim_y / obj.scale[0]

        # pour les grilles multi-objets on répète sur les enfants
        for c in obj.children:
            c.modifiers['Array_X'].count = obj.modifiers['Array_X'].count
            c.modifiers['Array_Y'].count = obj.modifiers['Array_Y'].count
            c.modifiers['Displace_X'].strength = obj.modifiers['Displace_X'].strength
            c.modifiers['Displace_Y'].strength = obj.modifiers['Displace_Y'].strength

        # réactive les mirrors et arrays
        bool_dimensions = bool.dimensions.copy()
        grid_dimensions = obj.dimensions.copy()

        for a in has_array:
            a.show_viewport = a.show_render = True
            if fluent_modifiers_name['array_x'] in a.name:
                obj.modifiers['ArrayX_from_bool'].relative_offset_displace[0] = bool_dimensions[0] * bool.modifiers[
                    fluent_modifiers_name['array_x']].relative_offset_displace[0] / grid_dimensions[0]
                obj.modifiers['ArrayX_from_bool'].relative_offset_displace[1] = 0
                obj.modifiers['ArrayX_from_bool'].relative_offset_displace[2] = 0
                obj.modifiers['ArrayX_from_bool'].count = a.count
                obj.modifiers['ArrayX_from_bool'].show_viewport = True
                obj.modifiers['ArrayX_from_bool'].show_render = True
                # pour les grilles multi-objets on répète sur les enfants
                for c in obj.children:
                    c.modifiers['ArrayX_from_bool'].relative_offset_displace[0] = \
                    obj.modifiers['ArrayX_from_bool'].relative_offset_displace[0]
                    c.modifiers['ArrayX_from_bool'].relative_offset_displace[1] = 0
                    c.modifiers['ArrayX_from_bool'].relative_offset_displace[2] = 0
                    c.modifiers['ArrayX_from_bool'].count = a.count
                    c.modifiers['ArrayX_from_bool'].show_viewport = True
                    c.modifiers['ArrayX_from_bool'].show_render = True
            elif fluent_modifiers_name['array_y'] in a.name:
                obj.modifiers['ArrayY_from_bool'].relative_offset_displace[1] = bool_dimensions[1] * bool.modifiers[
                    fluent_modifiers_name['array_y']].relative_offset_displace[1] / grid_dimensions[1]
                obj.modifiers['ArrayY_from_bool'].relative_offset_displace[0] = 0
                obj.modifiers['ArrayY_from_bool'].relative_offset_displace[2] = 0
                obj.modifiers['ArrayY_from_bool'].count = a.count
                obj.modifiers['ArrayY_from_bool'].show_viewport = True
                obj.modifiers['ArrayY_from_bool'].show_render = True
                # pour les grilles multi-objets on répète sur les enfants
                for c in obj.children:
                    c.modifiers['ArrayY_from_bool'].relative_offset_displace[1] = \
                    obj.modifiers['ArrayY_from_bool'].relative_offset_displace[1]
                    c.modifiers['ArrayY_from_bool'].relative_offset_displace[0] = 0
                    c.modifiers['ArrayY_from_bool'].relative_offset_displace[2] = 0
                    c.modifiers['ArrayY_from_bool'].count = a.count
                    c.modifiers['ArrayY_from_bool'].show_viewport = True
                    c.modifiers['ArrayY_from_bool'].show_render = True
            elif fluent_modifiers_name['array_z'] in a.name:
                obj.modifiers['ArrayZ_from_bool'].relative_offset_displace[2] = bool_dimensions[2] * bool.modifiers[
                    fluent_modifiers_name['array_z']].relative_offset_displace[2] / grid_dimensions[2]
                obj.modifiers['ArrayZ_from_bool'].relative_offset_displace[0] = 0
                obj.modifiers['ArrayZ_from_bool'].relative_offset_displace[1] = 0
                obj.modifiers['ArrayZ_from_bool'].count = a.count
                obj.modifiers['ArrayZ_from_bool'].show_viewport = True
                obj.modifiers['ArrayZ_from_bool'].show_render = True
                # pour les grilles multi-objets on répète sur les enfants
                for c in obj.children:
                    c.modifiers['ArrayZ_from_bool'].relative_offset_displace[2] = \
                    obj.modifiers['ArrayZ_from_bool'].relative_offset_displace[2]
                    c.modifiers['ArrayZ_from_bool'].relative_offset_displace[0] = 0
                    c.modifiers['ArrayZ_from_bool'].relative_offset_displace[1] = 0
                    c.modifiers['ArrayZ_from_bool'].count = a.count
                    c.modifiers['ArrayZ_from_bool'].show_viewport = True
                    c.modifiers['ArrayZ_from_bool'].show_render = True
        try:
            center_array_x_bool = bool.modifiers[fluent_modifiers_name['center_array_x']]
            center_array_y_bool = bool.modifiers[fluent_modifiers_name['center_array_y']]
        except:
            center_array_x_bool = False
            center_array_y_bool = False
        if center_array_x_bool and center_array_y_bool:
            if center_array_x_bool.show_viewport and center_array_x_bool.strength:
                scale = obj.scale.copy()
                obj.scale[0] = 1
                obj.scale[1] = 1
                obj.scale[2] = 1
                N = obj.modifiers['ArrayX_from_bool'].count
                obj.modifiers['ArrayX_from_bool'].show_viewport = False
                depsgraph = bpy.context.evaluated_depsgraph_get()
                depsgraph.id_type_updated('OBJECT')
                d = obj.dimensions[0]
                obj.modifiers['ArrayX_from_bool'].show_viewport = True
                offset = obj.modifiers['ArrayX_from_bool'].relative_offset_displace[0]
                obj.modifiers['DisplaceX_to_center'].strength = ((N - 1) * (d * offset)) * -1
                obj.modifiers['DisplaceX_to_center'].show_viewport = True
                obj.modifiers['DisplaceX_to_center'].show_render = True
                obj.scale = scale.copy()
                for c in obj.children:
                    c.modifiers['DisplaceX_to_center'].strength = obj.modifiers['DisplaceX_to_center'].strength
                    c.modifiers['DisplaceX_to_center'].show_viewport = True
                    c.modifiers['DisplaceX_to_center'].show_render = True
            else:
                obj.modifiers['DisplaceX_to_center'].show_viewport = False
                obj.modifiers['DisplaceX_to_center'].show_render = False
                for c in obj.children:
                    c.modifiers['DisplaceX_to_center'].show_viewport = False
                    c.modifiers['DisplaceX_to_center'].show_render = False
            if center_array_y_bool.show_viewport and center_array_y_bool.strength:
                scale = obj.scale.copy()
                obj.scale[0] = 1
                obj.scale[1] = 1
                obj.scale[2] = 1
                N = obj.modifiers['ArrayY_from_bool'].count
                obj.modifiers['ArrayY_from_bool'].show_viewport = False
                depsgraph = bpy.context.evaluated_depsgraph_get()
                depsgraph.id_type_updated('OBJECT')
                d = obj.dimensions[1]
                obj.modifiers['ArrayY_from_bool'].show_viewport = True
                offset = obj.modifiers['ArrayY_from_bool'].relative_offset_displace[1]
                obj.modifiers['DisplaceY_to_center'].strength = ((N - 1) * (d * offset)) * -1
                obj.modifiers['DisplaceY_to_center'].show_viewport = True
                obj.modifiers['DisplaceY_to_center'].show_render = True
                obj.scale = scale.copy()
                for c in obj.children:
                    c.modifiers['DisplaceY_to_center'].strength = obj.modifiers['DisplaceY_to_center'].strength
                    c.modifiers['DisplaceY_to_center'].show_viewport = True
                    c.modifiers['DisplaceY_to_center'].show_render = True
            else:
                obj.modifiers['DisplaceY_to_center'].show_viewport = False
                obj.modifiers['DisplaceY_to_center'].show_render = False
                for c in obj.children:
                    c.modifiers['DisplaceY_to_center'].show_viewport = False
                    c.modifiers['DisplaceY_to_center'].show_render = False

        for mirror in has_mirror:
            mirror.show_viewport = True
            mirror.show_render = True
            obj.modifiers['Mirror_from_bool'].use_axis[0] = mirror.use_axis[0]
            obj.modifiers['Mirror_from_bool'].use_axis[1] = mirror.use_axis[1]
            obj.modifiers['Mirror_from_bool'].use_axis[2] = mirror.use_axis[2]
            obj.modifiers['Mirror_from_bool'].use_bisect_flip_axis[0] = mirror.use_bisect_flip_axis[0]
            obj.modifiers['Mirror_from_bool'].use_bisect_flip_axis[1] = mirror.use_bisect_flip_axis[1]
            obj.modifiers['Mirror_from_bool'].use_bisect_flip_axis[2] = mirror.use_bisect_flip_axis[2]
            obj.modifiers['Mirror_from_bool'].mirror_object = mirror.mirror_object
            obj.modifiers['Mirror_from_bool'].show_viewport = True
            obj.modifiers['Mirror_from_bool'].show_render = True

        for bool in has_boolean:
            bool.show_viewport = True
            bool.show_render = True

    def add_grid(self, type):
        # si grille déjà présente, la supprimer
        if self.fluent_grid.get('grid_obj'):
            for c in self.fluent_grid['grid_obj'].children:
                bpy.data.objects.remove(c, do_unlink=True)
            bpy.data.objects.remove(self.fluent_grid['grid_obj'], do_unlink=True)
            self.fluent_grid['gid_obj'] = None
        if type == 'DIAMOND':
            file_path_wire = os.path.dirname(realpath(__file__)) + "/grids/grid_diamond.blend/Object/"
            bpy.ops.wm.append(filename='Grid_Diamond', directory=file_path_wire)
        elif type == 'CIRCLE-STAGGERED':
            file_path_wire = os.path.dirname(realpath(__file__)) + "/grids/grid_circle_staggered.blend/Object/"
            bpy.ops.wm.append(filename='Grid_Circle_Staggered', directory=file_path_wire)
        elif type == 'CIRCLE':
            print('--- import non staggered')
            file_path_wire = os.path.dirname(realpath(__file__)) + "/grids/grid_circle.blend/Object/"
            bpy.ops.wm.append(filename='Grid_Circle', directory=file_path_wire)
        elif type == 'HEXAGON':
            file_path_wire = os.path.dirname(realpath(__file__)) + "/grids/grid_hex.blend/Object/"
            bpy.ops.wm.append(filename='Grid_Hex', directory=file_path_wire)
        elif type == 'TRIANGLE':
            file_path_wire = os.path.dirname(realpath(__file__)) + "/grids/grid_triangle.blend/Object/"
            bpy.ops.wm.append(filename='Grid_Triangle', directory=file_path_wire)
        elif type == 'DELTA':
            file_path_wire = os.path.dirname(realpath(__file__)) + "/grids/grid_delta.blend/Object/"
            bpy.ops.wm.append(filename='Grid_Delta', directory=file_path_wire)
        elif type == 'ALPHA':
            file_path_wire = os.path.dirname(realpath(__file__)) + "/grids/grid_alpha.blend/Object/"
            bpy.ops.wm.append(filename='Grid_Alpha', directory=file_path_wire)
        elif type == 'BETA':
            file_path_wire = os.path.dirname(realpath(__file__)) + "/grids/grid_beta.blend/Object/"
            bpy.ops.wm.append(filename='Grid_Beta', directory=file_path_wire)
        elif type == 'GAMMA':
            file_path_wire = os.path.dirname(realpath(__file__)) + "/grids/grid_gamma.blend/Object/"
            bpy.ops.wm.append(filename='Grid_Gamma', directory=file_path_wire)
        elif type == 'OMEGA':
            file_path_wire = os.path.dirname(realpath(__file__)) + "/grids/grid_omega.blend/Object/"
            bpy.ops.wm.append(filename='Grid_Omega', directory=file_path_wire)
        elif type == 'SIGMA':
            file_path_wire = os.path.dirname(realpath(__file__)) + "/grids/grid_sigma.blend/Object/"
            bpy.ops.wm.append(filename='Grid_Sigma', directory=file_path_wire)
        elif type == 'SQUARE':
            file_path_wire = os.path.dirname(realpath(__file__)) + "/grids/grid_square.blend/Object/"
            bpy.ops.wm.append(filename='Grid_Square', directory=file_path_wire)
        elif type == 'EPSILON':
            file_path_wire = os.path.dirname(realpath(__file__)) + "/grids/grid_epsilon.blend/Object/"
            bpy.ops.wm.append(filename='Grid_Epsilon', directory=file_path_wire)
        elif type == 'ZETA':
            bpy.ops.object.select_all(action='DESELECT')
            file_path_wire = os.path.dirname(realpath(__file__)) + "/grids/grid_zeta.blend/Object/"
            bpy.ops.wm.append(filename='Zeta.002', directory=file_path_wire)
            children_01 = bpy.context.selected_objects[0]
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.wm.append(filename='Zeta.003', directory=file_path_wire)
            children_02 = bpy.context.selected_objects[0]
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.wm.append(filename='Grid_Zeta', directory=file_path_wire)
            grid = bpy.context.selected_objects[0]
            children_01.parent = grid
            children_02.parent = grid
        grid = bpy.context.selected_objects[0]
        grid.select_set(False)
        grid.location = self.fluent_grid['bool_obj'].matrix_world.translation
        grid.rotation_euler = self.fluent_grid['bool_obj'].matrix_world.to_euler('XYZ')
        self.fluent_grid['grid_obj'] = grid
        scaling = (self.fluent_grid['bool_obj'].dimensions[1] / 10) / self.fluent_grid['grid_obj'].dimensions[1]
        self.fluent_grid['grid_obj'].scale = [scaling, scaling, scaling]
        self.adjust_size()

        self.fluent_grid['grid_obj']['fluent_type'] = 'grid'
        self.fluent_grid['grid_obj'].select_set(True)
        active_object('SET', self.fluent_grid['bool_obj'])
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        bpy.ops.object.select_all(action='DESELECT')

    def modal(self, context, event):
        self.ui_items_list = [i for i in self.ui_items_list if not (type(i) is FLUENT_Ui_Layout and i.get_layout() in ['PIE', 'MIRROR', 'TAPER'])]
        self.ui_items_list.append(self.pie_menu_history[-1])
        context.area.tag_redraw()
        self.events = event_dico_refresh(self.events, event)

        if pass_through(event):
            return {'PASS_THROUGH'}

        # action via les bouttons
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

        # action des raccourcis
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            action = 'FINISHED'
        elif event.type == 'ESC' and event.value == 'PRESS':
            action = 'CANCELLED'

        if action:
            if action == 'FINISHED':
                self.end()
                return {'FINISHED'}
            elif action == 'CANCELLED':
                self.end(cancel=True)
                return {'FINISHED'}
            elif action == 'VALIDATE':
                del self.pie_menu_history[-1]
                if 'ADJUST' in self.statut:
                    if 'SCALE' in self.statut.split('#')[1]:
                        self.adjust_size()
                    self.statut = 'GRID_ADDED'
            elif action == 'CHANGE':
                del self.pie_menu_history[-1]
                self.statut = 'WAIT_SELECTION_GRID'
            elif 'ADD_' in action:
                self.add_grid(action.split('_')[1])
                self.statut = 'GRID_ADDED'
                self.pie_menu_history.append(self.pie_menu_adjust)
            elif action == 'THICKNESS':
                self.pie_menu_history.append(self.solidify_menu)
                self.statut = 'ADJUST#SOLIDIFY_THICKNESS'
                self.slider_origin_x = self.events['mouse_x']
                self.previous_value = self.fluent_grid['grid_obj'].modifiers['Solidify'].thickness
            elif action == 'DISPLACE':
                self.pie_menu_history.append(self.displace_menu)
                self.statut = 'ADJUST#DISPLACE'
                self.slider_origin_x = self.events['mouse_x']
                self.previous_value = self.fluent_grid['grid_obj'].modifiers['Displace_Z'].strength
            elif action == 'SCALE':
                self.pie_menu_history.append(self.displace_menu)
                self.statut = 'ADJUST#SCALE'
                self.slider_origin_x = self.events['mouse_x']
                self.previous_value = self.fluent_grid['grid_obj'].scale.copy()
            elif action == 'HOLE_SIZE':
                self.pie_menu_history.append(self.displace_menu)
                self.statut = 'ADJUST#HOLE'
                self.slider_origin_x = self.events['mouse_x']
                self.previous_value = self.fluent_grid['grid_obj'].data.shape_keys.key_blocks['HOLE_SIZE'].value

        # gestion affichage du pie menu
        if self.events['mouse_left_click']:
            for b in self.pie_menu_history[-1].get_items():
                try:
                    b.set_show(True)
                except:
                    print('--- ERROR Impossible to show button')
        else:
            if self.pie_menu_history[-1].get_layout() not in ['MIRROR', 'TAPER']:
                self.pie_menu_history[-1].spread(self.events['mouse_x'], self.events['mouse_y'])
                for b in self.pie_menu_history[-1].get_items():
                    try:
                        b.set_show(False)
                    except:
                        print('--- ERROR Impossible to hide button')

        if 'ADJUST' in self.statut and not self.events['mouse_left_click']:
            self.adjustment()

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # vérification
        self.fluent_grid = {}
        if self.operation == 'ADD':
            self.fluent_grid['bool_obj'] = active_object()
            if not self.fluent_grid['bool_obj'] or \
                not self.fluent_grid['bool_obj'].get('fluent_type') or \
                self.fluent_grid['bool_obj'].get('fluent_type') in ['unknow']:
                make_oops(['Select a Fluent boolean object'], 'How to use ?', 'ERROR')
                return {'FINISHED'}
            self.statut = 'WAIT_SELECTION_GRID'
        elif self.operation == 'EDIT':
            self.fluent_grid['grid_obj'] = active_object()
            self.fluent_grid['bool_obj'] = self.fluent_grid['grid_obj'].parent
            self.statut = 'GRID_ADDED'

        bpy.ops.object.select_all(action='DESELECT')

        self.ui_items_list = []
        self.pie_menu_history = []
        self.pie_menu_grid_list = grid_list_ui()
        self.pie_menu_adjust = grid_adjust_ui()
        self.solidify_menu = solidify_ui()
        self.displace_menu = displace_ui()
        self.scale_menu = scale_ui()
        self.hole_menu = hole_ui()

        self.events = event_dico_builder(event)
        self.slider_origin_x = 0
        self.previous_value = 0

        self.pie_menu_history.append(self.pie_menu_grid_list)
        if self.statut == 'GRID_ADDED':
            self.pie_menu_history.append(self.pie_menu_adjust)
        # TODO vérifier le fonctionnement du cancel
        button = make_button('CANCEL')
        self.ui_items_list.append(button)

        args = (self, context)

        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


classes = FLUENT_OT_Grids