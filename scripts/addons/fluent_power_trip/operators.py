import bpy
from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty

from .constants import *
from .helpers import *
from .viewport_drawing import *
from .math_functions import *
from .ui_button import *
from .drawing import *
from .modifiers import *
from .bevels import *
from .independant_helpers import *


def box_ui():
    # menu box
    pie_menu = FLUENT_Ui_Layout('BOX')
    pie_menu.set_layout('PIE')

    button = make_button('QUIT')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    button = make_button('SECOND_SOLIDIFY')
    pie_menu.add_item(button)

    button = make_button('TAPER')
    pie_menu.add_item(button)

    button = make_button('SECOND_BEVEL')
    pie_menu.add_item(button)

    button = make_button('FIRST_BEVEL')
    pie_menu.add_item(button)

    button = make_button('FIRST_SOLIDIFY')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    button = make_button('MIRROR')
    pie_menu.add_item(button)

    button = make_button('ARRAY')
    pie_menu.add_item(button)

    button = make_button('CIRCULAR_ARRAY')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def shape_ui():
    # menu shape
    pie_menu = FLUENT_Ui_Layout('POLY')
    pie_menu.set_layout('PIE')

    button = make_button('QUIT')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    button = make_button('CURVE')
    pie_menu.add_item(button)

    button = make_button('SECOND_SOLIDIFY')
    pie_menu.add_item(button)

    button = make_button('TAPER')
    pie_menu.add_item(button)

    button = make_button('SECOND_BEVEL')
    pie_menu.add_item(button)

    button = make_button('FIRST_BEVEL')
    pie_menu.add_item(button)

    button = make_button('FIRST_SOLIDIFY')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    button = make_button('MIRROR')
    pie_menu.add_item(button)

    button = make_button('ARRAY')
    pie_menu.add_item(button)

    button = make_button('CIRCULAR_ARRAY')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def path_ui():
    # menu path
    pie_menu = FLUENT_Ui_Layout('PATH')
    pie_menu.set_layout('PIE')

    button = make_button('QUIT')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    button = make_button('SECOND_SOLIDIFY')
    pie_menu.add_item(button)

    button = make_button('TAPER')
    pie_menu.add_item(button)

    button = make_button('SECOND_BEVEL')
    pie_menu.add_item(button)

    button = make_button('FIRST_BEVEL')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Thickness')
    button.set_shape('CIRCLE')
    button.set_icon('thickness')
    button.set_action('PATH_THICKNESS')
    pie_menu.add_item(button)

    button = FLUENT_Ui_Button()
    button.set_text('')
    button.set_tool_tip('Height')
    button.set_shape('CIRCLE')
    button.set_icon('first_solidify')
    button.set_action('PATH_HEIGHT')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    button = make_button('MIRROR')
    pie_menu.add_item(button)

    button = make_button('ARRAY')
    pie_menu.add_item(button)

    button = make_button('CIRCULAR_ARRAY')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def prism_ui():
    # menu prism
    pie_menu = FLUENT_Ui_Layout('PRISM')
    pie_menu.set_layout('PIE')

    button = make_button('QUIT')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    button = make_button('SECOND_SOLIDIFY')
    pie_menu.add_item(button)

    button = make_button('TAPER')
    pie_menu.add_item(button)

    button = make_button('SECOND_BEVEL')
    pie_menu.add_item(button)

    button = make_button('FIRST_SOLIDIFY')
    pie_menu.add_item(button)

    button = make_button('RESOLUTION')
    pie_menu.add_item(button)

    button = make_button('RADIUS')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    button = make_button('MIRROR')
    pie_menu.add_item(button)

    button = make_button('ARRAY')
    pie_menu.add_item(button)

    button = make_button('CIRCULAR_ARRAY')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def sphere_ui():
    # menu prism
    pie_menu = FLUENT_Ui_Layout('SPHERE')
    pie_menu.set_layout('PIE')

    button = make_button('QUIT')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    button = make_button('SECOND_SOLIDIFY')
    pie_menu.add_item(button)

    button = make_button('TAPER')
    pie_menu.add_item(button)

    button = make_button('RESOLUTION')
    pie_menu.add_item(button)

    button = make_button('RADIUS')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    button = make_button('MIRROR')
    pie_menu.add_item(button)

    button = make_button('ARRAY')
    pie_menu.add_item(button)

    button = make_button('CIRCULAR_ARRAY')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def revolver_ui():
    # menu revolver
    pie_menu = FLUENT_Ui_Layout('PRISM')
    pie_menu.set_layout('PIE')

    button = make_button('QUIT')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    button = FLUENT_Ui_Button()
    button.set_text('Flip')
    button.set_shape('CIRCLE')
    button.set_action('FLIP_SCREW')
    pie_menu.add_item(button)

    button = make_button('SECOND_SOLIDIFY')
    pie_menu.add_item(button)

    button = make_button('TAPER')
    pie_menu.add_item(button)

    button = make_button('SECOND_BEVEL')
    pie_menu.add_item(button)

    button = make_button('FIRST_BEVEL')
    pie_menu.add_item(button)

    button = make_button('RESOLUTION')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    button = make_button('MIRROR')
    pie_menu.add_item(button)

    button = make_button('ARRAY')
    pie_menu.add_item(button)

    button = make_button('CIRCULAR_ARRAY')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def unknow_ui():
    pie_menu = FLUENT_Ui_Layout('UNKNOW')
    pie_menu.set_layout('PIE')

    button = make_button('QUIT')
    pie_menu.add_item(button)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu


def plate_ui():
    # menu box
    pie_menu = FLUENT_Ui_Layout('BOX')
    pie_menu.set_layout('PIE')

    button = make_button('QUIT')
    pie_menu.add_item(button)

    button = make_button('FIRST_SOLIDIFY')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    button = make_button('MIRROR')
    pie_menu.add_item(button)

    pie_menu.add_separator()

    # pie_menu.set_decalage(-2)

    for b in pie_menu.get_items():
        try:
            b.set_show(False)
        except:
            pass
    return pie_menu

# TODO pourvoir faire des presets

class FLUENT_OT_Cutter(Operator):
    bl_idname = "fluent.cutter"
    bl_label = "Fluent cutter"
    bl_options = {'REGISTER', 'UNDO'}

    operation: StringProperty(
        default='CUT'
    )

    def init_variables(self, event):
        self.ui_items_list = []
        self.events = event_dico_builder(event)

        depsgraph = bpy.context.evaluated_depsgraph_get()

        if active_object('GET') and active_object('GET').select_get():
            self.cut_object = active_object('GET')
            remove_empty_bool_modifier(self.cut_object)
            self.cut_object.data.use_auto_smooth = True
            self.cut_object_eval = self.cut_object.evaluated_get(depsgraph)
        else:
            self.cut_object = None

        self.bool_obj = None
        self.fluent_adjustments = None

        self.drawing = FLUENT_Drawing()
        self.ui_items_list.append(self.drawing)

        self.statut = 'EN_ATTENTE_DU_DESSIN'

        self.slider_origin = None

        self.drawing_plane_saved_matrix = None
        self.drawing_plane_saved_vertices_position = []

        button = make_button('CANCEL')
        self.ui_items_list.append(button)

        rectangle_drawing_button = FLUENT_Ui_Button()
        rectangle_drawing_button.set_text('')
        rectangle_drawing_button.set_tool_tip('Rectangle (R)')
        rectangle_drawing_button.set_shape('CIRCLE')
        rectangle_drawing_button.set_action('RECTANGLE')
        rectangle_drawing_button.set_icon('rectangle')
        rectangle_drawing_button.set_active(True)

        circle_drawing_button = FLUENT_Ui_Button()
        circle_drawing_button.set_text('')
        circle_drawing_button.set_tool_tip('Circle (C)')
        circle_drawing_button.set_shape('CIRCLE')
        circle_drawing_button.set_action('PRISM')
        circle_drawing_button.set_icon('prism')

        sphere_drawing_button = FLUENT_Ui_Button()
        sphere_drawing_button.set_text('')
        sphere_drawing_button.set_tool_tip('Sphere')
        sphere_drawing_button.set_shape('CIRCLE')
        sphere_drawing_button.set_action('SPHERE')
        sphere_drawing_button.set_icon('sphere')

        shape_drawing_button = FLUENT_Ui_Button()
        shape_drawing_button.set_text('')
        shape_drawing_button.set_tool_tip('Shape (S)')
        shape_drawing_button.set_shape('CIRCLE')
        shape_drawing_button.set_action('SHAPE')
        shape_drawing_button.set_icon('shape')

        revolver_drawing_button = FLUENT_Ui_Button()
        revolver_drawing_button.set_text('')
        revolver_drawing_button.set_tool_tip('Revolver')
        revolver_drawing_button.set_shape('CIRCLE')
        revolver_drawing_button.set_action('REVOLVER')
        revolver_drawing_button.set_icon('revolver')

        inset_2_button = FLUENT_Ui_Button()
        inset_2_button.set_text('')
        inset_2_button.set_tool_tip('Face inset')
        inset_2_button.set_shape('CIRCLE')
        inset_2_button.set_action('INSET_2')
        inset_2_button.set_icon('inset_2')

        creation_button = FLUENT_Ui_Button()
        creation_button.set_text('')
        creation_button.set_tool_tip('Creation')
        creation_button.set_shape('CIRCLE')
        creation_button.set_action('CREATION')
        creation_button.set_icon('creation')
        if self.operation == 'CREATION':
            creation_button.set_active(True)

        cut_button = FLUENT_Ui_Button()
        cut_button.set_text('')
        cut_button.set_tool_tip('Cut/Add')
        cut_button.set_shape('CIRCLE')
        cut_button.set_action('CUT')
        cut_button.set_icon('cut')
        if self.operation == 'CUT':
            cut_button.set_active(True)

        slice_button = FLUENT_Ui_Button()
        slice_button.set_text('')
        slice_button.set_tool_tip('Slice')
        slice_button.set_shape('CIRCLE')
        slice_button.set_action('SLICE')
        slice_button.set_icon('slice')
        if self.operation == 'SLICE':
            slice_button.set_active(True)

        inset_button = FLUENT_Ui_Button()
        inset_button.set_text('')
        inset_button.set_tool_tip('Inset')
        inset_button.set_shape('CIRCLE')
        inset_button.set_action('INSET')
        inset_button.set_icon('inset')
        if self.operation == 'INSET':
            inset_button.set_active(True)

        row = FLUENT_Ui_Layout('DESSIN')
        row.add_item(creation_button)
        row.add_item(cut_button)
        row.add_item(slice_button)
        row.add_item(inset_button)
        row.add_item(rectangle_drawing_button)
        row.add_item(circle_drawing_button)
        row.add_item(sphere_drawing_button)
        row.add_item(shape_drawing_button)
        row.add_item(revolver_drawing_button)
        row.add_item(inset_2_button)
        row.spread()
        self.ui_items_list.append(row)
        #############################################################################
        widget_rotation = FLUENT_Ui_Layout('GRID_ROTATION')
        widget_rotation.set_obj(self.drawing.get_drawing_plane())

        button = make_button('VALIDATE')
        button.set_action('VALIDATE_ROTATION')
        widget_rotation.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+X_ROT')
        button.set_default_color((.9, 0, 0, 1))
        widget_rotation.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+Y_ROT')
        button.set_default_color((0, .9, 0, 1))
        widget_rotation.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+Z_ROT')
        button.set_default_color((0, 0, .9, 1))
        widget_rotation.add_item(button)

        widget_rotation.set_layout('TAPER')
        self.rot_grid_widget = widget_rotation
        ######################################################################
        #############################################################################
        widget_move = FLUENT_Ui_Layout('GRID_MOVE')
        widget_move.set_obj(self.drawing.get_drawing_plane())

        button = make_button('VALIDATE')
        button.set_action('VALIDATE_MOVE')
        widget_move.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+X_MOVE')
        button.set_default_color((.9, 0, 0, 1))
        widget_move.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+Y_MOVE')
        button.set_default_color((0, .9, 0, 1))
        widget_move.add_item(button)

        widget_move.set_layout('TAPER')
        self.move_grid_widget = widget_move
        ######################################################################
        #############################################################################
        widget_scale = FLUENT_Ui_Layout('GRID_SCALE')
        widget_scale.set_obj(self.drawing.get_drawing_plane())

        button = make_button('VALIDATE')
        button.set_action('VALIDATE_SCALE')
        widget_scale.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+X_SCALE')
        button.set_default_color((.9, 0, 0, 1))
        widget_scale.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+Y_SCALE')
        button.set_default_color((0, .9, 0, 1))
        widget_scale.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+Z_SCALE')
        button.set_default_color((0, 0, .9, 1))
        widget_scale.add_item(button)

        widget_scale.set_layout('TAPER')
        self.scale_grid_widget = widget_scale
        ######################################################################
        column = FLUENT_Ui_Layout('GRID_MANIPULATION')

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_tool_tip('Rotation')
        button.set_shape('CIRCLE')
        button.set_action('GRID_ROTATION')
        button.set_icon('rotation')
        column.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_tool_tip('Move')
        button.set_shape('CIRCLE')
        button.set_action('GRID_MOVE')
        button.set_icon('move')
        column.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_tool_tip('Scale')
        button.set_shape('CIRCLE')
        button.set_action('GRID_SCALE')
        button.set_icon('scale')
        column.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_tool_tip('Align (A)')
        button.set_shape('CIRCLE')
        button.set_action('GRID_ALIGN')
        button.set_icon('align')
        column.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_tool_tip('Resolution (V)')
        button.set_shape('CIRCLE')
        button.set_action('GRID_RESOLUTION')
        button.set_icon('grid_resolution')
        column.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_tool_tip('Square')
        button.set_shape('CIRCLE')
        button.set_action('GRID_SQUARE')
        button.set_icon('to_square')
        column.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_tool_tip('Align to view')
        button.set_shape('CIRCLE')
        button.set_action('GRID_VIEW')
        button.set_icon('align_view')
        column.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_tool_tip('Extend (X)')
        button.set_shape('CIRCLE')
        button.set_action('GRID_EXTENDED')
        button.set_icon('extend')
        button.set_active(True)
        column.add_item(button)

        column.set_layout('COLUMN_LEFT')
        column.spread()

        self.grid_manipulation = column

        self.cursor_infos = FLUENT_Cursor_Infos()
        self.ui_items_list.append(self.cursor_infos)

    def change_de_dessin(self, a):
        self.drawing.set_the_draw_type(a)

    def end(self, option='FINISHED'):
        if self.drawing.get_the_draw()['obj']:
            try:
                bpy.data.objects.remove(self.drawing.get_the_draw()['obj'], do_unlink=True)
            except:
                pass
        if self.drawing.get_drawing_plane():
            try:
                bpy.data.objects.remove(self.drawing.get_drawing_plane(), do_unlink=True)
            except:
                pass

        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')


        try:
            active_object('SET', self.cut_object, True)
        except:pass

    def modal(self, context, event):
        context.area.tag_redraw()

        self.events['mouse_x'] = event.mouse_region_x
        self.events['mouse_y'] = event.mouse_region_y

        self.events['value'] = event.value
        self.events['type'] = event.type

        self.events = event_dico_refresh(self.events, event)

        if pass_through(event):
            return {'PASS_THROUGH'}
        if bpy.context.active_object and bpy.context.active_object.mode == 'EDIT':
            return {'PASS_THROUGH'}

        # action via les bouttons
        action = None
        for b in self.ui_items_list:
            if 'FLUENT_Ui_Button' in str(type(b)):
                b.is_hover(self.events)
                if b.get_state() == 2:
                    action = b.get_action()
                    b.set_state(0)
                    break
                else:
                    action = None
            elif 'FLUENT_Ui_Layout' in str(type(b)):
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

        # action via les raccourcis clavier
        if event.type == 'S' and event.value == 'PRESS':
            action = 'SHAPE'
        elif event.type == 'C' and event.value == 'PRESS':
            action = 'PRISM'
        elif event.type == 'R' and event.value == 'PRESS':
            action = 'RECTANGLE'
        elif event.type == 'Q' and event.value == 'PRESS':
            action = 'FINISHED'
        elif event.type == 'X' and event.value == 'PRESS':
            action = 'GRID_EXTENDED'
        elif event.type == 'ESC' and event.value == 'PRESS':
            action = 'FINISHED'
        elif event.type == 'W' and event.value == 'PRESS':
            try:
                if self.cut_object.show_wire:
                    self.cut_object.show_wire = False
                else:
                    self.cut_object.show_wire = True
            except:pass

        if action:
            self.events['type'] = self.events['value'] = ''
            if action in ['FINISHED', 'CANCELLED']:
                self.end()
                return {'FINISHED'}
            elif action in ['RECTANGLE', 'PRISM', 'SHAPE', 'REVOLVER', 'SPHERE']:
                self.change_de_dessin(action)
                # desactive les autres
                for b in self.ui_items_list:
                    if 'FLUENT_Ui_Button' in str(type(b)):
                        if b.get_action() in ['RECTANGLE', 'PRISM', 'SHAPE', 'REVOLVER', 'SPHERE']:
                            if b.get_action() != action:
                                b.set_active(False)
                            else:
                                b.set_active(True)
                    elif 'FLUENT_Ui_Layout' in str(type(b)):
                        layout_items_list = b.get_items()
                        for bb in layout_items_list:
                            if bb.get_action() in ['RECTANGLE', 'PRISM', 'SHAPE', 'REVOLVER', 'SPHERE']:
                                if bb.get_action() != action:
                                    bb.set_active(False)
                                else:
                                    bb.set_active(True)
            elif action == 'INSET_2':
                self.end()
                active_object('SET', self.cut_object, True)
                bpy.ops.fluent.faceextraction('INVOKE_DEFAULT', call_by='CUT')
                return {'FINISHED'}
            elif action in ['CUT', 'SLICE', 'INSET', 'CREATION']:
                self.operation = action
                # desactive les autres
                for b in self.ui_items_list:
                    if 'FLUENT_Ui_Button' in str(type(b)):
                        if b.get_action() in ['CUT', 'SLICE', 'INSET']:
                            b.set_active(False)
                    elif 'FLUENT_Ui_Layout' in str(type(b)):
                        layout_items_list = b.get_items()
                        for bb in layout_items_list:
                            if bb.get_action() in ['CUT', 'SLICE', 'INSET']:
                                bb.set_active(False)
                i.set_active(True)
            elif action == 'GRID_ROTATION':
                remove_me = []
                for i, j in enumerate(self.ui_items_list):
                    if type(j) == FLUENT_Ui_Layout and j.get_id() in ['GRID_MOVE', 'GRID_SCALE']:
                        remove_me.append(i)
                        break
                for i in remove_me:
                    del self.ui_items_list[i]
                self.drawing.grid_to_square()
                self.rot_grid_widget.set_obj(self.drawing.get_drawing_plane())
                self.ui_items_list.append(self.rot_grid_widget)
            elif action == 'GRID_MOVE':
                remove_me = []
                for i, j in enumerate(self.ui_items_list):
                    if type(j) == FLUENT_Ui_Layout and j.get_id() in ['GRID_ROTATION', 'GRID_SCALE']:
                        remove_me.append(i)
                        break
                for i in remove_me:
                    del self.ui_items_list[i]
                self.drawing.grid_to_square()
                self.move_grid_widget.set_obj(self.drawing.get_drawing_plane())
                self.ui_items_list.append(self.move_grid_widget)
            elif action == 'GRID_SCALE':
                remove_me = []
                for i, j in enumerate(self.ui_items_list):
                    if type(j) == FLUENT_Ui_Layout and j.get_id() in ['GRID_MOVE', 'GRID_ROTATION']:
                        remove_me.append(i)
                        break
                for i in remove_me:
                    del self.ui_items_list[i]
                self.drawing.grid_to_square()
                self.scale_grid_widget.set_obj(self.drawing.get_drawing_plane())
                self.ui_items_list.append(self.scale_grid_widget)
            elif action == 'GRID_ALIGN':
                self.statut = 'GRID_ADJUSTMENT_ALIGN'
            elif action == 'VALIDATE_ROTATION':
                for i, j in enumerate(self.ui_items_list):
                    if type(j) == FLUENT_Ui_Layout and j.get_id() == 'GRID_ROTATION':
                        break
                del self.ui_items_list[i]
            elif action == 'VALIDATE_MOVE':
                for i, j in enumerate(self.ui_items_list):
                    if type(j) == FLUENT_Ui_Layout and j.get_id() == 'GRID_MOVE':
                        break
                del self.ui_items_list[i]
            elif action == 'VALIDATE_SCALE':
                for i, j in enumerate(self.ui_items_list):
                    if type(j) == FLUENT_Ui_Layout and j.get_id() == 'GRID_SCALE':
                        break
                del self.ui_items_list[i]
            elif action in ['+Z_ROT', '+X_ROT', '+Y_ROT']:
                self.statut = 'GRID_ADJUSTMENT' + '_ROTATION_' + action
                self.slider_origin = self.events['mouse_x']
                self.drawing_plane_saved_matrix = self.drawing.get_drawing_plane().matrix_world.copy()
            elif action in ['+Z_MOVE', '+X_MOVE', '+Y_MOVE']:
                self.statut = 'GRID_ADJUSTMENT' + '_MOVE_' + action
                self.slider_origin = self.events['mouse_x']
                self.drawing_plane_saved_matrix = self.drawing.get_drawing_plane().matrix_world.copy()
            elif action in ['+Z_SCALE', '+X_SCALE', '+Y_SCALE']:
                self.statut = 'GRID_ADJUSTMENT' + '_SCALE_' + action
                self.slider_origin = self.events['mouse_x']
                self.drawing_plane_saved_vertices_position = [v.co.copy() for v in
                                                              self.drawing.get_drawing_plane().data.vertices]
            elif action == 'GRID_RESOLUTION':
                self.statut = 'GRID_ADJUSTMENT_RESOLUTION'
                self.slider_origin = self.events['mouse_x']
            elif action == 'GRID_MOVE':
                self.statut = 'GRID_ADJUSTMENT_MOVE'
                self.slider_origin = self.events['mouse_x']
            elif action == 'GRID_SQUARE':
                self.drawing.grid_to_square()
            elif action == 'GRID_EXTENDED':
                self.drawing.set_extended(not self.drawing.get_extended())
                buttons = self.grid_manipulation.get_items()
                extended_button = [b for b in buttons if b.get_action() == 'GRID_EXTENDED'][0]
                if self.drawing.get_extended():
                    extended_button.set_active(True)
                else:
                    extended_button.set_active(False)
            elif action == 'GRID_VIEW':
                self.drawing.set_align_to_view(not self.drawing.get_align_to_view())
                self.drawing.grid_init(self.cut_object, self.events)
        else:
            if self.statut == 'EN_ATTENTE_DU_DESSIN':
                if self.drawing.get_statut() == 'TERMINE':
                    self.statut = 'DESSIN_TERMINE'
                    self.bool_obj = self.drawing.get_the_draw()['obj']

                # clique droit sur une face affiche la grille clique gauche lance le dessin
                # si aucun widget n'est affiché
                if not (type(self.ui_items_list[-1]) is FLUENT_Ui_Layout and self.ui_items_list[-1].get_id() in ['GRID_ROTATION', 'GRID_SCALE', 'GRID_MOVE']):
                    self.drawing.process(self.events)
                    if (self.drawing.get_statut() == None and self.events['value'] == 'RELEASE' and self.events['type'] in [
                        'RIGHTMOUSE', 'LEFTMOUSE']):
                        self.drawing.reset()
                        success = self.drawing.grid_init(self.cut_object, self.events)
                        if success:
                            if event.value == 'RELEASE' and event.type == 'RIGHTMOUSE':
                                self.drawing.set_display_grid(True)
                                self.rot_grid_widget.set_obj(self.drawing.get_drawing_plane())
                                self.ui_items_list.append(self.grid_manipulation)
                                if event.shift:
                                    self.drawing.set_display_dots(False)
                                else:
                                    self.drawing.set_display_dots(True)
                            self.drawing.process(self.events)
                    elif (self.drawing.get_statut() in ['EN_ATTENTE', 'GRILLE_OK'] and self.events['value'] == 'RELEASE' and
                          self.events['type'] in ['RIGHTMOUSE']):
                        self.drawing.reset()
                        success = self.drawing.grid_init(self.cut_object, self.events)
                        if success:
                            self.drawing.set_display_grid(True)
                            if event.shift:
                                self.drawing.set_display_dots(False)
                            else:
                                self.drawing.set_display_dots(True)
                            self.drawing.process(self.events)
                    elif self.events['value'] == 'PRESS' and self.events['type'] == 'ESC':
                        self.drawing.reset()
            elif self.statut == 'DESSIN_TERMINE':
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                active_object(action='SET', obj=self.bool_obj, solo=True)
                if self.bool_obj['fluent_type'] != 'revolver':
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                if self.cut_object and len(self.cut_object.data.polygons) and self.cut_object.data.polygons[0].use_smooth:
                    for p in self.bool_obj.data.polygons:
                        p.use_smooth = True
                self.bool_obj.data.use_auto_smooth = True

                if self.operation != 'CREATION' and self.cut_object:
                    if get_addon_preferences().auto_parent:
                        parent_relationship(self.cut_object, self.bool_obj)
                    add_in_bool_collection(self.bool_obj)
                    boolean_visibility_setup(self.bool_obj)
                    bpy.ops.fluent.editor('INVOKE_DEFAULT', bool_obj_name=self.bool_obj.name,
                                          cut_obj_name=self.cut_object.name, operation=self.operation)
                else:
                    self.bool_obj.hide_render = False
                    bpy.ops.fluent.editor('INVOKE_DEFAULT', bool_obj_name=self.bool_obj.name, cut_obj_name='',
                                          operation='CREATION')
                return {'FINISHED'}
            elif 'GRID_ADJUSTMENT' in self.statut:
                if 'ROTATION' in self.statut:
                    if self.events['type'] == 'MOUSEMOVE':
                        self.drawing.get_drawing_plane().matrix_world = self.drawing_plane_saved_matrix
                        delta = (self.events['mouse_x'] - self.slider_origin) / 8
                        if 'Z' in self.statut:
                            t = self.drawing.plane_rotation('Z', delta)
                        if 'X' in self.statut:
                            t = self.drawing.plane_rotation('X', delta)
                        if 'Y' in self.statut:
                            t = self.drawing.plane_rotation('Y', delta)
                        self.cursor_infos.set_text([str(t) + '°'])
                elif 'MOVE' in self.statut:
                    if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or self.events['ctrl_release']:
                        self.slider_origin = self.events['mouse_x']
                        self.drawing_plane_saved_matrix = self.drawing.get_drawing_plane().matrix_world.copy()
                    if self.events['type'] == 'MOUSEMOVE':
                        if self.events['shift_work']:
                            increment = 1000
                        elif self.events['ctrl_work']:
                            increment = 10
                        else:
                            increment = 100
                        self.drawing.get_drawing_plane().matrix_world = self.drawing_plane_saved_matrix
                        delta = (self.events['mouse_x'] - self.slider_origin) / increment
                        if 'X' in self.statut:
                            self.drawing.plane_move('X', delta)
                        if 'Y' in self.statut:
                            self.drawing.plane_move('Y', delta)
                elif 'SCALE' in self.statut:
                    if self.events['shift_press'] or self.events['shift_release'] or self.events['ctrl_press'] or self.events['ctrl_release']:
                        self.slider_origin = self.events['mouse_x']
                        self.drawing_plane_saved_matrix = self.drawing.get_drawing_plane().matrix_world.copy()
                    if self.events['type'] == 'MOUSEMOVE':
                        if self.events['shift_work']:
                            increment = 1000
                        elif self.events['ctrl_work']:
                            increment = 10
                        else:
                            increment = 100
                        for i, v in enumerate(self.drawing.get_drawing_plane().data.vertices):
                            v.co = self.drawing_plane_saved_vertices_position[i]
                        delta = (self.events['mouse_x'] - self.slider_origin) / increment
                        self.slider_origin = self.events['mouse_x']
                        if 'X' in self.statut:
                            self.drawing.plane_scale('X', delta)
                        elif 'Y' in self.statut:
                            self.drawing.plane_scale('Y', delta)
                        elif 'Z' in self.statut:
                            self.drawing.plane_scale('XY', delta)
                elif 'RESOLUTION' in self.statut:
                    if self.events['mouse_x'] - self.slider_origin > 50:
                        self.drawing.set_resolution(self.drawing.get_resolution() + 1)
                        self.slider_origin = self.events['mouse_x']
                    elif self.events['mouse_x'] - self.slider_origin < -50:
                        self.drawing.set_resolution(self.drawing.get_resolution() - 1)
                        self.slider_origin = self.events['mouse_x']
                elif 'ALIGN' in self.statut:
                    self.cursor_infos.set_text(['Align the grid', 'Click on two vertices.'])
                    step = None
                    if event.value == 'RELEASE' and event.type == 'LEFTMOUSE':
                        step = self.drawing.grid_align(self.events)
                    if step == 'FINISHED':
                        self.statut = 'EN_ATTENTE_DU_DESSIN'
                        self.cursor_infos.set_text([])
                if event.value == 'RELEASE' and event.type == 'LEFTMOUSE' and not 'ALIGN' in self.statut:
                    self.statut = 'EN_ATTENTE_DU_DESSIN'
                    self.cursor_infos.set_text([])

        if self.events['type'] == 'V' and self.events[
            'value'] == 'PRESS' and self.statut != 'GRID_ADJUSTMENT_RESOLUTION':
            self.statut = 'GRID_ADJUSTMENT_RESOLUTION'
            self.slider_origin = self.events['mouse_x']
        elif (self.events['type'] == 'V' and self.events['value'] == 'RELEASE' or self.events['type'] == 'LEFTMOUSE' and
              self.events['value'] == 'RELEASE') and self.statut == 'GRID_ADJUSTMENT_RESOLUTION':
            self.statut = 'EN_ATTENTE_DU_DESSIN'
        elif self.events['type'] == 'A' and self.events['value'] == 'PRESS' and self.statut == 'EN_ATTENTE_DU_DESSIN':
            self.statut = 'GRID_ADJUSTMENT_ALIGN'

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # VERIFICATIONS
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass

        # test si uniquement des objets sont sélectionnés
        for o in bpy.context.selected_objects:
            if o.type not in ['MESH']:
                make_oops(['You selected a non object thing.'], title="How to use ?", icon='ERROR')
                return {'FINISHED'}

        # test si dans le preview
        if not context.area.type == 'VIEW_3D':
            make_oops(['View3D not found, cannot run operator.'], title="How to use ?", icon='ERROR')
            return {'FINISHED'}

        self.init_variables(event)

        args = (self, context)

        # self.timer = context.window_manager.event_timer_add(1/25, window=context.window)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


class FLUENT_OT_CutStarter(Operator):
    """Cut/Add"""
    bl_idname = "fluent.cutstarter"
    bl_label = "Cut"

    def invoke(self, context, event):
        bpy.ops.fluent.cutter('INVOKE_DEFAULT', operation='CUT')
        return {'FINISHED'}


class FLUENT_OT_SliceStarter(Operator):
    """Slice"""
    bl_idname = "fluent.slicestarter"
    bl_label = "Slice"

    def invoke(self, context, event):
        bpy.ops.fluent.cutter('INVOKE_DEFAULT', operation='SLICE')
        return {'FINISHED'}


class FLUENT_OT_InsetStarter(Operator):
    """Inset"""
    bl_idname = "fluent.insetstarter"
    bl_label = "Inset"

    def invoke(self, context, event):
        bpy.ops.fluent.cutter('INVOKE_DEFAULT', operation='INSET')
        return {'FINISHED'}


class FLUENT_OT_CreateStarter(Operator):
    """Creation"""
    bl_idname = "fluent.createstarter"
    bl_label = "Creation"

    def invoke(self, context, event):
        bpy.ops.fluent.cutter('INVOKE_DEFAULT', operation='CREATION')
        return {'FINISHED'}


class FLUENT_OT_Editor(Operator):
    """Edit a Fluent object"""
    bl_idname = "fluent.editor"
    bl_label = "Fluent editor"
    bl_options = {'REGISTER', 'UNDO'}

    bool_obj_name: StringProperty(
        default=''
    )
    cut_obj_name: StringProperty(
        default=''
    )
    operation: StringProperty(
        default=''
    )

    def init_variables(self, event):
        self.ui_items_list = []
        self.pie_menu_history = []
        self.cursor_infos = FLUENT_Cursor_Infos()
        self.ui_items_list.append(self.cursor_infos)
        self.side_infos = FLUENT_Panel_Infos()
        self.ui_items_list.append(self.side_infos)
        self.bool_drawing = None
        self.blender_operator_running = False

        if self.operation != 'EDIT':
            if bpy.data.objects.get(self.cut_obj_name):
                self.cut_object = bpy.data.objects.get(self.cut_obj_name)
                depsgraph = bpy.context.evaluated_depsgraph_get()
                self.cut_object_eval = self.cut_object.evaluated_get(depsgraph)
            else:
                self.cut_object = None
                self.cut_object_eval = None

            self.bool_obj = bpy.data.objects.get(self.bool_obj_name)
            self.fluent_adjustments = None
        else:
            self.cut_object = None
            self.bool_obj = None
            self.fluent_adjustments = None

        self.bevel = F_outer_bevel()

        self.events = event_dico_builder(event)

        if event.value == 'PRESS' and event.type == 'LEFTMOUSE':
            self.events['mouse_left_click'] = True
        if event.value == 'RELEASE' and event.type == 'LEFTMOUSE':
            self.events['mouse_left_click'] = False

        self.statut = 'EN_ATTENTE'

        button = make_button('CANCEL')
        self.ui_items_list.append(button)

        row = FLUENT_Ui_Layout('CUT OPERATIONS')

        if self.operation not in ['EDIT', 'CREATION', 'PLATE']:
            button = FLUENT_Ui_Button()
            button.set_text('')
            button.set_tool_tip('Cut/Add')
            button.set_shape('CIRCLE')
            button.set_action('CUT')
            button.set_icon('cut')
            row.add_item(button)

            button = FLUENT_Ui_Button()
            button.set_text('')
            button.set_tool_tip('Slice')
            button.set_shape('CIRCLE')
            button.set_action('SLICE')
            button.set_icon('slice')
            row.add_item(button)

            button = FLUENT_Ui_Button()
            button.set_text('')
            button.set_tool_tip('Inset')
            button.set_shape('CIRCLE')
            button.set_action('INSET')
            button.set_icon('inset')
            row.add_item(button)

        if self.operation not in ['CREATION', 'PLATE']:
            button = FLUENT_Ui_Button()
            button.set_text('')
            button.set_tool_tip('New drawing (+SHIFT to draw on the boolean object)')
            button.set_action('NEW_DRAWING')
            button.set_shape('CIRCLE')
            button.set_icon('draw')
            row.add_item(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_tool_tip('Show/Hide boolean (H)')
        button.set_action('SHOW_BOOLEAN')
        button.set_shape('CIRCLE')
        button.set_icon('show_bool')
        row.add_item(button)

        row.spread()

        self.ui_items_list.append(row)

    def initialisation(self):
        if self.operation in ['CUT', 'SLICE', 'INSET', '*CUT']:
            # en cas de sortie de dessin le booléen est à rajouter
            if self.cut_object and self.bool_obj:
                bool = find_boolean_modifier(self.bool_obj, self.cut_object)

                if not bool:
                    bool = self.cut_object.modifiers.new(type='BOOLEAN', name=fluent_modifiers_name['boolean'])
                    bool.object = self.bool_obj
                    bool.solver = 'FAST'
                    bool.show_expanded = False
                    self.bool_obj['fluent_operation'] = 'CUT'
                    if self.bool_obj.get('fluent_type') in ['revolver']:
                        co_y_moyen = 0
                        for v in self.bool_obj.data.vertices:
                            co_y_moyen = co_y_moyen + v.co.y
                        co_y_moyen = co_y_moyen / len(self.bool_obj.data.vertices)
                        if co_y_moyen > 0:
                            bool.operation = 'UNION'

                # cut the cutter
                if self.cut_object.get('fluent_type') in ['box', 'prism', 'poly', 'path', 'revolver']:
                    place_in_stack(self.cut_object, bool)
        elif self.operation == 'EDIT':
            if len(bpy.context.selected_objects) != 1:
                make_oops(['Select only one object.'], title="How to use ?", icon='ERROR')
                return 'FINISHED'

            obj = active_object(action='GET')
            if obj.get('fluent_type') in ['box', 'prism', 'sphere', 'poly', 'path', 'revolver', 'unknow', 'plate', 'head_screw']:
                self.bool_obj = obj
                self.modifiers_stack_save = save_modifers_stack(obj)
                cut_objects = find_boolean_targets(self.bool_obj)
                try:
                    self.cut_object = cut_objects[0]['cut_object']
                    bool = cut_objects[0]['boolean_modifier']
                except:pass
            else:
                make_oops(['Select a Fluent object.'], title="How to use ?", icon='ERROR')
                return 'FINISHED'

        # on vérifie la présence de modifiers de base si rien, c'est que l'on sort de dessin et il faut les rajouter
        # et lancer l'ajustement du solidify
        if self.bool_obj:
            self.fluent_adjustments = modifiers_manager(obj=self.bool_obj, bool_target=self.cut_object)
            # if self.bool_obj.get('fluent_inset'):
            #     self.fluent_adjustments.prepare_edition(inset_obj=self.bool_obj.get('fluent_inset'))
            # else:
            #     self.fluent_adjustments.prepare_edition(inset_obj=False)
            if self.operation == 'EDIT' and self.bool_obj.get('fluent_type') not in ['box', 'poly', 'path', 'prism', 'sphere', 'revolver', 'plate', 'head_screw']:
                make_oops(
                    ['This object can\'t be edited.', 'It isn\'t a Fluent object'],
                    title="Problem", icon='ERROR')
                return 'FINISHED'

            if self.bool_obj['fluent_type'] == 'box':
                self.pie_menu_root = box_ui()
                self.pie_menu_history.append(self.pie_menu_root)
                layout = FLUENT_Ui_Layout('TRANSFORM')
                layout.set_layout('COLUMN_LEFT')
                button = make_button('DIMENSIONS')
                layout.add_item(button)
                button = make_button('ROTATION')
                layout.add_item(button)
                self.ui_items_list.append(layout)
                layout.spread()

                if self.operation not in ['CUT', 'EDIT', 'CREATION']:
                    self.operation = change_bool_operation(self.bool_obj, self.cut_object, self.operation)

            elif self.bool_obj['fluent_type'] == 'poly':
                self.pie_menu_root = shape_ui()
                self.pie_menu_history.append(self.pie_menu_root)

                layout = FLUENT_Ui_Layout('TRANSFORM')
                layout.set_layout('COLUMN_LEFT')
                button = make_button('DIMENSIONS')
                layout.add_item(button)
                button = make_button('ROTATION')
                layout.add_item(button)
                self.ui_items_list.append(layout)
                layout.spread()

                if self.operation not in ['CUT', 'EDIT', 'CREATION']:
                    self.operation = change_bool_operation(self.bool_obj, self.cut_object, self.operation)

            elif self.bool_obj['fluent_type'] == 'path':
                self.fluent_adjustments.first_solidify_action(action='ADD')
                self.pie_menu_root = path_ui()
                self.pie_menu_history.append(self.pie_menu_root)

                layout = FLUENT_Ui_Layout('TRANSFORM')
                layout.set_layout('COLUMN_LEFT')
                button = make_button('DIMENSIONS')
                layout.add_item(button)
                button = make_button('ROTATION')
                layout.add_item(button)
                self.ui_items_list.append(layout)
                layout.spread()

                if self.operation not in ['CUT', 'EDIT', 'CREATION']:
                    self.operation = change_bool_operation(self.bool_obj, self.cut_object, self.operation)

            elif self.bool_obj['fluent_type'] == 'prism':
                self.pie_menu_root = prism_ui()
                self.pie_menu_history.append(self.pie_menu_root)

                layout = FLUENT_Ui_Layout('TRANSFORM')
                layout.set_layout('COLUMN_LEFT')
                button = make_button('DIMENSIONS')
                layout.add_item(button)
                button = make_button('ROTATION')
                layout.add_item(button)
                self.ui_items_list.append(layout)
                layout.spread()

                if self.operation not in ['CUT', 'EDIT', 'CREATION']:
                    self.operation = change_bool_operation(self.bool_obj, self.cut_object, self.operation)

            elif self.bool_obj['fluent_type'] == 'sphere':
                self.pie_menu_root = sphere_ui()
                self.pie_menu_history.append(self.pie_menu_root)

                layout = FLUENT_Ui_Layout('TRANSFORM')
                layout.set_layout('COLUMN_LEFT')
                button = make_button('DIMENSIONS')
                layout.add_item(button)
                button = make_button('ROTATION')
                layout.add_item(button)
                self.ui_items_list.append(layout)
                layout.spread()

                if self.operation not in ['CUT', 'EDIT', 'CREATION']:
                    self.operation = change_bool_operation(self.bool_obj, self.cut_object, self.operation)

            elif self.bool_obj['fluent_type'] == 'revolver':
                self.pie_menu_root = revolver_ui()
                self.pie_menu_history.append(self.pie_menu_root)

                layout = FLUENT_Ui_Layout('TRANSFORM')
                layout.set_layout('COLUMN_LEFT')
                button = make_button('DIMENSIONS')
                layout.add_item(button)
                button = make_button('ROTATION')
                layout.add_item(button)
                self.ui_items_list.append(layout)
                layout.spread()

                if len(self.bool_obj.modifiers) == 0:
                    self.fluent_adjustments.stack_builder()

                if self.operation not in ['CUT', 'EDIT', 'CREATION']:
                    self.operation = change_bool_operation(self.bool_obj, self.cut_object, self.operation)

            elif self.bool_obj['fluent_type'] == 'unknow':
                self.pie_menu_root = unknow_ui()
                self.pie_menu_history.append(self.pie_menu_root)

                if self.operation not in ['CUT', 'EDIT', 'CREATION']:
                    self.operation = change_bool_operation(
                        self.bool_obj, self.cut_object, self.operation)
                if self.operation == 'INSET' or (self.operation == 'EDIT' and self.bool_obj.get('fluent_inset')):
                    self.fluent_adjustments.inset_action(
                        action='INIT', inset_obj=self.bool_obj['fluent_inset'])
                    button = make_button('INSET')
                    self.pie_menu_root.add_item(button)
                boolean_visibility_setup(self.bool_obj)

            elif self.bool_obj['fluent_type'] == 'plate':
                self.pie_menu_root = plate_ui()
                self.pie_menu_history.append(self.pie_menu_root)

            self.bool_drawing = FLUENT_Draw_Object(self.bool_obj, (1, 1, 1, .05))
            self.ui_items_list.append(self.bool_drawing)

            if self.bool_obj.display_type == 'WIRE':
                self.bool_obj.hide_set(True)
            else:
                self.bool_obj.hide_set(False)

            if self.operation == 'INSET' or (self.operation == 'EDIT' and self.bool_obj.get('fluent_inset')):
                self.fluent_adjustments.inset_action(action='INIT', inset_obj=self.bool_obj['fluent_inset'])
                button = make_button('INSET')
                self.pie_menu_root.add_item(button)

            if self.operation != '*CUT':
                if self.operation != 'EDIT' and self.bool_obj.get('fluent_type') in ['box', 'poly', 'prism']:
                    ui_items_list, pie_menu = self.fluent_adjustments.get_ui('FIRST_SOLIDIFY')
                    if self.operation == 'CREATION':
                        self.bool_obj.modifiers[fluent_modifiers_name['first_solidify']].offset = 0

                    self.pie_menu_history.append(pie_menu)
                    self.fluent_adjustments.prepare_adjustment('FIRST_SOLIDIFY', self.events)

                    self.statut = 'AJUSTEMENT_EN_COURS'
                elif self.operation != 'EDIT' and self.bool_obj.get('fluent_type') in ['path']:
                    ui_items_list, pie_menu = self.fluent_adjustments.get_ui('PATH_HEIGHT')
                    self.pie_menu_history.append(pie_menu)
                    self.fluent_adjustments.prepare_adjustment('PATH_HEIGHT', self.events)
                    self.statut = 'AJUSTEMENT_EN_COURS'
                elif self.operation != 'EDIT' and self.bool_obj.get('fluent_type') in ['plate']:
                    ui_items_list, pie_menu = self.fluent_adjustments.get_ui('FIRST_SOLIDIFY')
                    self.bool_obj.modifiers[fluent_modifiers_name['first_solidify']].thickness = bpy.context.scene.fluentProp.plate_solidify_thickness
                    if bpy.context.scene.fluentProp.plate_solidify_thickness == 0:
                        self.pie_menu_history.append(pie_menu)
                        self.fluent_adjustments.prepare_adjustment('FIRST_SOLIDIFY', self.events)
                        self.statut = 'AJUSTEMENT_EN_COURS'
                    # if get_addon_preferences().bevel_system == 'MULTIPLE':
                    #     if self.operation == 'CREATE':
                    #         self.bevel.set_target(self.bool_obj)
                    #         self.bevel.management()
                    #         self.fluent_adjustments.outer_bevel_preparation()
                    #     button = make_button('OUTER_BEVEL')
                    #     self.pie_menu_root.add_item(button)
                    # else:
                    #     self.bevel.set_target(self.bool_obj)
                    #     self.bevel.management()

        if self.cut_object and not self.cut_object.get('fluent_operation'):
            if get_addon_preferences().bevel_system == 'MULTIPLE':
                if self.operation != 'EDIT':
                    self.bevel.set_target(self.cut_object)
                    self.bevel.management()
                try:
                    self.fluent_adjustments.outer_bevel_preparation(cut_objects)
                except:
                    cut_objects = find_boolean_targets(self.bool_obj)
                    self.fluent_adjustments.outer_bevel_preparation(cut_objects)
                outer_bevel_button = [b.get_id() for b in self.pie_menu_root.get_items() if b.get_id() == 'OUTER_BEVEL']
                if not outer_bevel_button:
                    button = make_button('OUTER_BEVEL')
                    self.pie_menu_root.add_item(button)
            else:
                self.bevel.set_target(self.cut_object)
                self.bevel.management()
        # elif self.operation == 'EDIT' and self.bool_obj.get('fluent_type') == 'plate':
        #     if get_addon_preferences().bevel_system == 'MULTIPLE':
        #         self.bevel.set_target(self.bool_obj)
        #         self.fluent_adjustments.outer_bevel_preparation()
        #         button = make_button('OUTER_BEVEL')
        #         self.pie_menu_root.add_item(button)
        #     else:
        #         self.bevel.set_target(self.bool_obj)
        #         self.bevel.management()

        # Si on édite un booléen → on cache les autres
        if self.bool_obj.get('fluent_operation'):
            for o in bpy.data.collections['Bool_Objects'].objects:
                if o != self.bool_obj:
                    o.hide_set(True)

    def end(self, option='FINISHED'):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        if option == 'FINISHED':
            self.bool_obj.hide_viewport = False
            if get_addon_preferences().auto_hide_bool and self.cut_object and self.operation not in ['CREATION', 'PLATE'] or self.operation == 'EDIT' and self.bool_obj.display_type != 'TEXTURED':
                if len(bpy.data.collections['Bool_Objects'].objects) > 1:
                    obj_1 = bpy.data.collections['Bool_Objects'].objects[0]
                    obj_2 = bpy.data.collections['Bool_Objects'].objects[1]
                    if self.bool_obj != obj_1:
                        if obj_1.hide_get():
                            self.bool_obj.hide_set(True)
                        else:
                            self.bool_obj.hide_set(False)
                    else:
                        if obj_2.hide_get():
                            self.bool_obj.hide_set(True)
                        else:
                            self.bool_obj.hide_set(False)
                else:
                    self.bool_obj.hide_set(True)
            if self.bool_obj.get('fluent_type') == 'plate':
                bpy.context.scene.fluentProp.plate_solidify_thickness = self.bool_obj.modifiers[fluent_modifiers_name['first_solidify']].thickness
            if self.events['shift_work']:
                active_object('SET', self.bool_obj, True)
                bpy.ops.object.convert(target='MESH')
                try:
                    del self.bool_obj['fluent_type']
                except:pass
        elif option == 'CANCELLED':
            if self.operation != 'EDIT':
                try:
                    bpy.data.objects.remove(self.bool_obj, do_unlink=True)
                except:pass
                try:
                    boolean_cleaner([self.cut_object])
                except:pass
            else:
                remake_modifiers_stack(self.bool_obj, self.modifiers_stack_save)

        try:
            active_object('SET', self.cut_object, True)
        except:pass

    def modal(self, context, event):
        if pass_through(event) or event.type == 'TAB' or event.type in ['G', 'R']:
            try:
                if event.type == 'TAB' and event.value == 'PRESS':
                    active_object('SET', self.bool_obj, True)
                    if bpy.context.active_object:
                        if self.bool_obj.get('fluent_operation'):
                            if bpy.context.active_object.mode == 'OBJECT':
                                self.bool_obj.hide_set(False)
                            else:
                                self.bool_obj.hide_set(True)
                    else:
                        if self.bool_obj.get('fluent_operation'):
                            self.bool_obj.hide_set(False)
                        # active_object('SET', self.bool_obj, True)

                if event.type in ['G', 'R'] and event.value == 'PRESS':
                    active_object('SET', self.bool_obj, True)
                    if self.bool_obj.get('fluent_operation'):
                        self.bool_obj.hide_set(False)
                    # active_object('SET', self.bool_obj, True)
                    self.blender_operator_running = 'MOVE'

                return {'PASS_THROUGH'}
            except:pass

        try:
            if bpy.context.active_object.mode == 'EDIT' or self.blender_operator_running:
                if self.blender_operator_running == 'MOVE' and event.type in ['LEFTMOUSE', 'RIGHTMOUSE', 'ESC'] and event.value == 'PRESS':
                    self.blender_operator_running = False
                    if self.bool_obj.get('fluent_operation'):
                        self.bool_obj.hide_set(True)
                return {'PASS_THROUGH'}
        except:pass

        # temp_list = []
        # for i in self.ui_items_list:
        #     if not (type(i) is FLUENT_Ui_Layout and i.get_layout() in ['PIE', 'MIRROR', 'TAPER']) and type(i) is not FLUENT_Draw_Object:
        #         temp_list.append(i)
        #     if type(i) is FLUENT_Draw_Object:
        #         temp_list.insert(0, i)
        # self.ui_items_list = temp_list
        # temp_list = []
        self.ui_items_list = [i for i in self.ui_items_list if not (type(i) is FLUENT_Ui_Layout and i.get_layout() in ['PIE', 'MIRROR', 'TAPER'])]
        self.ui_items_list.append(self.pie_menu_history[-1])

        self.events = event_dico_refresh(self.events, event)

        context.area.tag_redraw()

        if self.statut == 'AJUSTEMENT_EN_COURS':
            callback, screen_text = self.fluent_adjustments.adjust(self.events)
            self.side_infos.reset()
            for i, j in enumerate(screen_text):
                self.side_infos.add_line(screen_text[i][0], screen_text[i][1])

        # action des bouttons
        action = None
        for b in self.ui_items_list:
            if 'FLUENT_Ui_Button' in str(type(b)):
                b.is_hover(self.events)
                if b.get_state() == 2:
                    action = b.get_action()
                    b.set_state(0)
                    break
                else:
                    action = None
            elif 'FLUENT_Ui_Layout' in str(type(b)):
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

        if 'callback' in locals() and 'STOP_ADJUSTMENT' in callback:
            self.side_infos.reset()
            del self.pie_menu_history[-1]
            self.ui_items_list = [i for i in self.ui_items_list if type(i) is not FLUENT_Draw_Dots]
            self.statut = 'EN_ATTENTE'
            return {'RUNNING_MODAL'}

        if event.type == 'H' and event.value == 'PRESS':
            action = 'SHOW_BOOLEAN'
        if event.type == 'W' and event.value == 'PRESS':
            try:
                if self.cut_object.show_wire:
                    self.cut_object.show_wire = False
                else:
                    self.cut_object.show_wire = True
            except:pass
        if event.type in ['RIGHTMOUSE'] and event.value == 'PRESS':
            action = 'FINISHED'
        if event.type in ['ESC'] and event.value == 'PRESS':
            action = 'CANCELLED'

        # boolean shortcut
        if self.operation not in ['EDIT', 'CREATION']:
            if event.type == 'I' and event.value == 'PRESS':
                action = 'INTERSECT'
                self.bool_obj['inib_auto_bool_switching'] = True
            if event.type == 'U' and event.value == 'PRESS':
                action = 'UNION'
                self.bool_obj['inib_auto_bool_switching'] = True
            if event.type == 'D' and event.value == 'PRESS':
                action = 'DIFFERENCE'
                self.bool_obj['inib_auto_bool_switching'] = True

        # adjustment shortcut
        if event.type == 'S' and event.value == 'PRESS'and self.statut != 'AJUSTEMENT_EN_COURS':
            action = 'FIRST_SOLIDIFY'
        elif event.type == 'B' and event.value == 'PRESS'and self.statut != 'AJUSTEMENT_EN_COURS':
            action = 'FIRST_BEVEL'
        elif event.type == 'M' and event.value == 'PRESS'and self.statut != 'AJUSTEMENT_EN_COURS':
            action = 'MIRROR'
        elif event.type == 'A' and event.value == 'PRESS'and self.statut != 'AJUSTEMENT_EN_COURS':
            action = 'ARRAY'

        if action:
            if action == 'FINISHED':
                self.end()
                return {'FINISHED'}
            if action == 'CANCELLED':
                self.end('CANCELLED')
                return {'FINISHED'}
            elif action in ['VALIDATE', 'CROSS', 'FAKE_SLICE']:
                del self.pie_menu_history[-1]
                self.ui_items_list = [i for i in self.ui_items_list if type(i) is not FLUENT_Draw_Dots]
                self.statut = 'EN_ATTENTE'
            elif action in ['FIRST_SOLIDIFY', 'FIRST_BEVEL', 'SECOND_BEVEL', 'SECOND_SOLIDIFY', 'MIRROR', 'TAPER',
                            'ARRAY', 'CIRCULAR_ARRAY', 'DIMENSIONS', 'ROTATION', 'RADIUS', 'RESOLUTION',
                            'INSET_THICKNESS', 'PATH_THICKNESS', 'PATH_HEIGHT', 'CURVE', 'OUTER_BEVEL']:
                ui_items_list, pie_menu = self.fluent_adjustments.get_ui(action)
                self.pie_menu_history.append(pie_menu)
                self.fluent_adjustments.prepare_adjustment(action, self.events)
                self.statut = 'AJUSTEMENT_EN_COURS'
                for i in ui_items_list:
                    if type(i) is FLUENT_Draw_Dots:
                        self.ui_items_list.append(i)
            elif action == 'FLIP_SCREW':
                self.bool_obj.modifiers[fluent_modifiers_name['screw']].use_normal_flip = not self.bool_obj.modifiers[
                    fluent_modifiers_name['screw']].use_normal_flip
            elif action == 'NEW_DRAWING':
                if self.operation != 'CREATION':
                    if self.operation != 'EDIT':
                        if event.shift:
                            if self.operation != 'CREATION': self.bool_obj.hide_set(False)
                            active_object(action='SET', obj=self.bool_obj, solo=True)
                        else:
                            if self.operation != 'CREATION':
                                if get_addon_preferences().auto_hide_bool:
                                    self.bool_obj.hide_set(True)
                            active_object(action='SET', obj=self.cut_object, solo=True)
                    else:
                        self.bool_obj.hide_set(False)
                        active_object(action='SET', obj=self.bool_obj, solo=True)
                    bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                    bpy.ops.fluent.cutter('INVOKE_DEFAULT')
                    return {'FINISHED'}
            elif action in ['CUT', 'SLICE', 'INSET', 'INTERSECT', 'UNION', 'DIFFERENCE']:
                if action != self.operation:
                    previous_operation = self.operation
                    self.operation = change_bool_operation(self.bool_obj, self.cut_object, action)
                    if self.operation == 'INSET' and previous_operation != 'INSET':
                        self.fluent_adjustments.inset_action(action='INIT', inset_obj=self.bool_obj['fluent_inset'])
                        for p in self.pie_menu_history:
                            if p.get_id() in ['BOX', 'POLY', 'PRISM', 'UNKNOW', 'PATH']:
                                button = make_button('INSET')
                                p.add_item(button)
                    elif previous_operation == 'INSET' and self.operation != 'INSET':
                        for p in self.pie_menu_history:
                            if p.get_id() in ['BOX', 'POLY', 'PRISM']:
                                p.remove_item('INSET')
                    cut_objects = find_boolean_targets(self.bool_obj)
                    self.fluent_adjustments.outer_bevel_preparation(cut_objects)
            elif action == 'SHOW_BOOLEAN':
                if self.events['shift_work']:
                    affichage_booleen()
                else:
                    if self.bool_obj['fluent_type'] not in ['plate']:
                        self.bool_obj.hide_viewport = not self.bool_obj.hide_viewport

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

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # VERIFICATIONS
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass

        # test si uniquement des objets sont sélectionnés
        for o in bpy.context.selected_objects:
            if o.type not in ['MESH', 'CURVE']:
                make_oops(['You selected a non object thing.'], title="How to use ?", icon='ERROR')
                return {'FINISHED'}

        # test si l'objet actif est un objet fluent
        if self.operation == 'EDIT':
            if active_object('GET').get('fluent_type') not in ['box', 'poly', 'prism', 'sphere', 'path', 'revolver', 'plate']:
                if active_object('GET').get('fluent_type') in ['grid']:
                    bpy.ops.fluent.grids('INVOKE_DEFAULT', operation='EDIT')
                    return{'FINISHED'}
                if active_object('GET').get('fluent_type') in ['wire']:
                    bpy.ops.fluent.wire('INVOKE_DEFAULT', operation='EDIT')
                    return{'FINISHED'}
                if active_object('GET').get('fluent_type') in ['pipe']:
                    bpy.ops.fluent.pipe('INVOKE_DEFAULT', operation='EDIT')
                    return{'FINISHED'}
                if active_object('GET').get('fluent_type') in ['head_screw']:
                    bpy.ops.fluent.screw('INVOKE_DEFAULT', operation='EDIT')
                    return{'FINISHED'}
                make_oops(['You can edit only Fluent object'], title="How to use ?", icon='ERROR')
                return{'FINISHED'}

        # test si dans le preview
        if not context.area.type == 'VIEW_3D':
            make_oops(['View3D not found, cannot run operator.'], title="How to use ?", icon='ERROR')
            return {'FINISHED'}

        self.init_variables(event)

        callback = self.initialisation()

        if self.bool_obj.modifiers.get(fluent_modifiers_name['head_screw']):
            return {'FINISHED'}

        if callback == 'FINISHED':
            return {'FINISHED'}

        args = (self, context)

        # self.timer = context.window_manager.event_timer_add(1/25, window=context.window)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class FLUENT_OT_BooleanOperator(Operator):
    """Boolean operation between 2 objects"""
    bl_idname = "fluent.booleanoperator"
    bl_label = "Boolean"
    bl_options = {'REGISTER', 'UNDO'}

    def verification(self):
        callback = []

        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass

        # test si uniquement des objets sont sélectionnés
        for i, o in enumerate(bpy.context.selected_objects):
            if o.type != 'MESH':
                make_oops(['You selected a non object thing.'], title="How to use ?", icon='ERROR')
                callback.append('FINISHED')

        # test si seulement 2 objets sont sélectionnés
        if i != 1:
            make_oops(['Select two objects.'], title="How to use ?", icon='ERROR')
            callback.append('FINISHED')

        # test si dans le preview
        if not bpy.context.area.type == 'VIEW_3D':
            make_oops(['View3D not found, cannot run operator.'], title="How to use ?", icon='ERROR')
            callback.append('FINISHED')

        return callback

    def invoke(self, context, event):
        callback = self.verification()
        if 'FINISHED' in callback:
            return {'FINISHED'}

        self.cut_object = active_object(action='GET')
        for o in bpy.context.selected_objects:
            if o != self.cut_object:
                self.bool_obj = o

        self.operation = '*CUT'

        # test si le type n'est pas déjà définit
        try:
            self.bool_obj['fluent_type']
        except:
            self.bool_obj['fluent_type'] = 'unknow'

        add_in_bool_collection(self.bool_obj)
        self.bool_obj.display_type = 'WIRE'
        self.bool_obj.hide_set(True)
        self.bool_obj.hide_render = True
        bpy.ops.fluent.editor('INVOKE_DEFAULT', bool_obj_name=self.bool_obj.name, cut_obj_name=self.cut_object.name,
                              operation=self.operation)
        return {'FINISHED'}


class FLUENT_OT_BooleanDisplay(Operator):
    """Show/Hide boolean objects"""
    bl_idname = "fluent.booleandisplay"
    bl_label = "Boolean visibility"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        try:
            if bpy.data.collections['Bool_Objects'].objects[0].hide_get():
                for o in bpy.data.collections['Bool_Objects'].objects:
                    if o.get('fluent_type') != 'grid':
                        o.hide_set(False)
            else:
                for o in bpy.data.collections['Bool_Objects'].objects:
                    if o.get('fluent_type') != 'grid':
                        o.hide_set(True)
        except:
            pass

        return {'FINISHED'}


class FLUENT_OT_AddLatestBevel(Operator):
    """Add a bevel
Hold Shift - Remove all bevels"""
    bl_idname = "fluent.addlatestbevel"
    bl_label = "Add the latest bevel"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        if active_object('GET'):
            if bpy.context.active_object.mode == 'EDIT':
                make_oops(['This function work only in object mode.'], title="Info", icon='ERROR')
                return {'CANCELLED'}
            for obj in bpy.context.selected_objects:
                if not obj.type == 'MESH':
                    continue
                bevel = F_outer_bevel()
                bevel.set_target(obj)
                bevel.first_as_current()
                if event.shift:
                    bevel.remove('ALL')
                else:
                    if not bevel.get_first_bevel():
                        bevel.add()
                        bevel.set_width(bpy.context.scene.fluentProp.width)
                    else:
                        bevel.set_width(bpy.context.scene.fluentProp.width)
        return {'FINISHED'}


class FLUENT_OT_TechnicalDisplay(Operator):
    """Show/Hide wireframe + boolean objects"""
    bl_idname = "fluent.technicaldisplay"
    bl_label = "Technical display"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.fluent.wireframedisplay('INVOKE_DEFAULT')
        bpy.ops.fluent.booleandisplay('INVOKE_DEFAULT')
        return {'FINISHED'}


class FLUENT_OT_WireframeDisplay(Operator):
    """Show/Hide wireframe"""
    bl_idname = "fluent.wireframedisplay"
    bl_label = "Wireframe display"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        if active_object(action='GET'):
            if bpy.context.object.show_wire == True:
                for o in bpy.context.selected_objects:
                    o.show_wire = False
                    o.show_all_edges = False
            else:
                for o in bpy.context.selected_objects:
                    o.show_wire = True
                    o.show_all_edges = True
        return {'FINISHED'}


class FLUENT_OT_AutoCompleteOne(Operator):
    """Completes your model.
Copy the object and apply every modifier.

Hold Ctrl - to apply without duplication.
Hold Alt - to keep the outer bevel as modifier.
Hold Shift - to remove the outer bevels.
Hold Ctrl+Shift - to revert to non-destructive."""
    bl_idname = "fluent.autocompleteone"
    bl_label = "Autocomplete"
    bl_options = {'REGISTER', 'UNDO'}

    from_normal_repair: bpy.props.BoolProperty(
        description="from_normal_repair",
        name="from_normal_repair",
        default=False
    )

    def macro(self):
        # mark sharp, seams, unwrap
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.edges_select_sharp(sharpness=0.610865)
        if not self.from_normal_repair:
            bpy.ops.mesh.mark_sharp()
        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.unwrap(method='CONFORMAL', fill_holes=True, correct_aspect=False, margin=0.003)
        bpy.ops.object.mode_set(mode='OBJECT')

    def mark_seam_in_cylinder(self, obj):
        # mark seam sur rayon avant solidify
        active_object(obj, 'SET', True)
        for mm in obj.modifiers:
            if mm.name != 'First_Solidify':
                if mm.type != 'BOOLEAN':
                    if mm.show_render:
                        try:
                            bpy.ops.object.modifier_apply(modifier=mm.name)
                        except:
                            obj.modifiers.remove(mm)
                    else:
                        obj.modifiers.remove(mm)
            else:
                # trouve un rayon et mark seam
                length = 0
                i = 0
                for e in obj.data.edges:
                    vertices = obj.data.vertices
                    v1 = vertices[e.vertices[0]]
                    v2 = vertices[e.vertices[1]]
                    next_length = length_between(
                        v1.co.x, v1.co.y, v2.co.x, v2.co.y)
                    if next_length > length:
                        length = next_length
                        if i >= 1:
                            first_seam = e
                            # mark seam et applique le solidify
                            e.use_seam = True
                            try:
                                bpy.ops.object.modifier_apply(modifier=mm.name)
                            except:
                                obj.modifiers.remove(mm)
                            break
                    i += 1
                # mark l'edge entre les 2 rayons
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_mode(type='EDGE')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                for e in obj.data.edges:
                    if e.use_seam:
                        e.select = True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.loop_multi_select(ring=False)
                bpy.ops.mesh.mark_seam(clear=False)
                bpy.ops.object.mode_set(mode='OBJECT')

    def cylinder(self, obj):
        # ajout de seams sur les coupes cylindriques
        # si boolean → regarde l'objet → si cylindre → duplique l'objet et l'utilise à la place → routine d'ajout de seam
        copy_list = []
        bool_list = []
        for m in obj.modifiers:
            if m.type == 'BOOLEAN' and m.object:
                bool = m.object
                bool_visibility = bool.hide_viewport
                bool_list.append([bool, bool_visibility])
                # if bool.get('fluent_type') == 'prism':
                #     bool.hide_viewport = False
                #     # active_object(bool, 'SET', True)
                #     # bpy.ops.object.duplicate()
                #     # copy = active_object(action='GET')
                #     copy = duplicate(bool)
                #     copy_list.append(copy)
                #     m.object = copy
                #     active_object(copy, 'SET', True)
                #     self.mark_seam_in_cylinder(copy)

        return copy_list, bool_list

    def autocomplete(self, obj, alt=False, shift=False, ctrl=False):
        # ctrl → pas de duplication
        # alt → garde le dernier bevel
        # shift → retire le dernier bevel

        # TODO pouvoir marker les seems dans les cylindres.
        # if obj.get('fluent_type') in {'prism'}:
        #     self.mark_seam_in_cylinder(obj)

        if ctrl or self.from_normal_repair:
            obj_completed = obj
            if not self.from_normal_repair:
                obj_completed.name += '.frozen'
        else:
            active_object('SET', obj, True)
            bpy.ops.object.duplicate()
            obj_completed = active_object('GET')
            obj_completed.name = obj.name + '.frozen'
            obj.hide_render = True
            obj.hide_set(True)
            obj_completed.hide_render = False
            obj_completed.hide_set(False)

        bevel = None
        weighted_normal = None
        if alt:
            modifiers_count = len(obj_completed.modifiers)
            if modifiers_count >= 2 and fluent_modifiers_name['outer_bevel'] in obj_completed.modifiers[
                modifiers_count - 2].name and obj_completed.modifiers[modifiers_count - 1].type == 'WEIGHTED_NORMAL':
                bevel = get_modifier_values(obj.modifiers[modifiers_count - 2])
                weighted_normal = get_modifier_values(obj_completed.modifiers[modifiers_count - 1])
                obj_completed.modifiers.remove(obj_completed.modifiers[len(obj_completed.modifiers) - 1])
                obj_completed.modifiers.remove(obj_completed.modifiers[len(obj_completed.modifiers) - 1])
        if shift:
            modifiers_count = len(obj_completed.modifiers)
            if modifiers_count >= 2 and fluent_modifiers_name['outer_bevel'] in obj_completed.modifiers[
                modifiers_count - 2].name and obj_completed.modifiers[modifiers_count - 1].type == 'WEIGHTED_NORMAL':
                obj_completed.modifiers.remove(obj_completed.modifiers[len(obj_completed.modifiers) - 1])
                obj_completed.modifiers.remove(obj_completed.modifiers[len(obj_completed.modifiers) - 1])

        active_object(action='SET', obj=obj_completed, solo=True)
        bpy.ops.object.convert(target='MESH')
        try:
            self.macro()
        except:
            bpy.ops.object.mode_set(mode='OBJECT')

        if bevel:
            bpy.ops.fluent.addlatestbevel('INVOKE_DEFAULT')
            set_modifier_value(obj_completed.modifiers[fluent_modifiers_name['outer_bevel']], bevel)
            set_modifier_value(obj_completed.modifiers[fluent_modifiers_name['weighted_normal']], weighted_normal)

        if obj_completed.get('fluent_obj'):
            obj_completed['fluent_obj'] = 0
        if obj_completed.get('fluent_type'):
            obj_completed['fluent_type'] = 'unknow'

        return obj_completed

    def invoke(self, context, event):
        latest_bevel_obj_list = []
        fluent_object_list = []
        object_completed_list = []

        if len(bpy.context.selected_objects):
            if event.ctrl and event.shift:  # suppression du frozen et réaffichage du non destructif
                for obj in bpy.context.selected_objects:
                    try:
                        original_name = obj.name.split('.frozen')[0]
                        bpy.data.objects.get(original_name).hide_viewport = False
                        bpy.data.objects.get(original_name).hide_render = False
                        bpy.data.objects.get(original_name).hide_set(False)
                        bpy.data.objects.remove(obj, do_unlink=True)
                    except:
                        pass
                return {'FINISHED'}
            else:
                # liste tous les objets fluent parmi la selection
                for obj in bpy.context.selected_objects:
                    if obj.type in {'MESH'}:
                        fluent_object_list.append(obj)
                for obj in bpy.context.selected_objects:
                    if obj.type in {'CURVE'}:
                        fluent_object_list.append(obj)

                # sélectionne les objets fluent et applique tous les modifiers
                for obj in fluent_object_list:
                    object_completed_list.append(
                        self.autocomplete(obj, ctrl=event.ctrl, alt=event.alt, shift=event.shift))

                # place les objets dans une collection dédiée et les rends visibles au rendu
                if not bpy.data.collections.get('Completed'):
                    coll = bpy.data.collections.new("Completed")
                    bpy.context.scene.collection.children.link(coll)

                for o in object_completed_list:
                    o.hide_render = o.hide_viewport = False
                    try:
                        bpy.context.scene.collection.objects.unlink(o)
                    except:
                        pass
                    try:
                        for c in bpy.data.collections:
                            for oo in c.objects:
                                if oo == o:
                                    c.objects.unlink(o)
                        bpy.data.collections['Completed'].objects.link(o)
                    except:
                        pass

                active_object(object_completed_list[0], 'SET', True)
                return {'FINISHED'}
        else:
            make_oops(['Select at least one object.'], title="How to use ?", icon='ERROR')

            return {'CANCELLED'}


class FLUENT_OT_NormalRepair(Operator):
    """Repair shading artifact
Be careful every modifier will be applied but the original object is kept.

Hold Shift - to remove a repaired object and revert to the live version"""
    bl_idname = "fluent.normalrepair"
    bl_label = "Normal Repair"
    bl_options = {'REGISTER', 'UNDO'}

    def make_source(self, obj):
        # réalise une copie sans booléen de l'objet
        self.normal_source_obj = duplicate(obj, name='_normalSource')
        self.normal_source_obj.hide_viewport = False
        if self.root_name:
            bpy.data.objects.get(self.root_name).hide_set(True)
        for m in self.normal_source_obj.modifiers:
            if m.type == 'BOOLEAN':
                self.normal_source_obj.modifiers.remove(m)
        active_object('SET', self.normal_source_obj, True)
        bpy.ops.object.convert(target='MESH')
        self.normal_source_obj.hide_render = True
        self.normal_source_obj.hide_set(True)
        bpy.ops.object.select_all(action='DESELECT')

    def prepare_data_transfer(self, already_fixed=False):
        active_object('SET', self.normal_fixed_obj, True)
        if not already_fixed:
            self.normal_fixed_obj.select_set(True)
            bpy.ops.fluent.autocompleteone('INVOKE_DEFAULT', from_normal_repair=True)
        self.normal_fixed_obj.hide_set(False)
        self.normal_fixed_obj.hide_render = False
        # self.normal_fixed_obj = active_object('GET')
        active_object('SET', self.normal_fixed_obj, solo=True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="FACE")
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode='OBJECT')

        # supprime les vertex groups si déjà présent
        for vg in self.normal_fixed_obj.vertex_groups:
            self.normal_fixed_obj.vertex_groups.remove(vg)
        # création du vertex group
        self.vertex_group = self.normal_fixed_obj.vertex_groups.new(name='NormalRepair')

        modif = self.normal_fixed_obj.modifiers.new(name=fluent_modifiers_name['data_transfer'], type='DATA_TRANSFER')
        modif.object = self.normal_source_obj
        modif.vertex_group = 'NormalRepair'
        modif.use_loop_data = True
        modif.data_types_loops = {'CUSTOM_NORMAL'}
        modif.loop_mapping = 'POLYINTERP_LNORPROJ'
        modif.show_in_editmode = True
        self.vertex_group.remove(
            [v.index for v in self.normal_fixed_obj.data.vertices])
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="FACE")
        bpy.ops.object.mode_set(mode='OBJECT')

    def modal(self, context, event):
        context.area.tag_redraw()
        try:
            self.update_display()
        except:
            pass

        if not event.type in {'RET', 'NUMPAD_ENTER', 'RIGHTMOUSE', 'TAB'} and self.build_step == 2:
            return {'PASS_THROUGH'}
        elif pass_through(event):
            return {'PASS_THROUGH'}

        if self.build_step == 0:  # ajuste le weld
            self.original_obj.modifiers['.f_weld_normal_repair'].merge_threshold = (event.mouse_region_x - self.x_mouse_slider_origin) / 4000
            if event.value == 'PRESS' and event.type == 'LEFTMOUSE':
                self.build_step = 0.5
                bpy.context.object.show_wire = False
                self.side_infos.add_line('STEP 2/3', 'Select the normal source.')
                return {'RUNNING_MODAL'}
        elif self.build_step == 0.5:  # affiche les booleans pour sélection de la source
            bpy.ops.fluent.booleandisplay('INVOKE_DEFAULT')
            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = None
            if '_normalFixed' in self.original_obj.name:
                bpy.data.objects.get(self.original_name).hide_set(False)
                self.original_obj.hide_set(True)
                # root_name = self.original_obj.name.split('_normalFixed')[0]
                # bpy.data.objects.get(root_name).hide_set(False)
            self.build_step = 1
            return {'RUNNING_MODAL'}
        elif self.build_step == 1 and event.value == 'PRESS' and event.type == 'LEFTMOUSE':  # selection de la source
            obj = click_on(event.mouse_region_x, event.mouse_region_y, ignore=False, search=['MESH'], ignore_display=[['BOUNDS']])
            if obj:
                try:
                    bpy.data.objects.get(self.original_name).hide_set(True)
                    self.original_obj.hide_set(True)
                except:pass
                self.make_source(obj)
                self.normal_fixed_obj = duplicate(self.original_obj)
                active_object('SET', self.normal_fixed_obj, True)
                for m in self.normal_fixed_obj.modifiers:
                    if m.type == 'WEIGHTED_NORMAL':
                        self.normal_fixed_obj.modifiers.remove(modifier=m)
                bpy.ops.object.convert(target='MESH')
                if self.normal_fixed_obj.get('fluent_obj'):
                    self.normal_fixed_obj['fluent_obj'] = 0
                if self.normal_fixed_obj.get('fluent_type'):
                    self.normal_fixed_obj['fluent_type'] = 'unknow'
                self.normal_fixed_obj.name = self.original_obj.name + '_normalFixed'
                self.original_obj.hide_set(True)
                self.original_obj.hide_render = True
                try:
                    self.original_obj.modifiers.remove(modifier=self.original_obj.modifiers['.f_weld_normal_repair'])
                except:
                    pass
                self.prepare_data_transfer()
                self.build_step = 2
                self.side_infos.add_line('STEP 3/3', 'Select faces then press enter.')
                self.side_infos.add_line('Quit', 'Right click')
                bpy.ops.fluent.booleandisplay('INVOKE_DEFAULT')
                active_object('SET', self.normal_fixed_obj, True)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.context.space_data.shading.type = 'SOLID'
                bpy.context.space_data.shading.light = 'MATCAP'
                bpy.context.space_data.shading.studio_light = 'metal_carpaint.exr'
                return {'RUNNING_MODAL'}
        elif self.build_step == 2 and event.value == 'PRESS' and event.type in {'RET', 'NUMPAD_ENTER'}:  # ajoute la selection au vertex group utilisé par le data transfer
            bpy.ops.object.mode_set(mode='OBJECT')
            selected_verts = [
                v.index for v in self.normal_fixed_obj.data.vertices if v.select]
            self.vertex_group.add(selected_verts, 1, "ADD")
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action="DESELECT")

        # sortie du modal
        if event.value == 'PRESS' and event.type in {'RIGHTMOUSE', 'TAB'} and self.build_step == 2:
            bpy.context.space_data.shading.type = self.previous_viewport_settings['type']
            bpy.context.space_data.shading.light = self.previous_viewport_settings['light']
            bpy.context.space_data.shading.studio_light = self.previous_viewport_settings['studio_light']
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.modifier_apply(modifier=fluent_modifiers_name['data_transfer'])
            self.normal_fixed_obj.vertex_groups.clear()
            bpy.data.objects.remove(self.normal_source_obj, do_unlink=True)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_two, 'WINDOW')
            return {'FINISHED'}

        if event.value == 'PRESS' and event.type == 'ESC':
            try:
                self.original_obj.show_wire = False
            except:
                pass
            bpy.types.SpaceView3D.draw_handler_remove(
                self._handle_two, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # étape 0 : weld modifier, étape 1 : selectionne la source, étape 2 : selectionne les faces
        self.original_obj = active_object('GET')
        # vérifications
        if len(bpy.context.selected_objects) != 1:
            make_oops(['Select one object.'], title="How to use ?", icon='ERROR')
            return {'FINISHED'}

        # initialisation
        self.adjustment = None
        self.previous_viewport_settings = {
            'type': bpy.context.space_data.shading.type,
            'studio_light': bpy.context.space_data.shading.studio_light,
            'light': bpy.context.space_data.shading.light
        }
        self.original_obj = active_object(action='GET')
        self.build_step = 0
        self.root_name = None
        self.x_mouse_slider_origin = event.mouse_region_x
        self.ui_items_list = []
        self.side_infos = FLUENT_Panel_Infos()
        self.ui_items_list.append(self.side_infos)
        self.events = {}

        # recherche de bevel
        has_bevel = [False, None]
        if len(self.original_obj.modifiers) >= 1 and self.original_obj.modifiers[-1].type == 'BEVEL':
            has_bevel = [True, -1]
        if len(self.original_obj.modifiers) >= 2 and self.original_obj.modifiers[-2].type == 'BEVEL':
            has_bevel = [True, -2]

        if not '_normalFixed' in self.original_obj.name:
            if not has_bevel[0]:
                make_oops(['No bevel modifier found.', 'Please add then try again.'], title="How to use ?",
                          icon='ERROR')
                return {'FINISHED'}
            try:
                # ajoute le weld modifier pour corriger l'overlapping
                self.weld_modifier = self.original_obj.modifiers.new(name='.f_weld_normal_repair', type='WELD')
                if has_bevel[1] == -1:
                    bpy.ops.object.modifier_move_up(modifier='.f_weld_normal_repair')
                elif has_bevel[1] == -2:
                    bpy.ops.object.modifier_move_up(modifier='.f_weld_normal_repair')
                    bpy.ops.object.modifier_move_up(modifier='.f_weld_normal_repair')
                bpy.context.object.show_wire = True
                self.side_infos.add_line('STEP 1/3', 'Merge close vertices')
            except:
                self.build_step = 0.5
        else:
            if event.shift:
                # supprime l'objet et sa normal source et réaffiche le suivant
                root_name = self.original_obj.name.split('_normalFixed')[0]
                live_object = bpy.data.objects.get(root_name)
                bpy.data.objects.remove(self.original_obj, do_unlink=True)
                live_object.hide_viewport = False
                live_object.hide_render = False
                return {'FINISHED'}
            else:
                # édition
                self.original_name = self.original_obj.name.split('_normalFixed')[0]

                try:
                    # ajoute le weld modifier pour corriger l'overlapping
                    self.weld_modifier = self.original_obj.modifiers.new(name='.f_weld_normal_repair', type='WELD')
                    if has_bevel[1] == -1:
                        bpy.ops.object.modifier_move_up(modifier='.f_weld_normal_repair')
                    elif has_bevel[1] == -2:
                        bpy.ops.object.modifier_move_up(modifier='.f_weld_normal_repair')
                        bpy.ops.object.modifier_move_up(modifier='.f_weld_normal_repair')
                    bpy.context.object.show_wire = True
                    self.side_infos.add_line('STEP 1/3', 'Merge close vertices')
                except:
                    self.build_step = 0.5

                # bpy.data.objects.get(self.original_name).hide_set(False)
                # self.original_obj.hide_set(True)
                # bpy.ops.fluent.booleandisplay('INVOKE_DEFAULT')
                # bpy.ops.object.select_all(action='DESELECT')
                # context.view_layer.objects.active = None
                # self.build_step = 1
                self.build_step = 0

        self._handle_two = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class FLUENT_OT_BooleanDuplicate(Operator):
    """Duplicate/Extract a boolean object
Select a boolean object to duplicate it.
Hold Shift - Extract the selected boolean object
"""
    bl_idname = "fluent.booleanduplicate"
    bl_label = "Boolean Instance"
    bl_options = {'REGISTER', 'UNDO'}

    def duplicate(self):
        self.copy = duplicate(self.first, linked=True)

        self.copy['fluent_id'] = self.fluent_id
        add_in_bool_collection(self.copy)

        # Cut the cutter, les sous booléens doivent suivre
        for child in self.first.children:
            child_copy = duplicate(child)
            if child.get('fluent_id'):
                child_copy['fluent_id'] = child.get('fluent_id')
            else:
                child['fluent_id'] = child_copy['fluent_id'] = search_last_fluent_id() + 1
            child_copy.display_type = 'WIRE'
            add_in_bool_collection(child_copy)
            if get_addon_preferences().auto_parent:
                child_copy.hide_viewport = False
                child_copy.hide_set(False)
                active_object(action='SET', obj=self.copy, solo=True)
                child_copy.select_set(True)
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
                bpy.ops.object.select_all(action='DESELECT')
                child_copy.hide_viewport = True
            for m in self.copy.modifiers:
                if m.type == 'BOOLEAN' and m.object == child:
                    m.object = child_copy
                    break

        try:
            self.copy.rotation_euler = self.drawing.get_drawing_plane().rotation_euler.copy()
        except:
            pass
        if self.copy.get('fluent_type') == 'revolver':
            self.copy.rotation_euler.rotate_axis('X', math.radians(90))

        self.copy.display_type = 'WIRE'
        self.ui_items_list = [i for i in self.ui_items_list if type(i) is not FLUENT_Draw_Object]
        self.bool_drawing = FLUENT_Draw_Object(self.copy, (1, 1, 1, 0.05))
        self.ui_items_list.append(self.bool_drawing)

    def modal(self, context, event):
        context.area.tag_redraw()

        self.events['mouse_x'] = event.mouse_region_x
        self.events['mouse_y'] = event.mouse_region_y

        self.events['value'] = event.value
        self.events['type'] = event.type

        self.events = event_dico_refresh(self.events, event)

        # action des bouttons
        action = None
        for b in self.ui_items_list:
            if 'FLUENT_Ui_Button' in str(type(b)):
                b.is_hover(self.events)
                if b.get_state() == 2:
                    action = b.get_action()
                    b.set_state(0)
                    break
                else:
                    action = None
            elif 'FLUENT_Ui_Layout' in str(type(b)):
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

        # raccourcis clavier
        if event.value == 'PRESS' and event.type in 'Q':
            action = 'QUIT'
        if event.value == 'PRESS' and event.type == 'R':
            action = 'ROT_Z'

        # execution de l'action
        if action == 'QUIT':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_two, 'WINDOW')
            for m in self.bool_list:
                m.operation = self.operation
                m.show_viewport = True
            for child in self.copy.children:
                bpy.data.objects.remove(child, do_unlink=True)
            bpy.data.objects.remove(self.copy, do_unlink=True)
            boolean_cleaner([self.duplicate_on])
            for copy in self.copies:
                for child in copy.children:
                    child.hide_viewport = False
            return {'FINISHED'}
        elif action == 'ROT_Z':
            self.copy.rotation_euler.rotate_axis('Z', math.radians(45))

        if event.type == 'MOUSEMOVE':
            self.previous_cast = self.cast.copy()
            if self.duplicate_on:
                self.cast = obj_ray_cast(self.duplicate_on, self.events['mouse_x'], self.events['mouse_y'])
            if not self.cast['success']:
                self.duplicate_on = click_on(self.events['mouse_x'], self.events['mouse_y'], ignore=self.copy,
                                             search=['MESH'])
            if (self.cast['success'] and self.cast['normal'] != self.previous_cast['normal']) or (
                    not self.drawing.get_extended() and self.cast['face_index'] != self.previous_cast['face_index']):
                self.duplicate_on = click_on(self.events['mouse_x'], self.events['mouse_y'], ignore=self.copy,
                                             search=['MESH'])
                if self.duplicate_on:
                    is_display = self.drawing.get_display_dots()
                    self.drawing.reset()
                    self.drawing.grid_init(self.duplicate_on, self.events)
                    self.drawing.set_display_grid(True)
                    self.drawing.set_display_dots(is_display)
                    try:
                        self.copy.rotation_euler = self.drawing.get_drawing_plane().rotation_euler.copy()
                        if self.copy.get('fluent_type') == 'revolver':
                            self.copy.rotation_euler.rotate_axis('X', math.radians(90))
                    except:
                        pass
            try:
                self.copy.location = self.duplicate_on.matrix_world @ \
                                     obj_ray_cast(self.duplicate_on, self.drawing.get_snaped_coords()[0],
                                                  self.drawing.get_snaped_coords()[1])['hit']
            except:
                pass

        # place la copie
        if event.value == 'PRESS' and event.type == 'LEFTMOUSE' and self.duplicate_on:
            if get_addon_preferences().auto_parent:
                parent_relationship(self.duplicate_on, self.copy)

            new_mod = self.duplicate_on.modifiers.new(name=fluent_modifiers_name['boolean'], type="BOOLEAN")
            new_mod.solver = 'FAST'
            new_mod.object = self.copy
            new_mod.show_expanded = False
            new_mod.show_viewport = False
            new_mod.operation = self.operation
            self.bool_list.append(new_mod)
            bevels = F_outer_bevel(self.duplicate_on)
            bevels.management()
            self.copies.append(self.copy)
            self.duplicate()

        # controle de la grille
        if event.value == 'PRESS' and event.type == 'C':
            self.drawing.set_display_dots(not self.drawing.get_display_dots())
        if event.value == 'PRESS' and event.type == 'V':
            self.drawing.set_resolution(self.drawing.get_resolution() + 1)
            bpy.context.scene.fluentProp.grid_resolution = self.drawing.get_resolution()
        if event.value == 'PRESS' and event.type == 'B':
            self.drawing.set_resolution(self.drawing.get_resolution() - 1)
            bpy.context.scene.fluentProp.grid_resolution = self.drawing.get_resolution()
        if event.value == 'PRESS' and event.type == 'X':
            self.drawing.set_extended(not self.drawing.get_extended())

        if pass_through(event):
            return {'PASS_THROUGH'}

        # Quit
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            bpy.data.objects.remove(self.copy, do_unlink=True)
            bpy.data.objects.remove(self.drawing.get_drawing_plane(), do_unlink=True)
            for b in self.bool_list:
                b.show_expanded = True
                b.show_viewport = True
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return{'FINISHED'}

        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        obj = active_object('GET')
        self.first = obj

        if not obj:
            make_oops(['Select one object at least.'], title="How to use?", icon='ERROR')
            return {'FINISHED'}
        else:
            if not obj.get('fluent_operation'):
                make_oops(['Select a boolean object.'], title="How to use?", icon='ERROR')
                return {'FINISHED'}

        if event.shift:  # extraction
            boolean_extraction()
            return {'FINISHED'}

        # duplicate
        self.previous_cast = None
        self.bool_list = []
        self.copy = None
        self.copies = []

        self.operation = 'DIFFERENCE'
        try:
            if obj.get('fluent_type') in ['box', 'prism', 'poly'] and obj.modifiers[fluent_modifiers_name['first_solidify']].thickness > 0:
                self.operation = 'UNION'

            if obj.get('fluent_type') in ['revolver']:
                co_y_moyen = 0
                for v in obj.data.vertices:
                    co_y_moyen = co_y_moyen + v.co.y
                co_y_moyen = co_y_moyen / len(obj.data.vertices)
                if co_y_moyen > 0:
                    self.operation = 'UNION'

            if obj.get('fluent_type') in ['path'] and obj.modifiers[fluent_modifiers_name['path_height']].screw_offset > 0:
                self.operation = 'UNION'
        except:
            pass
        self.ui_items_list = []
        self.drawing = FLUENT_Drawing()
        self.ui_items_list.append(self.drawing)
        self.side_infos = FLUENT_Panel_Infos()
        self.ui_items_list.append(self.side_infos)
        # button = make_button('CANCEL')
        # self.ui_items_list.append(button)

        self.side_infos.add_line('Put', 'Left click')
        self.side_infos.add_line('Rotate', 'R')
        self.side_infos.add_line('Grid resolution', 'V / B')
        self.side_infos.add_line('Grid displaying', 'C')
        self.side_infos.add_line('Grid extended', 'X')
        self.side_infos.add_line('Quit', 'Right click')

        self.events = event_dico_builder(event)

        self.duplicate_on = click_on(self.events['mouse_x'], self.events['mouse_y'], ignore=obj, search=['MESH'])
        if self.duplicate_on:
            self.drawing.grid_init(self.duplicate_on, self.events)
            self.drawing.set_display_grid(True)
            self.drawing.set_display_dots(True)
            self.cast = obj_ray_cast(self.duplicate_on, self.events['mouse_x'], self.events['mouse_y'])
        else:
            self.cast = {'success': False, 'normal': None}

        if obj.get('fluent_id'):
            self.fluent_id = obj.get('fluent_id')
        else:
            self.fluent_id = search_last_fluent_id() + 1
            obj['fluent_id'] = self.fluent_id

        self.duplicate()

        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class FLUENT_OT_BooleanSynchronization(Operator):
    """Synchronize boolean objects duplicated by Fluent duplicate function"""
    bl_idname = "fluent.booleansynchronization"
    bl_label = "Boolean Synchronization"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        obj = bpy.context.active_object
        modifiers_values = []
        if obj and obj.get('fluent_id'):
            fluent_id = obj.get('fluent_id')
            for m in obj.modifiers:
                modifiers_values.append(get_modifier_values(m))
            for o in bpy.data.objects:
                have_to_be_synchronized = []
                if o.get('fluent_id') and o.get('fluent_id') == fluent_id and o != obj:
                    o.modifiers.clear()
                    have_to_be_synchronized.append(o)
                    for s in have_to_be_synchronized:
                        for mSrc in obj.modifiers:
                            mDst = s.modifiers.get(mSrc.name, None)
                            if not mDst:
                                mDst = s.modifiers.new(mSrc.name, mSrc.type)
                            # collect names of writable properties
                            properties = [p.identifier for p in mSrc.bl_rna.properties if not p.is_readonly]
                            # copy those properties
                            for prop in properties:
                                setattr(mDst, prop, getattr(mSrc, prop))
        else:
            make_oops(['Select a duplicated Fluent boolean object'], title="Info", icon='ERROR')
            return {'FINISHED'}
        return {'RUNNING_MODAL'}


class FLUENT_OT_VGCleaner(Operator):
    """Remove selected vertices from each vertex groups"""
    bl_idname = "fluent.vgcleaner"
    bl_label = "VG Cleaner"

    def execute(self, context):
        obj = active_object('GET')
        bpy.ops.object.mode_set(mode='EDIT')
        displayed_bevels = []
        for m in obj.modifiers:
            if m.type == 'BEVEL' and 'First_Bevel' in m.name:
                m.show_viewport = False
                displayed_bevels.append(m)
        bpy.ops.object.mode_set(mode='OBJECT')
        selected_verts = [v.index for v in obj.data.vertices if v.select]
        for vg in obj.vertex_groups:
            vg.remove(selected_verts)
        for b in displayed_bevels:
            b.show_viewport = True
        return {'FINISHED'}


class FLUENT_OT_ToggleLoopSlide(Operator):
    """Toggle the bevel's loop slide option"""
    bl_idname = "fluent.toggleloopslide"
    bl_label = "Toggle Loop Slide"

    def execute(self, context):
        for o in bpy.context.selected_objects:
            for m in o.modifiers:
                if fluent_modifiers_name['outer_bevel'] in m.name and m.type == 'BEVEL':
                    m.loop_slide = not m.loop_slide
        return {'FINISHED'}


class FLUENT_OT_BecomeFluent(Operator):
    """Transform a plane to a Fluent object
Hold Alt - Extract a face from an object"""
    bl_idname = "fluent.becomefluent"
    bl_label = "Become Fluent"
    bl_options = {'REGISTER', 'UNDO'}

    call_from: bpy.props.StringProperty(
        name='call_from',
        default=''
    )

    def convert(self):
        print('--- CONVERT')
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = active_object()
        active_object('SET', obj, True)
        if obj.type == 'MESH':
            try:
                for m in obj.modifiers:
                    obj.modifiers.remove(m)
            except:
                pass
            bpy.ops.object.convert(target='MESH')
            if len(obj.data.polygons):
                decimate = obj.modifiers.new(type='DECIMATE', name='Decimate')
                decimate.decimate_type = 'DISSOLVE'
                bpy.ops.object.convert(target='MESH')
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
                error = False
                for i, p in enumerate(obj.data.polygons):
                    try:
                        if round(math.fabs(obj.data.polygons[i].normal.x), 5) != round(
                                math.fabs(obj.data.polygons[i - 1].normal.x), 5) or round(
                                math.fabs(obj.data.polygons[i].normal.y), 5) != round(
                                math.fabs(obj.data.polygons[i - 1].normal.y), 5) or round(
                                math.fabs(obj.data.polygons[i].normal.z), 5) != round(
                                math.fabs(obj.data.polygons[i - 1].normal.z), 5):
                            error = True
                    except:
                        pass
                if not error:
                    bpy.ops.object.shade_smooth()
                    bpy.context.object.data.use_auto_smooth = True
                    active_object('SET', obj, True)
                    if self.call_from == 'PRIMITIVE':
                        print('--- call from primitive')
                        obj['fluent_type'] = 'box'
                        bpy.ops.fluent.editor('INVOKE_DEFAULT', bool_obj_name=obj.name, cut_obj_name='',
                                              operation='CREATION')
                    else:
                        obj['fluent_type'] = 'poly'
                        active_object('SET', obj, True)
                        bpy.ops.fluent.editor('INVOKE_DEFAULT', operation='EDIT')
                    return {'FINISHED'}
                else:
                    make_oops(['Your object seems to not be a plane.'], title="Problem detected.", icon='ERROR')
                    return {'CANCELLED'}
            else:
                make_oops(['No faces. Your object have to be a plane.'], title="Problem detected.", icon='ERROR')
                return {'CANCELLED'}
        elif obj.type == 'CURVE':
            if len(obj.data.splines) == 1 and len(obj.data.splines[0].bezier_points):
                bpy.ops.fluent.wire('INVOKE_DEFAULT', operation='BECOME_FLUENT')
            else:
                if len(obj.data.splines) != 1:
                    make_oops(['Single curve is expected.'], title="How to use ?", icon='ERROR')
                elif not len(obj.data.splines[0].bezier_points):
                    make_oops(['A bezier curve is expected.'], title="How to use ?", icon='ERROR')
            return {'FINISHED'}

    def invoke(self, context, event):
        # vérifications
        if not active_object('GET'):
            make_oops(['No object selected.'], title="How to use ?", icon='ERROR')
            return {'FINISHED'}
        if not event.alt:
            self.convert()
            return {'FINISHED'}
        else:
            bpy.ops.fluent.faceextraction('INVOKE_DEFAULT')
            return {'FINISHED'}


class FLUENT_OT_FaceExtraction(Operator):
    """Face extraction
    Extract a face from an object then turn it into a Fluent object"""
    bl_idname = "fluent.faceextraction"
    bl_label = "Face extraction"
    bl_options = {'REGISTER', 'UNDO'}

    obj = None
    extracted = None
    ui_items_list = []
    events = {}
    call_by: StringProperty(
        default=''
    )

    def modal(self, context, event):
        context.area.tag_redraw()

        if not event.type in ['RET', 'NUMPAD_ENTER', 'ESC']:
            return {'PASS_THROUGH'}
        if event.type in ['RET', 'NUMPAD_ENTER'] and event.value == 'PRESS':
            save_view_mat = bpy.context.region_data.view_matrix.copy()
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set(mode='OBJECT')
            self.extracted = bpy.context.selected_objects[1]
            bpy.data.objects.remove(self.copy, do_unlink=True)
            self.obj.hide_viewport = False
            active_object('SET', self.extracted, True)

            # remettre à plat
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            if space.region_3d.is_perspective:
                                init_persp_ortho = 'PERSP'
                            else:
                                init_persp_ortho = 'ORTHO'

            context.region_data.view_perspective = 'ORTHO'
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.view3d.view_axis(type='TOP', align_active=True, relative=False)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')
            bpy.ops.object.empty_add(align='VIEW')
            temp_empty = bpy.context.active_object
            temp_empty.rotation_mode = 'XYZ'

            restoreRot_X = temp_empty.rotation_euler[0]
            restoreRot_Y = temp_empty.rotation_euler[1]
            restoreRot_Z = temp_empty.rotation_euler[2]

            bpy.ops.object.select_all(action='DESELECT')
            self.extracted.select_set(True)
            temp_empty.select_set(True)
            bpy.context.view_layer.objects.active = temp_empty
            bpy.ops.object.parent_set()

            bpy.ops.object.select_all(action='DESELECT')
            temp_empty.select_set(True)
            bpy.ops.object.rotation_clear()

            bpy.ops.object.select_all(action='DESELECT')
            self.extracted.select_set(True)
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

            self.extracted.rotation_mode = 'XYZ'
            self.extracted.rotation_euler[0] = restoreRot_X
            self.extracted.rotation_euler[1] = restoreRot_Y
            self.extracted.rotation_euler[2] = restoreRot_Z

            bpy.ops.object.select_all(action='DESELECT')
            temp_empty.select_set(True)
            bpy.ops.object.delete()

            active_object(self.extracted, 'SET', True)

            context.region_data.view_perspective = init_persp_ortho
            bpy.context.region_data.view_matrix = save_view_mat

            for p in self.extracted.data.polygons:
                p.use_smooth = True

            if self.call_by == 'CUT':
                self.extracted['fluent_type'] = 'poly'
                self.extracted.display_type == 'WIRE'
                boolean_visibility_setup(self.extracted)
                add_in_bool_collection(self.extracted)
                parent_relationship(self.obj, self.extracted)
                self.obj.hide_set(False)
                for p in self.extracted.data.polygons:
                    p.flip()
                bpy.ops.fluent.editor('INVOKE_DEFAULT', bool_obj_name=self.extracted.name,
                                      cut_obj_name=self.obj.name, operation='CUT')
            elif self.call_by == 'plate':
                bpy.context.scene.collection.objects.link
                self.extracted['fluent_type'] = 'plate'
                self.extracted.data.use_auto_smooth = True
                self.obj.hide_set(False)

                for p in self.extracted.data.polygons:
                    p.flip()

                active_object('SET', self.extracted, True)
                mirror = self.extracted.modifiers.new(name=fluent_modifiers_name['mirror'], type='MIRROR')
                mirror.mirror_object = self.obj
                mirror.show_viewport = False
                mirror.show_render = False
                mirror.use_axis[0] = False
                mirror.use_axis[1] = False
                mirror.use_axis[2] = False
                mirror.use_bisect_axis[0] = True
                mirror.use_bisect_axis[1] = True
                mirror.use_bisect_axis[2] = True
                mirror.show_expanded = False
                bpy.ops.fluent.editor('INVOKE_DEFAULT', bool_obj_name=self.extracted.name, operation='PLATE')

                if self.obj.modifiers.get(fluent_modifiers_name['outer_bevel']):
                    copy_modifiers_stack(self.obj, self.extracted, name=fluent_modifiers_name['outer_bevel'])
                    copy_modifiers_stack(self.obj, self.extracted, name=fluent_modifiers_name['weighted_normal'])

            else:
                for p in self.extracted.data.polygons:
                    p.flip()
                self.obj.hide_set(False)
                active_object('SET', self.extracted, True)
                bpy.ops.fluent.becomefluent('INVOKE_DEFAULT')

            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}
        if event.type == 'ESC' and event.value == 'PRESS':
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.data.objects.remove(self.copy)
            self.obj.hide_set(False)
            active_object('SET', self.obj, True)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if not self.obj and not active_object():
            make_oops(['Select an object'], title="How to use ?", icon='ERROR')
            return {'FINISHED'}

        if self.obj: active_object('SET', self.obj, True)
        if not self.obj: self.obj = active_object()

        if self.call_by == 'plate':
            self.copy = duplicate(self.obj, '.Plate')
        else:
            self.copy = duplicate(self.obj)
        apply_modifiers(self.copy)

        self.obj.hide_set(True)
        active_object('SET', self.copy, True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        bpy.ops.mesh.select_all(action='DESELECT')

        side_infos = FLUENT_Panel_Infos()
        side_infos.add_line('Select faces', '')
        side_infos.add_line('Validate', 'Enter')
        self.ui_items_list.append(side_infos)

        self.events = event_dico_builder(event)

        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


class FLUENT_OT_OtherAdjustments(Operator):
    """Options"""
    bl_idname = "fluent.otheradjustments"
    bl_label = "Other adjustments"
    bl_options = {'REGISTER', 'UNDO'}

    centered_array: bpy.props.BoolProperty(
        description="Draw array from the center",
        name="Centered array",
        default=True
    )
    auto_mirror_x: bpy.props.BoolProperty(
        description="Auto Mirror X",
        name="Auto Mirror X",
        default=False
    )
    auto_mirror_y: bpy.props.BoolProperty(
        description="Auto Mirror Y",
        name="Auto Mirror Y",
        default=False
    )
    auto_mirror_z: bpy.props.BoolProperty(
        description="Auto Mirror Z",
        name="Auto Mirror Z",
        default=False
    )
    loop_slide: bpy.props.BoolProperty(
        description="Use the loop slide option",
        name="Loop Slide",
        default=True
    )
    outer_bevel_segments: bpy.props.IntProperty(
        description="0 = automatic",
        name="Outer bevel segement",
        default=0,
        min=0,
        step=1
    )
    bevel_profile: bpy.props.FloatProperty(
        description="Bevel profil",
        name="Bevel profil",
        default=0.48,
        min=0,
        max=1,
        step=0.01
    )
    model_resolution: bpy.props.IntProperty(
        description='Resolution of bevels, cylinders and spheres (segments/m)',
        name='Model resolution',
        default=32,
        min=1,
        max=256
    )
    bevel_factor: bpy.props.FloatProperty(
        description="Increase/decrease the bevel size of selected object",
        name="Bevel factor",
        default=1,
        min=0.001,
        step=0.01
    )
    min_auto_bevel_segments: bpy.props.IntProperty(
        description="Minimum resolution of bevels (segments/m). 0 = automatic",
        name="Min. of segments for auto-bevel",
        default=1,
        min=0,
        step=1
    )
    min_auto_cylinder_segments: bpy.props.IntProperty(
        description="Minimum resolution of cylinders and spheres (segments/m). 0 = automatic",
        name="Min. of segments for auto-cylinder",
        default=1,
        min=0,
        step=1
    )

    def execute(self, context):

        if self.bevel_factor != 1:
            for o in bpy.context.selected_objects:
                for m in o.modifiers:
                    if m.type == 'BEVEL':
                        m.width *= self.bevel_factor

        if bpy.context.scene.fluentProp.bevel_profile != self.bevel_profile:
            bpy.context.scene.fluentProp.bevel_profile = self.bevel_profile

        if bpy.context.scene.fluentProp.auto_mirror_x != self.auto_mirror_x:
            bpy.context.scene.fluentProp.auto_mirror_x = self.auto_mirror_x

        if bpy.context.scene.fluentProp.auto_mirror_y != self.auto_mirror_y:
            bpy.context.scene.fluentProp.auto_mirror_y = self.auto_mirror_y

        if bpy.context.scene.fluentProp.auto_mirror_z != self.auto_mirror_z:
            bpy.context.scene.fluentProp.auto_mirror_z = self.auto_mirror_z

        if bpy.context.scene.fluentProp.centered_array != self.centered_array:
            bpy.context.scene.fluentProp.centered_array = self.centered_array

        if bpy.context.scene.fluentProp.loop_slide != self.loop_slide:
            bpy.context.scene.fluentProp.loop_slide = self.loop_slide

        if bpy.context.scene.fluentProp.outer_bevel_segments != self.outer_bevel_segments:
            bpy.context.scene.fluentProp.outer_bevel_segments = self.outer_bevel_segments

        if bpy.context.scene.fluentProp.model_resolution != self.model_resolution:
            bpy.context.scene.fluentProp.model_resolution = self.model_resolution
            # update_resolution()

        if bpy.context.scene.fluentProp.min_auto_bevel_segments != self.min_auto_bevel_segments:
            bpy.context.scene.fluentProp.min_auto_bevel_segments = self.min_auto_bevel_segments

        if bpy.context.scene.fluentProp.min_auto_cylinder_segments != self.min_auto_cylinder_segments:
            bpy.context.scene.fluentProp.min_auto_cylinder_segments = self.min_auto_cylinder_segments

        return {'FINISHED'}

    def invoke(self, context, event):
        self.bevel_factor = 1
        self.bevel_profile = bpy.context.scene.fluentProp.bevel_profile
        self.auto_mirror_x = bpy.context.scene.fluentProp.auto_mirror_x
        self.auto_mirror_y = bpy.context.scene.fluentProp.auto_mirror_y
        self.auto_mirror_z = bpy.context.scene.fluentProp.auto_mirror_z
        self.centered_array = bpy.context.scene.fluentProp.centered_array
        self.loop_slide = bpy.context.scene.fluentProp.loop_slide
        self.outer_bevel_segments = bpy.context.scene.fluentProp.outer_bevel_segments
        self.model_resolution = bpy.context.scene.fluentProp.model_resolution
        self.min_auto_bevel_segments = bpy.context.scene.fluentProp.min_auto_bevel_segments
        self.min_auto_cylinder_segments = bpy.context.scene.fluentProp.min_auto_cylinder_segments
        return context.window_manager.invoke_props_dialog(self)
