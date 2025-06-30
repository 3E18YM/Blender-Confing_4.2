import bpy
from .lib import *
from .ui import *
def clean_pickers(self, clean_batch=False):
    if clean_batch:
        self.vertices = []
        self.create_batch3d()
    for key in self.pickers.keys():
      self.pickers[key]['status'] = False
      self.pickers[key]['selecting'] = False
def clean_events(self):
    for key in self.events.keys():
      self.events[key]['status'] = False
def get_prefs(self,context):
    if 'Cablerator' not in context.preferences.addons:
        return
    if context.preferences.addons['Cablerator'].preferences is not None:
        self.subdivisions = context.preferences.addons['Cablerator'].preferences.subdivisions
        self.res = context.preferences.addons['Cablerator'].preferences.res
        self.bevel_res = context.preferences.addons['Cablerator'].preferences.bevel_res
        self.random_tension = .6
        try:
            self.right_click = '0' if context.window_manager.keyconfigs.active.preferences.select_mouse == 'LEFT' else '1'
        except:
            try:
                wm = bpy.context.window_manager
                kc = wm.keyconfigs.user
                km = kc.keymaps['Markers']
                kmi = get_hotkey_entry_item(km, 'marker.select', 'none', 'none')
                self.right_click = '0' if kmi.type == 'LEFTMOUSE' else '1'
            except:
                self.right_click = '0'
        FontGlobal.size = context.preferences.addons['Cablerator'].preferences.font_size
        if hasattr(self, 'use_method') and self.use_method == -1 or not hasattr(self, 'use_method'):
            self.twist = int(context.preferences.addons['Cablerator'].preferences.twist)
        else:
            self.twist = self.use_method
        if hasattr(self, 'active_curve'):
            if self.active_curve['width'] is None or self.active_curve['width'] == 0:
                self.active_curve['width'] = context.preferences.addons['Cablerator'].preferences.width
                self.width = context.preferences.addons['Cablerator'].preferences.width
        else:
            self.width = context.preferences.addons['Cablerator'].preferences.width
        if GV.is291:
            self.fill_caps = context.preferences.addons['Cablerator'].preferences.fill_caps
            self.show_fill_caps = context.preferences.addons['Cablerator'].preferences.show_fill_caps
        self.show_res = context.preferences.addons['Cablerator'].preferences.show_res
        self.show_bevel_res = context.preferences.addons['Cablerator'].preferences.show_bevel_res
        self.show_subdivisions = context.preferences.addons['Cablerator'].preferences.show_subdivisions
        self.show_twist = context.preferences.addons['Cablerator'].preferences.show_twist
        self.show_wire = context.preferences.addons['Cablerator'].preferences.show_wire
        self.show_tilt = context.preferences.addons['Cablerator'].preferences.show_tilt
        self.show_offset = context.preferences.addons['Cablerator'].preferences.show_offset
        self.show_curve_length = context.preferences.addons['Cablerator'].preferences.show_length
        self.show_grab_profile = context.preferences.addons['Cablerator'].preferences.show_grab_profile
        self.leave_rmb = context.preferences.addons['Cablerator'].preferences.leave_rmb
        self.cancel_buttons = {'ESC'} if self.leave_rmb else {'RIGHTMOUSE', 'ESC'}
        self.cancel_buttons_ret = {'ESC', 'RET', 'NUMPAD_ENTER'} if self.leave_rmb else {'RIGHTMOUSE', 'ESC', 'RET', 'NUMPAD_ENTER'}
        self.navigation = {'RIGHTMOUSE', 'MIDDLEMOUSE'} if self.leave_rmb else {'MIDDLEMOUSE'}
        self.empty_size = context.preferences.addons['Cablerator'].preferences.empty_size
        self.empties = context.preferences.addons['Cablerator'].preferences.empties
        self.parent_connectors = context.preferences.addons['Cablerator'].preferences.parent_connectors
        self.circle_points = context.preferences.addons['Cablerator'].preferences.circle_points
        self.circle_rad = context.preferences.addons['Cablerator'].preferences.circle_rad
def init_font_settings(self):
    if not FontGlobal.size:
        FontGlobal.size = 13
    temp = get_column_width(self, FontGlobal.font_id, FontGlobal.size, FontGlobal.dpi)
    FontGlobal.LN = get_line(FontGlobal.font_id, FontGlobal.size, FontGlobal.dpi)
    FontGlobal.column_width = temp[0]
    FontGlobal.add_width = temp[1]
    FontGlobal.column_height = get_column_height(self)