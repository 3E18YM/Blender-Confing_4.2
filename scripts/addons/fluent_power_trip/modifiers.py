import bpy
import mathutils
from .helpers import *
# from .viewport_drawing import *
# from .math_functions import *
# from .drawing import *
from .ui_button import *
from .constants import *
from .bevels import *
import bmesh


class modifiers_manager():
    def __init__(self, obj, bool_target = None):
        self.obj = obj
        self.draw_type = obj.get('fluent_type')
        self.bool_target = bool_target
        self.mirror = None
        self.array = None
        self.circular_array = None
        self.first_solidify = None
        self.second_solidify = None
        self.first_bevel = None
        self.second_bevel = None
        self.radius = None
        self.resolution = None
        self.curve = None
        self.path_height = None
        self.inset_solidify = None
        self.taper = None
        self.scale = None
        self.rotate = None
        self.outer_bevel = None
        self.keys = {
        'shift_work':False,
        'shift_press':False,
        'shift_release':False,
        'ctrl_work':False,
        'ctrl_press':False,
        'ctrl_release':False
        }
        self.x_mouse_slider_origin = None
        self.bool_operation = 'DIFFERENCE'
        self.adjust_what = None

    def get_widget(self):
        find = False
        if self.mirror:
            if self.mirror.get_widget():
                find = True
        if self.array:
            if self.array.get_widget():
                find = True
        return find

    def get_obj(self):
        return self.obj

    def get_ui(self, modifier):
        if modifier in ['FIRST_SOLIDIFY', 'PATH_THICKNESS']:
            try:
                return self.first_solidify.get_ui_items_list(), self.first_solidify.get_pie_menu()
            except:
                self.first_solidify_action(action='ADD')
                return self.first_solidify.get_ui_items_list(), self.first_solidify.get_pie_menu()
        elif modifier == 'FIRST_BEVEL':
            try:
                return self.first_bevel.get_ui_items_list(), self.first_bevel.get_pie_menu()
            except:
                self.first_bevel_action(action='ADD')
                if self.obj.display_type == 'WIRE':
                    self.obj.hide_set(True)
                return self.first_bevel.get_ui_items_list(), self.first_bevel.get_pie_menu()
        elif modifier == 'SECOND_BEVEL':
            try:
                return self.second_bevel.get_ui_items_list(), self.second_bevel.get_pie_menu()
            except:
                self.second_bevel_action(action='ADD')
                if self.obj.display_type == 'WIRE':
                    self.obj.hide_set(True)
                return self.second_bevel.get_ui_items_list(), self.second_bevel.get_pie_menu()
        elif modifier == 'SECOND_SOLIDIFY':
            try:
                return self.second_solidify.get_ui_items_list(), self.second_solidify.get_pie_menu()
            except:
                self.second_solidify_action(action='ADD')
                if self.obj.display_type == 'WIRE':
                    self.obj.hide_set(True)
                return self.second_solidify.get_ui_items_list(), self.second_solidify.get_pie_menu()
        elif modifier == 'MIRROR':
            try:
                return self.mirror.get_ui_items_list(), self.mirror.get_pie_menu()
            except:
                self.mirror_action(action='ADD', ref=self.bool_target)
                if self.obj.display_type == 'WIRE':
                    self.obj.hide_set(True)
                return self.mirror.get_ui_items_list(), self.mirror.get_pie_menu()
        elif modifier == 'TAPER':
            try:
                return self.taper.get_ui_items_list(), self.taper.get_pie_menu()
            except:
                self.taper_action(action='ADD')
                if self.obj.display_type == 'WIRE':
                    self.obj.hide_set(True)
                return self.taper.get_ui_items_list(), self.taper.get_pie_menu()
        elif modifier == 'ARRAY':
            try:
                return self.array.get_ui_items_list(), self.array.get_pie_menu()
            except:
                self.array_action(action='ADD')
                if self.obj.display_type == 'WIRE':
                    self.obj.hide_set(True)
                return self.array.get_ui_items_list(), self.array.get_pie_menu()
        elif modifier == 'CIRCULAR_ARRAY':
            try:
                return self.circular_array.get_ui_items_list(), self.circular_array.get_pie_menu()
            except:
                self.circular_array_action(action='ADD')
                if not self.rotate:
                    self.rotation_action(action='ADD')
                if self.obj.display_type == 'WIRE':
                    self.obj.hide_set(True)
                return self.circular_array.get_ui_items_list(), self.circular_array.get_pie_menu()
        elif modifier == 'DIMENSIONS':
            try:
                return self.scale.get_ui_items_list(), self.scale.get_pie_menu()
            except:
                self.scale_action(action='ADD')
                if self.obj.display_type == 'WIRE':
                    self.obj.hide_set(True)
                return self.scale.get_ui_items_list(), self.scale.get_pie_menu()
        elif modifier == 'ROTATION':
            try:
                return self.rotate.get_ui_items_list(), self.rotate.get_pie_menu()
            except:
                self.rotation_action(action='ADD')
                if self.obj.display_type == 'WIRE':
                    self.obj.hide_set(True)
                return self.rotate.get_ui_items_list(), self.rotate.get_pie_menu()
        elif modifier == 'RADIUS':
            try:
                return self.radius.get_ui_items_list(), self.radius.get_pie_menu()
            except:
                self.radius_action(action='ADD')
                if self.obj.display_type == 'WIRE':
                    self.obj.hide_set(True)
                return self.radius.get_ui_items_list(), self.radius.get_pie_menu()
        elif modifier == 'RESOLUTION':
            try:
                return self.resolution.get_ui_items_list(), self.resolution.get_pie_menu()
            except:
                self.resolution_action(action='ADD')
                if self.obj.display_type == 'WIRE':
                    self.obj.hide_set(True)
                return self.resolution.get_ui_items_list(), self.resolution.get_pie_menu()
        elif modifier == 'INSET_THICKNESS':
            return self.inset_solidify.get_ui_items_list(), self.inset_solidify.get_pie_menu()
        elif modifier == 'PATH_HEIGHT':
            try:
                return self.path_height.get_ui_items_list(), self.path_height.get_pie_menu()
            except:
                self.path_height_action(action='ADD')
                if self.obj.display_type == 'WIRE':
                    self.obj.hide_set(True)
                return self.path_height.get_ui_items_list(), self.path_height.get_pie_menu()
        elif modifier == 'CURVE':
            try:
                return self.curve.get_ui_items_list(), self.curve.get_pie_menu()
            except:
                self.curve_action(action='ADD')
                if self.obj.display_type == 'WIRE':
                    self.obj.hide_set(True)
                return self.curve.get_ui_items_list(), self.curve.get_pie_menu()
        elif modifier == 'OUTER_BEVEL':
            try:
                return self.outer_bevel.get_ui_items_list(), self.outer_bevel.get_pie_menu()
            except:
                self.outer_bevel_preparation()
                self.outer_bevel.get_ui_items_list(), self.outer_bevel.get_pie_menu()
                print('--- erreur de chargement du bevel')

    def prepare_edition(self, inset_obj):
        check_draw_type = False
        if self.draw_type == 'unknow':
            self.mirror = self.mirror_action(action='INIT')
            self.array = self.array_action(action='INIT')
            if self.mirror and self.array:
                return True
        if self.draw_type in {'box', 'poly', 'path'}:
            self.first_solidify = self.first_solidify_action(action='INIT')
            self.first_bevel = self.first_bevel_action(action='INIT')
            self.second_bevel = self.second_bevel_action(action='INIT')
            self.mirror = self.mirror_action(action='INIT')
            self.array = self.array_action(action='INIT')
            self.taper = self.taper_action(action='INIT')
            if self.draw_type in {'path'}:
                self.path_height = self.path_height_action(action='INIT')
            else:
                self.second_solidify = self.second_solidify_action(action='INIT')
                self.taper = self.taper_action(action='INIT')
            self.circular_array = self.circular_array_action(action='INIT')
            if self.draw_type in {'poly'}:
                self.curve = self.curve_action(action='INIT')
                if self.first_solidify and self.taper and self.second_bevel and self.mirror and self.array and self.second_solidify and self.circular_array and self.curve:
                    check_draw_type = True
            elif self.draw_type in {'box'}:
                if self.first_solidify and self.first_bevel and self.taper and self.second_bevel and self.mirror and self.array and self.second_solidify and self.circular_array:
                    check_draw_type = True
            elif self.draw_type in {'path'}:
                if self.first_solidify and self.second_bevel and self.mirror and self.array and self.path_height and self.circular_array:
                    check_draw_type = True
        elif self.draw_type in {'prism', 'revolver'}:
            self.taper = self.taper_action(action='INIT')
            self.second_bevel = self.second_bevel_action(action='INIT')
            self.mirror = self.mirror_action(action='INIT')
            self.array = self.array_action(action='INIT')
            self.second_solidify = self.second_solidify_action(action='INIT')
            self.circular_array = self.circular_array_action(action='INIT')
            self.resolution = self.resolution_action(action='INIT')
            if self.draw_type == 'prism':
                self.first_solidify = self.first_solidify_action(action='INIT')
                self.radius = self.radius_action(action='INIT')
                if self.first_solidify and self.taper and self.second_bevel and self.mirror and self.array and self.second_solidify and self.circular_array and self.radius and self.resolution:
                    check_draw_type = True
            elif self.draw_type == 'revolver':
                self.first_bevel = self.first_bevel_action(action='INIT')
                if self.first_bevel and self.taper and self.second_bevel and self.mirror and self.array and self.second_solidify and self.circular_array and self.resolution:
                    check_draw_type = True
        elif self.draw_type == 'sphere':
            self.radius = self.radius_action(action='INIT')
            self.resolution = self.resolution_action(action='INIT')
            self.first_solidify = self.first_solidify_action(action='INIT')
            self.taper = self.taper_action(action='INIT')
            self.mirror = self.mirror_action(action='INIT')
            self.array = self.array_action(action='INIT')
            self.circular_array = self.circular_array_action(action='INIT')
            if self.radius and self.resolution and self.first_solidify and self.taper and self.mirror and self.array and self.circular_array:
                check_draw_type = True
        elif self.draw_type == 'plate':
            self.first_solidify = self.first_solidify_action(action='INIT')
            self.mirror = self.mirror_action(action='INIT')
            if self.first_solidify and self.mirror:
                check_draw_type = True
        if inset_obj:
            self.inset_solidify = self.inset_action(action='INIT', inset_obj=inset_obj)
        if not inset_obj and check_draw_type:
            return True
        elif inset_obj and self.inset_solidify and check_draw_type:
            return True
        else:
            return False

    def prepare_adjustment(self, ajust_me, keys):
        self.adjust_what = ajust_me
        self.x_mouse_slider_origin = keys['mouse_x']

    def adjust(self, keys, action=None):
        callback = []
        screen_text = []
        if self.adjust_what:
            if self.adjust_what == 'FIRST_SOLIDIFY':
                callback, screen_text = self.first_solidify.adjust_solidify(keys)
                try:
                    if not self.obj.get('inib_auto_bool_switching'):
                        if 'BOOL_DIFFERENCE' in callback and self.obj.get('fluent_operation') == 'CUT':
                            self.bool_operation = change_bool_operation(self.obj, self.bool_target, 'DIFFERENCE')
                        if 'BOOL_UNION' in callback and self.obj.get('fluent_operation') == 'CUT':
                            self.bool_operation = change_bool_operation(self.obj, self.bool_target, 'UNION')
                except:pass
            elif self.adjust_what == 'FIRST_BEVEL':
                callback, screen_text = self.first_bevel.adjust_bevel(keys)
            elif self.adjust_what == 'SECOND_BEVEL':
                callback, screen_text = self.second_bevel.adjust_bevel(keys)
            elif self.adjust_what == 'SECOND_SOLIDIFY':
                callback, screen_text = self.second_solidify.adjust_solidify(keys)
            elif self.adjust_what == 'MIRROR':
                callback, screen_text = self.mirror.adjust_mirror(keys, action)
            elif self.adjust_what == 'TAPER':
                callback, screen_text = self.taper.adjust_tape(keys)
            elif self.adjust_what == 'ARRAY':
                callback, screen_text = self.array.adjust_array(keys)
            elif self.adjust_what == 'CIRCULAR_ARRAY':
                callback, screen_text = self.circular_array.adjust(keys)
            elif self.adjust_what == 'DIMENSIONS':
                callback, screen_text = self.scale.adjust_modifier(keys)
            elif self.adjust_what == 'ROTATION':
                callback, screen_text = self.rotate.adjust_modifier(keys)
            elif self.adjust_what == 'RADIUS':
                callback, screen_text = self.radius.adjust_modifier(keys)
            elif self.adjust_what == 'RESOLUTION':
                callback, screen_text = self.resolution.adjust_modifier(keys)
            elif self.adjust_what == 'INSET_THICKNESS':
                callback, screen_text = self.inset_solidify.adjust(keys)
                try:
                    if 'INSET_ADD' in callback:
                        self.bool_operation = change_bool_operation(self.obj, self.bool_target, 'INSET_ADD')
                    if 'INSET_DIFF' in callback:
                        self.bool_operation = change_bool_operation(self.obj, self.bool_target, 'INSET_DIFF')
                except:
                    pass
            elif self.adjust_what == 'PATH_HEIGHT':
                callback, screen_text = self.path_height.adjust(keys)
                try:
                    if 'BOOL_DIFFERENCE' in callback and self.obj.get('fluent_operation') == 'CUT':
                        self.bool_operation = change_bool_operation(self.obj, self.bool_target, 'DIFFERENCE')
                        self.obj.modifiers[fluent_modifiers_name['path_displace']].strength = 0.01
                    if 'BOOL_UNION' in callback and self.obj.get('fluent_operation') == 'CUT':
                        self.bool_operation = change_bool_operation(self.obj, self.bool_target, 'UNION')
                        self.obj.modifiers[fluent_modifiers_name['path_displace']].strength = -0.01
                except:pass
            elif self.adjust_what == 'PATH_THICKNESS':
                callback, screen_text = self.first_solidify.adjust_solidify(keys)
            elif self.adjust_what == 'CURVE':
                callback, screen_text = self.curve.adjust(keys)
            elif self.adjust_what == 'OUTER_BEVEL':
                callback, screen_text = self.outer_bevel.adjust(keys)

        if 'STOP_ADJUSTMENT' in callback:
            self.adjust_what = None
        return callback, screen_text

    def stack_builder(self):
        print('STACK BUILDER')
        t = time_tracker(init=True)
        if self.draw_type in ['box', 'poly']:
            self.scale_action(action='ADD')
            self.rotation_action(action='ADD')
            if self.draw_type == 'poly':
                self.curve_action(action='ADD')
            self.first_bevel_action(action='ADD')
            self.first_solidify_action(action='ADD')
            self.taper_action(action='ADD')
            self.second_bevel_action(action='ADD')
            self.second_solidify_action(action='ADD')
            self.array_action(action='ADD')
            self.circular_array_action(action='ADD')
            self.mirror_action(action='ADD', ref=self.bool_target)
            t = time_tracker(t, 'J')
            print('STACK BUILDER fin')
        elif self.draw_type == 'path':
            self.scale_action(action='ADD')
            self.rotation_action(action='ADD')
            self.first_bevel_action(action='ADD')
            self.path_height_action(action='ADD')
            modif = self.obj.modifiers.new(name='Decimate', type='DECIMATE')
            modif.decimate_type = 'DISSOLVE'
            self.first_solidify_action(action='ADD')
            self.taper_action(action='ADD')
            self.second_bevel_action(action='ADD')
            self.second_solidify_action(action='ADD')
            self.array_action(action='ADD')
            self.circular_array_action(action='ADD')
            self.mirror_action(action='ADD', ref=self.bool_target)
        elif self.draw_type == 'prism':
            self.radius_action(action='ADD')
            self.resolution_action(action='ADD')
            self.scale_action(action='ADD')
            self.rotation_action(action='ADD')
            self.first_solidify_action(action='ADD')
            self.taper_action(action='ADD')
            self.second_bevel_action(action='ADD')
            self.second_solidify_action(action='ADD')
            self.array_action(action='ADD')
            self.circular_array_action(action='ADD')
            self.mirror_action(action='ADD', ref=self.bool_target)
        elif self.draw_type == 'revolver':
            # self.scale_action(action='ADD')
            # self.rotation_action(action='ADD')
            # self.first_bevel_action(action='ADD')
            self.resolution_action(action='ADD')
            modif = self.obj.modifiers.new(name=fluent_modifiers_name['decimate'], type='DECIMATE')
            modif.decimate_type = 'DISSOLVE'
            modif.angle_limit = math.radians(0.1)
            # self.taper_action(action='ADD')
            # self.second_bevel_action(action='ADD')
            # self.second_solidify_action(action='ADD')
            # self.array_action(action='ADD')
            # self.circular_array_action(action='ADD')
            # self.mirror_action(action='ADD', ref=self.bool_target)
        elif self.draw_type == 'plate':
            self.first_solidify_action(action='ADD')
            self.mirror_action(action='ADD', ref=self.bool_target)

    def first_solidify_action(self, action=None, event=None, keys=None, value=None, tool_called=None):
        if action =='ADD':
            self.first_solidify = first_solidify_management(self.obj, bool_target = self.bool_target)
            self.first_solidify.add_solidify()
            return self.first_solidify.get_modifier()
        elif action == 'ADJUST':
            callback, screen_text = self.first_solidify.adjust_solidify(event, keys, tool_called)
            if 'BOOL_DIFFERENCE' in callback and self.bool_operation != 'DIFFERENCE':
                self.bool_operation = change_bool_operation(self.obj, self.bool_target, 'DIFFERENCE', self.bool_operation)
            if 'BOOL_UNION' in callback and self.bool_operation != 'UNION':
                self.bool_operation = change_bool_operation(self.obj, self.bool_target, 'UNION', self.bool_operation)
            return callback, screen_text
        elif action== 'INIT':
            self.first_solidify = first_solidify_management(self.obj, bool_target=self.bool_target)
            if self.first_solidify.initiation():
                return self.first_solidify
        elif action == 'GET_MODIFIER':
            return self.first_solidify.get_modifier()

    def first_bevel_action(self, action=None, event=None, keys=None):
        if action =='ADD':
            self.first_bevel = first_bevel_management(self.obj)
            self.first_bevel.add_bevel(draw_type = self.draw_type)
            return self.first_bevel.get_modifier()
        elif action == 'ADJUST':
            callback, screen_text = self.first_bevel.adjust_bevel(event, keys)
            return callback, screen_text
        elif action == 'GET_BEVEL_VERTEX_LIST':
            return self.first_bevel.get_vertex_list()
        elif action== 'INIT':
            self.first_bevel = first_bevel_management(self.obj)
            if self.first_bevel.initiation():
                return self.first_bevel

    def second_bevel_action(self, action=None, event=None, keys=None):
        if action =='ADD':
            self.second_bevel = second_bevel_management(self.obj)
            self.second_bevel.add_bevel()
            return self.second_bevel.get_modifier()
        elif action == 'ADJUST':
            callback, screen_text = self.second_bevel.adjust_bevel(event, keys)
            return callback, screen_text
        elif action == 'INIT':
            self.second_bevel = second_bevel_management(self.obj)
            if self.second_bevel.initiation():
                return self.second_bevel

    def mirror_action(self, action=None, ref=None, event=None, widget=None):
        if action =='ADD':
            self.mirror = mirror_management(self.obj)
            self.mirror.add_mirror(ref = ref)
        elif action == 'ADJUST':
            callback, screen_text = self.mirror.adjust_mirror(event)
            return callback, screen_text
        elif action == 'GET_REF':
            return self.mirror.get_modifier().mirror_object
        elif action == 'GET_MODIFIER':
            return self.mirror.get_modifier()
        elif action== 'INIT':
            self.mirror = mirror_management(self.obj)
            if self.mirror.initiation():
                return self.mirror
        elif action == 'SAVE':
            self.mirror.save()
        elif action == 'BACKUP':
            self.mirror.backup()

    def array_action(self, action=None, event=None, widget=None, keys=None, value=None):
        if action =='ADD':
            self.array = array_management(self.obj)
            self.array.add_array(x=True, y=True, z=True)
        elif action == 'ADJUST':
            callback, screen_text = self.array.adjust_array(event, keys)
            return callback, screen_text
        elif action == 'GET_MODIFIER_X':
            return self.array.get_modifier(axis='X')
        elif action == 'GET_MODIFIER_Y':
            return self.array.get_modifier(axis='Y')
        elif action == 'GET_MODIFIER_Z':
            return self.array.get_modifier(axis='Z')
        elif action == 'INIT':
            self.array = array_management(self.obj)
            if self.array.initiation():
                return self.array

    def second_solidify_action(self, action=None, event=None, keys=None):
        if action =='ADD':
            self.second_solidify = second_solidify_management(self.obj)
            self.second_solidify.add_solidify()
            return self.second_solidify.get_modifier()
        elif action == 'ADJUST':
            callback, screen_text = self.second_solidify.adjust_solidify(event, keys)
            return callback, screen_text
        elif action == 'INIT':
            self.second_solidify = second_solidify_management(self.obj)
            if self.second_solidify.initiation():
                return self.second_solidify

    def circular_array_action(self, action=None, event=None, keys=None):
        if action =='ADD':
            self.circular_array = circular_array_management(self.obj, self.bool_target)
            self.circular_array.add_circular_array()
            return self.circular_array.get_modifier()
        elif action == 'ADJUST':
            callback, screen_text = self.circular_array.adjust(event, keys, draw_type)
            return callback, screen_text
        elif action == 'INIT':
            self.circular_array = circular_array_management(self.obj)
            if self.circular_array.initiation():
                return self.circular_array

    def taper_action(self, action=None, event=None, keys=None, widget=None):
        if action =='ADD':
            self.taper = taper_management(self.obj)
            self.taper.add_taper()
            return self.taper.get_modifier()
        elif action == 'ADJUST':
            callback, screen_text = self.taper.adjust_tape(event, keys)
            return callback, screen_text
        elif action == 'INIT':
            self.taper = taper_management(self.obj)
            if self.taper.initiation():
                return self.taper

    def radius_action(self, action=None, event=None, keys=None):
        if action =='ADD':
            self.radius = radius_management(self.obj)
            self.radius.add_radius()
            return self.radius.get_modifier()
        elif action == 'ADJUST':
            callback, screen_text = self.radius.adjust_radius(event, keys)
            return callback, screen_text
        elif action == 'INIT':
            self.radius = radius_management(self.obj)
            if self.radius.initiation():
                return self.radius

    def resolution_action(self, action=None, event=None, keys=None):
        if action =='ADD':
            self.resolution = resolution_management(self.obj)
            self.resolution.add_resolution()
            return self.resolution.get_modifier()
        elif action == 'ADJUST':
            callback, screen_text = self.resolution.adjust_resolution(event, keys)
            return callback, screen_text
        elif action == 'FLIP':
            callback = self.resolution.flip()
            return callback
        elif action == 'INIT':
            self.resolution = resolution_management(self.obj)
            if self.resolution.initiation():
                return self.resolution

    def curve_action(self, action=None, event=None, keys=None):
        if action =='ADD':
            self.curve = curve_management(self.obj)
            self.curve.add_curve()
            return self.curve.get_modifier()
        elif action == 'ADJUST':
            callback, screen_text = self.curve.adjust_divisions(event, keys)
            return callback, screen_text
        elif action == 'INIT':
            self.curve = curve_management(self.obj)
            if self.curve.initiation():
                return self.curve

    def path_height_action(self, action=None, event=None, keys=None):
        if action =='ADD':
            self.path_height = path_height_management(self.obj)
            self.path_height.add_screw()
            return self.path_height.get_modifier()
        elif action == 'ADJUST':
            callback, screen_text = self.path_height.adjust_height(event, keys, tool_called)
            if 'BOOL_DIFFERENCE' in callback and self.bool_operation != 'DIFFERENCE':
                try:
                    switch_bool_operation(bool_operation='DIFFERENCE', bool_target=self.bool_target, bool_obj=self.obj)
                    self.bool_operation = 'DIFFERENCE'
                except:pass
                self.obj.modifiers[fluent_modifiers_name['path_displace']].strength = 0.01
            if 'BOOL_UNION' in callback and self.bool_operation != 'UNION':
                try:
                    switch_bool_operation(bool_operation='UNION', bool_target=self.bool_target, bool_obj=self.obj)
                    self.bool_operation = 'UNION'
                except:pass
                self.obj.modifiers[fluent_modifiers_name['path_displace']].strength = -0.01
            return callback, screen_text
        elif action == 'INIT':
            self.path_height = path_height_management(self.obj)
            if self.path_height.initiation():
                return self.path_height

    def inset_action(self, action=None, event=None, keys=None, inset_obj=None):
        if action =='ADD':
            self.inset_solidify = inset_management(obj=self.obj, inset_obj=inset_obj)
            self.inset_solidify.add_inset()
            return self.inset_solidify.get_modifier()
        elif action == 'ADJUST':
            callback, screen_text = self.inset_solidify.adjust_thickness(event, keys)
            return callback, screen_text
        elif action == 'INIT':
            self.inset_solidify = inset_management(self.obj, inset_obj=inset_obj)
            if self.inset_solidify.initiation():
                return self.inset_solidify

    def scale_action(self, action=None, event=None):
        if action == 'ADD':
            self.scale = scale_management(self.obj)
            self.scale.add_modifier()

    def rotation_action(self, action=None, event=None):
        if action == 'ADD':
            self.rotate = rotation_management(self.obj)
            self.rotate.add_modifier()

    def outer_bevel_preparation(self, cut_objects=[]):
        # cut_objects est un tableau d'objets.
        # chaque objet contient l'objet coupé (cut_object) et le modifier booléen qui le coupe (boolean_modifier).
        bevels = []
        if not len(cut_objects) and self.obj and self.obj.get('fluent_type') != 'plate':
            cut_objects = find_boolean_targets(self.obj)
        if len(cut_objects):
            for i in cut_objects:
                bevel = F_outer_bevel(i['cut_object'])
                if bevel.find_next_to_bool(i['boolean_modifier']):
                    bevels.append(bevel)
            self.outer_bevel = outer_bevel_management(bevels)
        else:
            # cherche un bevel sur l'objet lui même
            bevel = F_outer_bevel(self.obj)
            if bevel.find_last():
                bevel.last_as_current()
                bevels.append(bevel)
                self.outer_bevel = outer_bevel_management(bevels)
            else:
                print('--- outer bevel', 'no bevel found')


class mirror_management():
    def __init__(self, obj):
        self.obj = obj
        self.mirror = None
        self.empty = None
        self.original_value = None
        self.original_ref_obj = None
        self.init = None

        # affichage
        self.ui_items_list = []
        self.pie_menu = None
        self.action = None
        self.dots = None

        self.pie_menu = FLUENT_Ui_Layout('MIRROR')
        self.pie_menu.set_layout('MIRROR')

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+X')
        button.set_default_color((.9, 0, 0, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('-X')
        button.set_default_color((.9, 0, 0, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+Y')
        button.set_default_color((0, .9, 0, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('-Y')
        button.set_default_color((0, .9, 0, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+Z')
        button.set_default_color((0, 0, .9, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('-Z')
        button.set_default_color((0, 0, .9, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def add_mirror(self, ref):
        self.initiation()
        if not self.mirror:
            obj = self.obj
            self.mirror = obj.modifiers.new(name=fluent_modifiers_name['mirror'], type='MIRROR')
            self.mirror.mirror_object = ref
            self.mirror.show_viewport = False
            self.mirror.show_render = False
            self.mirror.use_axis[0] = False
            self.mirror.use_axis[1] = False
            self.mirror.use_axis[2] = False
            self.mirror.use_bisect_axis[0] = True
            self.mirror.use_bisect_axis[1] = True
            self.mirror.use_bisect_axis[2] = True
            self.mirror.show_expanded = False

            if bpy.context.scene.fluentProp.auto_mirror_x :
                self.mirror.use_axis[0] = True
                self.mirror.show_viewport = True
                self.mirror.show_render = True
            if bpy.context.scene.fluentProp.auto_mirror_y :
                self.mirror.use_axis[1] = True
                self.mirror.show_viewport = True
                self.mirror.show_render = True
            if bpy.context.scene.fluentProp.auto_mirror_z :
                self.mirror.use_axis[2] = True
                self.mirror.show_viewport = True
                self.mirror.show_render = True

            place_in_stack(self.obj, self.mirror)

    def get_modifier(self):
        return self.mirror

    def initiation(self):
        for m in self.obj.modifiers:
            if m.name == fluent_modifiers_name['mirror'] and m.type == 'MIRROR':
                self.mirror = m
                break
        return self.mirror

    def save(self):
        self.original_value = get_modifier_values(self.mirror)

    def backup(self):
        set_modifier_value(self.mirror, self.original_value)

    def end_of_adjustment(self):
        self.original_value = None
        self.init = False

    def adjust_mirror(self, keys, action=None):
        callback = []
        screen_text = []

        if action:
            self.action = action

        if not self.init:
            self.save()
            self.original_ref_obj = self.mirror.mirror_object
            self.pie_menu.set_obj(self.obj)
            self.init = True

        if keys['value'] == 'PRESS' and keys['type'] == 'C':
            target = click_on(keys['mouse_x'], keys['mouse_y'])
            if target and not keys['shift_work']:
                if target != self.obj:
                    self.mirror.mirror_object = target
                    self.original_ref_obj = self.mirror.mirror_object
                else:
                    self.mirror.mirror_object = None
            if target and keys['shift_work']:
                if self.empty:
                    bpy.data.objects.remove(self.empty, do_unlink=True)
                copy = duplicate(target)
                bpy.ops.object.add(type='EMPTY')
                self.empty = bpy.context.active_object
                for c in bpy.data.collections:
                    for o in c.objects:
                        if o == self.empty:
                            c.objects.unlink(self.empty)
                try:
                    bpy.context.scene.collection.objects.unlink(self.empty)
                except:pass
                if not bpy.data.collections.get('F_Empty'):
                    coll = bpy.data.collections.new("F_Empty")
                    bpy.context.scene.collection.children.link(coll)
                bpy.data.collections['F_Empty'].objects.link(self.empty)
                self.empty.location = copy.location
                bpy.data.objects.remove(copy, do_unlink=True)
                self.mirror.mirror_object = self.empty
                self.empty.hide_viewport = True
                self.original_ref_obj = self.mirror.mirror_object

        try:
            bool_position = self.obj.matrix_world.to_translation()
            ref_position = self.original_ref_obj.matrix_world.to_translation()
            ref_rotation = self.original_ref_obj.matrix_world.to_quaternion()

            reset_obj_position = bool_position - ref_position
            reset_obj_position.rotate(ref_rotation.to_matrix().to_4x4().inverted())
            if 'X' in self.action:
                if self.mirror.use_axis[0] :
                    self.mirror.use_axis[0] = False
                else:
                    self.mirror.show_viewport = True
                    self.mirror.show_render = True
                    self.mirror.use_axis[0] = True

                    if '+' in self.action:
                        self.mirror.use_bisect_flip_axis[0] = True
                    else:
                        self.mirror.use_bisect_flip_axis[0] = False
            elif 'Y' in self.action:
                if self.mirror.use_axis[1] :
                    self.mirror.use_axis[1] = False
                else:
                    self.mirror.show_viewport = True
                    self.mirror.show_render = True
                    self.mirror.use_axis[1] = True

                    if '+' in self.action:
                        self.mirror.use_bisect_flip_axis[1] = True
                    else:
                        self.mirror.use_bisect_flip_axis[1] = False
            elif 'Z' in self.action:
                if self.mirror.use_axis[2] :
                    self.mirror.use_axis[2] = False
                else:
                    self.mirror.show_viewport = True
                    self.mirror.show_render = True
                    self.mirror.use_axis[2] = True

                    if '+' in self.action:
                        self.mirror.use_bisect_flip_axis[2] = True
                    else:
                        self.mirror.use_bisect_flip_axis[2] = False
        except:pass

        if not self.mirror.use_axis[0] and not self.mirror.use_axis[1] and not self.mirror.use_axis[2]:
            self.mirror.show_viewport = False
            self.mirror.show_render = False
        else:
            self.mirror.show_viewport = True
            self.mirror.show_render = True

        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            self.backup()
            self.end_of_adjustment()
            callback.append('DO_NOT_QUIT_FLUENT')
            callback.append('STOP_ADJUSTMENT')

        self.action = None
        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    self.end_of_adjustment()
                    callback.append('STOP_ADJUSTMENT')
        callback.append(self.action)

        screen_text.append(['Set object reference', 'C'])

        return callback, screen_text


class array_management():
    def __init__(self, obj):
        self.obj = obj
        self.obj_dim = {}
        self.array_axis = ''
        self.slider_origin = None
        self.previous_value = {
            'x':{'count':None, 'offset':None},
            'y':{'count':None, 'offset':None},
            'z':{'count':None, 'offset':None}
        }
        self.other_adjustment = None
        self.enter_value = 'None'
        self.original_value = {
            'x':{'count':None, 'offset':None},
            'y':{'count':None, 'offset':None},
            'z':{'count':None, 'offset':None},
            'xc':None,
            'yc':None,
            'zc':None
        }
        self.backup = {}
        self.array = {
            'x':None,
            'y':None,
            'z':None,
            'xc':None,
            'yc':None,
            'zc':None
        }
        self.init = False

        # affichage
        self.ui_items_list = []
        self.pie_menu = None
        self.action = None
        self.dots = None

        self.pie_menu = FLUENT_Ui_Layout('ARRAY')
        self.pie_menu.set_layout('TAPER')
        self.pie_menu.set_obj(self.obj)

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+X')
        button.set_default_color((.9, 0, 0, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+Y')
        button.set_default_color((0, .9, 0, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+Z')
        button.set_default_color((0, 0, .9, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def initiation(self):
        for m in self.obj.modifiers:
            if m.name == fluent_modifiers_name['array_x'] and m.type == 'ARRAY':
                self.array['x'] = m
            if m.name == fluent_modifiers_name['array_y'] and m.type == 'ARRAY':
                self.array['y'] = m
            if m.name == fluent_modifiers_name['array_z'] and m.type == 'ARRAY':
                self.array['z'] = m
            if m.name == fluent_modifiers_name['center_array_x'] and m.type == 'DISPLACE':
                self.array['xc'] = m
            if m.name == fluent_modifiers_name['center_array_y'] and m.type == 'DISPLACE':
                self.array['yc'] = m
            if m.name == fluent_modifiers_name['center_array_z'] and m.type == 'DISPLACE':
                self.array['zc'] = m
        return self.array

    def add_array(self, x=False, y=False, z=False):
        self.initiation()
        if not (self.array['x'] and self.array['y'] and self.array['z'] and self.array['xc'] and self.array['yc'] and self.array['zc']):
            obj = self.obj
            if x:
                self.array['x'] = obj.modifiers.new(name=fluent_modifiers_name['array_x'], type='ARRAY')
                self.array['x'].relative_offset_displace[0] = 0
                self.array['x'].relative_offset_displace[1] = 0
                self.array['x'].relative_offset_displace[2] = 0
                self.array['x'].count = 2
                self.array['x'].show_render = False
                self.array['x'].show_viewport = False
                self.array['x'].show_expanded = False
                self.array['x'].show_in_editmode = True
                place_in_stack(self.obj, self.array['x'])
            if y:
                self.array['y'] = obj.modifiers.new(name=fluent_modifiers_name['array_y'], type='ARRAY')
                self.array['y'].relative_offset_displace[0] = 0
                self.array['y'].relative_offset_displace[1] = 0
                self.array['y'].relative_offset_displace[2] = 0
                self.array['y'].count = 2
                self.array['y'].show_render = False
                self.array['y'].show_viewport = False
                self.array['y'].show_expanded = False
                self.array['y'].show_in_editmode = True
                place_in_stack(self.obj, self.array['y'])
            if z:
                self.array['z'] = obj.modifiers.new(name=fluent_modifiers_name['array_z'], type='ARRAY')
                self.array['z'].relative_offset_displace[0] = 0
                self.array['z'].relative_offset_displace[1] = 0
                self.array['z'].relative_offset_displace[2] = 0
                self.array['z'].count = 2
                self.array['z'].show_render = False
                self.array['z'].show_viewport = False
                self.array['z'].show_expanded = False
                self.array['z'].show_in_editmode = True
                place_in_stack(self.obj, self.array['z'])
            if x:
                self.array['xc'] = obj.modifiers.new(name=fluent_modifiers_name['center_array_x'], type='DISPLACE')
                self.array['xc'].direction = 'X'
                self.array['xc'].strength = 0
                self.array['xc'].show_render = False
                self.array['xc'].show_viewport = False
                self.array['xc'].show_expanded = False
                self.array['xc'].show_in_editmode = True
                place_in_stack(self.obj, self.array['xc'])
            if y:
                self.array['yc'] = obj.modifiers.new(name=fluent_modifiers_name['center_array_y'], type='DISPLACE')
                self.array['yc'].direction = 'Y'
                self.array['yc'].strength = 0
                self.array['yc'].show_render = False
                self.array['yc'].show_viewport = False
                self.array['yc'].show_expanded = False
                self.array['yc'].show_in_editmode = True
                place_in_stack(self.obj, self.array['yc'])
            if z:
                self.array['zc'] = obj.modifiers.new(name=fluent_modifiers_name['center_array_z'], type='DISPLACE')
                self.array['zc'].direction = 'Z'
                self.array['zc'].strength = 0
                self.array['zc'].show_render = False
                self.array['zc'].show_viewport = False
                self.array['zc'].show_expanded = False
                self.array['zc'].show_in_editmode = True
                place_in_stack(self.obj, self.array['zc'])

    def get_modifier(self, axis):
        if axis == 'X':
            return self.array['x']
        elif axis == 'Y':
            return self.array['y']
        elif axis == 'Z':
            return self.array['z']

    def set_slider_origin(self, value):
        self.x_mouse_slider_origin = value

    def set_previous_value(self):
        self.previous_value['x']['count'] = self.array['x'].count
        self.previous_value['x']['offset'] = self.array['x'].relative_offset_displace[0]
        self.previous_value['y']['count'] = self.array['y'].count
        self.previous_value['y']['offset'] = self.array['y'].relative_offset_displace[1]
        self.previous_value['z']['count'] = self.array['z'].count
        self.previous_value['z']['offset'] = self.array['z'].relative_offset_displace[2]

    def end_of_adjustment(self):
        self.obj_dim = {}
        self.array_axis = ''
        self.slider_origin = None
        self.previous_value = {
            'x':{'count':None, 'offset':None},
            'y':{'count':None, 'offset':None},
            'z':{'count':None, 'offset':None}
        }
        self.other_adjustment = None
        self.enter_value = 'None'
        self.original_value = {
            'x':{'count':None, 'offset':None},
            'y':{'count':None, 'offset':None},
            'z':{'count':None, 'offset':None},
            'xc':None,
            'yc':None,
            'zc':None
        }
        self.init = False

    def save_values(self):
        self.original_value['x']['count'] = self.array['x'].count
        self.original_value['x']['offset'] = self.array['x'].relative_offset_displace[0]
        self.original_value['y']['count'] = self.array['y'].count
        self.original_value['y']['offset'] = self.array['y'].relative_offset_displace[1]
        self.original_value['z']['count'] = self.array['z'].count
        self.original_value['z']['offset'] = self.array['z'].relative_offset_displace[2]

    def make_backup(self):
        self.backup['x'] = get_modifier_values(self.array['x'])
        self.backup['y'] = get_modifier_values(self.array['y'])
        self.backup['z'] = get_modifier_values(self.array['z'])
        self.backup['xc'] = get_modifier_values(self.array['xc'])
        self.backup['yc'] = get_modifier_values(self.array['yc'])
        self.backup['zc'] = get_modifier_values(self.array['zc'])

    def restore_backup(self):
        set_modifier_value(self.array['x'], self.backup['x'])
        set_modifier_value(self.array['y'], self.backup['y'])
        set_modifier_value(self.array['z'], self.backup['z'])
        set_modifier_value(self.array['xc'], self.backup['xc'])
        set_modifier_value(self.array['yc'], self.backup['yc'])
        set_modifier_value(self.array['zc'], self.backup['zc'])

    def restore_value(self):
        self.array['x'].count = self.original_value['x']['count']
        self.array['x'].relative_offset_displace[0] = self.original_value['x']['offset']
        self.array['y'].count = self.original_value['y']['count']
        self.array['y'].relative_offset_displace[1] = self.original_value['y']['offset']
        self.array['z'].count = self.original_value['z']['count']
        self.array['z'].relative_offset_displace[2] = self.original_value['z']['offset']

        if self.array['x'].relative_offset_displace[0]:
            self.array['x'].show_viewport = self.array['xc'].show_render = True
        else:
            self.array['x'].show_viewport = self.array['xc'].show_render = False
        self.array['xc'].strength = (self.array['x'].count - 1)*self.array['x'].relative_offset_displace[0]*self.obj_dim['x']*(-1)

        if self.array['y'].relative_offset_displace[1]:
            self.array['y'].show_viewport = self.array['yc'].show_render = True
        else:
            self.array['y'].show_viewport = self.array['yc'].show_render = False
        self.array['yc'].strength = (self.array['y'].count - 1)*self.array['y'].relative_offset_displace[1]*self.obj_dim['y']*(-1)

        if self.array['z'].relative_offset_displace[2]:
            self.array['z'].show_viewport = self.array['zc'].show_render = True
        else:
            self.array['z'].show_viewport = self.array['zc'].show_render = False
        self.array['zc'].strength = (self.array['z'].count - 1)*self.array['z'].relative_offset_displace[2]*self.obj_dim['z']*(-1)

    def adjust_array(self, keys):
        self.enter_value = enter_value(self.enter_value, keys)
        callback = []

        if not self.init:
            self.slider_origin = keys['mouse_x']
            self.set_previous_value()
            self.save_values()
            self.make_backup()
            has_mirror = False
            has_array_x = False
            has_array_y = False
            has_array_z = False
            try:
                if self.obj.modifiers[fluent_modifiers_name['mirror']].show_viewport:
                    self.obj.modifiers[fluent_modifiers_name['mirror']].show_viewport = False
                    has_mirror = True
            except:pass
            if self.array['x'].show_viewport:
                self.array['x'].show_viewport = False
                has_array_x = True
            if self.array['y'].show_viewport:
                self.array['y'].show_viewport = False
                has_array_y = True
            if self.array['z'].show_viewport:
                self.array['z'].show_viewport = False
                has_array_z = True
            depsgraph = bpy.context.evaluated_depsgraph_get()
            depsgraph.id_type_updated('OBJECT')
            self.obj_dim['x'] = self.obj.dimensions[0]
            self.obj_dim['y'] = self.obj.dimensions[1]
            self.obj_dim['z'] = self.obj.dimensions[2]
            if has_array_x:
                self.array['x'].show_viewport = True
            if has_array_y:
                self.array['y'].show_viewport = True
            if has_array_z:
                self.array['z'].show_viewport = True
            if has_mirror:
                self.obj.modifiers[fluent_modifiers_name['mirror']].show_viewport = True
            self.init = True

        if self.array_axis and keys['value'] == 'PRESS' and keys['type'] == 'LEFTMOUSE':
            self.array_axis = ''

        if type(self.action) == str and 'X' in self.action:
            self.slider_origin = keys['mouse_x']
            self.previous_value['x']['offset'] = self.array['x'].relative_offset_displace[0]
            self.save_values()
            self.other_adjustment = 'OFFSET'
            self.array_axis = 'X'
            self.array['x'].show_viewport = True
            self.array['x'].show_render = True

        if type(self.action) == str and 'Y' in self.action:
            self.slider_origin = keys['mouse_x']
            self.previous_value['y']['offset'] = self.array['y'].relative_offset_displace[1]
            self.save_values()
            self.other_adjustment = 'OFFSET'
            self.array_axis = 'Y'
            self.array['y'].show_viewport = True
            self.array['y'].show_render = True

        if type(self.action) == str and 'Z' in self.action:
            self.slider_origin = keys['mouse_x']
            self.previous_value['z']['offset'] = self.array['z'].relative_offset_displace[2]
            self.save_values()
            self.other_adjustment = 'OFFSET'
            self.array_axis = 'Z'
            self.array['z'].show_viewport = True
            self.array['z'].show_render = True

        if keys['value'] == 'PRESS' and keys['type'] == 'C':
            if self.other_adjustment == 'COUNT':
                self.other_adjustment = 'OFFSET'
                self.slider_origin = keys['mouse_x']
                if self.array_axis == 'X':
                    self.previous_value['x']['offset'] = self.array['x'].relative_offset_displace[0]
                if self.array_axis == 'Y':
                    self.previous_value['y']['offset'] = self.array['y'].relative_offset_displace[1]
                if self.array_axis == 'Z':
                    self.previous_value['z']['offset'] = self.array['z'].relative_offset_displace[2]
            else:
                self.other_adjustment = 'COUNT'
                self.slider_origin = keys['mouse_x']
                if self.array_axis == 'X':
                    self.previous_value['x']['count'] = self.array['x'].count
                if self.array_axis == 'Y':
                    self.previous_value['y']['count'] = self.array['y'].count
                if self.array_axis == 'Z':
                    self.previous_value['z']['count'] = self.array['z'].count

        if keys['value'] == 'PRESS' and keys['type'] == 'V':
            bpy.context.scene.fluentProp.centered_array = not bpy.context.scene.fluentProp.centered_array
            if bpy.context.scene.fluentProp.centered_array:
                self.array['xc'].show_render = self.array['xc'].show_viewport = True
                self.array['yc'].show_render = self.array['yc'].show_viewport = True
                self.array['zc'].show_render = self.array['zc'].show_viewport = True
            else:
                self.array['xc'].show_render = self.array['xc'].show_viewport = False
                self.array['yc'].show_render = self.array['yc'].show_viewport = False
                self.array['zc'].show_render = self.array['zc'].show_viewport = False

        if keys['value'] == 'PRESS' and keys['type'] in {'DEL', 'BACK_SPACE'}:
            if self.array_axis == 'Z':
                self.array['z'].show_viewport = False
                self.array['z'].show_render = False
                self.array['z'].count = 2
                self.array['z'].relative_offset_displace[2] = 0
                try:
                    self.array['zc'].show_viewport = self.array['zc'].show_render = False
                except:pass
                self.array_axis = ''
            elif  self.array_axis == 'Y':
                self.array_axis = ''
                self.array['y'].show_viewport = False
                self.array['y'].show_render = False
                self.array['y'].count = 2
                self.array['y'].relative_offset_displace[1] = 0
                try:
                    self.array['yc'].show_viewport = self.array['yc'].show_render = False
                except:pass
            elif  self.array_axis == 'X':
                self.array_axis = ''
                self.array['x'].show_viewport = False
                self.array['x'].show_render = False
                self.array['x'].count = 2
                self.array['x'].relative_offset_displace[0] = 0
                try:
                    self.array['xc'].show_viewport = self.array['xc'].show_render = False
                except:pass

        if keys['shift_work']:
            increment = 1000
        elif keys['ctrl_work']:
            increment = 10
        else:
            increment = 100

        if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
            self.slider_origin = keys['mouse_x']
            self.set_previous_value()

        if self.array_axis != '':
            try:
                if self.array_axis == 'X':
                    if self.other_adjustment == 'OFFSET':
                        if keys['type'] == 'MOUSEMOVE':
                            self.array['x'].relative_offset_displace[0] = self.previous_value['x']['offset'] - ((keys['mouse_x'] - self.slider_origin)/increment)
                        if enter_value_validation(self.enter_value, keys)[0]:
                            self.array['x'].relative_offset_displace[0] = self.previous_value['x']['offset'] = enter_value_validation(self.enter_value, keys)[1]
                            self.enter_value = 'None'
                            self.array_axis = ''
                    else:
                        if enter_value_validation(self.enter_value, keys)[0]:
                            self.array['x'].count = self.previous_value['x']['count'] = int(enter_value_validation(self.enter_value, keys)[1])
                            self.enter_value = 'None'
                            self.array_axis = ''
                        if keys['type'] == 'MOUSEMOVE':
                            self.array['x'].count = int(self.previous_value['x']['count'] + (keys['mouse_x'] - self.slider_origin)/30)

                    if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
                        try:
                            self.restore_value()
                            callback.append('DO_NOT_QUIT_FLUENT')
                            self.end_of_adjustment()
                        except:pass

                    if bpy.context.scene.fluentProp.centered_array:
                        if self.array['x'].relative_offset_displace[0]:
                            self.array['xc'].show_viewport = self.array['xc'].show_render = True
                        else:
                            self.array['xc'].show_viewport = self.array['xc'].show_render = False
                        self.array['xc'].strength = (self.array['x'].count - 1)*self.array['x'].relative_offset_displace[0]*self.obj_dim['x']*(-1)

                if self.array_axis == 'Y':
                    if self.other_adjustment == 'OFFSET':
                        if enter_value_validation(self.enter_value, keys)[0]:
                            self.array['y'].relative_offset_displace[1] = self.previous_value['y']['offset'] = enter_value_validation(self.enter_value, keys)[1]
                            self.enter_value = 'None'
                            self.array_axis = ''
                        if keys['type'] == 'MOUSEMOVE':
                            self.array['y'].relative_offset_displace[1] = self.previous_value['y']['offset'] - ((keys['mouse_x'] - self.slider_origin)/increment)
                    else:
                        self.array['y'].count = int(self.previous_value['y']['count'] + (keys['mouse_x'] - self.slider_origin)/40)
                        if enter_value_validation(self.enter_value, keys)[0]:
                            self.array['y'].count = self.previous_value['y']['count'] = int(enter_value_validation(self.enter_value, keys)[1])
                            self.enter_value = 'None'
                            self.array_axis = ''

                    if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
                        try:
                            self.restore_value()
                            callback.append('DO_NOT_QUIT_FLUENT')
                            self.end_of_adjustment()
                        except:pass

                    if bpy.context.scene.fluentProp.centered_array:
                        if self.array['y'].relative_offset_displace[1]:
                            self.array['yc'].show_viewport = self.array['yc'].show_render = True
                        else:
                            self.array['yc'].show_viewport = self.array['yc'].show_render = False
                        self.array['yc'].strength = (self.array['y'].count - 1)*self.array['y'].relative_offset_displace[1]*self.obj_dim['y']*(-1)

                if self.array_axis == 'Z':
                    if self.other_adjustment == 'OFFSET':
                        if keys['type'] == 'MOUSEMOVE':
                            print('---')
                            print("self.array['z']", self.array['z'].name)
                            self.array['z'].relative_offset_displace[2] = self.previous_value['z']['offset'] - ((keys['mouse_x'] - self.slider_origin)/increment)
                        if enter_value_validation(self.enter_value, keys)[0]:
                            self.array['z'].relative_offset_displace[2] = self.previous_value['z']['offset'] = enter_value_validation(self.enter_value, keys)[1]
                            self.enter_value = 'None'
                            self.array_axis = ''
                    else:
                        if enter_value_validation(self.enter_value, keys)[0]:
                            self.array['z'].count = self.previous_value['z']['count'] = int(enter_value_validation(self.enter_value, keys)[1])
                            self.enter_value = 'None'
                            self.array_axis = ''
                        if keys['type'] == 'MOUSEMOVE':
                            self.array['z'].count = int(self.previous_value['z']['count'] + (keys['mouse_x'] - self.slider_origin)/30)

                    if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
                        try:
                            self.restore_value()
                            callback.append('DO_NOT_QUIT_FLUENT')
                            self.end_of_adjustment()
                        except:pass

                    if bpy.context.scene.fluentProp.centered_array:
                        if self.array['z'].relative_offset_displace[2]:
                            self.array['zc'].show_viewport = self.array['zc'].show_render = True
                        else:
                            self.array['zc'].show_viewport = self.array['zc'].show_render = False
                        self.array['zc'].strength = (self.array['z'].count - 1)*self.array['z'].relative_offset_displace[2]*self.obj_dim['z']*(-1)
            except:pass

        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            try:
                self.restore_backup()
            except:pass
            self.end_of_adjustment()
            callback.append('DO_NOT_QUIT_FLUENT')
            callback.append('STOP_ADJUSTMENT')

        # TEXT
        screen_text = []
        if self.array_axis == 'X':
            if self.other_adjustment == 'OFFSET':
                screen_text.append(['Offset', adjustment_value(self.array['x'].relative_offset_displace[0], self.enter_value) + ' / ' + modifier_value_converter(self.array['y'].relative_offset_displace[1]) + ' / ' + modifier_value_converter(self.array['z'].relative_offset_displace[2])])
                screen_text.append(['Count', modifier_value_converter(self.array['x'].count) + ' / ' + modifier_value_converter(self.array['y'].count) + ' / ' + modifier_value_converter(self.array['z'].count)])
            else:
                screen_text.append(['Offset', modifier_value_converter(self.array['x'].relative_offset_displace[0]) + ' / ' + modifier_value_converter(self.array['y'].relative_offset_displace[1]) + ' / ' + modifier_value_converter(self.array['z'].relative_offset_displace[2])])
                screen_text.append(['Count', adjustment_value(self.array['x'].count, self.enter_value) + ' / ' + modifier_value_converter(self.array['y'].count) + ' / ' + modifier_value_converter(self.array['z'].count)])
        elif self.array_axis == 'Y':
            if self.other_adjustment == 'OFFSET':
                screen_text.append(['Offset', modifier_value_converter(self.array['x'].relative_offset_displace[0]) + ' / ' + adjustment_value(self.array['y'].relative_offset_displace[1], self.enter_value) + ' / ' + modifier_value_converter(self.array['z'].relative_offset_displace[2])])
                screen_text.append(['Count',modifier_value_converter(self.array['x'].count) + ' / ' + modifier_value_converter(self.array['y'].count) + ' / ' + modifier_value_converter(self.array['z'].count)])
            else:
                screen_text.append(['Offset', modifier_value_converter(self.array['x'].relative_offset_displace[0]) + ' / ' + modifier_value_converter(self.array['y'].relative_offset_displace[1]) + ' / ' + modifier_value_converter(self.array['z'].relative_offset_displace[2])])
                screen_text.append(['Count', modifier_value_converter(self.array['x'].count) + ' / ' + adjustment_value(self.array['y'].count,self.enter_value) + ' / ' + modifier_value_converter(self.array['z'].count)])
        elif self.array_axis == 'Z':
            if self.other_adjustment == 'OFFSET':
                screen_text.append(['Offset', modifier_value_converter(self.array['x'].relative_offset_displace[0]) + ' / ' + modifier_value_converter(self.array['y'].relative_offset_displace[1]) + ' / ' + adjustment_value(self.array['z'].relative_offset_displace[2], self.enter_value)])
                screen_text.append(['Count',modifier_value_converter(self.array['x'].count) + ' / ' + modifier_value_converter(self.array['y'].count) + ' / ' + modifier_value_converter(self.array['z'].count)])
            else:
                screen_text.append(['Offset', modifier_value_converter(self.array['x'].relative_offset_displace[0]) + ' / ' + modifier_value_converter(self.array['y'].relative_offset_displace[1]) + ' / ' + modifier_value_converter(self.array['z'].relative_offset_displace[2])])
                screen_text.append(['Count', modifier_value_converter(self.array['x'].count) + ' / ' + modifier_value_converter(self.array['y'].count) + ' / ' + adjustment_value(self.array['z'].count,self.enter_value)])
        else:
            screen_text.append(['Offset', modifier_value_converter(self.array['x'].relative_offset_displace[0]) + ' / ' + modifier_value_converter(self.array['y'].relative_offset_displace[1]) + ' / ' + modifier_value_converter(self.array['z'].relative_offset_displace[2])])
            screen_text.append(['Count',modifier_value_converter(self.array['x'].count) + ' / ' + modifier_value_converter(self.array['y'].count) + ' / ' + modifier_value_converter(self.array['z'].count)])

        screen_text.append(['Validate axis', 'LEFT CLICK'])
        screen_text.append(['Toggle adjustment', 'C'])
        screen_text.append(['Centered array', 'V'])
        screen_text.append(['Slower/Faster', 'Shift/Ctrl'])

        self.action = None
        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    self.end_of_adjustment()
                    screen_text = []
                    callback.append('STOP_ADJUSTMENT')
                else:
                    self.slider_origin = keys['mouse_x']

        return callback, screen_text


class first_solidify_management():
    def __init__(self, obj, bool_target = None):
        self.obj = obj
        self.bool_target = bool_target
        self.draw_type = obj.get('fluent_type')
        self.solidify = None
        self.slider_origin = None
        self.previous_value = None
        self.other_adjustment = 'THICKNESS'
        self.enter_value = 'None'
        self.original_value = None
        self.init = False

        # menu
        self.ui_items_list = []
        self.pie_menu = None
        self.action = None
        self.pie_menu = FLUENT_Ui_Layout('FIRST_SOLIDIFY')
        self.pie_menu.set_layout('PIE')

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Offset (C)')
        button.set_shape('RECTANGLE')
        button.set_action('OFFSET')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Thickness (C)')
        button.set_shape('RECTANGLE')
        button.set_action('THICKNESS')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        if self.obj and self.obj.get('fluent_operation'):
            button = FLUENT_Ui_Button()
            button.set_text('Cross (V)')
            button.set_shape('RECTANGLE')
            button.set_action('CROSS')
            self.pie_menu.add_item(button)
            self.ui_items_list.append(button)

    def get_modifier(self):
        return self.solidify

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def initiation(self):
        for m in self.obj.modifiers:
            if m.name == fluent_modifiers_name['first_solidify'] and m.type == 'SOLIDIFY':
                self.solidify = m
                break
        return self.solidify

    def add_solidify(self):
        self.initiation()
        if not self.solidify:
            self.solidify = self.obj.modifiers.new(name=fluent_modifiers_name['first_solidify'], type='SOLIDIFY')
            self.solidify.show_in_editmode = True
            self.solidify.show_expanded = False
            self.solidify.use_even_offset = True
            if bpy.context.scene.fluentProp.depth:
                self.solidify.thickness = bpy.context.scene.fluentProp.depth
            else:
                self.solidify.thickness = 0
            if self.draw_type == 'sphere':
                self.solidify.thickness = 0
                self.solidify.offset = -1
                self.solidify.show_render = self.solidify.show_viewport = False
            elif self.draw_type in ['box', 'poly']:
                self.solidify.offset = -.95
            elif self.draw_type == 'prism':
                self.solidify.offset = -.95
            elif self.draw_type == 'path':
                self.solidify.solidify_mode = 'NON_MANIFOLD'
                self.solidify.nonmanifold_thickness_mode = 'EVEN'
                self.solidify.offset = 0
                self.solidify.thickness = .025
                self.solidify.use_even_offset = True
            place_in_stack(self.obj, self.solidify)
        return self.solidify

    def end_of_adjustment(self):
        self.slider_origin = None
        self.previous_value = None
        self.other_adjustment = 'THICKNESS'
        self.enter_value = 'None'
        self.original_value = None
        self.init = False
        if self.solidify.thickness == 0:
            self.solidify.show_render = False
            self.solidify.show_viewport = False

    def adjust_solidify(self, keys, tool_called = None, bool_operation = None):
        self.enter_value = enter_value(self.enter_value, keys)

        callback = []

        if not self.init:
            self.slider_origin = keys['mouse_x']
            self.previous_value = self.solidify.thickness
            self.original_value = get_modifier_values(self.solidify)
            self.solidify.show_render = self.solidify.show_viewport = True
            self.init = True

        # if keys['value'] == 'PRESS' and keys['type'] == 'C' or self.action in ['OFFSET', 'THICKNESS']:
        if self.draw_type in {'box', 'poly', 'prism', 'inset', 'sphere'}:
            if (self.other_adjustment == 'OFFSET' and keys['value'] == 'PRESS' and keys['type'] == 'C') or self.action == 'THICKNESS':
                self.other_adjustment = 'THICKNESS'
                self.previous_value = self.solidify.thickness
                self.slider_origin = keys['mouse_x']
            elif (self.other_adjustment == 'THICKNESS' and keys['value'] == 'PRESS' and keys['type'] == 'C') or self.action == 'OFFSET':
                self.other_adjustment = 'OFFSET'
                self.previous_value = self.solidify.offset
                self.slider_origin = keys['mouse_x']

        if keys['shift_work']:
            increment = 3000
        elif keys['ctrl_work']:
            increment = 30
        else:
            increment = 300

        if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
            self.slider_origin = keys['mouse_x']
            if self.other_adjustment == 'THICKNESS':
                self.previous_value = self.solidify.thickness
            elif self.other_adjustment == 'OFFSET':
                self.previous_value = self.solidify.offset

        if self.other_adjustment == 'THICKNESS':
            if keys['type'] == 'MOUSEMOVE' and not keys['mouse_left_click']:
                self.solidify.thickness = self.previous_value + ((keys['mouse_x'] - self.slider_origin)/increment)
            if enter_value_validation(self.enter_value, keys)[0]:
                self.solidify.thickness = enter_value_validation(self.enter_value, keys)[1]
                self.end_of_adjustment()
                callback.append('STOP_ADJUSTMENT')
        elif self.other_adjustment == 'OFFSET':
            if keys['type'] == 'MOUSEMOVE' and not keys['mouse_left_click']:
                self.solidify.offset = self.previous_value + ((keys['mouse_x'] - self.slider_origin)/increment)
            if enter_value_validation(self.enter_value, keys)[0]:
                self.solidify.offset = enter_value_validation(self.enter_value, keys)[1]
                self.end_of_adjustment()
                callback.append('STOP_ADJUSTMENT')

        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            try:
                set_modifier_value(self.solidify, self.original_value)
            except:pass
            self.end_of_adjustment()
            callback.append('DO_NOT_QUIT_FLUENT')
            callback.append('STOP_ADJUSTMENT')

        if self.solidify.thickness > 0 and self.draw_type != 'path':
            callback.append('BOOL_UNION')
        elif  self.solidify.thickness < 0 and self.draw_type != 'path':
            callback.append('BOOL_DIFFERENCE')

        if self.solidify.offset < -1 :
            self.solidify.offset = -1

        if self.solidify.offset > 1 :
            self.solidify.offset = 1

        # TEXT
        screen_text = []
        if self.other_adjustment == 'THICKNESS':
            screen_text.append(['Thickness', adjustment_value(self.solidify.thickness, self.enter_value)])
        else:
            screen_text.append(['Thickness', modifier_value_converter(self.solidify.thickness)])
        if self.draw_type != 'path':
            if self.other_adjustment == 'OFFSET':
                screen_text.append(['Offset', adjustment_value(self.solidify.offset, self.enter_value)])
            else:
                screen_text.append(['Offset', modifier_value_converter(self.solidify.offset)])
            if self.other_adjustment == 'THICKNESS':
                screen_text.append(['Offset', 'C'])
            elif self.other_adjustment == 'OFFSET':
                screen_text.append(['Thickness', 'C'])
        screen_text.append(['Slower/Faster', 'Shift/Ctrl'])

        self.action = None
        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    self.end_of_adjustment()
                    screen_text = []
                    callback.append('STOP_ADJUSTMENT')

        if ((keys['value'] == 'PRESS' and keys['type'] == 'V') or self.action == 'CROSS') and self.draw_type != 'sphere' and self.obj and self.obj.get('fluent_operation'):
            if self.draw_type in {'box', 'poly', 'prism'}:
                plus_grand_scalaire = cross_depth_research(self.obj, self.bool_target)
                self.solidify.thickness = plus_grand_scalaire * 1.01 * (2-math.fabs(self.solidify.offset)) * -1
                # self.solidify.thickness = plus_grand_scalaire * 1.01 * (2-math.fabs(self.solidify.offset))
                self.end_of_adjustment()
                callback.append('STOP_ADJUSTMENT')

        return callback, screen_text


class second_bevel_management():
    def __init__(self, obj):
        self.obj = obj
        self.bevel = None
        self.slider_origin = None
        self.previous_value = None
        self.other_adjustment = 'WIDTH'
        self.enter_value = 'None'
        self.original_value = None
        self.init = False
        self.prevent_auto_segments = False

        # affichage
        self.ui_items_list = []
        self.pie_menu = None
        self.action = None
        self.dots = None

        self.pie_menu = FLUENT_Ui_Layout('FIRST_BEVEL')
        self.pie_menu.set_layout('PIE')

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Width (V)')
        button.set_shape('RECTANGLE')
        button.set_action('WIDTH')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Segments (V)')
        button.set_shape('RECTANGLE')
        button.set_action('SEGMENTS')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Straight (C)')
        button.set_shape('RECTANGLE')
        button.set_action('STRAIGHT')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Concave (C)')
        button.set_shape('RECTANGLE')
        button.set_action('CONCAVE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Convex (C)')
        button.set_shape('RECTANGLE')
        button.set_action('CONVEX')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Angle limit')
        button.set_shape('RECTANGLE')
        button.set_action('ANGLE_LIMIT')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def get_modifier(self):
        return self.bevel

    def initiation(self):
        for m in self.obj.modifiers:
            if m.name == fluent_modifiers_name['second_bevel'] and m.type == 'BEVEL':
                self.bevel = m
                break
        return self.bevel

    def add_bevel(self):
        self.initiation()
        if not self.bevel:
            self.bevel = self.obj.modifiers.new(name=fluent_modifiers_name['second_bevel'], type='BEVEL')
            self.bevel.show_expanded = False
            self.bevel.limit_method = 'ANGLE'
            self.bevel.angle_limit = 0.523599
            self.bevel.width = bpy.context.scene.fluentProp.second_bevel_width
            if bpy.context.scene.fluentProp.second_bevel_straight:
                self.bevel.segments = 2
                self.bevel.profile = 0.25
            else:
                self.bevel.segments = auto_bevel_segments(bevel=self.bevel)
            self.bevel.use_clamp_overlap = get_addon_preferences().clamp_overlap
            self.bevel.miter_outer = 'MITER_ARC'
            if bpy.context.scene.fluentProp.second_bevel_width:
                self.bevel.show_viewport = True
                self.bevel.show_render = True
            else:
                self.bevel.show_viewport = False
                self.bevel.show_render = False
            place_in_stack(self.obj, self.bevel)

    def end_of_adjustment(self):
        self.slider_origin = None
        self.previous_value = None
        self.other_adjustment = 'WIDTH'
        self.enter_value = 'None'
        self.original_value = None
        if self.bevel.width == 0:
            self.bevel.show_viewport = False
            self.bevel.show_render = False
        self.init = False

    def adjust_bevel(self, keys):
        self.enter_value = enter_value(self.enter_value, keys)

        callback = []

        if not self.init:
            self.slider_origin = keys['mouse_x']
            self.previous_value = self.bevel.width
            self.original_value = get_modifier_values(self.bevel)
            self.init = True

        if keys['shift_work']:
            increment = 5000
        elif keys['ctrl_work']:
            increment = 50
        else:
            increment = 500

        if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
            self.slider_origin = keys['mouse_x']
            if self.other_adjustment == 'WIDTH':
                self.previous_value = self.bevel.width
            elif self.other_adjustment == 'ANGLE_LIMIT':
                self.previous_value = self.bevel.angle_limit
            elif self.other_adjustment == 'SEGMENTS':
                self.previous_value = self.bevel.segments

        if keys['value'] == 'PRESS' and keys['type'] == 'C':
            bevel_type = None
            if self.bevel.segments > 2 and round(self.bevel.profile, 2) != 0.08:
                bevel_type = 'convex'
            elif self.bevel.segments in {1, 2}:
                bevel_type = 'straight'
            elif self.bevel.segments != 1 and round(self.bevel.profile, 2) == 0.08:
                bevel_type = 'concave'
            if bevel_type == 'convex':
                self.action = 'STRAIGHT'
            elif bevel_type == 'straight':
                self.action = 'CONCAVE'
            elif bevel_type == 'concave':
                self.action = 'CONVEX'

        if keys['value'] == 'PRESS' and keys['type'] == 'B':
            self.action = 'STRAIGHT_1'

        if self.action == 'STRAIGHT_1':
            if self.bevel.segments == 2:
                self.bevel.segments = 1
                self.bevel.profile = 0.25
            elif self.bevel.segments == 1:
                self.bevel.segments = 2
                self.bevel.profile = 0.25
        elif self.action == 'STRAIGHT':
            self.bevel.segments = 2
            self.bevel.profile = 0.25
        elif self.action == 'CONCAVE':
            self.bevel.segments = auto_bevel_segments(self.bevel)
            self.bevel.profile = 0.08
        elif self.action == 'CONVEX':
            self.bevel.segments = auto_bevel_segments(self.bevel)
            self.bevel.profile = bpy.context.scene.fluentProp.bevel_profile
        elif self.action == 'ANGLE_LIMIT':
            self.other_adjustment = 'ANGLE_LIMIT'
            self.previous_value = self.bevel.angle_limit
            self.slider_origin = keys['mouse_x']
        elif self.action == 'SEGMENTS':
            self.other_adjustment = 'SEGMENTS'
            self.previous_value = self.bevel.segments
            self.slider_origin = keys['mouse_x']
        elif self.action == 'WIDTH':
            self.other_adjustment = 'WIDTH'
            self.previous_value = self.bevel.width
            self.slider_origin = keys['mouse_x']

        if keys['type'] == 'MOUSEMOVE':
            if self.other_adjustment == 'WIDTH' and not keys['mouse_left_click']:
                self.bevel.width = self.previous_value + ((keys['mouse_x'] - self.slider_origin)/increment)
            elif self.other_adjustment == 'ANGLE_LIMIT' and not keys['mouse_left_click']:
                self.bevel.angle_limit = self.previous_value + ((keys['mouse_x'] - self.slider_origin)/increment)
            elif self.other_adjustment == 'SEGMENTS' and not keys['mouse_left_click']:
                self.bevel.segments = int(self.previous_value + ((keys['mouse_x'] - self.slider_origin)/(increment/5)))
                self.prevent_auto_segments = True
        if enter_value_validation(self.enter_value, keys)[0]:
            if self.other_adjustment == 'WIDTH':
                self.bevel.width = enter_value_validation(self.enter_value, keys)[1]
            elif self.other_adjustment == 'ANGLE_LIMIT':
                self.bevel.angle_limit = math.radians(enter_value_validation(self.enter_value, keys)[1])
            if self.other_adjustment == 'SEGMENTS':
                self.bevel.segments = int(enter_value_validation(self.enter_value, keys)[1])
            callback.append('STOP_ADJUSTMENT')
            self.end_of_adjustment()

        if self.bevel.profile != 0.25:
            if not self.prevent_auto_segments:
                self.bevel.segments = auto_bevel_segments(bevel=self.bevel)

        if self.bevel.width == 0:
            self.bevel.show_viewport = False
            self.bevel.show_render = False
        else:
            self.bevel.show_viewport = True
            self.bevel.show_render = True

        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            try:
                set_modifier_value(self.bevel, self.original_value)
            except:pass
            self.end_of_adjustment()
            callback.append('DO_NOT_QUIT_FLUENT')
            callback.append('STOP_ADJUSTMENT')

        # TEXT
        screen_text = []
        if self.other_adjustment == 'WIDTH':
            screen_text.append(['Width', adjustment_value(self.bevel.width, self.enter_value)])
        else:
            screen_text.append(['Width', modifier_value_converter(self.bevel.width)])
        if self.other_adjustment == 'SEGMENTS':
            screen_text.append(['Segments', adjustment_value(self.bevel.segments, self.enter_value)])
        else:
            screen_text.append(['Segments', modifier_value_converter(self.bevel.segments)])
        if self.other_adjustment == 'ANGLE_LIMIT':
            screen_text.append(['Angle limit', adjustment_value(math.degrees(self.bevel.angle_limit), self.enter_value)])
        else:
            screen_text.append(['Angle limit', modifier_value_converter(math.degrees(self.bevel.angle_limit))])
        screen_text.append(['One segment', 'B'])
        screen_text.append(['Slower/Faster', 'Shift/Ctrl'])
        screen_text.append(['Remove', 'Del/Back space'])

        self.action = None
        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    screen_text = []
                    self.end_of_adjustment()
                    callback.append('STOP_ADJUSTMENT')
                else:
                    self.slider_origin = keys['mouse_x']
                    if self.other_adjustment == 'WIDTH':
                        self.previous_value = self.bevel.width
                    elif self.other_adjustment == 'ANGLE_LIMIT':
                        self.previous_value = self.bevel.angle_limit
                    elif self.other_adjustment == 'SEGMENTS':
                        self.previous_value = self.bevel.segments

        if keys['value'] == 'PRESS' and keys['type'] == 'V':
            if self.other_adjustment == 'WIDTH':
                self.action = 'SEGMENTS'
            elif self.other_adjustment == 'SEGMENTS':
                self.action = 'WIDTH'

        if keys['value'] == 'PRESS' and keys['type'] in {'DEL', 'BACK_SPACE'}:
            self.bevel.show_viewport = False
            self.bevel.show_render = False
            self.action = 'VALIDATE'
            self.end_of_adjustment()
            screen_text = []
            callback.append('STOP_ADJUSTMENT')

        return callback, screen_text


class second_solidify_management():
    def __init__(self, obj):
        self.obj = obj
        self.draw_type = None
        self.solidify = None
        self.slider_origin = None
        self.previous_value = None
        self.other_adjustment = None
        self.enter_value = 'None'
        self.original_value = None
        self.init = False

        # affichage
        self.ui_items_list = []
        self.pie_menu = None
        self.action = None
        self.dots = None

        self.pie_menu = FLUENT_Ui_Layout('SECOND_SOLIDIFY')
        self.pie_menu.set_layout('PIE')

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Fake slice')
        button.set_shape('RECTANGLE')
        button.set_action('FAKE_SLICE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def get_modifier(self):
        return self.solidify

    def initiation(self):
        for m in self.obj.modifiers:
            if m.name == fluent_modifiers_name['second_solidify'] and m.type == 'SOLIDIFY':
                self.solidify = m
                break
        return self.solidify

    def add_solidify(self):
        self.initiation()
        if not self.solidify:
            self.solidify = self.obj.modifiers.new(name=fluent_modifiers_name['second_solidify'], type='SOLIDIFY')
            self.solidify.offset = 0
            self.solidify.thickness = -0.01
            self.solidify.use_even_offset = True
            self.solidify.show_viewport = False
            self.solidify.show_render = False
            self.solidify.show_expanded = False
            place_in_stack(self.obj, self.solidify)

    def end_of_adjustment(self):
        self.slider_origin = None
        self.previous_value = None
        self.other_adjustment = None
        self.enter_value = 'None'
        self.original_value = None
        self.init = False

    def adjust_solidify(self, keys):
        self.enter_value = enter_value(self.enter_value, keys)

        callback = []

        if not self.init:
            self.slider_origin = keys['mouse_x']
            self.previous_value = self.solidify.thickness
            self.original_value = get_modifier_values(self.solidify)
            self.init = True

        if keys['shift_work']:
            increment = 10000
        elif keys['ctrl_work']:
            increment = 100
        else:
            increment = 1000
        if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
            self.slider_origin = keys['mouse_x']
            self.previous_value = self.solidify.thickness
        if keys['type'] == 'MOUSEMOVE' and not keys['mouse_left_click']:
            self.solidify.thickness = self.previous_value - ((keys['mouse_x'] - self.slider_origin)/increment)
        if enter_value_validation(self.enter_value, keys)[0]:
            self.solidify.thickness = enter_value_validation(self.enter_value, keys)[1]
            callback.append('STOP_ADJUSTMENT')
            self.end_of_adjustment()

        if self.solidify.thickness != 0:
            self.solidify.show_viewport = True
            self.solidify.show_render = True

        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            try:
                set_modifier_value(self.solidify, self.original_value)
            except:pass
            self.end_of_adjustment()
            callback.append('DO_NOT_QUIT_FLUENT')
            callback.append('STOP_ADJUSTMENT')

        # TEXT
        screen_text = []
        screen_text.append(['Thickness : ', adjustment_value(self.solidify.thickness, self.enter_value)])
        screen_text.append(['Remove', 'Del'])
        screen_text.append(['Slower/Faster', 'Shift/Ctrl'])

        self.action = None
        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    self.end_of_adjustment()
                    screen_text = []
                    callback.append('STOP_ADJUSTMENT')
                else:
                    self.slider_origin = keys['mouse_x']
                    self.previous_value = self.solidify.thickness

        if self.action == 'FAKE_SLICE':
            self.solidify.thickness = .0001
            callback.append('STOP_ADJUSTMENT')
            self.end_of_adjustment()

        if keys['value'] == 'PRESS' and keys['type'] in {'DEL', 'BACK_SPACE'}:
            self.solidify.show_viewport = False
            self.solidify.show_render = False
            self.action = 'VALIDATE'
            self.end_of_adjustment()
            screen_text = []
            callback.append('STOP_ADJUSTMENT')

        return callback, screen_text


class first_bevel_management():
    def __init__(self, obj):
        self.obj = obj
        self.bevels = []
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = []
        self.bevel_vertex_list = [] #rempli avec des tableaux : [vertex index, n° du vertex group]
        self.init = False
        self.prevent_auto_segments = False
        self.other_adjustment = 'WIDTH'

        # affichage
        self.ui_items_list = []
        self.pie_menu = None
        self.action = None
        self.dots = None

        self.pie_menu = FLUENT_Ui_Layout('FIRST_BEVEL')
        self.pie_menu.set_layout('PIE')

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Width (V)')
        button.set_shape('RECTANGLE')
        button.set_action('WIDTH')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Segments (V)')
        button.set_shape('RECTANGLE')
        button.set_action('SEGMENT')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Straight (C)')
        button.set_shape('RECTANGLE')
        button.set_action('STRAIGHT')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Concave (C)')
        button.set_shape('RECTANGLE')
        button.set_action('CONCAVE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Convex (C)')
        button.set_shape('RECTANGLE')
        button.set_action('CONVEX')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        self.dots = FLUENT_Draw_Dots()
        self.ui_items_list.append(self.dots)

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def get_modifier(self):
        return self.bevels

    def initiation(self):
        for m in self.obj.modifiers:
            if fluent_modifiers_name['first_bevel'] in m.name and m.type == 'BEVEL':
                self.bevels.append(m)
        return self.bevels

    def get_vertex_list(self):
        return self.bevel_vertex_list

    def end_of_adjustment(self):
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = []
        self.bevel_vertex_list = []
        self.init = False
        self.other_adjustment = 'WIDTH'

    def add_bevel(self, draw_type):
        self.initiation()
        if len(self.bevels) == 0:
            # supprime les vertex goup si déjà présent
            for vg in self.obj.vertex_groups:
                self.obj.vertex_groups.remove(vg)
            active_object('SET', self.obj, True)
            bm = bmesh.new()
            bm.from_mesh(self.obj.data)
            bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(5), use_dissolve_boundaries=False, verts=bm.verts, edges=bm.edges)
            bm.to_mesh(self.obj.data)
            self.obj.data.update()
            bm.clear()
            bm.free()

            beveled_vertices = []
            i = 0
            for v in self.obj.data.vertices:
                # un vertex recevant un bevel ne peut pas appartenir à plus de 2 edges
                v_in_e_count = 0
                for e in self.obj.data.edges:
                    if e.vertices[0] == v.index or e.vertices[1] == v.index:
                        v_in_e_count += 1
                if v_in_e_count == 2:
                    beveled_vertices.append(v)

                    v_group = self.obj.vertex_groups.new(name='bevel.' + str(i))
                    v_group.add([v.index], 1, 'ADD')

                    modif = self.obj.modifiers.new(name=fluent_modifiers_name['first_bevel'] + str(i), type='BEVEL')
                    modif.show_in_editmode = False
                    modif.show_expanded = False
                    modif.limit_method = 'VGROUP'
                    modif.vertex_group = v_group.name
                    modif.affect = 'VERTICES'
                    modif.width = 0
                    modif.use_clamp_overlap = get_addon_preferences().clamp_overlap
                    modif.loop_slide = False

                    if modif.width == 0:
                        modif.show_viewport = False
                        modif.show_render = False
                    else:
                        modif.show_viewport = True
                        modif.show_render = True
                    place_in_stack(self.obj, modif)
                    i += 1

    def refresh_dots(self):
        region = bpy.context.region
        rv3d = bpy.context.region_data
        matrix = self.obj.matrix_world.copy()
        self.dots.set_dots([])
        for v in self.obj.data.vertices:
            co_3d = matrix @ v.co
            co_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, co_3d)
            if self.bevel_vertex_list:
                for i, bv in enumerate(self.bevel_vertex_list):
                    if bv[0] == v.index:
                        self.dots.append_a_dot([co_2d.x, co_2d.y, 3, (1, 1, 1, 1)])
                        break
                    else:
                        self.dots.append_a_dot([co_2d.x, co_2d.y, 3, (0, 0, 0, 1)])

    def adjust_bevel(self, keys):
        self.refresh_dots()

        self.enter_value = enter_value(self.enter_value, keys)

        callback = []
        screen_text = []
        # Initialisation valable au premier tour
        if not self.slider_origin:
            self.slider_origin = keys['mouse_x']

        if not self.init:
            self.initiation()
            diff = False
            b_value = []
            for i in range(len(self.obj.vertex_groups)):
                b_value.append(self.obj.modifiers[fluent_modifiers_name['first_bevel']+str(i)].width)
            i=0
            for w in b_value:
                try:
                    if b_value[i] != b_value[i+1]:
                        diff = True
                except:pass
                i+=1
            i=0
            if not diff:
                for v in self.obj.data.vertices:
                    for v_group in self.obj.vertex_groups:
                        try:
                            if v_group.weight(v.index):
                                self.bevel_vertex_list.append([v.index, i])
                                i+=1
                                break
                        except:pass

            try:
                self.previous_value = self.obj.modifiers[fluent_modifiers_name['first_bevel']+str(self.bevel_vertex_list[0][1])].width
            except:pass

            self.original_value = []
            for b in self.bevels:
                self.original_value.append(get_modifier_values(b))

            self.init = True
        # FIN Initialisation

        if self.action == 'WIDTH':
            self.other_adjustment = 'WIDTH'
            self.slider_origin = keys['mouse_x']
            try:
                for m in self.obj.modifiers:
                    if fluent_modifiers_name['first_bevel'] in m.name and m.show_viewport:
                        self.previous_value = m.width
                        break
            except:
                pass
        elif self.action == 'SEGMENT':
            self.other_adjustment = 'SEGMENT'
            self.slider_origin = keys['mouse_x']
            try:
                for m in self.obj.modifiers:
                    if fluent_modifiers_name['first_bevel'] in m.name and m.show_viewport:
                        self.previous_value = m.segments
                        break
            except:
                pass

        if keys['value'] == 'PRESS' and keys['type'] == 'X':
            self.slider_origin = keys['mouse_x']
            region = bpy.context.region
            rv3d = bpy.context.region_data
            matrix = self.obj.matrix_world.copy()
            nearby = 10000
            candidate = None
            # try:
            # recherche du vertex le plus proche de la souris
            for v in self.obj.data.vertices:
                co_3d = matrix @ v.co
                co_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, co_3d)
                d = distance(x=co_2d.x, y=co_2d.y, xx=keys['mouse_x'], yy=keys['mouse_y'])
                if d < nearby:
                    nearby = d
                    candidate = v
            # si le vertex le plus proche est à moins de 32px de la souris
            if nearby <= 32:
                # vérifie si déjà dans la liste active
                j_y_suis = False
                for i, v in enumerate(self.bevel_vertex_list):
                    if v[1] == candidate.index:
                        # si oui on l'enlève
                        del self.bevel_vertex_list[i]
                        j_y_suis = True
                        break
                if not j_y_suis:
                    # sinon on l'ajoute
                    for i, v_group in enumerate(self.obj.vertex_groups):
                        try:
                            if v_group.weight(candidate.index):
                                self.bevel_vertex_list.append([candidate.index, i])
                                break
                        except:pass
                if self.bevel_vertex_list:
                    self.previous_value = self.obj.modifiers[fluent_modifiers_name['first_bevel']+str(self.bevel_vertex_list[0][1])].width
            else:
                # bascule entre tout séléctionner et rien
                if self.bevel_vertex_list:
                    self.bevel_vertex_list = []
                else:
                    for v in self.obj.data.vertices:
                        for i, v_group in enumerate(self.obj.vertex_groups):
                            try:
                                if v_group.weight(v.index):
                                    self.bevel_vertex_list.append([v.index, i])
                                    break
                            except:pass
                    self.previous_value = self.obj.modifiers[fluent_modifiers_name['first_bevel']+str(self.bevel_vertex_list[0][1])].width
            # except:pass

        if keys['shift_work']:
            increment = 5000
        elif keys['ctrl_work']:
            increment = 50
        else:
            increment = 500
        if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
            self.slider_origin = keys['mouse_x']
            try:
                for m in self.obj.modifiers:
                    if fluent_modifiers_name['first_bevel'] in m.name and m.show_viewport:
                        if self.other_adjustment == 'WIDTH':
                            self.previous_value = m.width
                        elif self.other_adjustment == 'SEGMENT':
                            self.previous_value = m.segments
                        break
            except:pass
        # try:
        for v in self.bevel_vertex_list:
            modifier_name = fluent_modifiers_name['first_bevel']+str(v[1])
            modif = self.obj.modifiers[modifier_name]
            if keys['type'] == 'MOUSEMOVE' and not keys['mouse_left_click']:
                if self.other_adjustment == 'WIDTH':
                    modif.width = self.previous_value + ((keys['mouse_x'] - self.slider_origin)/increment)
                elif self.other_adjustment == 'SEGMENT':
                    modif.segments = int(self.previous_value + ((keys['mouse_x'] - self.slider_origin) / (increment/5)))
                    self.prevent_auto_segments = True
                if modif.width == 0:
                    modif.show_viewport = False
                    modif.show_render = False
                else:
                    modif.show_viewport = True
                    modif.show_render = True

            if modif.profile != 0.25:
                if not self.prevent_auto_segments:
                    modif.segments = auto_bevel_segments(modif)

            if keys['value'] == 'PRESS' and keys['type'] == 'C':
                bevel_type = None
                if modif.segments > 2 and round(modif.profile, 2) != 0.08:
                    bevel_type = 'convex'
                elif modif.segments in {1, 2}:
                    bevel_type = 'straight'
                elif modif.segments != 1 and round(modif.profile, 2) == 0.08:
                    bevel_type = 'concave'
                if bevel_type == 'convex':
                    self.action = 'STRAIGHT'
                elif bevel_type == 'straight':
                    self.action = 'CONCAVE'
                elif bevel_type == 'concave':
                    self.action = 'CONVEX'

            if keys['value'] == 'PRESS' and keys['type'] == 'B':
                self.action = 'STRAIGHT_01'

            if self.action == 'STRAIGHT':
                modif.segments = 2
                modif.profile = 0.25
            elif self.action == 'CONCAVE':
                modif.segments = auto_bevel_segments(modif)
                modif.profile = 0.08
            elif self.action == 'CONVEX':
                modif.segments = auto_bevel_segments(modif)
                modif.profile = bpy.context.scene.fluentProp.bevel_profile
            elif self.action == 'STRAIGHT_01':
                if modif.segments == 2:
                    modif.segments = 1
                    modif.profile = 0.25
                elif modif.segments == 1:
                    modif.segments = 2
                    modif.profile = 0.25

        if enter_value_validation(self.enter_value, keys)[0]:
            for v in self.bevel_vertex_list:
                modifier_name = fluent_modifiers_name['first_bevel'] + str(v[1])
                modif = self.obj.modifiers[modifier_name]
                if self.other_adjustment == 'WIDTH':
                    modif.width = enter_value_validation(self.enter_value, keys)[1]
                elif self.other_adjustment == 'SEGMENT':
                    modif.segments = int(enter_value_validation(self.enter_value, keys)[1])
            self.end_of_adjustment()
            callback.append('STOP_ADJUSTMENT')
        # trie les bevels du plus petit en haut au plus large en bas
        for i in range(len(self.obj.modifiers)-1):
            if fluent_modifiers_name['first_bevel'] in self.obj.modifiers[i].name and fluent_modifiers_name['first_bevel'] in self.obj.modifiers[i+1].name and self.obj.modifiers[i].width > self.obj.modifiers[i+1].width:
                bpy.ops.object.modifier_move_down(modifier=self.obj.modifiers[i].name)
            elif not fluent_modifiers_name['first_bevel'] in self.obj.modifiers[i].name:
                break
        # except:pass

        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            for i, b in enumerate(self.bevels):
                set_modifier_value(b, self.original_value[i])
            callback.append('DO_NOT_QUIT_FLUENT')
            callback.append('STOP_ADJUSTMENT')
            self.end_of_adjustment()

        # TEXT
        screen_text = []
        if len(self.bevel_vertex_list):
            modifier_name = fluent_modifiers_name['first_bevel']+str(self.bevel_vertex_list[0][1])
            modif = self.obj.modifiers[modifier_name]
            if self.other_adjustment == 'WIDTH':
                screen_text.append(['Width', adjustment_value(modif.width, self.enter_value)])
            else:
                screen_text.append(['Width', modifier_value_converter(modif.width)])
            if self.other_adjustment == 'SEGMENT':
                screen_text.append(['Segments', adjustment_value(modif.segments, self.enter_value)])
            else:
                screen_text.append(['Segments', modifier_value_converter(modif.segments)])
        screen_text.append(['Vertex selection', 'X'])
        screen_text.append(['One segments', 'B'])
        screen_text.append(['Slower/Faster', 'Shift/Ctrl'])

        self.action = None
        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    self.end_of_adjustment()
                    screen_text = []
                    callback.append('STOP_ADJUSTMENT')
                else:
                    self.slider_origin = keys['mouse_x']
                    try:
                        for m in self.obj.modifiers:
                            if fluent_modifiers_name['first_bevel'] in m.name and m.show_viewport:
                                if self.other_adjustment == 'WIDTH':
                                    self.previous_value = m.width
                                elif self.other_adjustment == 'SEGMENT':
                                    self.previous_value = m.segments
                                break
                    except:pass

        if keys['type'] == 'V' and keys['value'] == 'PRESS':
            if self.other_adjustment == 'WIDTH':
                self.action = 'SEGMENT'
            elif self.other_adjustment == 'SEGMENT':
                self.action = 'WIDTH'

        return callback, screen_text


class taper_management():
    def __init__(self, obj):
        self.obj = obj
        self.taper = {'x':None, 'y':None, 'z':None}
        self.array_axis = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = None
        self.backup = {}
        self.init = False

        # affichage
        self.ui_items_list = []
        self.pie_menu = None
        self.action = None
        self.dots = None

        self.pie_menu = FLUENT_Ui_Layout('TAPER')
        self.pie_menu.set_layout('TAPER')
        self.pie_menu.set_obj(self.obj)

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+X')
        button.set_default_color((.9, 0, 0, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+Y')
        button.set_default_color((0, .9, 0, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+Z')
        button.set_default_color((0, 0, .9, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def initiation(self):
        for m in self.obj.modifiers:
            if m.name == fluent_modifiers_name['taper_x'] and m.type == 'SIMPLE_DEFORM':
                self.taper['x'] = m
            elif m.name == fluent_modifiers_name['taper_y'] and m.type == 'SIMPLE_DEFORM':
                self.taper['y'] = m
            elif m.name == fluent_modifiers_name['taper_z'] and m.type == 'SIMPLE_DEFORM':
                self.taper['z'] = m
        return self.taper

    def get_modifier(self):
        return self.taper

    def end_of_adjustment(self):
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = {'axis':None, 'factor':None, 'lock_x':None, 'lock_y':None, 'lock_z':None}
        self.init = False
        self.array_axis = ''

    def restore_value(self):
        self.taper['x'].factor = self.original_value['x']['factor']
        self.taper['x'].lock_y = self.original_value['x']['lock_y']
        self.taper['x'].lock_z = self.original_value['x']['lock_z']
        self.taper['y'].factor = self.original_value['y']['factor']
        self.taper['y'].lock_x = self.original_value['y']['lock_x']
        self.taper['y'].lock_z = self.original_value['y']['lock_z']
        self.taper['z'].factor = self.original_value['z']['factor']
        self.taper['z'].lock_x = self.original_value['z']['lock_x']
        self.taper['z'].lock_y = self.original_value['z']['lock_y']

    def add_taper(self):
        self.initiation()
        if not (self.taper['x'] and self.taper['y'] and self.taper['z']):
            self.taper['z'] = self.obj.modifiers.new(name=fluent_modifiers_name['taper_z'], type='SIMPLE_DEFORM')
            self.taper['z'].deform_method = 'TAPER'
            self.taper['z'].deform_axis = 'Z'
            self.taper['z'].factor = 0
            self.taper['z'].show_render = self.taper['z'].show_viewport = False
            self.taper['z'].show_expanded = False

            self.taper['x'] = self.obj.modifiers.new(name=fluent_modifiers_name['taper_x'], type='SIMPLE_DEFORM')
            self.taper['x'].deform_method = 'TAPER'
            self.taper['x'].deform_axis = 'X'
            self.taper['x'].factor = 0
            self.taper['x'].show_render = self.taper['x'].show_viewport = False
            self.taper['x'].show_expanded = False

            self.taper['y'] = self.obj.modifiers.new(name=fluent_modifiers_name['taper_y'], type='SIMPLE_DEFORM')
            self.taper['y'].deform_method = 'TAPER'
            self.taper['y'].deform_axis = 'Y'
            self.taper['y'].factor = 0
            self.taper['y'].show_render = self.taper['y'].show_viewport = False
            self.taper['y'].show_expanded = False

            place_in_stack(self.obj, self.taper['x'])
            place_in_stack(self.obj, self.taper['y'])
            place_in_stack(self.obj, self.taper['z'])

    def adjust_tape(self, keys):
        callback = []
        screen_text = []
        self.enter_value = enter_value(self.enter_value, keys)

        if not self.init:
            self.taper['x'].show_viewport = self.taper['x'].show_render = True
            self.taper['y'].show_viewport = self.taper['y'].show_render = True
            self.taper['z'].show_viewport = self.taper['z'].show_render = True
            self.original_value = {
                'x':{
                    'factor':self.taper['x'].factor,
                    'lock_y':self.taper['x'].lock_y,
                    'lock_z':self.taper['x'].lock_z
                    },
                'y':{
                    'factor':self.taper['y'].factor,
                    'lock_x':self.taper['y'].lock_x,
                    'lock_z':self.taper['y'].lock_z
                },
                'z':{
                    'factor':self.taper['z'].factor,
                    'lock_x':self.taper['z'].lock_x,
                    'lock_y':self.taper['z'].lock_y
                }
            }
            self.previous_value = {
                'x':self.taper['x'].factor,
                'y':self.taper['y'].factor,
                'z':self.taper['z'].factor
            }
            self.backup['x'] = get_modifier_values(self.taper['x'])
            self.backup['y'] = get_modifier_values(self.taper['y'])
            self.backup['z'] = get_modifier_values(self.taper['z'])
            self.init = True

        if keys['shift_work']:
            increment = 3000
        elif keys['ctrl_work']:
            increment = 30
        else:
            increment = 500

        if self.array_axis and keys['value'] == 'PRESS' and keys['type'] == 'LEFTMOUSE':
            self.array_axis = None

        if type(self.action) == str and 'X' in self.action:
            self.slider_origin = keys['mouse_x']
            self.previous_value['x'] = self.taper['x'].factor
            self.array_axis = 'X'
            self.taper['x'].show_viewport = True
            self.taper['x'].show_render = True
        elif type(self.action) == str and 'Y' in self.action:
            self.slider_origin = keys['mouse_x']
            self.previous_value['y'] = self.taper['y'].factor
            self.array_axis = 'Y'
            self.taper['y'].show_viewport = True
            self.taper['y'].show_render = True
        elif type(self.action) == str and 'Z' in self.action:
            self.slider_origin = keys['mouse_x']
            self.previous_value['z'] = self.taper['z'].factor
            self.array_axis = 'Z'
            self.taper['z'].show_viewport = True
            self.taper['z'].show_render = True

        if self.array_axis != None:
            if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
                self.slider_origin = keys['mouse_x']
                self.previous_value = {
                    'x':self.taper['x'].factor,
                    'y':self.taper['y'].factor,
                    'z':self.taper['z'].factor
                }

            if self.array_axis == 'X':
                if enter_value_validation(self.enter_value, keys)[0]:
                    self.taper['x'].factor = self.previous_value['x'] = enter_value_validation(self.enter_value, keys)[1]
                    self.enter_value = 'None'
                    self.array_axis = None
                if keys['type'] == 'MOUSEMOVE' and not keys['mouse_left_click']:
                    self.taper['x'].factor = self.previous_value['x'] + (keys['mouse_x'] - self.slider_origin)/increment

                if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
                    self.restore_value()
                    callback.append('DO_NOT_QUIT_FLUENT')
                    self.end_of_adjustment()

                if keys['value'] == 'PRESS' and keys['type'] == 'DEL':
                    self.taper['x'].factor = 0
                    self.taper['x'].show_viewport = self.taper['x'].show_render = False
                    self.array_axis = ''

                if keys['value'] == 'PRESS' and keys['type'] == 'C':
                    if not self.taper['x'].lock_y and not self.taper['x'].lock_z:
                        self.taper['x'].lock_y = True
                        self.taper['x'].lock_z = False
                    elif self.taper['x'].lock_y:
                        self.taper['x'].lock_y = False
                        self.taper['x'].lock_z = True
                    elif self.taper['x'].lock_z:
                        self.taper['x'].lock_y = False
                        self.taper['x'].lock_z = False

            if self.array_axis == 'Y':
                if enter_value_validation(self.enter_value, keys)[0]:
                    self.taper['y'].factor = self.previous_value['y'] = enter_value_validation(self.enter_value, keys)[1]
                    self.enter_value = 'None'
                    self.array_axis = None
                if keys['type'] == 'MOUSEMOVE':
                    self.taper['y'].factor = self.previous_value['y'] + (keys['mouse_x'] - self.slider_origin)/increment

                if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
                    self.restore_value()
                    callback.append('DO_NOT_QUIT_FLUENT')
                    self.end_of_adjustment()

                if keys['value'] == 'PRESS' and keys['type'] == 'DEL':
                    self.taper['y'].factor = 0
                    self.taper['y'].show_viewport = self.taper['y'].show_render = False
                    self.array_axis = ''

                if keys['value'] == 'PRESS' and keys['type'] == 'C':
                    if not self.taper['y'].lock_x and not self.taper['y'].lock_z:
                        self.taper['y'].lock_x = True
                        self.taper['y'].lock_z = False
                    elif self.taper['y'].lock_x:
                        self.taper['y'].lock_x = False
                        self.taper['y'].lock_z = True
                    elif self.taper['y'].lock_z:
                        self.taper['y'].lock_x = False
                        self.taper['y'].lock_z = False

            if self.array_axis == 'Z':
                if enter_value_validation(self.enter_value, keys)[0]:
                    self.taper['z'].factor = self.previous_value['z'] = enter_value_validation(self.enter_value, keys)[1]
                    self.enter_value = 'None'
                    self.array_axis = None
                if keys['type'] == 'MOUSEMOVE':
                    self.taper['z'].factor = self.previous_value['z'] + (keys['mouse_x'] - self.slider_origin)/increment

                if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
                    self.restore_value()
                    callback.append('DO_NOT_QUIT_FLUENT')
                    self.end_of_adjustment()

                if keys['value'] == 'PRESS' and keys['type'] == 'DEL':
                    self.taper['z'].factor = 0
                    self.taper['z'].show_viewport = self.taper['z'].show_render = False
                    self.array_axis = ''

                if keys['value'] == 'PRESS' and keys['type'] == 'C':
                    if not self.taper['z'].lock_x and not self.taper['z'].lock_y:
                        self.taper['z'].lock_x = True
                        self.taper['z'].lock_y = False
                    elif self.taper['z'].lock_x:
                        self.taper['z'].lock_x = False
                        self.taper['z'].lock_y = True
                    elif self.taper['z'].lock_y:
                        self.taper['z'].lock_x = False
                        self.taper['z'].lock_y = False

        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            try:
                set_modifier_value(self.taper['x'], self.backup['x'])
                set_modifier_value(self.taper['y'], self.backup['y'])
                set_modifier_value(self.taper['z'], self.backup['z'])
            except:pass
            self.end_of_adjustment()
            callback.append('DO_NOT_QUIT_FLUENT')
            callback.append('STOP_ADJUSTMENT')

        # TEXT
        if self.array_axis == 'X':
            screen_text.append(['X factor', adjustment_value(self.taper['x'].factor, self.enter_value)])
        else:
            screen_text.append(['X factor', modifier_value_converter(self.taper['x'].factor)])
        if self.array_axis == 'Y':
            screen_text.append(['Y factor', adjustment_value(self.taper['y'].factor, self.enter_value)])
        else:
            screen_text.append(['Y factor', modifier_value_converter(self.taper['y'].factor)])
        if self.array_axis == 'Z':
            screen_text.append(['Z factor', adjustment_value(self.taper['z'].factor, self.enter_value)])
        else:
            screen_text.append(['Z factor', modifier_value_converter(self.taper['z'].factor)])
        if self.array_axis != None:
            screen_text.append(['Lock axis', 'C'])
            screen_text.append(['Remove', 'Delete'])
            screen_text.append(['Slower/Faster', 'Shift/Ctrl'])

        self.action = None
        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    self.end_of_adjustment()
                    screen_text = []
                    callback.append('STOP_ADJUSTMENT')
                else:
                    self.slider_origin = keys['mouse_x']

        return callback, screen_text


class circular_array_management():
    def __init__(self, obj, target=None):
        self.obj = obj
        self.bool_target = target
        self.modifier = None
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = {
            'radius':None,
            'count':None,
            'end':None,
            'angle':None,
            'z':None
        }
        self.init = False
        self.empty = None
        self.empty_matrix_save = None
        self.other_adjustment = 'RADIUS'

        # menu
        self.ui_items_list = []
        self.action = None
        self.pie_menu = FLUENT_Ui_Layout('CIRCULAR_ARRAY')
        self.pie_menu.set_layout('PIE')

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Count')
        button.set_shape('RECTANGLE')
        button.set_action('COUNT')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Radius')
        button.set_shape('RECTANGLE')
        button.set_action('ARRAY_RADIUS')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Angle')
        button.set_shape('RECTANGLE')
        button.set_action('ANGLE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Array rotation')
        button.set_shape('RECTANGLE')
        button.set_action('ARRAY_ROT')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def get_modifier(self):
        return self.modifier

    def initiation(self):
        for m in self.obj.modifiers:
            if m.name == fluent_modifiers_name['circular_array'] and m.type == 'NODES':
                self.modifier = m
        return self.modifier

    def end_of_adjustment(self):
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = {}
        self.init = False
        self.other_adjustment = 'RADIUS'

    def restore(self):
        array_radius = self.modifier.node_group.nodes[fluent_modifiers_name['circular_array']].inputs['Radius']
        array_count = self.modifier.node_group.nodes[fluent_modifiers_name['circular_array']].inputs['Count']
        array_end = self.modifier.node_group.nodes[fluent_modifiers_name['circular_array']].inputs['End']
        array_angle = self.modifier.node_group.nodes[fluent_modifiers_name['circular_array']].inputs['Angle']
        array_z = self.modifier.node_group.nodes[fluent_modifiers_name['circular_array']].inputs['Z']
        support_object = self.modifier.node_group.nodes[fluent_modifiers_name['circular_array']].inputs['Support']
        array_radius.default_value = self.original_value['radius']
        array_count.default_value = self.original_value['count']
        array_end.default_value = self.original_value['end']
        array_angle.default_value = self.original_value['angle']
        array_z.default_value = self.original_value['z']
        support_object.default_value = self.original_value['support']

    def add_circular_array(self):
        self.initiation()
        if not self.modifier:
            main_dir = join(dirname(realpath(__file__)))
            blender_dir = join(main_dir,'geometry_nodes')
            blender_file = join(blender_dir,'array.blend')
            file_path_node_tree = join(blender_file,'NodeTree')

            group_name = fluent_modifiers_name['circular_array']
            if not bpy.data.node_groups.get(group_name):
                bpy.ops.wm.append(filename=group_name, directory=file_path_node_tree)

            self.modifier = self.obj.modifiers.new(name=fluent_modifiers_name['circular_array'], type='NODES')
            node_group = bpy.data.node_groups.new(name='Circular_Array', type='GeometryNodeTree')
            node_group.nodes.new(type='NodeGroupInput')
            node_group.nodes.new(type='NodeGroupOutput')
            self.modifier.node_group = node_group
            tree = self.modifier.node_group
            nodes = tree.nodes
            link = tree.links.new
            node_c_array = nodes.new(type='GeometryNodeGroup')
            node_c_array.name = group_name
            node_c_array.node_tree = bpy.data.node_groups.get(group_name)
            for n in nodes:
                if n.type == 'GROUP_INPUT':
                    group_in = n
                if n.type == 'GROUP_OUTPUT':
                    group_out = n
            link(group_in.outputs[0], node_c_array.inputs[0])
            link(node_c_array.outputs[0], group_out.inputs[0])
            # group_in.outputs.new(type = 'FLOAT', name='Radius')
            # link(group_in.outputs[1], node_c_array.inputs[1])
            # group_in.outputs.new(type = 'INTEGER', name='Count')
            # link(group_in.outputs[2], node_c_array.inputs[2])
            # group_in.outputs.new(type = 'FLOAT', name='Angle')
            # link(group_in.outputs[3], node_c_array.inputs[3])
            # group_in.outputs.new(type = 'FLOAT', name='Individual Rotation')
            # link(group_in.outputs[4], node_c_array.inputs[4])
            # group_in.outputs.new(type = 'FLOAT', name='Global rotation')
            # link(group_in.outputs[5], node_c_array.inputs[5])
            self.modifier.show_render = False
            self.modifier.show_viewport = False
            self.modifier.show_expanded = False
            self.modifier.node_group.nodes[fluent_modifiers_name['circular_array']].inputs['Current'].default_value = self.obj
            place_in_stack(self.obj, self.modifier)
        return self.modifier

    def adjust(self, keys=None, draw_type=None):
        self.enter_value = enter_value(self.enter_value, keys)

        callback = []
        screen_text = []

        array_radius = self.modifier.node_group.nodes[fluent_modifiers_name['circular_array']].inputs['Radius']
        array_count = self.modifier.node_group.nodes[fluent_modifiers_name['circular_array']].inputs['Count']
        array_end = self.modifier.node_group.nodes[fluent_modifiers_name['circular_array']].inputs['End']
        array_angle = self.modifier.node_group.nodes[fluent_modifiers_name['circular_array']].inputs['Angle']
        array_z = self.modifier.node_group.nodes[fluent_modifiers_name['circular_array']].inputs['Z']
        support_object = self.modifier.node_group.nodes[fluent_modifiers_name['circular_array']].inputs['Support']

        if not self.init:
            self.slider_origin = keys['mouse_x']
            self.previous_value = array_radius.default_value
            self.original_value['radius'] = array_radius.default_value
            self.original_value['count'] = array_count.default_value
            self.original_value['end'] = array_end.default_value
            self.original_value['angle'] = array_angle.default_value
            self.original_value['z'] = array_z.default_value
            self.original_value['support'] = support_object.default_value
            self.init = True
            self.modifier.show_render = self.modifier.show_viewport = True

        if self.action:
            self.empty_matrix_save = self.obj.matrix_world.copy()
            if self.action == 'ANGLE':
                self.other_adjustment = 'ANGLE'
                self.previous_value = array_end.default_value
                self.slider_origin = keys['mouse_x']
            elif self.action == 'COUNT':
                self.other_adjustment = 'COUNT'
                self.previous_value = array_count.default_value
                self.slider_origin = keys['mouse_x']
            elif self.action == 'ARRAY_RADIUS':
                self.other_adjustment = 'RADIUS'
                self.previous_value = array_radius.default_value
                self.slider_origin = keys['mouse_x']
            elif self.action == 'ARRAY_ROT':
                self.other_adjustment = 'ARRAY_ROT'
                self.previous_value = array_z.default_value
                self.slider_origin = keys['mouse_x']

        if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
            self.slider_origin = keys['mouse_x']
            if self.other_adjustment == 'COUNT':
                self.previous_value = array_count.default_value
            elif self.other_adjustment == 'RADIUS':
                self.previous_value = array_radius.default_value
            elif self.other_adjustment == 'ANGLE':
                self.previous_value = array_end.default_value
            elif self.other_adjustment == 'ARRAY_ROT':
                self.previous_value = array_z.default_value

        if not keys['mouse_left_click'] and (keys['type'] == 'MOUSEMOVE' or enter_value_validation(self.enter_value, keys)[0]):
            if self.other_adjustment == 'RADIUS':
                if keys['shift_work']:
                    increment = 2000
                elif keys['ctrl_work']:
                    increment = 20
                else:
                    increment = 200
                array_radius.default_value = self.previous_value + ((keys['mouse_x'] - self.slider_origin)/increment)
                if enter_value_validation(self.enter_value, keys)[0]:
                    array_radius.default_value = enter_value_validation(self.enter_value, keys)[1]
                    self.enter_value = 'None'
                    self.other_adjustment = None
            elif self.other_adjustment == 'COUNT':
                if keys['shift_work']:
                    increment = 300
                elif keys['ctrl_work']:
                    increment = 30
                else:
                    increment = 60
                a = array_count.default_value
                array_count.default_value = int(self.previous_value + ((keys['mouse_x'] - self.slider_origin)/increment))
                if enter_value_validation(self.enter_value, keys)[0]:
                    array_count.default_value = int(enter_value_validation(self.enter_value, keys)[1])
                    self.enter_value = 'None'
                    self.other_adjustment = None
            elif self.other_adjustment == 'ANGLE':
                if keys['shift_work']:
                    increment = 50
                elif keys['ctrl_work']:
                    increment = 1
                else:
                    increment = 5
                array_end.default_value = int(self.previous_value + ((keys['mouse_x'] - self.slider_origin)/increment))
                if keys['ctrl_work']:
                    array_end.default_value = int(math.ceil(array_end.default_value / 45)) * 45
                if enter_value_validation(self.enter_value, keys)[0]:
                    array_end.default_value = int(enter_value_validation(self.enter_value, keys)[1])
                    self.enter_value = 'None'
                    self.other_adjustment = None
                if array_end.default_value > 360:
                    array_end.default_value = 360
                elif array_end.default_value < 0:
                    array_end.default_value = 0
            elif self.other_adjustment == 'ARRAY_ROT':
                if keys['shift_work']:
                    increment = 500
                elif keys['ctrl_work']:
                    increment = 5
                else:
                    increment = 50
                array_z.default_value = self.previous_value + ((keys['mouse_x'] - self.slider_origin)/increment)

        if keys['value'] == 'PRESS' and keys['type'] == 'C' and not draw_type in {'prism', 'screw'}:
            self.obj.modifiers[fluent_modifiers_name['scale']].node_group.nodes['Transform'].inputs[2].default_value[2] += math.radians(45)

        if keys['value'] == 'PRESS' and keys['type'] == 'V' and not draw_type in {'prism', 'screw'}:
            self.obj.modifiers[fluent_modifiers_name['scale']].node_group.nodes['Transform'].inputs[2].default_value[0] += math.radians(45)

        if keys['value'] == 'PRESS' and keys['type'] == 'B' and self.bool_target:
            inputs = self.modifier.node_group.nodes[fluent_modifiers_name['circular_array']].inputs
            if inputs['Use Support'].default_value == 0:
                support_object.default_value = self.bool_target
                inputs['Axis'].default_value = Vector((0, 1, 0))
                inputs['Use Support'].default_value = 1
            else:
                inputs['Use Support'].default_value = 0
                inputs['Axis'].default_value = Vector((0, 0, 1))

        # TEXT
        if self.other_adjustment == 'COUNT':
            screen_text.append(['Count : ', adjustment_value(array_count.default_value, self.enter_value)])
            screen_text.append(['Radius : ', modifier_value_converter(array_radius.default_value)])
            screen_text.append(['Angle : ', modifier_value_converter(array_end.default_value)])
        elif self.other_adjustment == 'RADIUS':
            screen_text.append(['Count : ', modifier_value_converter(array_count.default_value)])
            screen_text.append(['Radius : ', adjustment_value(array_radius.default_value, self.enter_value)])
            screen_text.append(['Angle : ', modifier_value_converter(array_end.default_value)])
        elif self.other_adjustment == 'ANGLE':
            screen_text.append(['Count : ', modifier_value_converter(array_count.default_value)])
            screen_text.append(['Radius : ', modifier_value_converter(array_radius.default_value)])
            screen_text.append(['Angle : ', adjustment_value(array_end.default_value, self.enter_value)])
        else:
            screen_text.append(['Count : ', modifier_value_converter(array_count.default_value)])
            screen_text.append(['Radius : ', modifier_value_converter(array_radius.default_value)])
            screen_text.append(['Angle : ', modifier_value_converter(array_end.default_value)])
        screen_text.append(['Object Z rotation', 'C'])
        screen_text.append(['Object X rotation', 'V'])
        screen_text.append(['Object as axis', 'B'])
        screen_text.append(['Slower/Faster', 'Shift/Ctrl'])
        screen_text.append(['Remove', 'Del/Back space'])

        self.action = None

        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    self.end_of_adjustment()
                    screen_text = []
                    callback.append('STOP_ADJUSTMENT')
                else:
                    self.slider_origin = keys['mouse_x']

        if keys['value'] == 'PRESS' and keys['type'] in {'DEL', 'BACK_SPACE'}:
            self.modifier.show_viewport = False
            self.modifier.show_render = False
            self.action = 'VALIDATE'
            self.end_of_adjustment()
            screen_text = []
            callback.append('STOP_ADJUSTMENT')

        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            try:
                self.restore()
            except:pass
            self.end_of_adjustment()
            callback.append('DO_NOT_QUIT_FLUENT')
            callback.append('STOP_ADJUSTMENT')

        return callback, screen_text


class radius_management():
    def __init__(self, obj):
        self.obj = obj
        self.radius = None
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = None
        self.init = False

        # menu
        self.ui_items_list = []
        self.pie_menu = None
        self.action = None
        self.pie_menu = FLUENT_Ui_Layout('FIRST_SOLIDIFY')
        self.pie_menu.set_layout('PIE')

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

    def get_modifier(self):
        return self.solidify

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def get_modifier(self):
        return self.radius

    def initiation(self):
        for m in self.obj.modifiers:
            if m.name == fluent_modifiers_name['radius'] and m.type == 'DISPLACE':
                self.radius = m
                break
        return self.radius

    def end_of_adjustment(self):
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = None
        self.init = False

    def add_radius(self):
        self.initiation()
        if not self.radius:
            found = False
            for m in self.obj.modifiers:
                if m.name == fluent_modifiers_name['radius']:
                    found = True
                    self.radius = m
            if not found:
                self.radius = self.obj.modifiers.new(name=fluent_modifiers_name['radius'], type='DISPLACE')
                self.radius.show_in_editmode = True
                self.radius.show_on_cage = True
                self.radius.direction = 'X'
                self.radius.vertex_group = 'radius'
                self.radius.strength = 0
                self.radius.mid_level = 0
                self.radius.show_expanded = False
                place_in_stack(self.obj, self.radius)

    def adjust_modifier(self, keys):
        callback = []
        screen_text = []

        self.enter_value = enter_value(self.enter_value, keys)

        if not self.init:
            self.previous_value = self.radius.strength
            self.original_value = self.radius.strength
            self.slider_origin = keys['mouse_x']
            self.init = True

        if keys['shift_work']:
            increment = 3000
        elif keys['ctrl_work']:
            increment = 30
        else:
            increment = 500

        if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
            self.slider_origin = keys['mouse_x']
            self.previous_value = self.radius.strength

        if keys['type'] == 'MOUSEMOVE' and not keys['mouse_left_click']:
            self.radius.strength = self.previous_value + ((keys['mouse_x'] - self.slider_origin)/increment)

            if self.obj['fluent_type'] != 'sphere' and (self.obj.get('fluent_auto_res') == 'ENABLE' or not self.obj.get('fluent_auto_res')):
                screw = self.obj.modifiers[fluent_modifiers_name['screw']]
                screw.steps = screw.render_steps = auto_bevel_segments(displace=self.radius)
            elif self.obj['fluent_type'] == 'sphere' and (self.obj.get('fluent_auto_res') == 'ENABLE' or not self.obj.get('fluent_auto_res')):
                screw_2 = self.obj.modifiers[fluent_modifiers_name['screw_2']]
                screw_2.steps = screw_2.render_steps = int(auto_bevel_segments(displace=self.obj.modifiers[fluent_modifiers_name['radius']]) / 2)
                screw = self.obj.modifiers[fluent_modifiers_name['screw']]
                screw.steps = screw.render_steps = int(screw_2.steps / 3)

        if enter_value_validation(self.enter_value, keys)[0]:
            self.radius.strength = enter_value_validation(self.enter_value, keys)[1]
            if self.obj['fluent_type'] != 'sphere' and (self.obj.get('fluent_auto_res') == 'ENABLE' or not self.obj.get('fluent_auto_res')):
                screw = self.obj.modifiers[fluent_modifiers_name['screw']]
                screw.steps = screw.render_steps = int(auto_bevel_segments(displace=self.radius))
            elif self.obj['fluent_type'] == 'sphere' and (self.obj.get('fluent_auto_res') == 'ENABLE' or not self.obj.get('fluent_auto_res')):
                screw_2 = self.obj.modifiers[fluent_modifiers_name['screw_2']]
                screw_2.steps = screw_2.render_steps = int(auto_bevel_segments(displace=self.obj.modifiers[fluent_modifiers_name['radius']]) / 2)
                screw = self.obj.modifiers[fluent_modifiers_name['screw']]
                screw.steps = screw.render_steps = int(screw_2.steps / 3)
            self.end_of_adjustment()
            callback.append('STOP_ADJUSTMENT')

        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            self.radius.strength = self.original_value
            self.end_of_adjustment()
            callback.append('STOP_ADJUSTMENT')
            callback.append('DO_NOT_QUIT_FLUENT')

        # TEXT
        screen_text.append(['Radius', adjustment_value(self.radius.strength, self.enter_value)])
        screen_text.append(['Slower/Faster', 'Shift/Ctrl'])

        self.action = None
        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    self.end_of_adjustment()
                    screen_text = []
                    callback.append('STOP_ADJUSTMENT')
                else:
                    self.slider_origin = keys['mouse_x']

        return callback, screen_text


class resolution_management():
    def __init__(self, obj):
        self.obj = obj
        self.resolution = None
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = None
        self.init = False

        # menu
        self.ui_items_list = []
        self.action = None
        self.pie_menu = FLUENT_Ui_Layout('CIRCULAR_ARRAY')
        self.pie_menu.set_layout('PIE')

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

    def initiation(self):
        for m in self.obj.modifiers:
            if m.name == fluent_modifiers_name['screw'] and m.type == 'SCREW':
                self.resolution = m
                break
        return self.resolution

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def get_modifier(self):
        return self.resolution

    def end_of_adjustment(self):
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = None
        self.init = False

    def add_resolution(self):
        self.initiation()
        if not self.resolution:
            found = False
            for m in self.obj.modifiers:
                if m.name == fluent_modifiers_name['screw']:
                    found = True
                    self.resolution = m
                    break
            if not found:
                self.resolution = self.obj.modifiers.new(name=fluent_modifiers_name['screw'], type='SCREW')
                self.resolution.merge_threshold = 0.0001
                self.resolution.use_merge_vertices = True
                self.resolution.use_smooth_shade = True
                self.resolution.steps = self.resolution.render_steps = auto_bevel_segments(revolver_obj=self.obj)
                self.resolution.use_normal_calculate = True
                self.resolution.show_expanded = False
                if self.obj.get('fluent_type') == 'revolver':
                    self.resolution.axis = 'Y'
                place_in_stack(self.obj, self.resolution)

    def adjust_modifier(self, keys):
        callback = []
        screen_text = []

        self.enter_value = enter_value(self.enter_value, keys)

        if not self.init:
            self.previous_value = self.resolution.steps
            self.original_value = self.resolution.steps
            self.slider_origin = keys['mouse_x']
            self.init = True

        if keys['shift_work']:
            increment = 300
        elif keys['ctrl_work']:
            increment = 3
        else:
            increment = 30

        if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
            self.slider_origin = keys['mouse_x']
            self.previous_value = self.resolution.steps

        if keys['type'] == 'MOUSEMOVE' and not keys['mouse_left_click']:
            self.resolution.steps = self.resolution.render_steps = int(self.previous_value + ((keys['mouse_x'] - self.slider_origin)/increment))

            if self.obj['fluent_type'] == 'sphere':
                screw_2 = self.obj.modifiers[fluent_modifiers_name['screw_2']]
                screw_2.steps = screw_2.render_steps = self.resolution.steps * 3

        if enter_value_validation(self.enter_value, keys)[0]:
            self.resolution.steps = self.resolution.render_steps = self.resolution.render_steps = int(enter_value_validation(self.enter_value, keys)[1])
            # synchro
            again = self.obj.modifiers.get(fluent_modifiers_name['screw']+'.again')
            if again:
                again.steps = again.render_steps = self.resolution.steps * 2
            callback.append('STOP_ADJUSTMENT')
            self.end_of_adjustment()

        if keys['type'] == 'C' and keys['value'] == 'PRESS':
            self.resolution.steps = self.resolution.render_steps = auto_bevel_segments(revolver_obj=self.obj)
            self.end_of_adjustment()

        if keys['type'] == 'V' and keys['value'] == 'PRESS':
            if self.obj.get('fluent_auto_res') == 'ENABLE' or not self.obj.get('fluent_auto_res'):
                self.obj['fluent_auto_res'] = 'PREVENT'
            else:
                self.obj['fluent_auto_res'] = 'ENABLE'

        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            self.resolution.steps = self.resolution.render_steps = self.original_value
            self.end_of_adjustment()
            callback.append('STOP_ADJUSTMENT')
            callback.append('DO_NOT_QUIT_FLUENT')

        screen_text.append(['Resolution : ', adjustment_value(self.resolution.steps, self.enter_value)])
        screen_text.append(['Default resolution', 'C'])
        if self.obj.get('fluent_auto_res') == 'ENABLE' or not self.obj.get('fluent_auto_res'):
            screen_text.append(['Prevent auto resolution', 'V'])
        else:
            screen_text.append(['Enable auto resolution', 'V'])
        screen_text.append(['Slower/Faster', 'Shift/Ctrl'])

        self.action = None
        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    self.end_of_adjustment()
                    screen_text = []
                    callback.append('STOP_ADJUSTMENT')
                else:
                    self.slider_origin = keys['mouse_x']

        return callback, screen_text

    def flip(self):
        callback = []
        self.resolution.use_normal_flip = not self.resolution.use_normal_flip
        callback.append('STOP_ADJUSTMENT')
        return callback


class curve_management():
    def __init__(self, obj):
        self.obj = obj
        # curve est un modifier Subdiv
        self.curve = None
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = None
        self.init = False

        # menu
        self.ui_items_list = []
        self.pie_menu = None
        self.action = None
        self.pie_menu = FLUENT_Ui_Layout('CURVE')
        self.pie_menu.set_layout('PIE')

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def get_modifier(self):
        return self.curve

    def initiation(self):
        for m in self.obj.modifiers:
            if m.name == fluent_modifiers_name['curve_subdivision'] and m.type == 'SUBSURF':
                self.curve = m
                break
        return self.curve

    def end_of_adjustment(self):
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = None
        self.init = False

    def add_curve(self):
        self.initiation()
        if not self.curve:
            modif = self.obj.modifiers.new(name=fluent_modifiers_name['curve_triangulate'], type='TRIANGULATE')
            modif.min_vertices = 4
            modif.ngon_method = 'BEAUTY'
            modif.quad_method = 'SHORTEST_DIAGONAL'
            modif.show_expanded = modif.show_render = modif.show_viewport = False
            move_modifier(obj=self.obj, mod_name=fluent_modifiers_name['curve_triangulate'], where='BEFORE', mod_target_name=fluent_modifiers_name['first_bevel'])
            modif = self.curve = self.obj.modifiers.new(name=fluent_modifiers_name['curve_subdivision'], type='SUBSURF')
            modif.quality = 6
            modif.levels = 3
            modif.render_levels = 3
            modif.show_expanded = modif.show_render = modif.show_viewport = False
            move_modifier(obj=self.obj, mod_name=fluent_modifiers_name['curve_subdivision'], where='AFTER', mod_target_name=fluent_modifiers_name['curve_triangulate'])
            modif = self.obj.modifiers.new(name=fluent_modifiers_name['curve_decimate'], type='DECIMATE')
            modif.decimate_type = 'DISSOLVE'
            modif.angle_limit = 0.00174533
            modif.show_expanded = modif.show_render = modif.show_viewport = False
            move_modifier(obj=self.obj, mod_name=fluent_modifiers_name['curve_decimate'], where='AFTER', mod_target_name=fluent_modifiers_name['curve_subdivision'])

    def adjust(self, keys):
        callback = []
        screen_text = []

        self.enter_value = enter_value(self.enter_value, keys)

        if not self.init:
            self.previous_value = self.curve.levels
            self.original_value = self.curve.levels
            self.slider_origin = keys['mouse_x']
            self.init = True
            self.curve.show_render = self.curve.show_viewport = True
            self.obj.modifiers[fluent_modifiers_name['curve_triangulate']].show_render = self.obj.modifiers[fluent_modifiers_name['curve_triangulate']].show_viewport = True
            self.obj.modifiers[fluent_modifiers_name['curve_decimate']].show_render = self.obj.modifiers[fluent_modifiers_name['curve_decimate']].show_viewport = True

        if keys['shift_work']:
            increment = 600
        elif keys['ctrl_work']:
            increment = 6
        else:
            increment = 50

        if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
            self.slider_origin = keys['mouse_x']
            self.previous_value = self.curve.levels

        if keys['type'] == 'MOUSEMOVE':
            level = round(self.previous_value + ((keys['mouse_x'] - self.slider_origin)/increment))
            if level > 6:
                level = 6
            elif level < 0:
                level = 0
            self.curve.render_levels = self.curve.levels = level
            if self.curve.levels != 0:
                self.curve.show_render = self.curve.show_viewport = True
                self.obj.modifiers[fluent_modifiers_name['curve_triangulate']].show_render = self.obj.modifiers[fluent_modifiers_name['curve_triangulate']].show_viewport = True
                self.obj.modifiers[fluent_modifiers_name['curve_decimate']].show_render = self.obj.modifiers[fluent_modifiers_name['curve_decimate']].show_viewport = True
            else:
                self.curve.show_render = self.curve.show_viewport = False
                self.obj.modifiers[fluent_modifiers_name['curve_triangulate']].show_render = self.obj.modifiers[fluent_modifiers_name['curve_triangulate']].show_viewport = False
                self.obj.modifiers[fluent_modifiers_name['curve_decimate']].show_render = self.obj.modifiers[fluent_modifiers_name['curve_decimate']].show_viewport = False

        if enter_value_validation(self.enter_value, keys)[0]:
            self.curve.render_levels = self.curve.levels = enter_value_validation(self.enter_value, keys)[1]
            self.end_of_adjustment()
            callback.append('STOP_ADJUSTMENT')

        if keys['value'] == 'PRESS' and keys['type'] == 'LEFTMOUSE':
            self.end_of_adjustment()
            callback.append('STOP_ADJUSTMENT')

        if (keys['value'] == 'PRESS' and keys['type'] in {'DEL', 'BACK_SPACE'}):
            hideModifier(self.curve)
            hideModifier(self.obj.modifiers[fluent_modifiers_name['curve_triangulate']])
            hideModifier(self.obj.modifiers[fluent_modifiers_name['curve_decimate']])
            self.end_of_adjustment()
            callback.append('STOP_ADJUSTMENT')


        # TEXT
        screen_text.append(['Curve', ''])
        screen_text.append(['Subdivisions', adjustment_value(self.curve.levels, self.enter_value)])
        screen_text.append(['Slower/Faster', 'Shift/Ctrl'])
        screen_text.append(['Remove', 'Del'])

        return callback, screen_text


class path_height_management():
    def __init__(self, obj):
        self.obj = obj
        self.screw = None
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = None
        self.bool_obj_location = [0, 0, 0]
        self.backup = None
        self.init = False

        # menu
        self.ui_items_list = []
        self.action = None
        self.pie_menu = FLUENT_Ui_Layout('PATH_HEIGHT')
        self.pie_menu.set_layout('PIE')

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

    def get_pie_menu(self):
        return self.pie_menu

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_modifier(self):
        return self.screw

    def initiation(self):
        ok = 0
        for m in self.obj.modifiers:
            if m.name == fluent_modifiers_name['path_height'] and m.type == 'SCREW':
                self.screw = m
                ok+=1
            if m.name == fluent_modifiers_name['path_displace'] and m.type == 'DISPLACE':
                ok+=1
            if ok == 2:
                break
        if ok==2:
            return True
        else:
            return False

    def make_backup(self):
        self.backup = get_modifier_values(self.screw)

    def restore(self):
        set_modifier_value(self.screw, self.backup)

    def end_of_adjustment(self):
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = None
        self.bool_obj_location = [0, 0, 0]
        self.init = False

    def add_screw(self):
        self.initiation()
        if not self.screw:
            displace = self.obj.modifiers.new(name=fluent_modifiers_name['path_displace'], type='DISPLACE')
            displace.direction = 'Z'
            displace.strength = 0.01
            modif = self.screw = self.obj.modifiers.new(name=fluent_modifiers_name['path_height'], type='SCREW')
            modif.merge_threshold = 0.0001
            modif.angle = 0
            modif.axis = 'Z'
            modif.steps = 1
            modif.use_normal_calculate = True
            modif.render_steps = 1
            modif.show_expanded = False
            # decimate = self.obj.modifiers.new(name=fluent_modifiers_name['path_decimate'], type='DECIMATE')
            # decimate.decimate_type = 'DISSOLVE'
            place_in_stack(self.obj, displace)
            place_in_stack(self.obj, modif)
            # place_in_stack(self.obj, decimate)

    def adjust(self, keys, tool_called = None):
        callback = []
        screen_text = []

        self.enter_value = enter_value(self.enter_value, keys)

        if not self.init:
            self.previous_value = self.screw.screw_offset
            self.original_value = self.screw.screw_offset
            self.slider_origin = keys['mouse_x']
            self.bool_obj_location[0] = self.obj.location.x
            self.bool_obj_location[1] = self.obj.location.y
            self.bool_obj_location[2] = self.obj.location.z
            self.make_backup()
            self.init = True

        if keys['shift_work']:
            increment = 3000
        elif keys['ctrl_work']:
            increment = 30
        else:
            increment = 300

        if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
            self.slider_origin = keys['mouse_x']
            self.previous_value = self.screw.screw_offset

        if keys['type'] == 'MOUSEMOVE' and not keys['mouse_left_click']:
            self.screw.screw_offset = self.previous_value + ((keys['mouse_x'] - self.slider_origin)/increment)

        if enter_value_validation(self.enter_value, keys)[0]:
            self.screw.screw_offset = enter_value_validation(self.enter_value, keys)[1]
            callback.append('STOP_ADJUSTMENT')
            self.end_of_adjustment()

        if keys['value'] == 'PRESS' and keys['type'] == 'V':
            self.screw.screw_offset = max(self.obj.dimensions[0] * 1.414, self.obj.dimensions[1] * 1.414, self.obj.dimensions[2] * 1.414) * (-1)

        if self.screw.screw_offset > 0:
            callback.append('BOOL_UNION')
        elif  self.screw.screw_offset < 0:
            callback.append('BOOL_DIFFERENCE')

        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            self.restore()
            self.end_of_adjustment()
            callback.append('STOP_ADJUSTMENT')
            callback.append('DO_NOT_QUIT_FLUENT')

        # TEXT
        screen_text.append(['DEPTH/HEIGHT ADJUSTMENT', adjustment_value(self.screw.screw_offset, self.enter_value)])
        screen_text.append(['Slower/Faster', 'Shift/Ctrl'])

        self.action = None
        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    self.end_of_adjustment()
                    screen_text = []
                    callback.append('STOP_ADJUSTMENT')

        return callback, screen_text


class inset_management():
    def __init__(self, obj, inset_obj):
        self.obj = obj
        self.inset_obj = inset_obj
        self.solidify = None
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = None
        self.init = False

        # menu
        self.ui_items_list = []
        self.pie_menu = None
        self.action = None
        self.pie_menu = FLUENT_Ui_Layout('FIRST_SOLIDIFY')
        self.pie_menu.set_layout('PIE')

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        # button = FLUENT_Ui_Button()
        # button.set_text('Offset')
        # button.set_shape('RECTANGLE')
        # button.set_action('OFFSET')
        # self.pie_menu.add_item(button)
        # self.ui_items_list.append(button)
        #
        # button = FLUENT_Ui_Button()
        # button.set_text('Thickness')
        # button.set_shape('RECTANGLE')
        # button.set_action('THICKNESS')
        # self.pie_menu.add_item(button)
        # self.ui_items_list.append(button)
        #
        # button = FLUENT_Ui_Button()
        # button.set_text('Cross (V)')
        # button.set_shape('RECTANGLE')
        # button.set_action('CROSS')
        # self.pie_menu.add_item(button)
        # self.ui_items_list.append(button)

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def get_modifier(self):
        return self.solidify

    def initiation(self):
        for m in self.inset_obj.modifiers:
            if m.name == fluent_modifiers_name['inset_solidify'] and m.type == 'SOLIDIFY':
                self.solidify = m
        return self.solidify

    def end_of_adjustment(self):
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = None
        self.init = False

    def add_inset(self):
        self.initiation()
        if not self.solidify:
            self.solidify = self.inset_obj.modifiers.new(name=fluent_modifiers_name['inset_solidify'], type='SOLIDIFY')
            self.solidify.show_expanded = False

    def adjust(self, keys):
        callback = []
        screen_text = []

        self.enter_value = enter_value(self.enter_value, keys)

        if not self.init:
            self.previous_value = self.solidify.thickness
            self.original_value = self.solidify.thickness
            self.slider_origin = keys['mouse_x']
            self.init = True

        if keys['shift_work']:
            increment = 3000
        elif keys['ctrl_work']:
            increment = 30
        else:
            increment = 500

        if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
            self.slider_origin = keys['mouse_x']
            self.previous_value = self.solidify.thickness

        if keys['type'] == 'MOUSEMOVE' and not keys['mouse_left_click']:
            self.solidify.thickness = self.previous_value - ((keys['mouse_x'] - self.slider_origin)/increment)
            if self.solidify.thickness < 0:
                callback.append('INSET_ADD')
            else:
                callback.append('INSET_DIFF')

        if enter_value_validation(self.enter_value, keys)[0]:
            self.solidify.thickness = enter_value_validation(self.enter_value, keys)[1]
            self.end_of_adjustment()
            callback.append('STOP_ADJUSTMENT')

        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            self.solidify.thickness = self.original_value
            self.end_of_adjustment()
            callback.append('STOP_ADJUSTMENT')
            callback.append('DO_NOT_QUIT_FLUENT')

        # TEXT
        screen_text.append(['Thickness', adjustment_value(self.solidify.thickness, self.enter_value)])
        screen_text.append(['Slower/Faster', 'Shift/Ctrl'])

        self.action = None
        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    self.end_of_adjustment()
                    screen_text = []
                    callback.append('STOP_ADJUSTMENT')
                else:
                    self.slider_origin = keys['mouse_x']

        return callback, screen_text


class scale_management():
    def __init__(self, obj):
        self.obj = obj
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = None
        self.scale = None
        self.init = False
        self.array_axis = ''

        # affichage
        self.ui_items_list = []
        self.pie_menu = None
        self.action = None
        self.dots = None

        self.pie_menu = FLUENT_Ui_Layout('SCALE')
        self.pie_menu.set_layout('TAPER')
        self.pie_menu.set_obj(self.obj)

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+X')
        button.set_default_color((.9, 0, 0, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+Y')
        button.set_default_color((0, .9, 0, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def initiation(self):
        for m in self.obj.modifiers:
            if m.name == fluent_modifiers_name['scale'] and m.type == 'NODES':
                self.scale = m
        return self.scale

    def get_modifier(self):
        return self.scale

    def end_of_adjustment(self):
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = {
            'x':None,
            'y':None,
            'x':None,
            'y':None
        }
        self.init = False
        self.array_axis = ''

    def restore_value(self):
        self.scale.node_group.nodes['Transform'].inputs[3].default_value[0] = self.original_value['x']
        self.scale.node_group.nodes['Transform'].inputs[3].default_value[1] = self.original_value['y']

    def add_modifier(self):
        self.initiation()
        if not self.scale:
            self.scale = self.obj.modifiers.new(name=fluent_modifiers_name['scale'], type='NODES')
            node_group = bpy.data.node_groups.new(name='Scale_Rotation', type='GeometryNodeTree')
            node_group.nodes.new(type='NodeGroupInput')
            node_group.nodes.new(type='NodeGroupOutput')
            self.scale.node_group = node_group
            tree = self.scale.node_group
            nodes = tree.nodes
            link = tree.links.new
            node_transform = nodes.new(type='GeometryNodeTransform')
            node_transform.name = 'Transform'
            for n in nodes:
                if n.type == 'GROUP_INPUT':
                    group_in = n
                if n.type == 'GROUP_OUTPUT':
                    group_out = n
            link(group_in.outputs[0], node_transform.inputs[0])
            link(node_transform.outputs[0], group_out.inputs[0])
            place_in_stack(self.obj, self.scale)
        return self.scale

    def adjust_modifier(self, keys):
        callback = []
        screen_text = []
        self.enter_value = enter_value(self.enter_value, keys)

        if not self.init:
            # bpy.ops.object.modifier_move_to_index(modifier=self.scale.name, index=0)
            self.original_value = {
                'x':self.scale.node_group.nodes['Transform'].inputs[3].default_value[0],
                'y':self.scale.node_group.nodes['Transform'].inputs[3].default_value[1]
            }
            self.previous_value = {
                'x':self.scale.node_group.nodes['Transform'].inputs[3].default_value[0],
                'y':self.scale.node_group.nodes['Transform'].inputs[3].default_value[1]
            }
            self.init = True

        if keys['shift_work']:
            increment = 3000
        elif keys['ctrl_work']:
            increment = 30
        else:
            increment = 500

        if self.array_axis and keys['value'] == 'PRESS' and keys['type'] == 'LEFTMOUSE':
            self.array_axis = None

        if type(self.action) == str and 'X' in self.action:
            self.slider_origin = keys['mouse_x']
            self.previous_value['x'] = self.scale.node_group.nodes['Transform'].inputs[3].default_value[0]
            self.array_axis = 'X'
        elif type(self.action) == str and 'Y' in self.action:
            self.slider_origin = keys['mouse_x']
            self.previous_value['y'] = self.scale.node_group.nodes['Transform'].inputs[3].default_value[1]
            self.array_axis = 'Y'

        if self.array_axis != None:
            if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
                self.slider_origin = keys['mouse_x']
                self.previous_value = {
                    'x':self.scale.node_group.nodes['Transform'].inputs[3].default_value[0],
                    'y':self.scale.node_group.nodes['Transform'].inputs[3].default_value[1],
                }

            if self.array_axis == 'X':
                if enter_value_validation(self.enter_value, keys)[0]:
                    self.scale.node_group.nodes['Transform'].inputs[3].default_value[0] = self.previous_value['x'] = enter_value_validation(self.enter_value, keys)[1]
                    self.enter_value = 'None'
                elif keys['type'] == 'MOUSEMOVE' and not keys['mouse_left_click']:
                    self.scale.node_group.nodes['Transform'].inputs[3].default_value[0] = self.previous_value['x'] + (keys['mouse_x'] - self.slider_origin)/increment
                elif keys['value'] == 'PRESS' and keys['type'] == 'ESC':
                    self.restore_value()
                    callback.append('DO_NOT_QUIT_FLUENT')
                    self.end_of_adjustment()

            if self.array_axis == 'Y':
                if enter_value_validation(self.enter_value, keys)[0]:
                    self.scale.node_group.nodes['Transform'].inputs[3].default_value[1] = self.previous_value['y'] = enter_value_validation(self.enter_value, keys)[1]
                    self.enter_value = 'None'
                elif keys['type'] == 'MOUSEMOVE':
                    self.scale.node_group.nodes['Transform'].inputs[3].default_value[1] = self.previous_value['y'] + (keys['mouse_x'] - self.slider_origin)/increment

                elif keys['value'] == 'PRESS' and keys['type'] == 'ESC':
                    self.restore_value()
                    callback.append('DO_NOT_QUIT_FLUENT')
                    self.end_of_adjustment()

        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            try:
                self.restore_value()
            except:pass
            self.end_of_adjustment()
            callback.append('DO_NOT_QUIT_FLUENT')
            callback.append('STOP_ADJUSTMENT')

        # TEXT
        screen_text.append(['Slower/Faster', 'Shift/Ctrl'])

        self.action = None
        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    self.end_of_adjustment()
                    screen_text = []
                    callback.append('STOP_ADJUSTMENT')
                else:
                    self.slider_origin = keys['mouse_x']

        return callback, screen_text


class rotation_management():
    def __init__(self, obj):
        self.obj = obj
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = None
        self.rotate = None
        self.init = False
        self.array_axis = ''

        # affichage
        self.ui_items_list = []
        self.pie_menu = None
        self.action = None
        self.dots = None

        self.pie_menu = FLUENT_Ui_Layout('SCALE')
        self.pie_menu.set_layout('TAPER')
        self.pie_menu.set_obj(self.obj)

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+X')
        button.set_default_color((.9, 0, 0, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+Y')
        button.set_default_color((0, .9, 0, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('')
        button.set_shape('CIRCLE')
        button.set_action('+Z')
        button.set_default_color((0, 0, .9, 1))
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def initiation(self):
        for m in self.obj.modifiers:
            if m.name == fluent_modifiers_name['scale'] and m.type == 'NODES':
                self.rotate = m
        return self.rotate

    def get_modifier(self):
        return self.rotate

    def end_of_adjustment(self):
        self.slider_origin = None
        self.previous_value = None
        self.enter_value = 'None'
        self.original_value = {'axis':None, 'factor':None, 'lock_x':None, 'lock_y':None, 'lock_z':None}
        self.init = False
        self.array_axis = ''

    def restore_value(self):
        self.rotate.node_group.nodes['Transform'].inputs[2].default_value[0] = self.original_value['r_x']
        self.rotate.node_group.nodes['Transform'].inputs[2].default_value[1] = self.original_value['r_y']
        self.rotate.node_group.nodes['Transform'].inputs[2].default_value[2] = self.original_value['r_z']

    def add_modifier(self):
        self.initiation()
        if not self.rotate:
            self.rotate = self.obj.modifiers.new(name=fluent_modifiers_name['scale'], type='NODES')
            node_group = bpy.data.node_groups.new(name='Scale_Rotation', type='GeometryNodeTree')
            node_group.nodes.new(type='NodeGroupInput')
            node_group.nodes.new(type='NodeGroupOutput')
            self.rotate.node_group = node_group
            tree = self.rotate.node_group
            nodes = tree.nodes
            link = tree.links.new
            node_transform = nodes.new(type='GeometryNodeTransform')
            node_transform.name = 'Transform'
            for n in nodes:
                if n.type == 'GROUP_INPUT':
                    group_in = n
                if n.type == 'GROUP_OUTPUT':
                    group_out = n
            link(group_in.outputs[0], node_transform.inputs[0])
            link(node_transform.outputs[0], group_out.inputs[0])
            place_in_stack(self.obj, self.rotate)
        return self.rotate

    def adjust_modifier(self, keys):
        callback = []
        screen_text = []
        self.enter_value = enter_value(self.enter_value, keys)

        if not self.init:
            self.original_value = {
                'r_x':self.rotate.node_group.nodes['Transform'].inputs[2].default_value[0],
                'r_y':self.rotate.node_group.nodes['Transform'].inputs[2].default_value[1],
                'r_z':self.rotate.node_group.nodes['Transform'].inputs[2].default_value[2]
            }
            self.previous_value = {
                'r_x':self.rotate.node_group.nodes['Transform'].inputs[2].default_value[0],
                'r_y':self.rotate.node_group.nodes['Transform'].inputs[2].default_value[1],
                'r_z':self.rotate.node_group.nodes['Transform'].inputs[2].default_value[2]
            }
            self.init = True

        if keys['shift_work']:
            increment = 3000
        elif keys['ctrl_work']:
            increment = 30
        else:
            increment = 300

        if self.array_axis and keys['value'] == 'PRESS' and keys['type'] == 'LEFTMOUSE':
            self.array_axis = None

        if type(self.action) == str and 'X' in self.action:
            self.slider_origin = keys['mouse_x']
            self.previous_value['x'] = self.rotate.node_group.nodes['Transform'].inputs[2].default_value[0]
            self.array_axis = 'X'
        elif type(self.action) == str and 'Y' in self.action:
            self.slider_origin = keys['mouse_x']
            self.previous_value['y'] = self.rotate.node_group.nodes['Transform'].inputs[2].default_value[1]
            self.array_axis = 'Y'
        elif type(self.action) == str and 'Z' in self.action:
            self.slider_origin = keys['mouse_x']
            self.previous_value['r_z'] = self.rotate.node_group.nodes['Transform'].inputs[2].default_value[2]
            self.array_axis = 'Z'

        if self.array_axis != None:
            if keys['ctrl_work']:
                snap = math.radians(45)
            else:
                snap = math.radians(5)

            if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
                self.slider_origin = keys['mouse_x']
                self.previous_value = {
                    'r_x':self.rotate.node_group.nodes['Transform'].inputs[2].default_value[0],
                    'r_y':self.rotate.node_group.nodes['Transform'].inputs[2].default_value[1],
                    'r_z':self.rotate.node_group.nodes['Transform'].inputs[2].default_value[2]
                }

            if self.array_axis == 'X':
                if enter_value_validation(self.enter_value, keys)[0]:
                    self.rotate.node_group.nodes['Transform'].inputs[2].default_value[0] = self.previous_value['x'] = enter_value_validation(self.enter_value, keys)[1]
                    self.enter_value = 'None'
                if keys['type'] == 'MOUSEMOVE' and not keys['mouse_left_click']:
                    self.rotate.node_group.nodes['Transform'].inputs[2].default_value[0] = snap_slider_value(self.previous_value['r_x'], snap) + snap_slider_value((keys['mouse_x'] - self.slider_origin)/increment, snap)

            elif self.array_axis == 'Y':
                if enter_value_validation(self.enter_value, keys)[0]:
                    self.rotate.node_group.nodes['Transform'].inputs[2].default_value[1] = self.previous_value['y'] = enter_value_validation(self.enter_value, keys)[1]
                    self.enter_value = 'None'
                if keys['type'] == 'MOUSEMOVE' and not keys['mouse_left_click']:
                    self.rotate.node_group.nodes['Transform'].inputs[2].default_value[1] = snap_slider_value(self.previous_value['r_y'], snap) + snap_slider_value((keys['mouse_x'] - self.slider_origin)/increment, snap)
            elif self.array_axis == 'Z':
                if enter_value_validation(self.enter_value, keys)[0]:
                    self.rotate.node_group.nodes['Transform'].inputs[2].default_value[2] = self.previous_value['r_z'] = enter_value_validation(self.enter_value, keys)[1]
                    self.enter_value = 'None'
                if keys['type'] == 'MOUSEMOVE' and not keys['mouse_left_click']:
                    self.rotate.node_group.nodes['Transform'].inputs[2].default_value[2] = snap_slider_value(self.previous_value['r_z'], snap) + snap_slider_value((keys['mouse_x'] - self.slider_origin)/increment, snap)

            if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
                self.restore_value()
                callback.append('DO_NOT_QUIT_FLUENT')

        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            self.restore_value()
            callback.append('STOP_ADJUSTMENT')
            callback.append('DO_NOT_QUIT_FLUENT')
            self.end_of_adjustment()

        # TEXT
        screen_text.append(['Angle : ', adjustment_value(
            math.degrees(self.rotate.node_group.nodes['Transform'].inputs[2].default_value[0]),
            self.enter_value) + ' / ' + adjustment_value(
            math.degrees(self.rotate.node_group.nodes['Transform'].inputs[2].default_value[1]),
            self.enter_value) + ' / ' + adjustment_value(
            math.degrees(self.rotate.node_group.nodes['Transform'].inputs[2].default_value[2]),
            self.enter_value)])
        screen_text.append(['45° snap', 'HOLD CTRL'])
        if self.array_axis != None:
            screen_text.append(['Validate', 'LEFT CLICK'])
        screen_text.append(['Slower/Faster', 'Shift/Ctrl'])

        self.action = None
        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    self.end_of_adjustment()
                    screen_text = []
                    callback.append('STOP_ADJUSTMENT')
                else:
                    self.slider_origin = keys['mouse_x']

        return callback, screen_text


class outer_bevel_management():
    def __init__(self, bevel):
        self.slider_origin = None
        self.previous_value = None
        self.other_adjustment = 'WIDTH'
        self.enter_value = 'None'
        self.original_value = None
        self.init = False
        self.bevels = bevel # tableau contenant toutes les class outer bevel

        # menu
        self.ui_items_list = []
        self.pie_menu = None
        self.action = None
        self.pie_menu = FLUENT_Ui_Layout('OUTER_BEVEL')
        self.pie_menu.set_layout('PIE')

        button = make_button('VALIDATE')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Width')
        button.set_shape('RECTANGLE')
        button.set_action('WIDTH')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

        button = FLUENT_Ui_Button()
        button.set_text('Angle limit')
        button.set_shape('RECTANGLE')
        button.set_action('ANGLE_LIMIT')
        self.pie_menu.add_item(button)
        self.ui_items_list.append(button)

    def get_ui_items_list(self):
        return self.ui_items_list

    def get_pie_menu(self):
        return self.pie_menu

    def end_of_adjustment(self):
        self.slider_origin = None
        self.previous_value = None
        self.other_adjustment = 'WIDTH'
        self.enter_value = 'None'
        self.original_value = None
        self.init = False

    def adjust(self, keys):
        self.enter_value = enter_value(self.enter_value, keys)

        callback = []

        if not self.init:
            self.slider_origin = keys['mouse_x']
            self.previous_value = self.bevels[0].get_width()
            self.original_value = self.bevels[0].get_width()
            self.init = True

        if self.action == 'WIDTH':
            self.other_adjustment = 'WIDTH'
            self.previous_value = self.bevels[0].get_width()
        elif self.action == 'ANGLE_LIMIT':
            self.other_adjustment = 'ANGLE_LIMIT'
            self.previous_value = self.bevels[0].get_angle_limit()

        if keys['shift_work']:
            increment = 5000
        elif keys['ctrl_work']:
            increment = 50
        else:
            increment = 500

        if keys['shift_press'] or keys['shift_release'] or keys['ctrl_press'] or keys['ctrl_release']:
            self.slider_origin = keys['mouse_x']
            if self.other_adjustment == 'WIDTH':
                self.previous_value = self.bevels[0].get_width()
            if self.other_adjustment == 'ANGLE_LIMIT':
                self.previous_value = self.bevels[0].get_angle_limit()

        if keys['type'] == 'MOUSEMOVE':
            if self.other_adjustment == 'WIDTH' and not keys['mouse_left_click']:
                for b in self.bevels:
                    b.set_width(self.previous_value + ((keys['mouse_x'] - self.slider_origin) / increment))
            if self.other_adjustment == 'ANGLE_LIMIT' and not keys['mouse_left_click']:
                for b in self.bevels:
                    b.set_angle_limit(self.previous_value + ((keys['mouse_x'] - self.slider_origin) / increment))
        if enter_value_validation(self.enter_value, keys)[0]:
            if self.other_adjustment == 'WIDTH':
                for b in self.bevels:
                    b.set_width(enter_value_validation(self.enter_value, keys)[1])
            if self.other_adjustment == 'ANGLE_LIMIT':
                for b in self.bevels:
                    b.set_angle_limit(enter_value_validation(self.enter_value, keys)[1])
            callback.append('STOP_ADJUSTMENT')
            self.end_of_adjustment()


        if keys['value'] == 'PRESS' and keys['type'] == 'ESC':
            try:
                for b in self.bevels:
                    b.set_width(self.original_value)
            except:
                pass
            self.end_of_adjustment()
            callback.append('DO_NOT_QUIT_FLUENT')
            callback.append('STOP_ADJUSTMENT')
        # TEXT
        screen_text = []
        screen_text.append(['Width', adjustment_value(self.bevels[0].get_width(), self.enter_value)])
        screen_text.append(['Angle limit', adjustment_value(math.degrees(self.bevels[0].get_angle_limit()), self.enter_value)])

        self.action = None
        for i in self.ui_items_list:
            i.is_hover(keys)
            if i.get_state() == 2:
                self.action = i.get_action()
                i.set_state(0)
                if self.action == 'VALIDATE':
                    screen_text = []
                    self.end_of_adjustment()
                    callback.append('STOP_ADJUSTMENT')
                else:
                    self.slider_origin = keys['mouse_x']

        return callback, screen_text