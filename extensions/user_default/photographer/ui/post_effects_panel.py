import bpy
from bpy.types import Panel
from .. import camera_presets
from ..icons.icons import preview_collections
from .. import __package__ as base_package

def post_effects_header(context,layout,use_scene_camera=False):
    custom_icons = preview_collections["icons"]

    if use_scene_camera:
        cam = context.scene.camera
        settings = cam.data.post_effects
    else:
        cam = context.camera
        settings = cam.post_effects

    main_cam = context.scene.photographer.main_camera
    layout.prop(settings, "post_effects_enabled", text="")
    if main_cam:
        if main_cam != 'NONE':
            if main_cam.post_effects != settings:
                if not settings.post_effects_enabled:
                    layout.label(text='', icon_value=custom_icons['MAIN_CAMERA'].icon_id)
            else:
                layout.label(text='', icon_value=custom_icons['MAIN_CAMERA'].icon_id)

def post_effects_draw(context,layout,use_scene_camera=False):
    layout.use_property_split = True
    layout.use_property_decorate = False

    scene = context.scene
    if use_scene_camera:
        cam_obj = scene.camera
        cam = cam_obj.data
        post_effects = cam.post_effects
    else:
        cam = context.camera
        cam_obj = cam.id_data
        post_effects = cam.post_effects

    layout.enabled = post_effects.post_effects_enabled

    view = context.space_data
    shading = None
    if bpy.app.version >= (3,5,0):
        if view.type == 'VIEW_3D':
            shading = view.shading
            layout.prop(shading, "use_compositor", text="Viewport Compositing")
            col = layout.column(align=True)
            if shading.use_compositor != 'DISABLED':
                if cam.passepartout_alpha != 1.0:
                    col.operator('photographer.set_passepartout_full',icon='ERROR').camera = scene.camera.name
                # split = layout.split(factor=0.8)
                # split.label(text='Set Zoom for accurate size in Viewport',icon='ERROR')
                col.operator('view3d.zoom_camera_1_to_1', icon='VIEWZOOM', text='Zoom 1:1')

    # Main Column to align boxes together
    main_col = layout.column(align=True)

    # Distortion
    box = main_col.box()
    if bpy.app.version >= (2, 90, 1):
        col = box.column(heading='Distortion')
    else:
        col = box.column()
    col.use_property_decorate = False
    row = col.row(align=True)
    sub = row.row(align=True)
    if bpy.app.version >= (2, 90, 1):
        sub.prop(post_effects, "lens_distortion", text="")
    else:
        sub.prop(post_effects, "lens_distortion", text="Distortion")
    sub = sub.row(align=True)
    sub.active = post_effects.lens_distortion
    sub.prop(post_effects, "lens_distortion_amount", text="", slider=True)
    if post_effects.lens_distortion:
        col = box.column(align=True)
        col.prop(post_effects, "lens_distortion_type", text="Type")
        if post_effects.lens_distortion_type == 'STMAP':
            col.prop(post_effects, "lens_distortion_scale_comp", text="Upscale %")
            col.template_icon_view(post_effects, "stmap_tex", show_labels=True, scale=5)     
        # col.active = settings.lens_distortion

    # Chromatic Aberration
    box = main_col.box()
    if bpy.app.version >= (2, 90, 1):
        col = box.column(heading='Lateral CA')
    else:
        col = box.column()
    col.use_property_decorate = False
    row = col.row(align=True)
    sub = row.row(align=True)
    if bpy.app.version >= (2, 90, 1):
        sub.prop(post_effects, "lateral_ca", text="")
    else:
        sub.prop(post_effects, "lateral_ca", text="Lateral CA")
    sub = sub.row(align=True)
    sub.active = post_effects.lateral_ca
    sub.prop(post_effects, "lateral_ca_amount", text="", slider=True)
    if post_effects.lateral_ca:
        col = box.column(align=True)
        col.prop(post_effects, "lateral_ca_type", text="Type")
        # col.active = settings.lateral_ca

    # Lens Softness
    box = main_col.box()
    if bpy.app.version >= (2, 90, 1):
        col = box.column(heading="Lens Softness")
    else:
        col = box.column()
    col.use_property_decorate = False
    row = col.row(align=True)
    sub = row.row(align=True)
    if bpy.app.version >= (2, 90, 1):
        sub.prop(post_effects, "lens_softness", text="")
    else:
        sub.prop(post_effects, "lens_softness", text="Lens Softness")
    sub = sub.row(align=True)
    sub.active = post_effects.lens_softness
    sub.prop(post_effects, "lens_softness_amount", text="", slider=True)
    if post_effects.lens_softness:
        col = box.column(align=True)
        col.prop(post_effects, "corner_softness_amount")
        col.prop(post_effects, "center_softness_amount", slider=True)
        col.separator()
        col.prop(post_effects, "corner_softness_falloff", slider=True)
        row = col.row(align=True)
        row.prop(post_effects, "corner_mask_width", text="Scale X")
        row.prop(post_effects, "corner_mask_height", text="Y")
        # col.active = settings.lens_softness

    # Fringing
    box = main_col.box()
    if bpy.app.version >= (2, 90, 1):
        col = box.column(heading='Fringing')
    else:
        col = box.column()
    col.use_property_decorate = False
    row = col.row(align=True)
    sub = row.row(align=True)
    if bpy.app.version >= (2, 90, 1):
        sub.prop(post_effects, "fringing", text="")
    else:
        sub.prop(post_effects, "fringing", text="Fringing")
    sub = sub.row(align=True)
    sub.active = post_effects.fringing
    sub.prop(post_effects, "fringing_amount", text="", slider=True)
    if post_effects.fringing:
        col = box.column(align=True)
        col.prop(post_effects, "fringing_size", text="Size")
        col.prop(post_effects, "fringing_threshold", text="Threshold")
        col.prop(post_effects, "fringing_color", text="Color")

    # Bloom
    box = main_col.box()
    if bpy.app.version >= (2, 90, 1):
        col = box.column(heading='Bloom')
    else:
        col = box.column()
    col.use_property_decorate = False
    row = col.row(align=True)
    sub = row.row(align=True)
    if bpy.app.version >= (2, 90, 1):
        sub.prop(post_effects, "bloom", text="")
    else:
        sub.prop(post_effects, "bloom", text="Bloom")
    sub = sub.row(align=True)
    sub.active = post_effects.bloom
    sub.prop(post_effects, "bloom_amount", text="", slider=True)
    if post_effects.bloom:
        col = box.column(align=True)
        col.prop(post_effects, "bloom_type", text="Type")
        if post_effects.bloom_type in {'GLARE','BLOOM'}:
            # Using Glare Node
            if bpy.app.version >= (4,4,0):
                col.prop(post_effects, "bloom_size", text="Size")
                col.prop(post_effects, "bloom_threshold", text="Threshold")
                col.prop(post_effects, "bloom_smoothness", text="Smoothness")
                col.prop(post_effects, "bloom_maximum", text="Maximum")

                col.prop(post_effects, "bloom_saturation", text="Saturation")
                col.prop(post_effects, "bloom_tint", text="Tint")
                col.prop(post_effects, "bloom_quality", text="Quality")
            else:
                col.prop(post_effects, "bloom_glare_size", text="Size")
                col.prop(post_effects, "bloom_threshold", text="Threshold")
                col.prop(post_effects, "bloom_quality", text="Quality")
                col= col.column(align=True)
                col.alignment='RIGHT'
                col.label(text=' Viewport Compositing not supported', icon='INFO')   
        else:
            col.prop(post_effects, "bloom_size", text="Size")
            col.prop(post_effects, "bloom_stretch_ratio", text="Stretch Ratio")
            col.prop(post_effects, "bloom_threshold", text="Threshold")
            col.separator()
            col.prop(post_effects, "bloom_saturation", text="Saturation")
            col.prop(post_effects, "bloom_tint", text="Tint")

    # Streaks
    box = main_col.box()
    if bpy.app.version >= (2, 90, 1):
        col = box.column(heading='Streaks')
    else:
        col = box.column()
    col.use_property_decorate = False
    row = col.row(align=True)
    sub = row.row(align=True)
    if bpy.app.version >= (2, 90, 1):
        sub.prop(post_effects, "streaks", text="")
    else:
        sub.prop(post_effects, "streaks", text="Streaks")
    sub = sub.row(align=True)
    sub.active = post_effects.streaks
    sub.prop(post_effects, "streaks_amount", text="", slider=True)
    if post_effects.streaks:
        col = box.column(align=True)
        col.prop(post_effects, "streaks_number", text="Number")
        col.prop(post_effects, "streaks_angle_offset", text="Angle", slider=True)
        col.prop(post_effects, "streaks_fade", text="Fade", slider=True)
        col.prop(post_effects, "streaks_threshold", text="Threshold")

    # Lens Vignetting
    box = main_col.box()
    if bpy.app.version >= (2, 90, 1):
        col = box.column(heading='Vignetting')
    else:
        col = box.column()
    col.use_property_decorate = False
    row = col.row(align=True)
    sub = row.row(align=True)
    if bpy.app.version >= (2, 90, 1):
        sub.prop(post_effects, "lens_vignetting", text="")
    else:
        sub.prop(post_effects, "lens_vignetting", text="Vignetting")
    sub = sub.row(align=True)
    sub.active = post_effects.lens_vignetting
    sub.prop(post_effects, "lens_vignetting_amount", text="", slider=True)
    if post_effects.lens_vignetting:
        col = box.column(align=True)
        col.prop(post_effects, "lens_vignetting_falloff", text="Falloff")
        row = col.row(align=True)
        row.prop(post_effects, "lens_vignetting_width", text="Scale X")
        row.prop(post_effects, "lens_vignetting_height", text="Y")
        # col.active = settings.lens_vignetting

    # Sharpen
    box = main_col.box()
    if bpy.app.version >= (2, 90, 1):
        col = box.column(heading="Sharpen")
    else:
        col = box.column()
    col.use_property_decorate = False
    row = col.row(align=True)
    sub = row.row(align=True)
    if bpy.app.version >= (2, 90, 1):
        sub.prop(post_effects, "sharpen", text="")
    else:
        sub.prop(post_effects, "sharpen", text="Sharpen")
    sub = sub.row(align=True)
    sub.active = post_effects.sharpen
    sub.prop(post_effects, "sharpen_amount", text="", slider=True)
    if post_effects.sharpen:
        col = box.column(align=True)
        col.prop(post_effects, "sharpen_radius", text="Radius")

    # Film Grain
    box = main_col.box()
    if bpy.app.version >= (2, 90, 1):
        col = box.column(heading="Film Grain")
    else:
        col = box.column()
    col.use_property_decorate = False
    row = col.row(align=True)
    sub = row.row(align=True)
    if bpy.app.version >= (2, 90, 1):
        sub.prop(post_effects, "film_grain", text="")
    else:
        sub.prop(post_effects, "film_grain", text="Film Grain")
    sub = sub.row(align=True)
    sub.active = post_effects.film_grain
    sub.prop(post_effects, "film_grain_amount", text="", slider=True)
    if post_effects.film_grain:
        col = box.column(align=True)
        col.prop(post_effects, "film_grain_size", text="Size")
        col.prop(post_effects, "film_grain_displace", text="Displace")
        col.prop(post_effects, "film_grain_animated", text="Animated")
        col.template_icon_view(post_effects, "film_grain_tex", show_labels=True, scale=8)     

class PHOTOGRAPHER_PT_ViewPanel_LensEffects(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = 'Camera Post FX'
    bl_order = 5
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        pfxpe = context.preferences.addons[base_package].preferences.postfx_panel_enable
        return context.scene.camera is not None and context.scene.camera.type == 'CAMERA'  and pfxpe  
    
    def draw_header_preset(self, context):
        camera_presets.PHOTOGRAPHER_PT_LensEffectsPresets.draw_panel_header(self.layout)
    
    def draw_header(self,context):
        post_effects_header(context,self.layout,True)

    def draw(self, context):
        post_effects_draw(context,self.layout,True)

class PHOTOGRAPHER_PT_Panel_LensEffects(Panel):
    bl_parent_id = "PHOTOGRAPHER_PT_Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = 'Camera Post FX'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.camera
    
    def draw_header_preset(self, context):
        camera_presets.PHOTOGRAPHER_PT_LensEffectsPresets.draw_panel_header(self.layout)

    def draw_header(self,context):
        post_effects_header(context,self.layout)
    
    def draw(self, context):
        post_effects_draw(context,self.layout)

class PHOTOGRAPHER_PT_NodeEditor_LensEffects(Panel):
    bl_category = 'Photographer'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = 'Camera Post FX'
    bl_order = 5
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        snode = context.space_data
        scene = context.scene
        pfxpe = context.preferences.addons[base_package].preferences.postfx_panel_enable
        show_image_panels =  context.preferences.addons[base_package].preferences.show_image_panels
        return scene.camera and scene.camera.type == 'CAMERA' and show_image_panels and pfxpe and snode.tree_type == 'CompositorNodeTree'
    
    def draw_header_preset(self, context):
        camera_presets.PHOTOGRAPHER_PT_LensEffectsPresets.draw_panel_header(self.layout)
    
    def draw_header(self,context):
        post_effects_header(context,self.layout,True)

    def draw(self, context):
        post_effects_draw(context,self.layout,True)

class PHOTOGRAPHER_PT_ImageEditor_LensEffects(Panel):
    bl_category = 'Photographer'
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_label = 'Camera Post FX'
    bl_order = 5
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        pfxpe = context.preferences.addons[base_package].preferences.postfx_panel_enable
        show_image_panels =  context.preferences.addons[base_package].preferences.show_image_panels
        return show_image_panels and pfxpe

    def draw_header_preset(self, context):
        camera_presets.PHOTOGRAPHER_PT_LensEffectsPresets.draw_panel_header(self.layout)
    
    def draw_header(self,context):
        post_effects_header(context,self.layout,True)

    def draw(self, context):
        post_effects_draw(context,self.layout,True)