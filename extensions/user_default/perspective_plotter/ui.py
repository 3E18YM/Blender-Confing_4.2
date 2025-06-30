# -*- coding:utf-8 -*-
from .iBlender_perspective_plotter import _z

import bpy
from bpy.types import Panel
from bpy.utils import register_class, unregister_class

from . import operators, util

import textwrap

def checkCamera(context):
    camera_obj = util.get_camera(context, context.region)
    return len(util.get_valid_regions(context, camera_obj)) != 0

class PERSPECTIVEPLOTTER_PT_GeneralPanel(bpy.types.Panel):
    """Perspective Plotter
Perspective Plotter Object Panel"""
    bl_idname = "PERSPECTIVEPLOTTER_PT_GeneralPanel"
    bl_label = _z("Perspective Plotter")
    bl_category = _z("P.Plotter")
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    
    @classmethod
    def poll(self, context):
        addon_prefs = context.preferences.addons[__package__].preferences
        if addon_prefs.hide_panel_in_normal_view:
            return checkCamera(context)
        return True

    def draw_header_preset(self, context):
        layout = self.layout
        row = layout.row()
        props = row.operator("mesh.ppplot_open_help_url", icon='QUESTION', text="")
        props.url = "https://perspective-plotter.readthedocs.io/"
        props.description = "Open Perspective Plotter Documentation"

        row.operator('wm.url_open', text = '', icon = 'QUESTION').url = "https://www.bilibili.com/video/BV1w34y1474r/"
        row.operator('wm.url_open', text = '', icon = 'GHOST_ENABLED').url = "http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=LOP7dt3N9TrKLQTzU0hO_rgqr_rOl8sb&authKey=iOM7p2Juuj%2BURJffZXBYNhSfdnb9TPjI5mAG1um2h8KSJJj1hsLNxFL%2BiyY%2BjgOu&noverify=0&group_code=242343175"
        row.operator('wm.url_open', text = '', icon = 'HOME').url = "https://shop344526458.taobao.com"


    def draw(self, context):
        pass



    def draw(self, context):

        from . import __package__ as base_package
        addon_prefs = context.preferences.addons[base_package].preferences

        layout = self.layout
        box = layout.box()
        box.prop(addon_prefs, 'language', expand=False)

        layout = self.layout
        col = layout.column()
        
        col.enabled = self.poll(context)

        camera_obj = util.get_camera(context, context.region)

        if not camera_obj:
            col.alert = True
            col.label(text=_z("No Camera Found"))
            return

        if camera_obj and not camera_obj.perspective_plotter.is_valid:
            alert_col = col.column(align=True)
            alert_col.alignment = 'CENTER'
            alert_col.alert=True
            # an_row.label(text="Invalid Configuration")
            text = _z("Invalid Configuration")
            alert_col.operator("mesh.ppplot_open_help_url", icon='ERROR', text=_z("Invalid Configuration"), emboss=False).url = "https://perspective-plotter.readthedocs.io/en/latest/troubleshooting.html#invalid-configuration"

        if camera_obj and camera_obj.perspective_plotter.error_message:
            wrapp = textwrap.TextWrapper(width=30)

            wList = wrapp.wrap(text=camera_obj.perspective_plotter.error_message) 

            error_col = col.column(align=True)
            error_col.alignment = 'CENTER'
            error_col.alert=True
            for text in wList: 
                error_row = error_col.row()
                error_row.alignment = 'CENTER'
                error_row.label(text=text)

        box = col.box()
        box_col = box.column()

        operator_id = None
        text = None
        if checkCamera(context):
            operator_id = 'view3d.perspective_plotter' if not camera_obj.perspective_plotter.running_uuid else 'view3d.perspective_plotter_cancel'
            text = _z("Plotting...") if camera_obj.perspective_plotter.running_uuid else _z("Plot Perspective")
        else:
            operator_id = 'view3d.pp_switch_to_camera'
            text = _z("Plot Perspective")
        box_col.operator(operator_id, depress=camera_obj.perspective_plotter.running_uuid != '', text=text, icon='GRID',)



        box_col_props = box_col.column()
        box_col_props_row = box_col_props.split(factor=0.7)
        box_col_props_row.label(text=_z("Vanishing Points: "))
        box_col_props_row.prop(camera_obj.perspective_plotter, 'vanishing_point_num', text="")

        box_col_props_row = box_col_props.split(factor=0.8)
        box_col_props_row.label(text=_z("Update Camera: "))
        box_col_props_row.alignment="RIGHT"
        box_col_props_row2 = box_col_props_row.row()
        box_col_props_row2.alignment="RIGHT"
        box_col_props_row2.prop(camera_obj.perspective_plotter, 'is_camera_sync', text="")

_measure_icon = "FIXED_SIZE" if bpy.app.version >= (3, 0, 0) else "ORIENTATION_VIEW"
class PERSPECTIVEPLOTTER_PT_Parameters(Panel):
    bl_space_type = 'VIEW_3D'
    bl_label = _z('Parameters')
    bl_description = 'Parameters'
    bl_region_type = 'UI'
    bl_category = _z("P.Plotter")
    bl_idname = "PERSPECTIVEPLOTTER_PT_Parameters"
    bl_parent_id = 'PERSPECTIVEPLOTTER_PT_GeneralPanel'
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        layout = self.layout
        col = layout.column()


        camera_obj = util.get_camera(context, context.region)

        if not camera_obj:
            return
        
        box = col.box()
        box_col = box.column()
        box_col_props = box_col.column(align=True)

        box_col_props.enabled = camera_obj.perspective_plotter.running_uuid != ''

        box_col_props.label(text=_z("Focal Length:"))
        if int(camera_obj.perspective_plotter.vanishing_point_num) == 1:
            
            box_col_props.prop(camera_obj.perspective_plotter, 'one_point_focal_length', text="") 
        else:
            box_col_props_lens = box_col_props.column(align=True)
            box_col_props_lens.alignment = 'CENTER'
            box_col_props_lens_row = box_col_props.row(align=True)
            box_col_props_lens_row.alignment = 'CENTER'
            box_col_props_lens_row.label(text=str(round(camera_obj.data.lens, 2)) + ' mm')
            
        box_col_props.separator()
        box_col_props.label(text=_z("Reference Distance:"))
        box_col_props.prop(camera_obj.perspective_plotter, 'ref_distance_mode', text="")

        
        box_col_props_box = box_col_props.box()
        box_col_props_box_col = box_col_props_box.column(align=True)

        global _measure_icon
        if camera_obj.perspective_plotter.ref_distance_mode == 'camera_distance':
            box_col_props_box_col.label(text=_z("Camera Distance: "))
            box_col_props_box_col.prop(camera_obj.perspective_plotter, 'camera_distance', text="")
        elif camera_obj.perspective_plotter.ref_distance_mode != 'camera_distance':
            box_col_props_box_col.label(text=_z("Reference Length: "))
            box_col_props_box_col_row = box_col_props_box_col.split(factor=0.9, align=True)
            box_col_props_box_col_row.prop(camera_obj.perspective_plotter, 'ref_length', text="")
            box_col_props_box_col_row.prop(camera_obj.perspective_plotter, 'is_manual_length_point', text="", icon=_measure_icon)
            
            if camera_obj.perspective_plotter.is_manual_length_point:
                box_col_props_box_col.separator()
                box_col_props_box_col_row = box_col_props_box_col.split(factor=0.1, align=True)
                box_col_props_box_col_row.label(icon=_measure_icon, text="")
                box_col_props_box_col_row.prop(camera_obj.perspective_plotter, 'length_point_a', text="A:")
                box_col_props_box_col_row = box_col_props_box_col.split(factor=0.1, align=True)
                box_col_props_box_col_row.label(icon=_measure_icon, text="")
                box_col_props_box_col_row.prop(camera_obj.perspective_plotter, 'length_point_b', text="B:")

        box_col_props.separator()

        box_col_props.label(text=_z("Vanishing Point 1:"))
        box_col_props.prop(camera_obj.perspective_plotter, 'vp_1_type', text="")

        box_col_props.separator()

        box_col_props.label(text=_z("Vanishing Point 2:"))
        box_col_props.prop(camera_obj.perspective_plotter, 'vp_2_type', text="")

        box_col_props.separator()


        if int(camera_obj.perspective_plotter.vanishing_point_num) < 3:
            box_col_props_pp = box_col_props.column()
            box_col_props_pp.label(text=_z("Principal Point:"))
            box_col_props_pp.prop(camera_obj.perspective_plotter, 'principal_point_mode', text="")
            box_col_props.separator()
            if camera_obj.perspective_plotter.principal_point_mode == 'manual':
                box_col_props_row = box_col_props.split(factor=0.5)
                box_col_props_row_row = box_col_props_row.row(align=True)
                box_col_props_row_row.alignment = 'RIGHT'
                box_col_props_row_row.label(text=_z("Shift X:"))
                box_col_props_row_row = box_col_props_row.row(align=True)
                box_col_props_row_row.alignment = 'CENTER'
                box_col_props_row_row.label(text=str(round(camera_obj.data.shift_x, 3)) )

                box_col_props_row = box_col_props.split(factor=0.5)
                box_col_props_row_row = box_col_props_row.row(align=True)
                box_col_props_row_row.alignment = 'RIGHT'
                box_col_props_row_row.label(text="Y:")
                box_col_props_row_row = box_col_props_row.row(align=True)
                box_col_props_row_row.alignment = 'CENTER'
                box_col_props_row_row.label(text=str(round(camera_obj.data.shift_y, 3)) )
                
                box_col_props.separator()

        box_col_props.label(text=_z("Target Location:"))
        box_col_props.row(align=True).prop(camera_obj.perspective_plotter, 'camera_origin_mode', text="")
        if camera_obj.perspective_plotter.camera_origin_mode == 'manual':
            box_col_props.row(align=True).prop(camera_obj.perspective_plotter, 'camera_offset', text="")
            box_col_props.row(align=True).prop(camera_obj.perspective_plotter, 'camera_rotation', text="")

            box_col_props.operator('view3d.pp_set_target_origin')

        box_col_props.separator()



        box_col_props_row = box_col_props.split(factor=0.8)
        box_col_props_row.label(text=_z("Freeze Guides: "))
        box_col_props_row.alignment="RIGHT"
        box_col_props_row2 = box_col_props_row.row()
        box_col_props_row2.alignment="RIGHT"
        box_col_props_row2.prop(camera_obj.perspective_plotter, 'disable_control_points', text="")

        box_col_props.separator()
        box_col_props.operator('view3d.pp_reset_defaults', text=_z("Reset Defaults"))
        box_col_props.separator()


class PERSPECTIVEPLOTTER_PT_Tools(Panel):
    bl_space_type = 'VIEW_3D'
    bl_label = _z('Tools')
    bl_description = 'Tools'
    bl_region_type = 'UI'
    bl_category = _z("P.Plotter")
    bl_idname = "PERSPECTIVEPLOTTER_PT_Tools"
    bl_parent_id = 'PERSPECTIVEPLOTTER_PT_GeneralPanel'
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        layout = self.layout

        tools_col = layout.column()

        tools_col.operator('view3d.move_along_view', icon='VIEW3D', text=_z("Move Along View"))
        tools_col_match = tools_col.column()
        camera_obj = util.get_camera(context, context.region)
        match_text = _z("Match Background")
        if camera_obj:
            img = util.get_background_image(camera_obj)
            if img and not util.does_img_match(context, img):
                tools_col_match.alert = True
                match_text = _z("Background Unmatched")

        tools_col_match.operator('view3d.pp_match_resolution_to_bg_image', icon='IMAGE_PLANE', text=match_text)
        tools_col.operator('view3d.pp_flatten_horizon_line', text=_z("Flatten Horizon Line"), icon='NOCURVE')

class PERSPECTIVEPLOTTER_PT_Animation(Panel):
    bl_space_type = 'VIEW_3D'
    bl_label = _z('Animation')
    bl_description = 'Animation'
    bl_region_type = 'UI'
    bl_category = _z("P.Plotter")
    bl_idname = "PERSPECTIVEPLOTTER_PT_Animation"
    bl_parent_id = 'PERSPECTIVEPLOTTER_PT_GeneralPanel'
    # bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):

        layout = self.layout

        tools_col = layout.column()

        tools_col.operator('view3d.pp_set_keyframe', text=_z("Set Keyframe"), icon='KEYFRAME_HLT')
        tools_col.operator('view3d.pp_delete_keyframe', text=_z("Delete Keyframe"), icon='KEYFRAME')
        tools_col.operator('view3d.pp_delete_all_keyframes', text=_z("Delete All Keyframes"), icon='X')
        
class PERSPECTIVEPLOTTER_PT_About(Panel):
    bl_space_type = 'VIEW_3D'
    bl_label = _z('Inspired by fSpy')
    bl_description = 'Inspired by fSpy'
    bl_region_type = 'UI'
    bl_category = _z("P.Plotter")
    bl_idname = "PERSPECTIVEPLOTTER_PT_About"
    bl_parent_id = 'PERSPECTIVEPLOTTER_PT_GeneralPanel'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):

        layout = self.layout

        col = layout.column(align=True)

        wrapp = textwrap.TextWrapper(width=30)

        wList = wrapp.wrap(text=_z("fSpy is a free standalone camera matching application which can be used with other 3D tools."))

        msg_col = col.column(align=True)
        msg_col.alignment = 'CENTER'
        for text in wList: 
            msg_row = msg_col.row()
            msg_row.alignment = 'CENTER'
            msg_row.label(text=text)

        col.separator()
        props = col.operator("mesh.ppplot_open_help_url", text=_z("Download fSpy"))
        props.url = "https://item.taobao.com/item.htm?ft=t&id=750873139199"
        props.description = "Go to the fSpy tool website"


classes = [
    PERSPECTIVEPLOTTER_PT_GeneralPanel,
    PERSPECTIVEPLOTTER_PT_Parameters,
    PERSPECTIVEPLOTTER_PT_Tools,
    PERSPECTIVEPLOTTER_PT_Animation,
    PERSPECTIVEPLOTTER_PT_About
    ]


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
