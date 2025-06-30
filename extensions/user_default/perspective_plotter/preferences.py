# -*- coding:utf-8 -*-
from .iBlender_perspective_plotter import _z

import bpy
from bpy.types import AddonPreferences
from bpy.props import FloatVectorProperty, IntProperty, BoolProperty
import os
from bpy.utils import register_class, unregister_class
from .operators import MESH_OT_ProjectMoveOperator
import numpy as np


def addon_name():
    return __package__

class ProjectMovePreferences(AddonPreferences):
    """Custom preferences and associated UI for add on properties."""

    def update_language(self, context):
        try:
            context.preferences.view.language = self.language
            
            if context.preferences.view.language != "en_US":
                context.preferences.view.use_translate_new_dataname = False
        
            bpy.ops.script.reload()
        except Exception as e:
            print("Couldn't parse: {}".format(e))

    if 'zh_CN' in bpy.app.translations.locales:
        language: bpy.props.EnumProperty(
            name = _z("Language"),
            description = _z("Language Description"),
            update = update_language,
            default = bpy.context.preferences.view.language,
            items =  [
                ("en_US", "English", "English"),
                # ("es", "Español", "Spanish"),
                # ("it_IT", "Italiano", "Italian"),
                # ("ja_JP", "日本語", "Japanese"),
                ("zh_CN", "简体中文", "Simplified Chinese"),
                ("zh_TW", "繁體中文", "Traditional Chinese"),
                # ("ru_RU", "русский", "Russian"),
                # ("fr_FR", "Français", "French"),
                # ("de_DE", "Deutsch", "German"),
                # ("ko_KR", "한국어(한국)", "Korean")
                # ('pt_PT', 'Português', 'Portuguese'),
                # ('nl_NL', 'Nederlands', 'Dutch'), 
            ]
        )
    else:
        language: bpy.props.EnumProperty(
            name = _z("Language"),
            description = _z("Language Description"),
            update = update_language,
            default = bpy.context.preferences.view.language,
            items =  [
                ("en_US", "English", "English"),
                # ("es", "Español", "Spanish"),
                # ("it_IT", "Italiano", "Italian"),
                # ("ja_JP", "日本語", "Japanese"),
                ("zh_HANS", "简体中文", "Simplified Chinese"),
                ("zh_HANT", "繁體中文", "Traditional Chinese"),
                # ("ru_RU", "русский", "Russian"),
                # ("fr_FR", "Français", "French"),
                # ("de_DE", "Deutsch", "German"),
                # ("ko_KR", "한국어(한국)", "Korean")
                # ('pt_PT', 'Português', 'Portuguese'),
                # ('nl_NL', 'Nederlands', 'Dutch'), 
            ]
        )
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = addon_name()

    line_color : FloatVectorProperty(name=_z("Preview Line Color"),
                                        subtype='COLOR',
                                        size=4,
                                        default=[1, .5, 0, 0.8], description = "Preview Line Color")

    line_thickness : IntProperty(name=_z("Line thickness"),
                                description="Line thickness\nThickness of perspective lines",
                                default=1,
                                min=0)

    show_axis : BoolProperty(
        name = _z("Display Axis Guides"),
        description="Display Axis Guides\nDisplay Axis Guids when placing",
        default=False)

    x_axis_color : FloatVectorProperty(name=_z("X Axis Line Color"),
                                        subtype='COLOR',
                                        size=4,
                                        default=[1, 0, 0, 0.5], description = "X Axis Line Color")


    y_axis_color : FloatVectorProperty(name=_z("Y Axis Line Color"),
                                        subtype='COLOR',
                                        size=4,
                                        default=[0, 1, 0, 0.5], description = "Y Axis Line Color")


    z_axis_color : FloatVectorProperty(name=_z("Z Axis Line Color"),
                                        subtype='COLOR',
                                        size=4,
                                        default=[0, 0, 1, 0.5], description = "Z Axis Line Color")

    axis_thickness : IntProperty(name=_z("Line thickness"),
                                description="Line thickness\nThickness of perspective line",
                                default=1,
                                min=0)         

    horizon_line_color : FloatVectorProperty(name=_z("Horizon Line Color"),
                                        subtype='COLOR',
                                        size=4,
                                        default=[1, .5, 0, 0.8], description = "Horizon Line Color")


    horizon_line_thickness : IntProperty(name=_z("Line thickness"),
                                description="Line thickness\nThickness of horizon line",
                                default=1,
                                min=0)

    grid_point_color : FloatVectorProperty(name=_z("Grid Point Color"),
                                        subtype='COLOR',
                                        size=4,
                                        default=[1, 1, 1, 0.5], description = "Grid Point Color")

    grid_point_size : IntProperty(name=_z("Grid Point Size"),
                                description="Grid Point Size\nsize of grid point",
                                default=8,
                                min=0)



    principal_point_color : FloatVectorProperty(name=_z("Principal Point Color"),
                                        subtype='COLOR',
                                        size=4,
                                        default=[1, .5, 0, 0.8], description = "Principal Point Color")


    principal_point_size : IntProperty(name=_z("Principal Point thickness"),
                                description="Principal Point thickness\nThickness of Principal Point",
                                default=1,
                                min=0)


    measurement_line_color : FloatVectorProperty(name=_z("Measurement Line Color"),
                                        subtype='COLOR',
                                        size=4,
                                        default=[0, .7, 1, 0.8], description = "Measurement Line Color")


    measurement_line_thickness : IntProperty(name=_z("Line thickness"),
                                description="Line thickness\nThickness of horizon line",
                                default=2,
                                min=0)

    sensitivity_axis_point : IntProperty(
        name=_z("Axis Point Sensitivity"),
        description="Axis Point Sensitivity\nHow close to the Axis Point the mouse needs to be",
        default=10,
        subtype='PIXEL',
        min=0
    )

    sensitivity_grid_point : IntProperty(
        name=_z("Grid Point Sensitivity"),
        description="Grid Point Sensitivity\nHow close to the Grid Point the mouse needs to be",
        default=10,
        subtype='PIXEL',
        min=0
    )

    sensitivity_principal_point : IntProperty(
        name=_z("Principal Point Sensitivity"),
        description="Principal Point Sensitivity\nHow close to the Principal Point the mouse needs to be",
        default=10,
        subtype='PIXEL',
        min=0
    )

    sensitivity_measuring_point : IntProperty(
        name=_z("Measuring Point Sensitivity"),
        description="Measuring Point Sensitivity\nHow close to the Measuring Point the mouse needs to be",
        default=20,
        subtype='PIXEL',
        min=0
    )

    hide_panel_in_normal_view : BoolProperty(
        name=_z("Hide this Panel when not in Camera View"),
        description="Hide this panel tab completely when not in camera view mode for space saving purposes.",
        default=False
    )

    def draw(self, context):

        layout = self.layout
        box = layout.box()       

        box.prop(self, "language")

        box.label(text=_z("Translation is in progress. Whole text isn't translated"))

        row = self.layout.row()
        row.operator("wm.url_open", text=_z("Watch online video tutorials")).url = "https://www.bilibili.com/video/BV1w34y1474r/"
        row.operator("wm.url_open", text=_z("Chat Room")).url = "https://pd.qq.com/s/2des7a5di"
        row.operator("wm.url_open", text=_z("Buy More")).url = "https://mesh.taobao.com/"
        layout = self.layout
        # layout.label(text="Colors:")
        col = layout.column()
        col.alignment = 'CENTER'

        box = col.box()
        box.label(text=_z("General"))
        box_col = box.column(align=True)
        row = box_col.row(align=True)
        row.prop(self, "hide_panel_in_normal_view", text=_z('Hide P.Plotter Panel when not in camera view.'))


        box = col.box()
        box.label(text=_z("Axis Display"))

        

        box_col = box.column(align=True)
        row = box_col.row(align=True)
        row.label(text=_z('X Axis Line Color:'))
        row.prop(self, "x_axis_color", text='')

        row = box_col.row(align=True)
        row.label(text=_z('Y Axis Line Color:'))
        row.prop(self, "y_axis_color", text='')

        row = box_col.row(align=True)
        row.label(text=_z('Z Axis Line Color:'))
        row.prop(self, "z_axis_color", text='')

        row = box_col.row(align=True)
        row.label(text=_z('Axis Thickness:'))
        row.prop(self, "axis_thickness", text='')
        
        box_col.separator()

        row = box_col.row(align=True)
        row.label(text=_z('Horizon Line Color:'))
        row.prop(self, "horizon_line_color", text='')

        row = box_col.row(align=True)
        row.label(text=_z('Horizon Line Thickness:'))
        row.prop(self, "horizon_line_thickness", text='')

        box_col.separator()
        
        row = box_col.row(align=True)
        row.label(text=_z('Grid Point Color:'))
        row.prop(self, "grid_point_color", text='')

        row = box_col.row(align=True)
        row.label(text=_z('Grid Point Size:'))
        row.prop(self, "grid_point_size", text='')

        box_col.separator()

        row = box_col.row(align=True)
        row.label(text=_z('Principal Point Color:'))
        row.prop(self, "principal_point_color", text='')

        row = box_col.row(align=True)
        row.label(text=_z('Principal Point Size:'))
        row.prop(self, "principal_point_size", text='')

        box_col.separator()

        row = box_col.row(align=True)
        row.label(text=_z('Measurement Line Color:'))
        row.prop(self, "measurement_line_color", text='')

        row = box_col.row(align=True)
        row.label(text=_z('Measurement Line Thickness:'))
        row.prop(self, "measurement_line_thickness", text='')

        box = col.box()
        box.label(text=_z("Move Along View"))
        box_col = box.column(align=True)

        kc = context.window_manager.keyconfigs.addon
        km = kc.keymaps['3D View']
        kmis = km.keymap_items
        if MESH_OT_ProjectMoveOperator.bl_idname in km.keymap_items:
            kmi = km.keymap_items[MESH_OT_ProjectMoveOperator.bl_idname]
            row = box_col.row(align=True)
            row.label(text=_z('Keyboard Shortcut:'))
            row.prop(kmi, 'type', text='', full_event=True)
        else:
            col.alert = True
            col = box_col.column()
            row = col.row()
            row.alignment = 'CENTER'
            row.label(text=_z("Hotkey entry not found"))
            col = col.column()
            row = col.row()
            row.alignment = 'CENTER'
            row.label(text=_z("restore hotkeys from Keymap tab"))

            


        row = box_col.row(align=True)
        row.label(text=_z('Line Color:'))
        row.prop(self, "line_color", text='')
        row = box_col.row(align=True)
        row.label(text=_z('Line Thickness:'))
        row.prop(self, "line_thickness", text='')
        row = box_col.row(align=True)
        row.label(text=_z('Show Axis Guides:'))
        row.prop(self, "show_axis", text='')
        
        box = col.box()
        box.label(text=_z("Mouse Sensitivity"))
        box_col = box.column(align=True)


        row = box_col.row(align=True)
        row.label(text=_z('Axis Point Sensitivity:'))
        row.prop(self, "sensitivity_axis_point", text='')

        row = box_col.row(align=True)
        row.label(text=_z('Grid Point Sensitivity:'))
        row.prop(self, "sensitivity_grid_point", text='')

        row = box_col.row(align=True)
        row.label(text=_z('Principal Point Sensitivity:'))
        row.prop(self, "sensitivity_principal_point", text='')

        row = box_col.row(align=True)
        row.label(text=_z('Measuring Point Sensitivity:'))
        row.prop(self, "sensitivity_measuring_point", text='')



classes = [
    ProjectMovePreferences]


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)