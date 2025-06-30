import bpy
from ..functions.functions import (
    calc_exposure_value,
    update_exposure_guide,
    shutter_speed_to_angle,
    shutter_angle_to_speed,
    lc_exposure_check,
)
from ..functions.lens_sim_compatibility import get_lens_sim_node
from ..operators.autofocus import dof_hyperfocal
from .. import camera_presets
from ..ui import bokeh
from ..constants import panel_value_size
from ..icons.icons import preview_collections
from .. import __package__ as base_package

class PHOTOGRAPHER_PT_Panel(bpy.types.Panel):
    # bl_idname = "CAMERA_PT_Photographer"
    bl_label = "Photographer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        # Add Panel properties to cameras
        return context.camera

    def draw(self, context):
        layout = self.layout
        # layout.use_property_split = True
        settings = context.camera.photographer
        scene = bpy.context.scene

        # UI if camera isn't active
        if scene.camera != bpy.context.active_object:

            main_cam = context.scene.photographer.main_camera
            if main_cam:
                if main_cam == context.camera:
                    layout.label(text="This is the Main Camera, but is it not currently Active.")
                else:
                    layout.label(text="This is not the Active Camera.")
                    layout.label(text="Changing settings won't be visible in the viewport.")

            row = layout.row()
            row.operator("photographer.makecamactive", text="Make Active Camera")
            row.operator("photographer.selectactivecam", text="Select Active Camera")

        col = layout.column()
        # # Enable UI if Camera is Active
        # if scene.camera != bpy.context.active_object:
        #     col.enabled = False

        col.operator("photographer.applyphotographersettings",
            icon='FILE_REFRESH')
        col.prop(settings,'renderable')

        # World Override
        row = col.row(align=True)
        split = row.split(factor=0.33)
        split.prop(settings, "override_world", text="World Override")
        sub = split.row(align=True)
        sub.active = settings.override_world
        sub.prop(settings, "cam_world", text="")

        # Frame range Override
        row = col.row(align=True)
        row.prop(settings, "override_frames")
        sub = row.row(align=True)
        sub.active = settings.override_frames
        if context.scene.renderqueue.frame_mode == 'STILL':
            sub.prop(settings, "cam_frame_current", text="Frame")
        else:
            sub.prop(settings, "cam_frame_start", text="Start")
            sub.prop(settings, "cam_frame_end", text="End")

        # Samples Override
        row = col.row(align=True)
        row.prop(settings, "override_samples")
        sub = row.row(align=True)
        sub.active = settings.override_samples
        if context.scene.render.engine == 'CYCLES':
            sub.prop(settings, "samples", text='')
            row = col.row(align=True)
            row.prop(settings, "use_adaptive_threshold")
            sub = row.row(align=True)
            row.active = settings.override_samples
            sub.active = settings.use_adaptive_threshold
            sub.prop(settings, "adaptive_threshold", text='')
        else:
            sub.prop(settings, "taa_render_samples", text='')

        # Flip canvas
        row = col.row(align=True)
        # row.alignment = 'RIGHT'
        # split = row.split(factor=0.41, align=True)
        # sub = split.row()
        # sub.alignment='RIGHT'
        row.label(text='Flip Camera ')
        flip_x = row.operator("photographer.flip_image", text='X')
        flip_x.x = True
        flip_x.y = False
        flip_x.use_scene_camera = False
        flip_y = row.operator("photographer.flip_image", text= 'Y')
        flip_y.x = False
        flip_y.y = True
        flip_y.use_scene_camera = False

def camera_panel_draw_header_preset(context,layout):
    cam_obj = context.scene.camera
    cam = cam_obj.data
    settings = cam.photographer

    row = layout.row(align=False)
    main_cam = context.scene.photographer.main_camera
    if main_cam:
        if cam_obj == main_cam:
            row.label(text='Main')

    if context.scene.camera == bpy.data.objects.get('DroneCamera'):
        layout.enabled = False

    if context.preferences.addons[base_package].preferences.show_compact_ui:
        row.alignment = 'RIGHT'
        row.scale_x = 0.9
        row.prop(settings,'sensor_type', text="")

def camera_panel_draw(context,layout):
    layout.use_property_split = True
    layout.use_property_decorate = False

    cam = context.scene.camera.data
    settings = cam.photographer

    main_col = layout.column(align=True)
    if context.scene.camera == bpy.data.objects.get('DroneCamera'):
        main_col.enabled = False

    col = main_col.column(align=True)
    if not context.preferences.addons[base_package].preferences.show_compact_ui:
        col.prop(settings,'sensor_type')
    sensor_col = col.column(align=True)
    if settings.sensor_type == 'Custom':
        sensor_col.enabled = True
    else:
        sensor_col.enabled = False
    row_width = sensor_col.row()
    row_width.prop(cam,'sensor_width')

    row_height = sensor_col.row()
    row_height.prop(cam,'sensor_height')

    col.prop(cam,"show_sensor")

    if not settings.fit_inside_sensor:
        if cam.sensor_fit == 'VERTICAL':
            row_height.enabled = True
            row_width.enabled = False
        else:
            row_height.enabled = False
            row_width.enabled = True

    # Clip values
    col = layout.column(align=True)
    col.prop(cam, "clip_start")
    col.prop(cam, "clip_end")

    # Passepartout
    if bpy.app.version >= (2, 90, 1):
        col = layout.column(align=False, heading='Passepartout')
    else:
        col = layout.column(align=False)
    col.use_property_decorate = False
    row = col.row(align=True)
    sub = row.row(align=True)
    if bpy.app.version >= (2, 90, 1):
        sub.prop(cam, "show_passepartout", text="")
    else:
        sub.prop(cam, "show_passepartout", text="Passepartout")
    sub = sub.row(align=True)
    sub.active = cam.show_passepartout
    sub.prop(cam, "passepartout_alpha", text="")

    # Flip canvas
    row = col.row(align=True)
    row.alignment = 'RIGHT'
    split = row.split(factor=0.41, align=True)
    sub = split.row()
    sub.alignment='RIGHT'
    sub.label(text='Flip Camera ')
    flip_x = split.operator("photographer.flip_image", text='X')
    flip_x.x = True
    flip_x.y = False
    flip_x.use_scene_camera = True
    flip_y = split.operator("photographer.flip_image", text= 'Y')
    flip_y.x = False
    flip_y.y = True
    flip_y.use_scene_camera = True


    # Composition guides
    row = col.row(align=True)
    split = row.split(factor=0.41, align=True)
    split.label(text='')
    split.popover(
        panel="ADD_CAMERA_RIGS_PT_composition_guides",
        text="Composition Guides",)


    # World Override per camera
    override_col = layout.column(align=True)
    if bpy.app.version >= (2, 90, 1):
        col = override_col.column(align=False, heading='World Override')
    else:
        col = override_col.column(align=False)
    col.use_property_decorate = False
    row = col.row(align=True)
    sub = row.row(align=True)
    if bpy.app.version >= (2, 90, 1):
        sub.prop(settings, "override_world", text="")
    else:
        sub.prop(settings, "override_world")
    sub = sub.row(align=True)
    sub.active = settings.override_world
    sub.prop_search(settings, "cam_world", bpy.data, "worlds", text="", results_are_suggestions=True)

    # Frames Override per camera
    if bpy.app.version >= (2, 90, 1):
        col = override_col.column(align=False, heading='Frames Override')
    else:
        col = override_col.column(align=False)
    col.use_property_decorate = False
    row = col.row(align=True)
    sub = row.row(align=True)
    if bpy.app.version >= (2, 90, 1):
        sub.prop(settings, "override_frames", text="")
    else:
        sub.prop(settings, "override_frames")
    sub = sub.row(align=True)
    sub.active = settings.override_frames
    if context.scene.renderqueue.frame_mode == 'STILL':
        sub.prop(settings, "cam_frame_current", text="")
    else:
        sub.prop(settings, "cam_frame_start", text="")
        sub.prop(settings, "cam_frame_end", text="")

    # Frames Override per camera
    if context.scene.render.engine in {'CYCLES','BLENDER_EEVEE'}:
        if bpy.app.version >= (2, 90, 1):
            col = override_col.column(align=True, heading='Samples Override')
        else:
            col = override_col.column(align=True)
        col.use_property_decorate = False
        row = col.row(align=True)
        sub = row.row(align=True)
        if bpy.app.version >= (2, 90, 1):
            sub.prop(settings, "override_samples", text="")
        else:
            sub.prop(settings, "override_samples")

        if context.scene.render.engine == 'CYCLES':
            sub = sub.row(align=True)
            sub.prop(settings, "samples", text='')
            sub.active = settings.override_samples

            if bpy.app.version >= (2, 90, 1):
                col = override_col.column(align=True, heading='Noise Threshold')
            else:
                col = override_col.column(align=True)
            col.use_property_decorate = False
            row = col.row(align=True)
            row.active = settings.override_samples
            if bpy.app.version >= (2, 90, 1):
                row.prop(settings, "use_adaptive_threshold", text="")
            else:
                row.prop(settings, "use_adaptive_threshold")
            sub = row.row(align=False)
            sub.prop(settings, "adaptive_threshold", text='')
            sub.active = settings.use_adaptive_threshold
        else:
            sub = sub.row(align=True)
            sub.prop(settings, "taa_render_samples", text='')
            sub.active = settings.override_samples

#### CAMERA SETTINGS PANEL ####
class PHOTOGRAPHER_PT_ViewPanel_Camera(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = 'Camera'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 1

    @classmethod
    def poll(cls, context):
        cpe = context.preferences.addons[base_package].preferences.camera_panel_enable
        return context.scene.camera is not None and context.scene.camera.type == 'CAMERA' and cpe

    def draw_header_preset(self, context):
        layout = self.layout
        camera_panel_draw_header_preset(context,layout)
        camera_presets.PHOTOGRAPHER_PT_CameraPresets.draw_panel_header(layout)

    def draw(self, context):
        camera_panel_draw(context,self.layout)


def dof_panel_draw_header_preset(context,layout):
    if context.preferences.addons[base_package].preferences.show_compact_ui:
        if context.scene.camera == bpy.data.objects.get('DroneCamera'):
            layout.enabled = False
        row = layout.row(align=False)
        row.alignment = 'RIGHT'
        row.scale_x = panel_value_size

        cam = context.scene.camera
        settings = cam.data.photographer
        if not settings.aperture_slider_enable:
            sub = row.row(align=False)
            sub.scale_x = 1.09
            sub.prop(settings, 'aperture_preset', text="")
        else:
            row.prop(settings, 'aperture', text="")
        sub = layout.row(align=False)
        sub.scale_x = 1.26
        sub.prop(settings,'aperture_slider_enable', icon='SETTINGS',
            text='',emboss=False)

        layout.enabled = settings.use_dof

def dof_panel_draw(self,context,layout):
    layout.use_property_split = False
    layout.use_property_decorate = False

    cam_obj = context.scene.camera
    cam = cam_obj.data
    settings = cam.photographer
    layout.enabled = settings.use_dof

    if not context.preferences.addons[base_package].preferences.show_compact_ui:
        row = layout.row(align=True)
        if not settings.aperture_slider_enable:
            row.prop(settings, 'aperture_preset', text='Aperture')
        else:
            row.prop(settings, 'aperture', slider=True, text='Aperture F-stop')
        row.prop(settings,'aperture_slider_enable', icon='SETTINGS', text='')

    col = layout.column()
    col.enabled = not cam_obj.get('lens_sim_cam',False)
    bokeh.bokeh_ui(self, context,col,True)

    if context.scene.render.engine == 'LUXCORE':
        lc_bokeh = cam.luxcore.bokeh
        col = layout.column(align=True)
        col.prop(lc_bokeh,'non_uniform')

        col = layout.column(align=True)
        col.enabled = lc_bokeh.non_uniform
        col.prop(lc_bokeh, "blades")
        col.prop(lc_bokeh, "anisotropy")
        col.prop(lc_bokeh, "distribution")
        if lc_bokeh.distribution in {"EXPONENTIAL", "INVERSEEXPONENTIAL"}:
            col.prop(lc_bokeh, "power")
        elif lc_bokeh.distribution == "CUSTOM":
            col.template_ID(lc_bokeh, "image", open="image.open")
            lc_bokeh.image_user.draw(col, context.scene)

    else:
        box = layout.box()
        col = box.column(align=True)
        col.enabled = not cam_obj.get('lens_sim_cam',False)
        col.prop(cam.dof,'aperture_blades')
        col.prop(cam.dof,'aperture_rotation')
        col.separator()
        col.prop(cam.dof,'aperture_ratio', text="Anamorphic Ratio")
        col.prop(settings,'lock_vertical_fov')

class PHOTOGRAPHER_PT_ViewPanel_DOF(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = "Depth of Field"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 3

    @classmethod
    def poll(cls, context):
        dpe = context.preferences.addons[base_package].preferences.dof_panel_enable
        return context.scene.camera is not None and context.scene.camera.type == 'CAMERA' and dpe

    def draw_header(self, context):
        cam = context.scene.camera.data
        settings = cam.photographer
        self.layout.prop(settings, "use_dof", text="")

    def draw_header_preset(self, context):
        dof_panel_draw_header_preset(context,self.layout)

    def draw(self, context):
        dof_panel_draw(self,context,self.layout)

#### EXPOSURE PANELS ####

def exposure_header_preset(context, layout, settings, guide):
        if context.scene.camera == bpy.data.objects.get('DroneCamera'):
            layout.enabled = False
        row = layout.row(align=False)
        row.alignment = 'RIGHT'
        row.scale_x = panel_value_size + 0.1
        row.enabled = settings.exposure_enabled

        ev = calc_exposure_value(settings, context)
        ev_guide = update_exposure_guide(ev)

        if settings.exposure_mode == 'EV':
            if guide == True:
                row.label(text = ev_guide)
            if context.preferences.addons[base_package].preferences.show_compact_ui:
                row.prop(settings,'ev',text='')
        elif settings.exposure_mode == 'MANUAL':
            if guide == True:
                row.label(text = ev_guide + " - Manual  EV" + str("%.2f" % ev))
            else:
                row.label(text = "M - EV" + str("%.2f" % ev))
        elif settings.exposure_mode == 'AUTO':
            if guide == True:
                row.label(text = ev_guide + " - Auto  EV" + str("%.2f" % ev))
            else:
                row.label(text = "A - EV " + str("%.2f" % ev))

def exposure_header(context,layout, use_scene_camera=False):
    custom_icons = preview_collections["icons"]

    if use_scene_camera:
        cam = context.scene.camera
        settings = cam.data.photographer
    else:
        cam = context.camera
        settings = cam.photographer  
    main_cam = context.scene.photographer.main_camera
    if cam == bpy.data.objects.get('DroneCamera'):
        layout.enabled = False
    layout.prop(settings, "exposure_enabled", text="")
    if main_cam:
        if main_cam != 'NONE':
            if main_cam.photographer != settings:
                if cam.name != 'DroneCamera' and not settings.exposure_enabled:
                    layout.label(text='', icon_value=custom_icons['MAIN_CAMERA'].icon_id)
            else:
                layout.label(text='', icon_value=custom_icons['MAIN_CAMERA'].icon_id)

def exposure_settings(context,settings,parent_ui,guide,image_editor):
    # Settings in Manual
    layout = parent_ui.column()
    layout.enabled = settings.exposure_enabled
    if settings.exposure_mode == 'MANUAL':
        # Shutter Speed parameter
        row = layout.row(align = True)
        if settings.shutter_mode == 'SPEED':
            if not settings.shutter_speed_slider_enable:
                row.prop(settings, 'shutter_speed_preset', text='Shutter Speed')
            else:
                row.prop(settings, 'shutter_speed', slider=True)
            row.operator("photographer.setshutterangle",icon="DRIVER_ROTATIONAL_DIFFERENCE", text="")
            row.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')

        if settings.shutter_mode == 'ANGLE':
            if not settings.shutter_speed_slider_enable:
                row.prop(settings, 'shutter_angle_preset', text='Shutter Angle')
            else:
                row.prop(settings, 'shutter_angle', slider=True)
            row.operator("photographer.setshutterspeed",icon="PREVIEW_RANGE", text="")
            row.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')

        # Aperture parameter
        row = layout.row(align = True)
        if not settings.aperture_slider_enable:
            row.prop(settings, 'aperture_preset', text='Aperture')
        else:
            row.prop(settings, 'aperture', slider=True, text='Aperture F-stop')
        row.prop(settings,'aperture_slider_enable', icon='SETTINGS', text='')

        # ISO parameter
        row = layout.row(align = True)
        if not settings.iso_slider_enable:
            row.prop(settings, 'iso_preset', text='ISO')
        else:
            row.prop(settings, 'iso', slider=True)
        row.prop(settings,'iso_slider_enable', icon='SETTINGS', text='')

        # Exposure Compensation
        layout.prop(settings, 'exposure_compensation', text='Exp. Compensation')

    # Settings in EV Mode
    else:
        col = layout.column(align=True)
        col.use_property_split = False
        if settings.exposure_mode == 'EV':
            col.prop(settings, 'ev', slider=True)
            # col.separator()
            col.prop(settings, 'exposure_compensation', text='Exposure Compensation', slider=True)

        auto_col = layout.column(align=True)
        auto_col.use_property_split = False

        if settings.exposure_mode == 'AUTO':
            # No Auto Exposure if using LuxCore and CPU
            engine = context.scene.render.engine
            if engine == 'LUXCORE':
                lc_device = context.scene.luxcore.config.device
                if lc_device == 'CPU':
                    col.operator("photographer.changelcdevice",icon="INFO", text="Requires GPU device")
                    auto_col.enabled = False
            if engine == 'BLENDER_EEVEE':
                if context.scene.eevee.use_soft_shadows:
                    col.operator("photographer.disablesoftshadows",icon="INFO",
                        text="Soft shadows might cause issues")
            auto_col.prop(settings, 'center_weight', slider=True)
            auto_col.prop(settings, 'ae_speed', text='Speed', slider=True)
            # auto_col.separator()
            auto_col.prop(settings, 'exposure_compensation', text='Exposure Compensation', slider=True)

            # Show AE Set Key if 3D view and Auto Exposure mode
            if guide:
                auto_col.separator()
                if context.area.spaces.active.shading.type != 'RENDERED':
                    auto_col.operator('photographer.set_viewport_shading',
                                      text='Auto requires Rendered shading',
                                      icon='INFO').type='RENDERED'
                    col.enabled = False
                col = auto_col.column(align=True)

                col.operator("photographer.ae_set_key", icon="KEY_HLT")
                bake = col.operator("photographer.bake_auto_exposure", icon="KEYINGSET")
                row = col.row(align=True)
                row.prop(settings, 'ae_bake_step')
                row.prop(settings, 'ae_bake_wait_time', slider=True)
                if context.area.spaces.active.shading.type != 'RENDERED':
                    col.enabled = False

            if image_editor:
                auto_col.enabled = False

def exposure_panel(context, layout, settings, prop_panel, guide, image_editor=False):
        
        scene = bpy.context.scene

        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.enabled = settings.exposure_enabled

        if context.scene.camera == bpy.data.objects.get('DroneCamera'):
            layout.enabled = False

        if lc_exposure_check(context):
            layout.label(text="Settings need to be reapplied", icon='INFO')
            layout.operator("photographer.applyphotographersettings",
                icon='FILE_REFRESH')

        col = layout.column(align=True)
        col.use_property_split = False
        row = col.row(align=True)
        row.alignment = "CENTER"
        row.scale_y = 1.5
        if not prop_panel:
        #     row.operator('exposure.picker', text = '', icon = 'EYEDROPPER').use_scene_camera = False
        # else:
            row.operator('exposure.picker', text='', icon = 'EYEDROPPER').use_scene_camera = True
        row.prop(settings, 'exposure_mode', expand=True)

        exposure_settings(context,settings,layout,guide,image_editor)

        if settings.exposure_mode != 'MANUAL':
            # Shutter Speed parameter
            row = layout.row(align = True)
            row.enabled = settings.motionblur_enabled
            if settings.shutter_mode == 'SPEED':
                if not settings.shutter_speed_slider_enable:
                    row.prop(settings, 'shutter_speed_preset', text='Shutter Speed')
                else:
                    row.prop(settings, 'shutter_speed', slider=True)
                row.operator("photographer.setshutterangle",icon="DRIVER_ROTATIONAL_DIFFERENCE", text="")
                row.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')

            if settings.shutter_mode == 'ANGLE':
                if not settings.shutter_speed_slider_enable:
                    row.prop(settings, 'shutter_angle_preset', text='Shutter Angle')
                else:
                    row.prop(settings, 'shutter_angle', slider=True)
                row.operator("photographer.setshutterspeed",icon="PREVIEW_RANGE", text="")
                row.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')

            # Aperture parameter
            row = layout.row(align = True)
            use_dof = settings.use_dof

            row.enabled = use_dof
            if prop_panel:
                if not settings.aperture_slider_enable:
                    row.prop(settings, 'aperture_preset', text='Aperture')
                else:
                    row.prop(settings, 'aperture', slider=True, text='Aperture F-stop / DOF only')
                row.prop(settings,'aperture_slider_enable', icon='SETTINGS', text='')

        col = layout.column(align=False)
        col.prop(settings, 'motionblur_enabled', text='Affect Motion Blur')

        # Check if the Motion Blur is enabled in the Render Settings
        if settings.motionblur_enabled and not scene.render.use_motion_blur:
            row = layout.row(align = True)
            row.label(icon= 'ERROR', text="")
            row.operator("photographer.rendermotionblur", text="Enable Motion Blur")

        # Hide Affect Depth of Field in 3D View Panel
        if prop_panel:
            col.prop(settings, "use_dof", text='Affect Depth of Field')

        col.prop(settings, 'falsecolor_enabled')
        col.prop(settings, 'colorchart_enabled')
        col.prop(scene.photographer, 'comp_exposure')

        view = context.space_data
        if view.type == 'VIEW_3D':
            shading = view.shading
        else:
            shading = None

        if bpy.app.version >= (3,5,0):
            if shading:
                col = layout.column()
                if scene.photographer.comp_exposure:
                    col.prop(shading,'use_compositor', text='Viewport Compositing')
                    if shading.use_compositor == 'DISABLED':
                        col.label(text="Exposure won't be visible in Viewport.", icon='INFO')
        else:
            if scene.photographer.comp_exposure:
                col.label(text="Exposure won't be visible in Viewport.", icon='INFO')

        # EV Guide for ViewPanel
        if guide:
            row = layout.row()
            row.alignment = 'RIGHT'
            ev = calc_exposure_value(settings, context)
            ev_guide = update_exposure_guide(ev)
            row.label(text = "EV Guide: " + ev_guide )

        # FPS / Shutter Angle info
        row = layout.row()
        row.alignment = 'RIGHT'
        fps = scene.render.fps/scene.render.fps_base
        framerate_guide = "FPS : " + str(round(fps,2))
        if settings.shutter_mode == 'ANGLE':
            shutter_speed_guide = " - " + "Shutter Speed : 1/" + str(int(shutter_angle_to_speed(settings,context))) + "s"
            framerate_guide += shutter_speed_guide
        if settings.shutter_mode == 'SPEED':
            shutter_angle_guide = " - " + "Shutter Angle : " + str(round(shutter_speed_to_angle(settings,context),1))
            framerate_guide += shutter_angle_guide
        row.label(text = framerate_guide)

        # Light Sampling Threshold warning
        col = layout.column(align=True)
        row = col.row()
        row.alignment = 'RIGHT'
        if context.scene.render.engine in {'CYCLES','BLENDER_EEVEE','BLENDER_EEVEE_NEXT'}:
            prefs = bpy.context.preferences.addons[base_package].preferences
            alt = prefs.auto_light_threshold
            hltw = prefs.hide_light_threshold_warning
            show = False
            if not alt and settings.exposure_mode != 'AUTO':
                if settings.light_threshold_warning and not hltw:
                    show = True

            if bpy.app.version >= (3,6,0):
                if not context.scene.cycles.use_light_tree and show:
                    row.label(text="Potential Sampling issue", icon='INFO')
                    col.operator("photographer.updatelightthreshold", text='Update Light Threshold')
            else:
                if show:
                    row.label(text="Potential Sampling issue", icon='INFO')
                    col.operator("photographer.updatelightthreshold", text='Update Light Threshold')


class PHOTOGRAPHER_PT_Panel_Exposure(bpy.types.Panel):
    bl_label = 'Exposure'
    bl_parent_id = 'PHOTOGRAPHER_PT_Panel'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.camera

    def draw_header_preset(self, context):
        settings = context.camera.photographer
        exposure_header_preset(context,self.layout,settings,True)
        camera_presets.PHOTOGRAPHER_PT_ExposurePresets.draw_panel_header(self.layout)

    def draw_header(self, context):
        exposure_header(context,self.layout)

    def draw(self, context):
        settings = context.camera.photographer
        prop_panel = True
        guide = False
        exposure_panel(context,self.layout,settings,prop_panel,guide)

class PHOTOGRAPHER_PT_ViewPanel_Exposure(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = 'Exposure'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 6

    @classmethod
    def poll(cls, context):
        epe = context.preferences.addons[base_package].preferences.exposure_panel_enable
        return context.scene.camera and context.scene.camera.type == 'CAMERA' and epe

    def draw_header_preset(self, context):
        settings = context.scene.camera.data.photographer
        exposure_header_preset(context,self.layout,settings,False)
        camera_presets.PHOTOGRAPHER_PT_ExposurePresets.draw_panel_header(self.layout)

    def draw_header(self, context):
        exposure_header(context,self.layout,True)

    def draw(self, context):
        settings = context.scene.camera.data.photographer
        prop_panel = False
        guide = True
        exposure_panel(context,self.layout,settings,prop_panel, guide)

class PHOTOGRAPHER_PT_ImageEditor_Exposure(bpy.types.Panel):
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_space_type = 'IMAGE_EDITOR'
    bl_label = 'Exposure'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 6

    @classmethod
    def poll(cls, context):
        epe = context.preferences.addons[base_package].preferences.exposure_panel_enable
        show_image_panels =  bpy.context.preferences.addons[base_package].preferences.show_image_panels
        return context.scene.camera and context.scene.camera.type == 'CAMERA' and show_image_panels and epe
    
    def draw_header_preset(self, context):
        settings = context.scene.camera.data.photographer
        exposure_header_preset(context,self.layout,settings,False)
        camera_presets.PHOTOGRAPHER_PT_ExposurePresets.draw_panel_header(self.layout)

    def draw_header(self, context):
        exposure_header(context,self.layout,True)

    def draw(self, context):
        settings = context.scene.camera.data.photographer
        prop_panel = False
        guide = True
        image_editor = True
        exposure_panel(context,self.layout,settings,prop_panel, guide, image_editor)

class PHOTOGRAPHER_PT_NodeEditor_Exposure(bpy.types.Panel):
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_space_type = 'NODE_EDITOR'
    bl_label = 'Exposure'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 6

    @classmethod
    def poll(cls, context):
        epe = context.preferences.addons[base_package].preferences.exposure_panel_enable
        show_image_panels =  context.preferences.addons[base_package].preferences.show_image_panels
        snode = context.space_data
        scene = context.scene
        return scene.camera and scene.camera.type == 'CAMERA' and show_image_panels and epe and snode.tree_type == 'CompositorNodeTree'
    
    def draw_header_preset(self, context):
        settings = context.scene.camera.data.photographer
        exposure_header_preset(context,self.layout,settings,False)
        camera_presets.PHOTOGRAPHER_PT_ExposurePresets.draw_panel_header(self.layout)

    def draw_header(self, context):
        exposure_header(context,self.layout,True)

    def draw(self, context):
        settings = context.scene.camera.data.photographer
        prop_panel = False
        guide = True
        image_editor = True
        exposure_panel(context,self.layout,settings,prop_panel, guide, image_editor)

#### WHITE BALANCE PANELS ####

def whitebalance_header_preset(context,layout,use_scene_camera,ui_context=None):
    if context.scene.camera == bpy.data.objects.get('DroneCamera'):
        layout.enabled = False
    row = layout.row(align=True)
    row.alignment = 'RIGHT'
    if not ui_context=='3D_VIEW_MENU':
        row.scale_x = panel_value_size

    if use_scene_camera:
        settings = context.scene.camera.data.photographer
    else:
        settings = context.camera.photographer

    if not settings.wb_enabled :
        row.enabled = False

    prefs = bpy.context.preferences.addons[base_package].preferences

    if prefs.show_compact_ui:
        row.prop(settings,'color_temperature', text="", slider=True)

    sub = layout.row(align=False)
    sub.scale_x = 1.27
    if ui_context=='IMAGE_EDITOR':
        sub.scale_x = 0.45
        sub.prop(settings, "wb_color", text='')
    elif use_scene_camera:
        sub.operator("white_balance.picker", text='', icon='EYEDROPPER', emboss=False).use_scene_camera=use_scene_camera
    else:
        sub.operator("white_balance.reset", text='', icon='LOOP_BACK', emboss=False).use_scene_camera=use_scene_camera

def whitebalance_header(context, layout, use_scene_camera=False):
    custom_icons = preview_collections["icons"]

    if use_scene_camera:
        cam = context.scene.camera
        settings = cam.data.photographer
    else:
        cam = context.camera
        settings = cam.photographer
        
    main_cam = context.scene.photographer.main_camera
    if cam == bpy.data.objects.get('DroneCamera'):
        layout.enabled = False
    layout.prop(settings, "wb_enabled", text="")
    if main_cam:
        if main_cam != 'NONE':
            if main_cam.photographer != settings:
                if cam.name != 'DroneCamera' and not settings.wb_enabled:
                    layout.label(text='', icon_value=custom_icons['MAIN_CAMERA'].icon_id)
            else:
                layout.label(text='', icon_value=custom_icons['MAIN_CAMERA'].icon_id)

def whitebalance_panel(context,layout,settings):
    scene = context.scene
    if scene.camera == bpy.data.objects.get('DroneCamera'):
        layout.enabled = False
    else:
        layout.enabled = settings.wb_enabled
    layout.use_property_split = True
    layout.use_property_decorate = False  # No animation.

    row = layout.row(align=True)
    row.prop(settings, "color_temperature", slider=True, text='Temperature')
    row.prop(settings, "preview_color_temp", text='')

    row = layout.row(align=True)
    row.prop(settings, "tint", slider=True)
    row.prop(settings, "preview_color_tint", text='')

    col = layout.column(align=True)
    col.prop(settings, 'colorchart_enabled')
    row = col.row()
    row.prop(scene.photographer,"comp_wb")
    prefs = bpy.context.preferences.addons[base_package].preferences
    if prefs.color_temperature_mode == 'BLENDER':
        row.enabled = False

    view = context.space_data
    if view.type == 'VIEW_3D':
        shading = view.shading
    else:
        shading = None

    if bpy.app.version >= (3,5,0):
        if shading:
            col = layout.column()
            if scene.photographer.comp_wb:
                col.prop(shading,'use_compositor', text='Viewport Compositing')
                if shading.use_compositor == 'DISABLED':
                    col.label(text="White Balance won't be visible in Viewport.", icon='INFO')

class PHOTOGRAPHER_PT_Panel_WhiteBalance(bpy.types.Panel):
    bl_label = "White Balance"
    bl_parent_id = "PHOTOGRAPHER_PT_Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.camera

    def draw_header_preset(self, context):
        whitebalance_header_preset(context,self.layout,False)

    def draw_header(self, context):
        whitebalance_header(context,self.layout)

    def draw(self, context):
        settings = context.camera.photographer
        whitebalance_panel(context,self.layout,settings)

class PHOTOGRAPHER_PT_ViewPanel_WhiteBalance(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = 'White Balance'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 7

    @classmethod
    def poll(cls, context):
        wbpe = context.preferences.addons[base_package].preferences.wb_panel_enable
        return context.scene.camera and context.scene.camera.type == 'CAMERA' and wbpe

    def draw_header_preset(self, context):
        whitebalance_header_preset(context,self.layout,True)

    def draw_header(self, context):
        whitebalance_header(context,self.layout,True)

    def draw(self, context):
        settings = context.scene.camera.data.photographer
        whitebalance_panel(context,self.layout,settings)

class PHOTOGRAPHER_PT_ImageEditor_WhiteBalance(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = 'White Balance'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 7

    @classmethod
    def poll(cls, context):
        wbpe = context.preferences.addons[base_package].preferences.wb_panel_enable
        show_image_panels = bpy.context.preferences.addons[base_package].preferences.show_image_panels
        return context.scene.camera and context.scene.camera.type == 'CAMERA' and show_image_panels and wbpe

    def draw_header_preset(self, context):
        whitebalance_header_preset(context,self.layout,True,'IMAGE_EDITOR')

    def draw_header(self, context):
        whitebalance_header(context,self.layout,True)

    def draw(self, context):
        settings = context.scene.camera.data.photographer
        whitebalance_panel(context,self.layout,settings)    

class PHOTOGRAPHER_PT_NodeEditor_WhiteBalance(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = 'White Balance'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 7

    @classmethod
    def poll(cls, context):
        wbpe = context.preferences.addons[base_package].preferences.wb_panel_enable
        show_image_panels = context.preferences.addons[base_package].preferences.show_image_panels
        snode = context.space_data
        scene = context.scene
        return scene.camera and scene.camera.type == 'CAMERA' and show_image_panels and wbpe and snode.tree_type == 'CompositorNodeTree'

    def draw_header_preset(self, context):
        whitebalance_header_preset(context,self.layout,True,'IMAGE_EDITOR')

    def draw_header(self, context):
        whitebalance_header(context,self.layout,True)

    def draw(self, context):
        settings = context.scene.camera.data.photographer
        whitebalance_panel(context,self.layout,settings)   

def focus_panel_draw_header_preset(context, layout):
    custom_icons = preview_collections["icons"]
    cam_obj = context.scene.camera
    cam = cam_obj.data
    prefs = context.preferences.addons[base_package].preferences
    if context.scene.camera == bpy.data.objects.get('DroneCamera'):
        layout.enabled = False
    row = layout.row(align=False)
    row.alignment = 'RIGHT'

    if prefs.show_compact_ui:
        if prefs.focus_eyedropper_func != 'BL_PICKER':
            if cam_obj.get('lens_sim_cam',False):
                lens_sim = get_lens_sim_node(cam_obj)
                if lens_sim.inputs["focus mode"].default_value == 1:
                    row.prop(lens_sim.inputs[58], 'default_value',text="")
                else:
                    row.operator("photographer.lens_sim_set_focus_distance_mode", text='Set Lens Sim Distance', icon='ERROR').cam_obj=cam_obj.name
            else:
                row.scale_x = panel_value_size
                if cam.dof.focus_object is None:
                    row.prop(cam.dof, 'focus_distance',text="")
                else:
                    row.scale_x = 1
                    txt = "Tracking"
                    tracked_obj = cam.get('tracked_object',None)
                    if tracked_obj:
                        txt += ": " + tracked_obj + "  "
                    row.label(text=txt)

    sub = layout.row(align=False)
    sub.scale_x = 1.26
    if cam_obj.get('lens_sim_cam',False):
        lens_sim = get_lens_sim_node(cam_obj)
        focus_screen_button = ""
        props = context.scene.my_addon_props
        focusing_screen = lens_sim.inputs["focusing screen"].default_value
        if focusing_screen:
            focus_screen_button = "focusing_screen0"
        else:
            focus_screen_button = "focusing_screen1"
        sub.prop(props, focus_screen_button, text="", invert_checkbox=True, icon="CON_CAMERASOLVER", emboss=True)
    else:
        if prefs.focus_eyedropper_func == 'BL_PICKER':
            row.scale_x = panel_value_size + 0.1
            row.prop(cam.dof, 'focus_object', text="")
        if cam.dof.focus_object:
            sub.scale_x = 0.9
            target = cam.dof.focus_object
            if target:
                if target.select_get():
                    icn = 'TARGET_SELECT_ON'
                else:
                    icn = 'TARGET_SELECT_OFF'
            sel = sub.operator("photographer.select", text="", icon_value=custom_icons[icn].icon_id,emboss=False)
            sel.obj_name=target.name
            sel.is_target=True
            sub.operator("photographer.focus_tracking_cancel", text="", icon_value=custom_icons['TARGET_DELETE'].icon_id,emboss=False)
            sub.separator()
        else:
            if prefs.focus_eyedropper_func == 'AFS':
                sub.operator("photographer.focus_single", text="", icon='EYEDROPPER',emboss=False)
            elif prefs.focus_eyedropper_func == 'AFT':
                sub.operator("photographer.focus_tracking", text="", icon_value=custom_icons['TARGET'].icon_id,emboss=False)


def focus_panel_draw(context,layout):
    cam_obj = context.scene.camera
    cam = cam_obj.data
    prefs = context.preferences.addons[base_package].preferences
    settings = cam.photographer
    layout.use_property_split = True
    layout.use_property_decorate = False  # No animation.

    if not prefs.show_compact_ui:
        if cam_obj.get('lens_sim_cam',False):
            lens_sim = get_lens_sim_node(cam_obj)
            if lens_sim.inputs["focus mode"].default_value == 1:
                row.prop(lens_sim.inputs[58], 'default_value',text="")
        else:
            layout.prop(cam.dof, 'focus_distance')

    if prefs.focus_eyedropper_func == 'BL_PICKER':
        row = layout.row()
        row.prop(cam.dof, 'focus_distance')
        if cam.dof.focus_object is not None:
            row.enabled = False

    # Focus Plane
    cam_name = context.scene.camera.name
    col = layout.column(align=True)
    col.use_property_decorate = False
    if settings.show_focus_plane:
        col.operator("photographer.delete_focus_plane", text="Hide Focus Plane", icon='CANCEL').camera=cam_name
    else:
        col.operator("photographer.create_focus_plane", text="Show Focus Plane", icon='NORMALS_FACE').camera=cam_name
    col_fp = col.column(align=True)
    col_fp.prop(settings, "focus_plane_color")
    if bpy.app.version >= (4,2,0):
        col_fp.prop(settings, "focus_plane_edge")
    col_fp.prop(settings,"dof_limits")
    col_fp.enabled = settings.show_focus_plane

    col.enabled = not cam_obj.get('lens_sim_cam',False)
    
    col = layout.column()
    col.alignment = 'RIGHT'
    if cam_obj.get('lens_sim_cam',False):
        col.label(text='Hyperfocal Distance: N/A')
    else:
        col.label(text='Hyperfocal Distance: '+ str(dof_hyperfocal(cam)))


class PHOTOGRAPHER_PT_ViewPanel_Focus(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = "Focus"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 4

    @classmethod
    def poll(cls, context):
        fpe = context.preferences.addons[base_package].preferences.focus_panel_enable
        return context.scene.camera is not None and context.scene.camera.type == 'CAMERA' and fpe

    def draw_header_preset(self, context):
        focus_panel_draw_header_preset(context, self.layout)

    def draw(self, context):
        focus_panel_draw(context,self.layout)

def autofocus_panel_draw(context,layout):
    cam_obj = context.scene.camera
    cam = cam_obj.data
    custom_icons = preview_collections["icons"]
    settings = cam.photographer
    layout.use_property_split = False
    layout.use_property_decorate = False  # No animation.

    col = layout.column(align=True)
    col.enabled = not cam_obj.get('lens_sim_cam',False)

    if context.scene.camera:
        if context.scene.camera.type == 'CAMERA':
            if cam.dof.focus_object is None:
                icon_afs = 'EYEDROPPER'
                if settings.af_animate:
                    icon_afs = 'KEYTYPE_KEYFRAME_VEC'
                row = col.row(align=True)
                row.operator("photographer.focus_single", text="AF-S", icon=icon_afs)
                row.prop(settings, "af_animate", text="", icon="KEY_HLT")
                col.operator("photographer.focus_tracking", text="AF-Track", icon_value=custom_icons['TARGET'].icon_id)

                col_afc = layout.column(align=True)
                col_afc.enabled = False
                icon_afc = 'HOLDOUT_ON'
                if settings.af_animate:
                    icon_afc = 'KEYTYPE_KEYFRAME_VEC'
                row = col_afc.row(align=True)
                row.prop(settings, "af_continuous_enabled", text="Enable AF-C", icon=icon_afc)
                row.prop(settings, "af_animate", text="", icon="KEY_HLT")
                col_afc_int = col_afc.column(align=True)
                col_afc_int.enabled = settings.af_continuous_enabled
                col_afc_int.prop(settings, "af_continuous_interval", slider=True)
                col_afc_int.operator("photographer.bake_autofocus", text="Bake AF-C", icon="KEYINGSET")

                # Disable AF-C button if not looking through scene camera
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        if area.spaces[0].region_3d.view_perspective == 'CAMERA' :
                            if context.scene.camera:
                                if context.scene.camera.type == 'CAMERA':
                                    col_afc.enabled = True
            else:
                col2 = layout.column(align=True)
                target = cam.dof.focus_object
                if target:
                    if target.select_get():
                        icn = 'TARGET_SELECT_ON'
                    else:
                        icn = 'TARGET_SELECT_OFF'
                    sel = col2.operator("photographer.select", text="Select AF Tracker", icon_value = custom_icons[icn].icon_id)
                    sel.obj_name=target.name
                    sel.is_target=True
                col2.operator("photographer.focus_tracking_cancel", text="Cancel AF Tracking", icon_value = custom_icons['TARGET_DELETE'].icon_id)

class PHOTOGRAPHER_PT_ViewPanel_Autofocus(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = "Autofocus"
    bl_parent_id = "PHOTOGRAPHER_PT_ViewPanel_Focus"

    @classmethod
    def poll(cls, context):
        fpe = context.preferences.addons[base_package].preferences.focus_panel_enable
        return context.scene.camera is not None and context.scene.camera.type == 'CAMERA' and fpe

    def draw(self, context):
        autofocus_panel_draw(context,self.layout)

class PHOTOGRAPHER_PT_Panel_Autofocus(bpy.types.Panel):
    # bl_idname = "CAMERA_PT_Photographer_Autofocus"
    bl_label = "Continuous Autofocus"
    bl_parent_id = "PHOTOGRAPHER_PT_Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        settings = context.camera.photographer
        self.layout.prop(settings, "af_continuous_enabled", text="")

    def draw(self, context):
        settings = context.camera.photographer
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        col = layout.column(align=True)
        col.prop(settings, "af_continuous_interval", slider=True)

class PHOTOGRAPHER_OT_ChangeLuxCoreDevice(bpy.types.Operator):
    bl_idname = "photographer.changelcdevice"
    bl_label = "Set LuxCore device to GPU"
    bl_description = "Auto Exposure requires using GPU device"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        engine = context.scene.render.engine
        if engine == 'LUXCORE':
            lc_device = context.scene.luxcore.config.device
            if lc_device == 'CPU':
                context.scene.luxcore.config.device = 'OCL'
            return{'FINISHED'}

class PHOTOGRAPHER_OT_EEVEE_DisableSoftShadows(bpy.types.Operator):
    bl_idname = "photographer.disablesoftshadows"
    bl_label = "Disable Soft Shadows"
    bl_description = "Click to disable EEVEE Soft Shadows that may lock Auto Exposure into an infinite update loop"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        engine = context.scene.render.engine
        if engine == 'BLENDER_EEVEE':
            usf = context.scene.eevee.use_soft_shadows
            if usf:
                context.scene.eevee.use_soft_shadows = False
        return{'FINISHED'}
