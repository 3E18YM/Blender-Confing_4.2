import bpy
import math
from .constants import *
from .independant_helpers import *

class F_outer_bevel():
    def __init__(self, target = None):
        self.target = target
        self.bool_obj = None
        self.current_bevel = None
        self.first_bevel = None
        self.last_bevel = None
        self.previous_bevel = None
        self.weighted_normal = None
        self.bevel_system = get_addon_preferences().bevel_system

    def set_target(self, target):
        self.target = target

    def set_bool_obj(self, bool_obj):
        self.bool_obj = bool_obj

    def get_current_bevel(self):
        return self.current_bevel

    def get_first_bevel(self):
        if not self.first_bevel:
            self.find_first()
        return self.first_bevel

    def get_last(self):
        if not self.last_bevel:
            self.find_last()
        return self.last_bevel

    def get_width(self):
        return self.current_bevel.width

    def get_segments(self):
        return self.current_bevel.segments

    def get_angle_limit(self):
        return self.current_bevel.angle_limit

    def set_angle_limit(self, a):
        self.current_bevel.angle_limit = a

    def set_width(self, b_width=0, same=None, first=False):
        if same:
            self.current_bevel.width = self.previous_bevel.width
            if bpy.context.scene.fluentProp.outer_bevel_segments == 0:
                self.current_bevel.segments = auto_bevel_segments(self.current_bevel)
            else:
                self.current_bevel.segments = bpy.context.scene.fluentProp.outer_bevel_segments
        elif first:
            self.first_bevel.width = b_width
            if bpy.context.scene.fluentProp.outer_bevel_segments == 0:
                self.first_bevel.segments = auto_bevel_segments(self.first_bevel)
            else:
                self.current_bevel.segments = bpy.context.scene.fluentProp.outer_bevel_segments
        else:
            self.current_bevel.width = b_width
            if bpy.context.scene.fluentProp.outer_bevel_segments == 0 and self.current_bevel.segments != 1:
                self.current_bevel.segments = auto_bevel_segments(self.current_bevel)
            else:
                self.current_bevel.segments = auto_bevel_segments(self.current_bevel)
                # self.current_bevel.segments = bpy.context.scene.fluentProp.outer_bevel_segments

    def management(self):
        previous_active_object = active_object(action='GET')
        if self.bevel_system == 'SIMPLE':
            # trouve le dernier bevel et le place à la fin avec le weighted normal
            self.find_last()
            self.wn_check()
            if self.last_bevel:
                if self.target:
                    nb_de_modifier = len(self.target.modifiers)
                    active_object(action='SET', obj=self.target, solo=True)
                    bpy.ops.object.modifier_move_to_index(modifier=self.last_bevel.name, index=nb_de_modifier-1)
                    if not self.weighted_normal:
                        self.wn_add()
                    else:
                        if nb_de_modifier-1>=0:
                            bpy.ops.object.modifier_move_to_index(modifier=self.weighted_normal.name, index=nb_de_modifier-1)
            elif not self.last_bevel and get_addon_preferences().auto_beveled_cut:
                self.add()
        elif self.bevel_system == 'MULTIPLE':
            active_object(action='SET', obj=self.target, solo=True)
            # trouve le dernier booléen
            last_bool = None
            last_bool_index = None
            modif_after_bool = None
            self.weighted_normal = None
            for i, m in enumerate(self.target.modifiers):
                if m.type == 'WEIGHTED_NORMAL':
                    self.weighted_normal = m
                if m.type == 'BOOLEAN':
                    last_bool_index = i
                    modif_after_bool = None
                    try:
                        modif_after_bool = self.target.modifiers[i+1]
                    except:pass
            # ajoute un bevel après le dernier booléen si pas de bevel après
            if modif_after_bool == None or (modif_after_bool and modif_after_bool.type != 'BEVEL'):
                self.find_last()
                self.add(source=self.last_bevel)
                self.current_bevel.angle_limit = math.radians(40)
                try:
                    bpy.ops.object.modifier_move_to_index(modifier=self.current_bevel.name, index=last_bool_index+1)
                except:pass

            # place le weighted normal à fin
            if not self.weighted_normal:
                self.wn_add()
            else:
                bpy.ops.object.modifier_move_to_index(modifier=self.weighted_normal.name, index=len(self.target.modifiers)-1)


        active_object(action='SET', obj=previous_active_object, solo=True)

        # if not self.previous_bevel:
        #     self.find_previous_bevel()
        # if self.previous_bevel and self.current_bevel:
        #     if self.current_bevel.width == self.previous_bevel.width:
        #         self.previous_bevel.show_render = self.previous_bevel.show_viewport = False
        #         self.current_bevel.loop_slide = self.previous_bevel.loop_slide
        #     else:
        #         self.previous_bevel.show_render = self.previous_bevel.show_viewport = True
        # if not self.wn_check() and self.previous_bevel or self.current_bevel:
        #     self.wn_remove()
        #     self.wn_add()
        # if self.current_bevel:
        #     if self.current_bevel.width == 0:
        #         self.current_bevel.show_render = self.current_bevel.show_viewport = False
        #         self.weighted_normal.show_render = self.weighted_normal.show_viewport = False
        #         shade_smooth(self.target, a = False)
        #     else:
        #         self.current_bevel.show_render = self.current_bevel.show_viewport = True
        #         self.weighted_normal.show_render = self.weighted_normal.show_viewport = True
        #         shade_smooth(self.target, a = True)

    def simple_management(self):
        angle_bevel = None
        if self.target:
            for m in self.target.modifiers:
                if m.type == 'BEVEL' and m.limit_method == 'ANGLE' and fluent_modifiers_name['outer_bevel'] in m.name:
                    angle_bevel = m
        if angle_bevel:
            active_object(self.target, 'SET', True)
            self.wn_remove()
            bpy.ops.object.modifier_move_down(modifier=angle_bevel.name)
            bpy.ops.object.modifier_move_down(modifier=angle_bevel.name)
            self.wn_add()
            if angle_bevel.width != 0:
                angle_bevel.show_render = angle_bevel.show_viewport = True
            else:
                angle_bevel.show_render = angle_bevel.show_viewport = False
                self.weighted_normal.show_render = self.weighted_normal.show_viewport = False

    def get_loop_slide(self):
        return self.current_bevel.loop_slide

    def toggle_loop_slide(self):
        self.current_bevel.loop_slide = not self.current_bevel.loop_slide

    def set_loop_slide(self, a):
        self.current_bevel.loop_slide = a

    def toggle_profile(self):
        if self.current_bevel.segments != 1:
            self.current_bevel.segments = 1
        else:
            self.current_bevel.segments = auto_bevel_segments(self.current_bevel)

    def find(self):
        try:
            if self.target and self.bool_obj:
                for i in range(len(self.target.modifiers)):
                    if self.target.modifiers[i].type == 'BOOLEAN' and self.target.modifiers[i].object == self.bool_obj and fluent_modifiers_name['outer_bevel'] in self.target.modifiers[i+1].name:
                        self.current_bevel = self.target.modifiers[i+1]
                        break
                return self.current_bevel
        except:
            return None

    def find_first(self, find_hidden = False):
        for m in self.target.modifiers:
            if fluent_modifiers_name['outer_bevel'] in m.name and m.show_viewport and find_hidden == False:
                self.first_bevel = m
                break
            elif fluent_modifiers_name['outer_bevel'] in m.name and m.show_viewport == False and find_hidden == True:
                self.first_bevel = m
                break
        return self.first_bevel

    def first_as_current(self):
        if not self.first_bevel:
            self.find_first()
        self.current_bevel = self.first_bevel

    def previous_as_current(self):
        self.previous_bevel = self.current_bevel

    def last_as_previous(self):
        if not self.last_bevel:
            self.find_last()
        self.previous_bevel = self.last_bevel

    def last_as_current(self):
        self.current_bevel = self.last_bevel

    def find_last(self, target=None):
        found = False
        if not target: target = self.target
        for m in reversed(target.modifiers):
            if fluent_modifiers_name['outer_bevel'] in m.name:
                self.last_bevel = m
                found = True
                break
        if found:
            return self.last_bevel
        else:
            self.last_bevel = False

    def find_previous_bevel(self, target = None):
        if target == None : target = self.target
        for m in target.modifiers:
            if m.type == 'BOOLEAN' and m.object == self.bool_obj:
                break;
            if fluent_modifiers_name['outer_bevel'] in m.name:
                self.previous_bevel = m

    def find_next_to_bool(self, bool):
        for i, m in enumerate(self.target.modifiers):
            try:
                if m == bool and self.target.modifiers[i+1].type == 'BEVEL':
                    self.current_bevel = self.target.modifiers[i+1]
                    return self.current_bevel
                    break
            except:
                return None

    def add(self, source = None, manage=True):
        if self.previous_bevel and not source:
            pb = self.previous_bevel
            modif = self.target.modifiers.new(name=fluent_modifiers_name['outer_bevel'], type='BEVEL')
            modif.limit_method = pb.limit_method
            modif.angle_limit = pb.angle_limit
            modif.width = pb.width
            modif.segments = pb.segments
            modif.miter_outer = pb.miter_outer
            modif.use_clamp_overlap = pb.use_clamp_overlap
            modif.harden_normals = pb.harden_normals
            modif.show_expanded = pb.show_expanded
            modif.loop_slide = False
        elif source:
            modif = self.target.modifiers.new(name=fluent_modifiers_name['outer_bevel'], type='BEVEL')
            modif.limit_method = source.limit_method
            modif.angle_limit = source.angle_limit
            modif.width = source.width
            modif.segments = source.segments
            modif.miter_outer = source.miter_outer
            modif.use_clamp_overlap = source.use_clamp_overlap
            modif.harden_normals = source.harden_normals
            modif.show_expanded = source.show_expanded
            modif.loop_slide = source.loop_slide
        else:
            modif = self.target.modifiers.new(name=fluent_modifiers_name['outer_bevel'], type='BEVEL')
            modif.limit_method = 'ANGLE'
            modif.angle_limit = math.radians(40)
            modif.width = 0.01
            if bpy.context.scene.fluentProp.outer_bevel_segments == 0:
                modif.segments = auto_bevel_segments(modif)
            else:
                modif.segments = bpy.context.scene.fluentProp.outer_bevel_segments
            modif.miter_outer = 'MITER_ARC'
            modif.use_clamp_overlap = get_addon_preferences().clamp_overlap
            modif.harden_normals = True
            modif.show_expanded = False
            modif.loop_slide = bpy.context.scene.fluentProp.loop_slide
        if self.current_bevel:
            self.previous_bevel = self.current_bevel
        self.current_bevel = modif
        self.target.data.use_auto_smooth = True
        for p in self.target.data.polygons:
            p.use_smooth = True
        if get_addon_preferences().bevel_system == 'SIMPLE':
            self.management()

    def remove(self, m = None):
        bevel_list = []
        if m == 'ALL':
            bevel_list = []
            for modif in self.target.modifiers:
                if fluent_modifiers_name['outer_bevel'] in modif.name:
                    bevel_list.append(modif)
            for b in bevel_list:
                self.target.modifiers.remove(b)
            if self.wn_check():
                self.wn_remove()
                # shade_smooth(self.target, a = False)
        else:
            if m == None or m == 'CURRENT' :
                m = self.current_bevel
            elif m == 'FIRST':
                if not self.first_bevel:
                    self.find_first()
                m = self.first_bevel
            elif m == 'LAST':
                if not self.last_bevel:
                    self.find_last()
                m = self.last_bevel
            if m:
                self.target.modifiers.remove(m)
                if self.wn_check():
                    self.wn_remove()
            self.management()

    def wn_add(self):
        modif = self.target.modifiers.new(name=fluent_modifiers_name['weighted_normal'], type='WEIGHTED_NORMAL')
        modif.show_expanded = False
        self.weighted_normal = modif

    def wn_remove(self):
        for m in self.target.modifiers:
            if m.type == 'WEIGHTED_NORMAL':
                self.target.modifiers.remove(m)
                self.weighted_normal = None
                break

    def wn_check(self):
        find = False
        for m in self.target.modifiers:
            if m.type == 'WEIGHTED_NORMAL':
                find = True
                self.weighted_normal = m
        return find
