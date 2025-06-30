import bpy, math
from ..icons.icons import preview_collections
from ..import camera_presets
from ..operators import resolution
from .. import __package__ as base_package

#### RESOLUTION PANELS ####

def resolution_header_preset(context,layout,use_scene_camera=True):
    row = layout.row(align=True)
    row.alignment = 'RIGHT'
    # Resolution
    if not use_scene_camera:
        settings = context.camera.photographer
        resolution_x = str(int(settings.resolution_x * context.scene.render.resolution_percentage/100))
        resolution_y = str(int(settings.resolution_y * context.scene.render.resolution_percentage/100))
        
    else:
        resolution_x = str(int(context.scene.render.resolution_x * context.scene.render.resolution_percentage/100))
        resolution_y = str(int(context.scene.render.resolution_y * context.scene.render.resolution_percentage/100))
    row.label(text = resolution_x + "x" + resolution_y)

def resolution_header(context, layout, use_scene_camera=True, show_label=False):
    custom_icons = preview_collections["icons"]

    if use_scene_camera:
        cam = context.scene.camera
        settings = cam.data.photographer
    else:
        cam = context.camera
        settings = cam.photographer    
    main_cam = context.scene.photographer.main_camera

    layout.prop(settings, "resolution_enabled", text="Resolution" if show_label else "")
    if main_cam:
        if main_cam != 'NONE':
            if main_cam.photographer != settings:
                if not settings.resolution_enabled:
                    layout.label(text='', icon_value=custom_icons['MAIN_CAMERA'].icon_id)
            else:
                layout.label(text='', icon_value=custom_icons['MAIN_CAMERA'].icon_id)

def resolution_panel(context, settings, layout):

    layout.use_property_split = True
    layout.use_property_decorate = False  # No animation.
    layout.enabled = settings.resolution_enabled

    col = layout.column()
    col.alignment = 'RIGHT'

    col.prop(settings, 'resolution_mode')

    sub = col.column(align=True)

    if settings.resolution_mode == 'CUSTOM_RES':
        sub.prop(settings, "resolution_x", text='Resolution X')
        sub.prop(settings, "resolution_y", text='Y')
        col.row().prop(settings, 'resolution_rotation',expand=True)

    elif settings.resolution_mode == 'CUSTOM_RATIO':
        sub.prop(settings, "ratio_x", text='Ratio X')
        sub.prop(settings, "ratio_y", text='Y')
        sub.separator()
        sub.prop(settings, "longedge")
        col.row().prop(settings, 'resolution_rotation',expand=True)

    else:
        sub.prop(settings, "longedge")
        if not settings.resolution_mode == '11':
            col.row().prop(settings, 'resolution_rotation',expand=True)
    
    col.prop(settings, 'fit_inside_sensor')

def resize_anchor_button(layout,anchors,context,camera):
    for a in anchors:
        row = layout.row()
        icn = 'RADIOBUT_ON' if context.scene.photographer.resize_anchor == a else 'RADIOBUT_OFF'
        op = row.operator("photographer.set_resize_anchor",icon=icn,text='')
        op.anchor=a
        op.camera=camera.name

def resize_canvas_panel(context,layout,use_scene_camera):
    if use_scene_camera:
        camera = context.scene.camera.data
    else:
        camera = context.camera
    settings = camera.photographer
    scene_pg = context.scene.photographer
    warning=layout.row()

    panel = layout.column()

    if camera.sensor_fit == 'AUTO' or settings.fit_inside_sensor:
        panel.enabled = False
        warning.operator('photographer.set_fixed_sensor_fit', icon='INFO',text='Requires a fixed Sensor Fit').use_scene_camera=True
    col = panel.column(align=True)
    row = col.row(align=True)
    row.prop(scene_pg, "resize_mode", text='')
    row.operator('photographer.reset_resize_resolution', text='',icon='FILE_REFRESH').camera=camera.name
    
    if scene_pg.resize_mode == 'PIXEL':
        if settings.resolution_mode == 'CUSTOM_RES':
            col.prop(scene_pg, "resize_resolution_x")
            col.prop(scene_pg, "resize_resolution_y")
        else:
            col.prop(scene_pg, "resize_longedge")
    elif scene_pg.resize_mode == 'PIXEL_OFFSET':
        if settings.resolution_mode == 'CUSTOM_RES':
            col.prop(scene_pg, "resize_offset_x")
            col.prop(scene_pg, "resize_offset_y")
        else:
            col.prop(scene_pg, "resize_offset_longedge")       
    
    ui_scale = 1.7
    col = panel.column(align=True)
    row_top = col.row(align=True)
    row_top.alignment='CENTER'
    row_top.scale_x = row_top.scale_y = ui_scale

    anchors_top = ['TOP_LEFT','TOP','TOP_RIGHT']
    resize_anchor_button(row_top,anchors_top,context,camera)

    row_center = col.row(align=True)
    row_center.scale_x = row_center.scale_y = ui_scale
    row_center.alignment='CENTER'

    anchors_center = ['LEFT','CENTER','RIGHT']
    resize_anchor_button(row_center,anchors_center,context,camera)

    row_bottom = col.row(align=True)
    row_bottom.scale_x = row_bottom.scale_y = ui_scale
    row_bottom.alignment='CENTER'

    anchors_bottom = ['BOTTOM_LEFT','BOTTOM','BOTTOM_RIGHT']
    resize_anchor_button(row_bottom,anchors_bottom,context,camera)


    if scene_pg.resize_stored_anchor and scene_pg.resize_anchor != scene_pg.resize_stored_anchor:
        panel.operator("photographer.revert_resize_canvas", icon='CANCEL').camera=camera.name
    else:
        panel.operator("photographer.resize_canvas").camera=camera.name

class PHOTOGRAPHER_PT_ViewPanel_ResizeCanvas(bpy.types.Panel):
    bl_label = "Resize Canvas (Experimental)"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_parent_id = "PHOTOGRAPHER_PT_ViewPanel_Resolution"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self,context):
        layout = self.layout
        layout.use_property_decorate=False

        resize_canvas_panel(context,layout,use_scene_camera=True)

class PHOTOGRAPHER_PT_Panel_ResizeCanvas(bpy.types.Panel):
    bl_label = "Resize Canvas (Experimental)"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = 'Photographer'
    bl_parent_id = "PHOTOGRAPHER_PT_Panel_Resolution"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self,context):
        layout = self.layout
        layout.use_property_decorate=False

        resize_canvas_panel(context,layout,use_scene_camera=False)

                      
class PHOTOGRAPHER_PT_Panel_Resolution(bpy.types.Panel):

    bl_label = "Resolution"
    bl_parent_id = "PHOTOGRAPHER_PT_Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.camera

    def draw_header_preset(self, context):
        resolution_header_preset(context,self.layout,False)
        camera_presets.PHOTOGRAPHER_PT_ResolutionPresets.draw_panel_header(self.layout)

    def draw_header(self, context):
        resolution_header(context,self.layout,False)

    def draw(self, context):
        settings = context.camera.photographer
        resolution_panel(context,settings,self.layout)

class PHOTOGRAPHER_PT_ViewPanel_Resolution(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = 'Resolution'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 8

    @classmethod
    def poll(cls, context):
        rpe = context.preferences.addons[base_package].preferences.resolution_panel_enable
        return context.scene.camera is not None and context.scene.camera.type == 'CAMERA' and rpe

    def draw_header_preset(self, context):
        if context.preferences.addons[base_package].preferences.show_compact_ui:
            resolution_header_preset(context,self.layout)
        camera_presets.PHOTOGRAPHER_PT_ResolutionPresets.draw_panel_header(self.layout)

    def draw_header(self, context):
        resolution_header(context,self.layout)

    def draw(self, context):
        settings = context.scene.camera.data.photographer
        resolution_panel(context,settings,self.layout)

class PHOTOGRAPHER_PT_ImageEditor_Resolution(bpy.types.Panel):
    bl_category = 'Photographer'
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_label = 'Resolution'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 8

    @classmethod
    def poll(cls, context):
        rpe = context.preferences.addons[base_package].preferences.resolution_panel_enable
        show_image_panels = bpy.context.preferences.addons[base_package].preferences.show_image_panels
        return context.scene.camera and context.scene.camera.type == 'CAMERA' and show_image_panels and rpe
    
    def draw_header_preset(self, context):
        if context.preferences.addons[base_package].preferences.show_compact_ui:
            resolution_header_preset(context,self.layout)
        camera_presets.PHOTOGRAPHER_PT_ResolutionPresets.draw_panel_header(self.layout)

    def draw_header(self, context):
        resolution_header(context,self.layout)

    def draw(self, context):
        settings = context.scene.camera.data.photographer
        resolution_panel(context,settings,self.layout)

class PHOTOGRAPHER_PT_NodeEditor_Resolution(bpy.types.Panel):
    bl_category = 'Photographer'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = 'Resolution'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 8

    @classmethod
    def poll(cls, context):
        rpe = context.preferences.addons[base_package].preferences.resolution_panel_enable
        show_image_panels = context.preferences.addons[base_package].preferences.show_image_panels
        snode = context.space_data
        scene = context.scene
        return scene.camera and scene.camera.type == 'CAMERA' and show_image_panels and rpe and snode.tree_type == 'CompositorNodeTree'
    
    def draw_header_preset(self, context):
        if context.preferences.addons[base_package].preferences.show_compact_ui:
            resolution_header_preset(context,self.layout)
        camera_presets.PHOTOGRAPHER_PT_ResolutionPresets.draw_panel_header(self.layout)

    def draw_header(self, context):
        resolution_header(context,self.layout)

    def draw(self, context):
        settings = context.scene.camera.data.photographer
        resolution_panel(context,settings,self.layout)
