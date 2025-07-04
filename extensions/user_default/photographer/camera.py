from .operators import bokeh
import bpy
import math

from . import camera_sensors
from .functions.functions import calc_exposure_value, shutter_speed_to_angle, srgb_to_linear,should_update
from .operators.autofocus import stop_playback, focus_continuous, hide_dof_objects, update_dof_limits
from .operators.white_balance import convert_rgb_to_whitebalance, convert_temperature_to_rgb, convert_rgb_to_white_level
from .operators.resolution import get_resolution_ratio
from .view_layer import update_cam_view_layer
from .operators.sampling_threshold import update_light_threshold, check_light_threshold
from .constants import base_ev, color_temp_desc,DEFAULT_COLOR_TEMPERATURE, DEFAULT_TINT
from .functions.nodes import get_comp_group_node, get_comp_node_in_group
from .functions.lens_sim_compatibility import get_lens_sim_node
from .properties.post_effects import postfx_grp_name
from .operators.world import update_hdri_ground, set_film_transparent

# Default variables
min_color_temperature = 1000
max_color_temperature = 14000
min_color_tint = -150
max_color_tint = 150
stored_cm_view_transform = None
eevee_soft_shadows = False
stored_lens_shift = 0
stored_lens_shift_x = 0
stored_dof_objects = []
WORLDS = []
VIEW_LAYERS = []

#Camera Exposure update functions ##############################################################
# def should_update(self,context,prop_enabled):
#     settings = context.scene.camera.data.photographer
#     update = False
#     pg_main_cam_settings = None
#     pg_main_cam = bpy.data.objects.get(context.scene.photographer.main_camera,None)

#     if pg_main_cam:
#         pg_main_cam_settings = pg_main_cam.data.photographer
    
#     if self == settings:
#         update = True
        
#     elif pg_main_cam_settings:
#         if self == pg_main_cam_settings and not settings.get(prop_enabled,False):
#             # if pg_main_cam_settings.get(prop_enabled,False):
#             update = True
    
#     return update

def reset_exposure(scene):
    scene.view_settings.exposure = 0
    if scene.photographer.comp_exposure:
        pfx_node = get_comp_group_node(bpy.context,postfx_grp_name)
        if pfx_node:
            exposure_node = get_comp_node_in_group(pfx_node,'exposure')
            if exposure_node:
                exposure_node.inputs['Exposure'].default_value = 0

def reset_wb(scene):
    if bpy.app.version >= (4,3,0):
        bpy.context.scene.view_settings.use_white_balance = False
    if scene.view_settings.curve_mapping:
        scene.view_settings.curve_mapping.white_level = (1,1,1)

        if scene.photographer.comp_wb:
            pfx_node = get_comp_group_node(bpy.context,postfx_grp_name)
            if pfx_node:
                white_balance_node = get_comp_node_in_group(pfx_node,'wb_curves')
                if white_balance_node:
                    white_balance_node.mute = True

def update_settings(self,context):
    scene = context.scene
    pg_main_cam = scene.photographer.main_camera
    prefs = bpy.context.preferences.addons[__package__].preferences
    
    if pg_main_cam:
        pg_main_cam_settings = pg_main_cam.photographer
    
    if scene.camera and scene.camera.type == 'CAMERA':
        settings = scene.camera.data.photographer

        if scene.render.engine == 'LUXCORE':
            tonemapper = scene.camera.data.luxcore.imagepipeline.tonemapper

            if settings.exposure_enabled:
                tonemapper.enabled = True
                tonemapper.type = 'TONEMAP_LINEAR'
                tonemapper.linear_scale = 0.001464 #1/683
                tonemapper.use_autolinear = False

        if settings.exposure_enabled:
            if self == settings:
                update_aperture(settings, context)
                update_shutter_speed(settings, context)
                update_shutter_angle(settings, context)
                update_falsecolor(settings,context)
        elif pg_main_cam:
            if not pg_main_cam_settings.exposure_enabled and prefs.reset_exposure:
                reset_exposure(scene)
            else:
                update_aperture(pg_main_cam_settings, context)
                update_shutter_speed(pg_main_cam_settings, context)
                update_shutter_angle(pg_main_cam_settings, context)
                update_falsecolor(pg_main_cam_settings,context)
        elif prefs.reset_exposure:
            reset_exposure(scene)

        update_aperture(settings, context)

        if settings.resolution_enabled:
            if self == settings:
                update_resolution(settings,context)
        elif pg_main_cam:
            update_resolution(pg_main_cam_settings,context)       

        if settings.wb_enabled:
            if self == settings:
                update_wb_enabled(settings,context)
        elif pg_main_cam:
            if not pg_main_cam_settings.wb_enabled and prefs.reset_wb:
                reset_wb(scene)
            else:
                update_wb_enabled(pg_main_cam_settings,context)
        elif prefs.reset_wb:
            reset_wb(scene)

        if settings.override_world:
            if self == settings:
                update_world(settings,context)
        elif pg_main_cam:
            update_world(pg_main_cam_settings,context)

        if settings.override_frames:
            if self == settings:
                update_frames(settings,context)
        elif pg_main_cam:
            update_frames(pg_main_cam_settings,context)

        if settings.override_samples:
            if self == settings:
                update_samples(settings,context)
        elif pg_main_cam:
            update_samples(pg_main_cam_settings,context)

        # # Doing it seperately to avoid unnecessary updates
        # if settings.view_layer_enabled:
        #     bpy.ops.photographer.set_view_layer(view_layer=settings.active_view_layer, use_scene_camera=True)

        if context.scene.camera.data.dof.focus_distance == 0:
            context.scene.camera.data.dof.focus_distance = 3     

# Update EV
def update_ev(self,context):
    update = should_update(self,context,"exposure_enabled")
    if self.exposure_enabled and update:
        EV = calc_exposure_value(self,context)

        bl_exposure = -EV + base_ev

        prefs = bpy.context.preferences.addons[__package__].preferences

        aces_ue_match = prefs.aces_ue_match
        display_device = context.scene.display_settings.display_device
        view_transform = context.scene.view_settings.view_transform
        if aces_ue_match and display_device == 'ACES' and view_transform != 'Raw':
            # Blender ACES is darker than Unreal ACES which has specific modifications. Brighness difference supposedly 1.45.
            bl_exposure += 0.536 # 2^0.536 = 1.45

        bl_exposure -= math.log2(0.78/prefs.lens_attenuation)

        if context.scene.photographer.comp_exposure:
            context.scene.view_settings.exposure = 0
            pfx_node = get_comp_group_node(bpy.context,postfx_grp_name)
            if pfx_node:
                exposure_node = get_comp_node_in_group(pfx_node,'exposure')
                if exposure_node:
                    exposure_node.inputs['Exposure'].default_value = bl_exposure
        else:
            context.scene.view_settings.exposure = bl_exposure

        # Updating Light Sampling Threshold when Exposure changes if Auto
        if prefs.auto_light_threshold:
            if context.scene.render.engine == 'CYCLES' and not context.scene.cycles.get('use_light_tree',False):
                update_light_threshold(self,context)
            elif context.scene.render.engine == 'EEVEE':
                update_light_threshold(self,context)

        # Setting Warning Light Threshold
        else:
            if not prefs.hide_light_threshold_warning:
                if context.scene.render.engine == 'CYCLES' and not context.scene.cycles.get('use_light_tree',False):
                    check_light_threshold(self,context)
                elif context.scene.render.engine == 'EEVEE':
                    check_light_threshold(self,context)
                    
def get_ev(self):
    default_ev =  base_ev - math.log2(0.78 / bpy.context.preferences.addons[__package__].preferences.lens_attenuation)
    return self.get('ev',  default_ev)

def set_ev(self,value):
    self['ev'] = value
    update_ev(self,bpy.context)
    return None

def get_exposure_compensation(self):
    return self.get('exposure_compensation',  0)

def set_exposure_compensation(self,value):
    self['exposure_compensation'] = value
    update_ev(self,bpy.context)
    return None

def get_ae(self):
    return self.get('ae',  0)

def set_ae(self,value):
    self['ae'] = value
    self.ev = base_ev - value
    update_ev(self,bpy.context)
    return None

# Update Aperture
def update_aperture(self, context):
    if context.scene.camera and context.scene.camera.type == 'CAMERA':

        cam = context.scene.camera
        # Aperture should never retrieve the Main Camera settings, can't use self here.
        settings = cam.data.photographer

        if not self.aperture_slider_enable:
            fstop = float(settings.aperture_preset) * context.scene.unit_settings.scale_length
        else:
            fstop = settings.aperture * context.scene.unit_settings.scale_length

        if cam.get('lens_sim_cam',False):
                cam.data.dof.aperture_fstop = 50
                lens_sim = get_lens_sim_node(cam)
                lens_sim.inputs['f stop'].default_value = fstop
        else:
            cam.data.dof.aperture_fstop = fstop

    # Using self and Main Camera for EV calculation
    update_ev(self, context)

def get_aperture(self):
    return self.get('aperture',  2.4)

def set_aperture(self,value):
    self['aperture'] = value
    update_aperture(self,bpy.context)
    return None

def get_aperture_preset(self):
    return self.get('aperture_preset',  6)

def set_aperture_preset(self,value):
    self['aperture_preset'] = value
    update_aperture(self,bpy.context)
    return None

# Update Shutter Speed
def update_shutter_speed(self,context):
    scene = context.scene

    if self.shutter_mode == 'SPEED':
        # fps = scene.render.fps / scene.render.fps_base

        if self.motionblur_enabled:
            if scene.render.engine == 'CYCLES':
                scene.render.motion_blur_shutter = shutter_speed_to_angle(self,context) / 360
            elif scene.render.engine in {'BLENDER_EEVEE','BLENDER_EEVEE_NEXT'}:
                scene.eevee.motion_blur_shutter = shutter_speed_to_angle(self,context) / 360

    if self.exposure_mode == 'MANUAL':
        update_ev(self, context)


def get_shutter_speed(self):
    return self.get('shutter_speed', 100)

def set_shutter_speed(self,value):
    self['shutter_speed'] = value
    update_shutter_speed(self,bpy.context)
    return None

def get_shutter_speed_preset(self):
    return self.get('shutter_speed_preset',  35)

def set_shutter_speed_preset(self,value):
    self['shutter_speed_preset'] = value
    update_shutter_speed(self,bpy.context)
    return None

# Update Shutter Angle
def update_shutter_angle(self,context):
    scene = context.scene
    settings = scene.camera.data.photographer

    if settings.shutter_mode == 'ANGLE':
        fps = scene.render.fps / scene.render.fps_base

        if not settings.shutter_speed_slider_enable:
            shutter_angle = float(settings.shutter_angle_preset)
        else:
            shutter_angle = settings.shutter_angle

        if settings.motionblur_enabled:
            if scene.render.engine == 'CYCLES':
                scene.render.motion_blur_shutter = shutter_angle / 360
            elif scene.render.engine in {'BLENDER_EEVEE','BLENDER_EEVEE_NEXT'}:
                scene.eevee.motion_blur_shutter = shutter_angle / 360

    if settings.exposure_mode == 'MANUAL':
        update_ev(self, context)

def get_shutter_angle(self):
    return self.get('shutter_angle', 180)

def set_shutter_angle(self,value):
    self['shutter_angle'] = value
    update_shutter_angle(self,bpy.context)
    return None

def get_shutter_angle_preset(self):
    return self.get('shutter_angle_preset',  8)

def set_shutter_angle_preset(self,value):
    self['shutter_angle_preset'] = value
    update_shutter_angle(self,bpy.context)
    return None

# Update Iso
def get_iso(self):
    return self.get('iso', 100)

def set_iso(self,value):
    self['iso'] = value
    update_ev(self,bpy.context)
    return None

def get_iso_preset(self):
    return self.get('iso_preset', 0)

def set_iso_preset(self,value):
    self['iso_preset'] = value
    update_ev(self,bpy.context)
    return None

# Update Motion Blur
def get_motionblur_enabled(self):
    return self.get('motionblur_enabled', False)

def set_motionblur_enabled(self,value):
    self['motionblur_enabled'] = value
    update_settings(self,bpy.context)
    return None

# Update False Color
def update_falsecolor(self,context):
    fc_luts = ['False Color', 'AgX False Color']
    if context.scene.view_settings.view_transform not in fc_luts:
        global stored_cm_view_transform
        stored_cm_view_transform = context.scene.view_settings.view_transform

    if self.falsecolor_enabled:
        for fc in fc_luts:
            try:
                context.scene.view_settings.view_transform = fc
            except:
                pass
    else:
        if stored_cm_view_transform:
            context.scene.view_settings.view_transform = stored_cm_view_transform

# Update Color Chart
def update_colorchart(self,context):
    colorcharts=[obj for obj in bpy.data.objects if obj.get('is_color_chart', False)]
    if not colorcharts and self.colorchart_enabled:
        bpy.ops.photographer.add_color_chart()
    else:
        for obj in colorcharts:
            if self.colorchart_enabled:
                obj.hide_set(False)
                if bpy.ops.object.mode_set.poll():
                    bpy.ops.object.mode_set(mode="OBJECT")
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)                
            else:
                obj.hide_set(True)


# Fisheye Functions
def update_fisheye(self,context):
    camera = self.id_data
    if self.fisheye and context.scene.render.engine == 'CYCLES':
        camera.type = 'PANO'

        if bpy.app.version >= (4,0,0):
            camera.panorama_type == 'FISHEYE_EQUISOLID'
        else:
            camera.cycles.panorama_type == 'FISHEYE_EQUISOLID'
        self.fisheye_focal = camera.lens
    else:
        camera.type = 'PERSP'

    # Disable lens_shift for Fisheye Equisolid (doesn't support lens shift)
    if bpy.app.version < (3,1,0):
        global stored_lens_shift
        global stored_lens_shift_x
        if self.fisheye:
            stored_lens_shift = self.lens_shift
            stored_lens_shift_x = self.lens_shift_x
            self.lens_shift = 0
            self.lens_shift_x = 0
        else:
            self.lens_shift = stored_lens_shift
            self.lens_shift_x = stored_lens_shift_x

def get_fisheye_focal(self):
    return self.get('fisheye_focal', 50)

def set_fisheye_focal(self, value):
    self['fisheye_focal'] = value
    camera = self.id_data
    if bpy.app.version >= (4,0,0):
        camera.fisheye_lens = value
    else:
        camera.cycles.fisheye_lens = value
    camera.lens = value

def get_focal(self):
    return self.id_data.lens
    # return self['focal']

def set_focal(self, value):
    camera = self.id_data

    # Animated camera was returning a different id_data (evaluated), using original
    obj = [o for o in bpy.data.objects if o.type == 'CAMERA' and o.data.original is camera.original]    

    if self.lens_shift != 0:
        old_rot = obj[0].rotation_euler.x
        old_focal = self.focal

        if camera.sensor_fit == 'VERTICAL':
            sensor_size = camera.sensor_height
        else:
            sensor_size = camera.sensor_width
        old_atan = math.atan(self.lens_shift/(old_focal/sensor_size))
        rot = old_rot + old_atan
        self['focal'] = value
        atan = math.atan(self.lens_shift/(value/sensor_size))
        obj[0].rotation_euler.x = rot - atan
    else:
        self['focal'] = value
    camera.lens = value #+ (camera.dof.focus_distance * self.breathing/10)
    return None

def update_ls_compensated(self,context):

    camera = self.id_data

    # Animated camera was returning a different id_data (evaluated), using original
    obj = [o for o in bpy.data.objects if o.type == 'CAMERA' and o.data.original is camera.original]    

    rot = obj[0].rotation_euler.to_matrix().to_euler('XYZ')
    new_rot = rot

    rot_h = obj[0].rotation_euler.to_matrix().to_euler('YZX')
    new_rot_h = rot_h

    if camera.sensor_fit == 'VERTICAL':
        sensor_size = camera.sensor_height
    else:
        sensor_size = camera.sensor_width

    atan_v = math.atan(self.lens_shift/(camera.lens/sensor_size))
    atan_h = math.atan(self.lens_shift_x/(camera.lens/sensor_size))

    if not self.lens_shift_compensated:
        new_rot.x = rot.x + atan_v
        new_rot_h.y = rot_h.y - atan_h
    else:
        new_rot.x = rot.x - atan_v
        new_rot_h.y = rot_h.y + atan_h

    obj[0].rotation_euler = new_rot.to_matrix().to_euler(obj[0].rotation_mode)
    obj[0].rotation_euler = new_rot_h.to_matrix().to_euler(obj[0].rotation_mode)


def get_lens_shift_y(self):
    return self.get('lens_shift', 0)

def set_lens_shift_y(self, value):
    camera = self.id_data

    if self.lens_shift_compensated:
        # Animated camera was returning a different id_data (evaluated), using original
        obj = [o for o in bpy.data.objects if o.type == 'CAMERA' and o.data is camera]    
        if obj:
            if camera.sensor_fit == 'VERTICAL':
                sensor_size = camera.sensor_height
            else:
                sensor_size = camera.sensor_width
            old_rot = obj[0].rotation_euler.to_matrix().to_euler('XYZ')
            old_atan = math.atan(self.lens_shift/(camera.lens/sensor_size))

            rot = old_rot
            rot.x = old_rot.x + old_atan

            self['lens_shift'] = value
            atan = math.atan(value/(camera.lens/sensor_size))
            camera.shift_y = value + self.resize_shift_y

            new_rot = rot
            new_rot.x = rot.x - atan
            obj[0].rotation_euler = new_rot.to_matrix().to_euler(obj[0].rotation_mode)
    else:
        self['lens_shift'] = value
        camera.shift_y = value + self.resize_shift_y

    return None

def get_lens_shift_x(self):
    return self.get('lens_shift_x', 0)

def set_lens_shift_x(self, value):
    camera = self.id_data

    if self.lens_shift_compensated:
        # Animated camera was returning a different id_data (evaluated), using original
        obj = [o for o in bpy.data.objects if o.type == 'CAMERA' and o.data is camera]    
        # old_rot = obj[0].rotation_euler.y
        old_rot = obj[0].rotation_euler.to_matrix().to_euler('YZX')
        # old_vert_shift = self.lens_shift_x
        if camera.sensor_fit == 'VERTICAL':
            sensor_size = camera.sensor_height
        else:
            sensor_size = camera.sensor_width

        old_atan = math.atan(self.lens_shift_x/(camera.lens/sensor_size))
        rot = old_rot
        rot.y = old_rot.y - old_atan
        self['lens_shift_x'] = value
        atan = math.atan(value/(camera.lens/sensor_size))
        camera.shift_x = value + self.resize_shift_x
        new_rot = rot
        new_rot.y = rot.y + atan
        obj[0].rotation_euler = new_rot.to_matrix().to_euler(obj[0].rotation_mode)
    else:
        self['lens_shift_x'] = value
        camera.shift_x = value + self.resize_shift_x

    return None

# def get_breathing(self):
#     return self.get('breathing', 0)
#
# def set_breathing(self, value):
#     camera = self.id_data
#     self['breathing'] = value
#     self.focal = self.focal
#     return None

def inside_sensor_fit(cam,resolution_x, resolution_y):
    values = [cam.sensor_height,cam.sensor_width,resolution_x,resolution_y]
    new_sensor_fit = None
    if all(v != 0 for v in values):
        if cam.sensor_width >= cam.sensor_height:
            sensor_ratio = cam.sensor_width / cam.sensor_height
        else:
            sensor_ratio = cam.sensor_height / cam.sensor_width
        if resolution_x >= resolution_y:
            resolution_ratio = resolution_x / resolution_y
            if cam.sensor_width < cam.sensor_height:
                cam.sensor_width, cam.sensor_height = cam.sensor_height, cam.sensor_width
        else:
            resolution_ratio = resolution_y / resolution_x
            if cam.sensor_width > cam.sensor_height:
                cam.sensor_width, cam.sensor_height = cam.sensor_height, cam.sensor_width
        if cam.photographer.resolution_rotation == 'LANDSCAPE':
            if sensor_ratio >= resolution_ratio or resolution_ratio == 1:
                new_sensor_fit = 'VERTICAL'
            else:
                new_sensor_fit = 'HORIZONTAL'
            if cam.photographer.lock_vertical_fov:
                new_sensor_fit = 'VERTICAL'
        elif cam.photographer.resolution_rotation == 'PORTRAIT':
            if sensor_ratio <= resolution_ratio or resolution_ratio == 1:
                new_sensor_fit = 'VERTICAL'
            else:
                new_sensor_fit = 'HORIZONTAL'
            if cam.photographer.lock_vertical_fov:
                new_sensor_fit = 'HORIZONTAL'
    return new_sensor_fit

def update_sensor_fit(self,context):
    cam = self.id_data
    # We want to update camera sensors if inheriting from Main Camera
    main_cam = context.scene.photographer.main_camera
    scene_cam = context.scene.camera
    if scene_cam and scene_cam.type == 'CAMERA':
        if main_cam != 'NONE':
            if scene_cam.data != main_cam and not scene_cam.data.photographer.resolution_enabled:
                cam = scene_cam.data
                
        render = context.scene.render
        new_cam_sensor_fit = inside_sensor_fit(cam,render.resolution_x, render.resolution_y)
        if new_cam_sensor_fit:
            cam.sensor_fit = new_cam_sensor_fit

# Update Resolution
def update_resolution(self,context):

    update = should_update(self,context,"resolution_enabled")
    if self.resolution_enabled and update:

        if self.resolution_mode == 'CUSTOM_RES':
            if self.resolution_rotation == 'PORTRAIT':
                resolution_x = self.resolution_y
                resolution_y = self.resolution_x
            else:
                resolution_x = self.resolution_x
                resolution_y = self.resolution_y
        else:
            ratio_x, ratio_y = get_resolution_ratio(self)

            resolution_x = self.longedge
            resolution_y = self.longedge * ratio_y / ratio_x

        if self.resolution_rotation == 'PORTRAIT':
             resolution_x,resolution_y =  resolution_y,resolution_x

        context.scene.render.resolution_x = int(resolution_x)
        context.scene.render.resolution_y = int(resolution_y)

        if self.fit_inside_sensor:
            update_sensor_fit(self,context)

        # Update Photographer Resolution when tweaking Ratios
        if self.resolution_mode != 'CUSTOM_RES':
            self.resolution_x = context.scene.render.resolution_x
            self.resolution_y = context.scene.render.resolution_y
        # Update Photographer Ratio when tweaking Resolution
        else:
            if resolution_x > resolution_y and resolution_y != 0 :
                self.ratio_x = context.scene.render.resolution_x / context.scene.render.resolution_y
                self.ratio_y = 1
            elif resolution_x < resolution_y and resolution_x != 0 :
                self.ratio_x = 1
                self.ratio_y = context.scene.render.resolution_y / context.scene.render.resolution_x

def update_resolution_value(self,context):
    # Avoid Resolution set infinite loop
    if self.resolution_mode == 'CUSTOM_RES':
        update_resolution(self,context)

def update_ratio_value(self,context):
    # Avoid Ratio set infinite loop
    if self.resolution_mode != 'CUSTOM_RES':
        update_resolution(self,context)
            
            
def update_fit_inside_sensor(self,context):
    if self.fit_inside_sensor:
        update_sensor_fit(self,context)
    else:
        if not self.lock_vertical_fov:
            self.id_data.sensor_fit = 'AUTO'

def get_resolution_rotation(self):
    if self.resolution_mode == 'CUSTOM_RES':
        if self.resolution_x >= self.resolution_y:
            return 0
        elif self.resolution_x < self.resolution_y:
            return 1
    else:
        if self.ratio_x >= self.ratio_y:
            return 0
        elif self.ratio_x < self.ratio_y:
            return 1       

def set_resolution_rotation(self,value):
    prev = 1 if self.resolution_rotation == 'PORTRAIT' else 0
    if prev != value:
        self.resolution_x, self.resolution_y = self.resolution_y, self.resolution_x
        self.ratio_x,self.ratio_y = self.ratio_y,self.ratio_x
    return None

def get_preview_color_temp(self):
    return self.get('preview_color_temp', (1,1,1))

def set_preview_color_temp(self,value):
    return None

def get_color_temperature(self):
    return self.get('color_temperature', DEFAULT_COLOR_TEMPERATURE)

def set_color_temperature(self, value):
    self['color_temperature'] = value
    # Convert Temperature to Color
    white_balance_color = convert_temperature_to_rgb(self.color_temperature)
    # Set preview color in the UI - inverting red and blue channels
    self['preview_color_temp'] = (white_balance_color[2],white_balance_color[1],white_balance_color[0])
    
    prefs = bpy.context.preferences.addons[__package__].preferences
    if bpy.app.version >= (4,3,0):
        if prefs.color_temperature_mode == 'BLENDER':
            if bpy.context.scene.view_settings.curve_mapping:
                bpy.context.scene.view_settings.curve_mapping.white_level = (1,1,1)
            bpy.context.scene.view_settings.white_balance_temperature = value
            if bpy.context.scene.photographer.comp_wb:
                pfx_node = get_comp_group_node(bpy.context,postfx_grp_name)
                if pfx_node:
                    white_balance_node = get_comp_node_in_group(pfx_node,'wb_curves')
                    if white_balance_node and not white_balance_node.mute:
                        white_balance_node.mute=True
            return None
        else:
            bpy.context.scene.view_settings.white_balance_temperature = DEFAULT_COLOR_TEMPERATURE

    # Convert Color to White Balance
    white_level = convert_rgb_to_white_level(white_balance_color)

    if bpy.context.scene.photographer.comp_wb:
        pfx_node = get_comp_group_node(bpy.context,postfx_grp_name)
        if pfx_node:
            white_balance_node = get_comp_node_in_group(pfx_node,'wb_curves')
            if white_balance_node:
                white_balance_node.inputs[3].default_value = (*white_level, 1.0)
    else:
        # Apply values to Red and Blue white levels
        if bpy.context.scene.view_settings.curve_mapping:
            bpy.context.scene.view_settings.curve_mapping.white_level = white_level
    
    set_tint(self,self.tint)

    #Little trick to update viewport as Color Management Curves don't update automatically
    exposure = bpy.context.scene.view_settings.exposure
    bpy.context.scene.view_settings.exposure = exposure

    return None

def get_preview_color_tint(self):
    return self.get('preview_color_tint', (1,1,1))

def set_preview_color_tint(self,value):
    return None

def get_tint(self):
    return self.get('tint', DEFAULT_TINT)

def set_tint(self, value):
    self['tint'] = value
    self['preview_color_tint'] = convert_tint_to_color_preview(value)

    prefs = bpy.context.preferences.addons[__package__].preferences

    if bpy.app.version >= (4,3,0):
        if prefs.color_temperature_mode == 'BLENDER':
            if bpy.context.scene.view_settings.curve_mapping:
                bpy.context.scene.view_settings.curve_mapping.white_level = (1,1,1)
            bpy.context.scene.view_settings.white_balance_tint = value
            if bpy.context.scene.photographer.comp_wb:
                pfx_node = get_comp_group_node(bpy.context,postfx_grp_name)
                if pfx_node:
                    white_balance_node = get_comp_node_in_group(pfx_node,'wb_curves')
                    if white_balance_node and not white_balance_node.mute:
                        white_balance_node.mute=True
            return None
        else:
            bpy.context.scene.view_settings.white_balance_tint = 10

    rgb = convert_temperature_to_rgb(self.color_temperature)
    if prefs.color_temperature_mode == 'ALGORITHM':
        white_level_g = convert_rgb_to_white_level(rgb)[1]
    elif prefs.color_temperature_mode == 'BLACKBODY':
        white_level_g = convert_rgb_to_white_level(rgb)[1]
    else:
        white_level_g = 1

    if self.tint < 0:
        tint_curve_mult = self.tint / 200 + white_level_g # Diving by 200 instead of 100 to avoid green level to go lower than 0.5. Gives more precision to the slider.
    else:
        tint_curve_mult = self.tint / 50 + white_level_g # Diving by 50 to avoid green level to go higher than 3. Gives more precision to the slider.

    if tint_curve_mult < 0.01:
        tint_curve_mult = 0.01

    if bpy.context.scene.photographer.comp_wb:
        pfx_node = get_comp_group_node(bpy.context,postfx_grp_name)
        if pfx_node:
            white_balance_node = get_comp_node_in_group(pfx_node,'wb_curves')
            if white_balance_node:
                white_balance_node.inputs[3].default_value[1] = tint_curve_mult
                
    else:
        # Apply value to Green white level
        bpy.context.scene.view_settings.curve_mapping.white_level[1] = tint_curve_mult

        #Little trick to update viewport as Color Management Curves don't update automatically
        exposure = bpy.context.scene.view_settings.exposure
        bpy.context.scene.view_settings.exposure = exposure
    return None

def convert_tint_to_color_preview(color_tint):
    red = 1.0
    green = 1.0
    blue = 1.0

    if color_tint < 0:
        red = red + color_tint / 150 # Dividing with 150.
        #Not an accurate match to the actual Tint math, purposefully different so the preview color is pleasing
        blue = blue + color_tint / 150

    if color_tint > 0:
        green = green - color_tint / 150

    return red, green, blue

def update_wb_color(self,context):
    picked_color = (self.wb_color[0],self.wb_color[1],self.wb_color[2])
    convert_rgb_to_whitebalance(picked_color, True)

def update_wb_enabled(self,context):
    update = should_update(self,context,"wb_enabled")
    if self.wb_enabled:
        if update:
            prefs = bpy.context.preferences.addons[__package__].preferences

            if prefs.color_temperature_mode == 'BLENDER' and bpy.app.version >= (4,3,0):
                bpy.context.scene.view_settings.use_white_balance = True
            else:
                if bpy.app.version >= (4,3,0) and bpy.context.scene.view_settings.use_white_balance:
                    bpy.context.scene.view_settings.use_white_balance = False
                if not bpy.context.scene.view_settings.use_curve_mapping:
                    bpy.context.scene.view_settings.use_curve_mapping = True

            set_color_temperature(self, self.color_temperature)
            set_tint(self, self.tint)

            # Update Apply at Compositing
            pfx_node = get_comp_group_node(context,postfx_grp_name)
        
            if pfx_node:
                # Make sure PostFX node is also enabled
                if pfx_node.mute:
                    pfx_node.mute = False

                # Get White Balance node in PFX group
                white_balance_node = get_comp_node_in_group(pfx_node,'wb_curves')
                if white_balance_node:
                    white_balance_node.mute = not context.scene.photographer.comp_wb

    # Never reached as we are using update_settings and reset_wb function
    # else:
    #     bpy.context.scene.view_settings.curve_mapping.white_level = (1,1,1)
    #     if bpy.app.version >= (4,3,0):
    #         bpy.context.scene.view_settings.use_white_balance = False

def update_af_continuous(self,context):
    global stored_dof_objects
    if self.af_continuous_enabled:
        # Disable Focus Plane
        if self.show_focus_plane:
            self.show_focus_plane = False

        # Hide DoF objects that create render refresh loop
        stored_dof_objects = hide_dof_objects()

        if self.id_data.dof.focus_object is not None:
            self.report({'WARNING'}, "There is an object set as focus target which will override the results of the Autofocus.")

        self.id_data.show_limits = True
        bpy.app.timers.register(focus_continuous)
        if self.af_animate:
            bpy.app.handlers.frame_change_pre.append(stop_playback)
    else:
        for o in stored_dof_objects:
            o.hide_viewport = False
        stored_dof_objects = []
        self.id_data.show_limits = False
        if bpy.app.timers.is_registered(focus_continuous):
            bpy.app.timers.unregister(focus_continuous)

# Update Sensor Size
def update_sensor_type(self,context):
    cam = self.id_data
    if self.sensor_type != 'Custom':
        width, height = camera_sensors.sensor_types[self.sensor_type]
        cam.sensor_width = width
        cam.sensor_height = height

    if self.fit_inside_sensor:
        update_sensor_fit(self,context)

    # Refresh viewport and render
    self.id_data.sensor_width = self.id_data.sensor_width

def get_sensor_type(self):
    return self.get('sensor_type', 0)

def set_sensor_type(self,value):
    self['sensor_type'] = value
    update_sensor_type(self,bpy.context)
    return None

def lock_camera_button(self, context):
    # Hide Camera Lock button if not enabled in preferences
    if bpy.context.preferences.addons[__package__].preferences.show_cam_buttons_pref:
        # for area in bpy.context.screen.areas:
        if context.area.type == 'VIEW_3D':
            if context.area.spaces[0].region_3d.view_perspective == 'CAMERA' :
                if context.scene.camera:
                    if context.scene.camera.type == 'CAMERA' :
                        if context.area.spaces[0].lock_camera:
                            if bpy.app.version >= (4,4,0):
                                icon="VIEW_LOCKED"
                            else:
                                icon="LOCKVIEW_ON"
                        else:
                            if bpy.app.version >= (4,4,0):
                                icon="VIEW_UNLOCKED"
                            else:
                                icon="LOCKVIEW_OFF"
                        self.layout.prop(context.area.spaces[0], "lock_camera", text="", icon=icon )
                        row = self.layout.row(align=True)
                        row.scale_x = 0.7
                        row.operator('view3d.zoom_camera_1_to_1', text='1:1')

def get_use_dof(self):
    return self.id_data.dof.use_dof

def set_use_dof(self, value):
    cam_obj = [o for o in bpy.data.objects if o.type == 'CAMERA' and o.data is self.id_data][0]
    if self.show_focus_plane:
        for c in cam_obj.children:
            if c.get("is_focus_plane", False):
                if isinstance(c, bpy.types.Object):
                    c.hide_viewport = not value
    if self.opt_vignetting:
        for c in cam_obj.children:
            if c.get("is_opt_vignetting", False):
                if isinstance(c, bpy.types.Object):
                    c.hide_viewport = not value
    if self.bokeh:
        for c in cam_obj.children:
            if c.get("is_bokeh_plane", False):
                if isinstance(c, bpy.types.Object):
                    c.hide_viewport = not value
    self.id_data.dof.use_dof = value
    return None

def get_focus_plane_color(self):
    return self.get('focus_plane_color',  (1,0,0,0.4))

def set_focus_plane_color(self,value):
    self['focus_plane_color'] = value
    # Get Camera Object
    cam_obj = [o for o in bpy.data.objects if o.type == 'CAMERA' and o.data is self.id_data][0]
    # Get Focus Plane as children object with "is_focus_plane"
    for c in cam_obj.children:
        if c.get("is_focus_plane", False):
            # Get first material
            if c.data.materials:
                # Assign to 1st material slot
                mat = c.data.materials[0]
                mat.diffuse_color = value
                # New shader with Light path
                mix_node = False
                for node in mat.node_tree.nodes:
                    if node.name == "Focus Plane Color":
                        mix_node = node
                if mix_node:
                    mix_node.inputs[2].default_value = value
                # Keep for old scenes
                else:
                    mat.node_tree.nodes["Emission"].inputs[0].default_value = value
                if mat.node_tree.nodes.get('Alpha',False):
                    mat.node_tree.nodes["Alpha"].outputs[0].default_value = value[3]
    return None

def get_focus_plane_edge(self):
    return self.get('focus_plane_edge',  0.5)

def set_focus_plane_edge(self,value):
    self['focus_plane_edge'] = value
    # Get Camera Object
    cam_obj = [o for o in bpy.data.objects if o.type == 'CAMERA' and o.data is self.id_data][0]
    # Get Focus Plane as children object with "is_focus_plane"
    for c in cam_obj.children:
        if c.get("is_focus_plane", False):
            # Get first material
            if c.data.materials:
                # Assign to 1st material slot
                mat = c.data.materials[0]
                if mat.node_tree.nodes.get('Edge Detection',False):
                    mat.node_tree.nodes["Edge Detection"].outputs[0].default_value = value * 10
    return None

def worlds_items(self,context):
    global WORLDS
    WORLDS = []
    for w in bpy.data.worlds:
        WORLDS.append((w.name,w.name,''))
    return WORLDS

def update_world(self,context): 
    update = should_update(self,context,"override_world")
    if self.override_world and update:
        # Do not update the world if it's already the right one, fixes freezes
        if self.cam_world:
            if context.scene.world != self.cam_world:
                context.scene.world = self.cam_world
            # Make sure the world gets saved even if not looking through the camera
            self.cam_world.use_fake_user = True
    # Refresh HDRI preview
    # if bpy.context.preferences.addons[__package__].preferences.hdri_lib_path:
    #     if context.scene.world and context.scene.world.get('is_world_hdri',False):
    #         bpy.ops.lightmixer.refresh_hdri_preview()
    wd_lightmixer = context.scene.world.lightmixer
    set_film_transparent(wd_lightmixer,wd_lightmixer.film_transparent)
    update_hdri_ground(context)

def view_layers_items(self,context):
    global VIEW_LAYERS
    VIEW_LAYERS = []
    for vl in context.scene.view_layers:
        VIEW_LAYERS.append((vl.name,vl.name,''))
    return VIEW_LAYERS

def update_active_view_layer(self,context):
    update_cam_view_layer(self.id_data,context)

def update_lock_vfov(self,context):
    if self.lock_vertical_fov:
        self.id_data.sensor_fit = "VERTICAL"
    else:
        if self.fit_inside_sensor:
            update_sensor_fit(self,context)
        else:
            self.id_data.sensor_fit = "AUTO"

def update_frames(self,context):
    update = should_update(self,context,"override_frames")
    if self.override_frames and update:
        if context.scene.renderqueue.frame_mode == 'STILL':
            context.scene.frame_current = self.cam_frame_current
        else:
            context.scene.frame_start = self.cam_frame_start
            context.scene.frame_end = self.cam_frame_end

def update_frame_start(self,context):
    update = should_update(self,context,"override_frames")
    if self.override_frames and update:
        if self.cam_frame_start > self.cam_frame_end: self.cam_frame_end = self.cam_frame_start
        context.scene.frame_start = self.cam_frame_start

def update_frame_end(self,context):
    update = should_update(self,context,"override_frames")
    if self.override_frames and update:
        if self.cam_frame_end < self.cam_frame_start: self.cam_frame_start = self.cam_frame_end
        context.scene.frame_end = self.cam_frame_end

def update_samples(self,context):
    update = should_update(self,context,"override_samples")
    if self.override_samples and update:
        if context.scene.render.engine == 'CYCLES':
            context.scene.cycles.samples = self.samples
            context.scene.cycles.use_adaptive_threshold = self.use_adaptive_threshold
            context.scene.cycles.adaptive_threshold = self.adaptive_threshold
        elif context.scene.render.engine == 'BLENDER_EEVEE':
            context.scene.eevee.taa_render_samples = self.taa_render_samples
        elif context.scene.render.engine == 'BLENDER_EEVEE_NEXT':
            context.scene.eevee.taa_samples = self.taa_render_samples

class PHOTOGRAPHER_OT_MakeCamActive(bpy.types.Operator):
    bl_idname = "photographer.makecamactive"
    bl_label = "Make Camera Active"
    bl_description = "Make this Camera the active camera in the Scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.camera = bpy.context.active_object
        settings = context.scene.camera.data.photographer
        update_settings(settings,context)
        bpy.ops.photographer.set_view_layer(view_layer=settings.active_view_layer, use_scene_camera=True)
        return{'FINISHED'}

class PHOTOGRAPHER_OT_ApplyPhotographerSettings(bpy.types.Operator):
    bl_idname = "photographer.applyphotographersettings"
    bl_label = "Refresh Photographer Settings"
    bl_description = "If you changed Render engines and settings outside " \
                    "of the Photographer addon, reapply the settings to make sure they are up to date"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.camera.data.photographer
        update_settings(settings,context)
        bokeh.update_bokeh_size(self,context)
        bpy.ops.photographer.applylightsettings()
        bpy.ops.photographer.set_view_layer(view_layer=settings.active_view_layer, use_scene_camera=True)
        return{'FINISHED'}

class PHOTOGRAPHER_OT_SelectActiveCam(bpy.types.Operator):
    bl_idname = "photographer.selectactivecam"
    bl_label = "Select Active Camera"
    bl_description = "Select the Active Camera in the Scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.data.objects[context.scene.camera.name].select_set(True)
        context.view_layer.objects.active = context.scene.camera
        return{'FINISHED'}

class PHOTOGRAPHER_OT_SetShutterAngle(bpy.types.Operator):
    bl_idname = "photographer.setshutterangle"
    bl_label = "Switch to Shutter Angle"
    bl_description = "Switch to Shutter Angle"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            context.camera.photographer.shutter_mode = 'ANGLE'
        except AttributeError:
            context.scene.camera.data.photographer.shutter_mode = 'ANGLE'
        settings = context.scene.camera.data.photographer
        update_settings(settings,context)
        return{'FINISHED'}

class PHOTOGRAPHER_OT_SetShutterSpeed(bpy.types.Operator):
    bl_idname = "photographer.setshutterspeed"
    bl_label = "Switch to Shutter Speed"
    bl_description = "Switch to Shutter Speed"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            context.camera.photographer.shutter_mode = 'SPEED'
        except AttributeError:
            context.scene.camera.data.photographer.shutter_mode = 'SPEED'
        settings = context.scene.camera.data.photographer
        update_settings(settings,context)
        return{'FINISHED'}

class PHOTOGRAPHER_OT_RenderMotionBlur(bpy.types.Operator):
    bl_idname = "photographer.rendermotionblur"
    bl_label = "Enable Motion Blur render"
    bl_description = "Enable Motion Blur in the Render Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.render.use_motion_blur = True
        context.scene.eevee.use_motion_blur = True
        return{'FINISHED'}

class PhotographerCameraSettings(bpy.types.PropertyGroup):

    renderable : bpy.props.BoolProperty(
        name = "Include Camera in Render Queue", description = "The camera will be rendered when using Render All Enabled",
        default = True,
    )
    target_enabled : bpy.props.BoolProperty(
        name = "Camera Target", description = "Camera Target Tracking: Place a target on an object and the camera "
        "will aim at it and keep it centered",
        options = {'HIDDEN'},
        default = False,
    )
    sensor_type : bpy.props.EnumProperty(
        name = "Sensor Type", description = "Camera Sensor Size",
        items = camera_sensors.sensor_type_items,
        # default = 0,
        get = get_sensor_type,
        set = set_sensor_type,
    )
    fisheye : bpy.props.BoolProperty(
        name = "Fisheye",
        default = False,
        options = {'HIDDEN'},
        update = update_fisheye,
    )
    fisheye_focal : bpy.props.FloatProperty(
        name = "Fisheye Focal Length", description = "Fisheye Focal Length in mm",
        default = 50, step = 100,
        min = 1, max = 100, precision = 0,
        unit = 'CAMERA',
        get = get_fisheye_focal,
        set = set_fisheye_focal,
    )
    focal : bpy.props.FloatProperty(
        name = "Focal Length", description = "Focal Length in mm",
        default = 50, step = 100,
        min = 1, precision = 0,
        unit = 'CAMERA',
        get = get_focal,
        set = set_focal,
    )
    lens_shift_compensated : bpy.props.BoolProperty(
        name = "Compensated",
        description =("Maintains framing when applying Lens Shift."
            "Disabling it will revert to default Blender behavior"),
        default = True,
        options = {'HIDDEN'},
        update = update_ls_compensated,
    )
    lens_shift : bpy.props.FloatProperty(
        name = "Lens Shift V", description = "Adjusts Vertical Shift while maintaining framing",
        default = 0,
        soft_min = -2, soft_max = 2,
        precision = 3,
        options = {'HIDDEN'},
        get = get_lens_shift_y,
        set = set_lens_shift_y,
    )
    lens_shift_x : bpy.props.FloatProperty(
        name = "Lens Shift H", description = "Adjusts Horizontal Shift while maintaining framing",
        default = 0,
        soft_min = -2, soft_max = 2,
        precision = 3,
        options = {'HIDDEN'},
        get = get_lens_shift_x,
        set = set_lens_shift_x,
    )
    # breathing : bpy.props.FloatProperty(
    #     name = "Focus Breathing", description = "Changing the focus distance will slightly affect the focal length."
    #     "Negative values will narrow the Field of View, Positive values with expand the Field of View",
    #     default = 0,
    #     soft_min = -1, soft_max = 1,
    #     get = get_breathing,
    #     set = set_breathing,
    # )
    exposure_enabled : bpy.props.BoolProperty(
        name = "Enable Exposure Controls",
        default = False,
        options = {'HIDDEN'},
        update = update_settings
    )
    motionblur_enabled : bpy.props.BoolProperty(
        name = "Enable Motion Blur control",
        description = "Motion Blur will be controlled by the Shutter Speed / Shutter Angle values",
        default = False,
        options = {'HIDDEN'},
        get = get_motionblur_enabled,
        set = set_motionblur_enabled,
    )

    # Exposure properties
    exposure_mode : bpy.props.EnumProperty(
        name = "Exposure Mode",
        description = ("EV mode: Only adjusts the brightness of the images without affecting Depth of Field or Motion Blur. \n"
                        "Auto Exposure: Samples the viewport luminance and adjusts the Exposure value until the average luminance reaches half-grey (sRGB 127). \n"
                        "Manual: Exposure is calculated using Shutter Speed or Angle, Aperture and ISO. These will also affect Motion Blur and Depth of Field"),
        items = [('EV','EV', 'Exposure Value'),('AUTO','Auto','Auto Exposure metering'),('MANUAL','Manual','Manual Settings using Shutter Speed, Aperture and ISO')],
        default = 'EV', #bpy.context.preferences.addons[__package__].preferences.exposure_mode_pref if bpy.context.preferences.addons[__package__].preferences.exposure_mode_pref else 'EV',
        options = {'HIDDEN'},
        update = update_settings
    )
    ev : bpy.props.FloatProperty(
        name = "Exposure Value",
        description = "",
        default = base_ev, #- math.log2(0.78 / bpy.context.preferences.addons[__package__].preferences.lens_attenuation),
        soft_min = -6, soft_max = 16, step = 1, precision = 2,
        get = get_ev,
        set = set_ev,
    )
    exposure_compensation : bpy.props.FloatProperty(
        name = "Exposure Compensation", description = "Additive Exposure Value adjustment",
        default = 0, soft_min = -10,    soft_max = 10, step = 1, precision = 2,
        get = get_exposure_compensation,
        set = set_exposure_compensation,
    )
    ae : bpy.props.FloatProperty(
        name = "Auto Exposure", description = "Auto Exposure compensation value",
        default = 0, soft_min = -3, soft_max = 3, step = 25, precision = 2,
        get = get_ae,
        set = set_ae,
    )
    center_weight : bpy.props.IntProperty(
        name = "Center Weight", description = "Gives more weight to the center of the frame instead of the entire viewport",
        default = 25, min = 0, max = 100,
        subtype = 'PERCENTAGE'
    )
    ae_speed : bpy.props.FloatProperty(
        name = "AE Speed", description = "Speed at which the Auto Exposure will reach its luminance target",
        default = 0.1, min = 0.02, soft_max = 0.5, max = 1,
    )
    ae_bake_step: bpy.props.IntProperty(
        name = "Frame Step",
        description = "Sets a key every frame step",
        default = 24, min = 1,
    )
    ae_bake_wait_time : bpy.props.FloatProperty(
        name = "Wait Time",
        description = "Time in seconds for the render to progress before calculating Auto Exposure",
        default = 2, min = 0.1, soft_max = 10,
    )
    falsecolor_enabled : bpy.props.BoolProperty(
        name = "False Color",
        description = "Enable False Color view transform to validate your exposure",
        default = False,
        options = {'HIDDEN'},
        update = update_falsecolor,
    )
    colorchart_enabled : bpy.props.BoolProperty(
        name = "Color Chart",
        description = "Enable Color Chart to preview colors and grey swatches",
        default = False,
        options = {'HIDDEN'},
        update = update_colorchart,
    )
    wb_enabled : bpy.props.BoolProperty(
        name = "Enable White Balance controls",
        description = "Adjusts colors using Temperature and Tint values",
        default = False,
        options = {'HIDDEN'},
        update = update_settings
    )
    # Shutter Speed properties
    shutter_mode : bpy.props.EnumProperty(
        name = "Shutter Mode", description = "Switch between Shutter Speed and Shutter Angle",
        items = [('SPEED','Shutter Speed',''),('ANGLE','Shutter Angle', '')],
        default = 'SPEED',
        options = {'HIDDEN'},
        update = update_settings,
    )
    shutter_speed : bpy.props.FloatProperty(
        name = "Shutter Speed 1/X second", description = "Shutter Speed - controls the amount of Motion Blur",
        default = 100, soft_min = 0.1, soft_max = 1000,    precision = 2,
        get = get_shutter_speed,
        set = set_shutter_speed,
    )
    shutter_speed_slider_enable : bpy.props.BoolProperty(
        name = "Shutter Speed Slider", description = "Enable Shutter Speed slider instead of preset list",
        # default = bpy.context.preferences.addons[__package__].preferences.shutter_speed_slider_pref if bpy.context.preferences.addons[__package__].preferences.shutter_speed_slider_pref else False,
        options = {'HIDDEN'},
        update = update_shutter_speed,
    )
    shutter_speed_preset : bpy.props.EnumProperty(
        name = "Shutter Speed",    description = "Camera Shutter Speed",
        items = [('0.033','30 "',''),('0.04','25 "',''),('0.05','20 "',''),('0.066','15 "',''),('0.077','13 "',''),('0.1','10 "',''),('0.125','8 "',''),('0.1666','6 "',''),('0.2','5 "',''),('0.25','4 "',''),('0.3125','3.2 "',''),('0.4','2.5 "',''),
        ('0.5','2 "',''),('0.625','1.6 "',''),('0.769','1.3 "',''),('1','1 "',''),('1.25','0.8 "',''),('1.666','0.6 "',''),('2','0.5 "',''),('2.5','0.4 "',''),('3.333','0.3 "',''),('4','1 / 4 s',''),('5','1 / 5 s',''),('6','1 / 6 s',''),
        ('8','1 / 8 s',''),('10','1 / 10 s',''),('13','1 / 13 s',''),('15','1 / 15 s',''),('20','1 / 20 s',''),('25','1 / 25 s',''),('30','1 / 30 s',''),('40','1 / 40 s',''),('50','1 / 50 s',''),('60','1 / 60 s',''),('80','1 / 80 s',''),
        ('100','1 / 100 s',''),('125','1 / 125 s',''),('160','1 / 160 s',''),('200','1 / 200 s',''),('250','1 / 250 s',''),('320','1 / 320 s',''),('400','1 / 400 s',''),('500','1 / 500 s',''),('640','1 / 640 s',''),('800','1 / 800 s',''),
        ('1000','1 / 1000 s',''),('1250','1 / 1250 s',''),('1600','1 / 1600 s',''),('2000','1 / 2000 s',''),('2500','1 / 2500 s',''),('3200','1 / 3200 s',''),('4000','1 / 4000 s',''),('5000','1 / 5000 s',''),('6400','1 / 6400 s',''),('8000','1 / 8000 s', '')],
        default = '100',
        get = get_shutter_speed_preset,
        set = set_shutter_speed_preset,
    )

    # Shutter Angle properties
    shutter_angle : bpy.props.FloatProperty(
        name = "Shutter Angle", description = "Shutter Angle in degrees - controls the Shutter Speed and amount of Motion Blur",
        default = 180, soft_min = 1, soft_max = 360, precision = 1,
        get = get_shutter_angle,
        set = set_shutter_angle,
    )
    shutter_angle_preset : bpy.props.EnumProperty(
        name = "Shutter Angle",    description = "Camera Shutter Angle",
        items = [('8.6','8.6 degree',''),('11','11 degree',''),('22.5','22.5 degree',''),
        ('45','45 degree',''),('72','72 degree',''),('90','90 degree',''),
        ('144','144 degree',''),('172.8','172.8 degree',''),('180','180 degree',''),
        ('270','270 degree',''),('360','360 degree','')],
        default = '180',
        get = get_shutter_angle_preset,
        set = set_shutter_angle_preset,
    )

    # Aperture properties
    aperture : bpy.props.FloatProperty(
        name = "Aperture F-stop", description = "Lens aperture - controls the Depth of Field",
        default = 2.4, min = 0, soft_min = 0.1, soft_max = 32, precision = 1, step = 100,
        get = get_aperture,
        set = set_aperture,
    )
    aperture_slider_enable : bpy.props.BoolProperty(
        name = "Aperture Slider", description = "Enable Aperture slider instead of preset list",
        # default = bpy.context.preferences.addons[__package__].preferences.aperture_slider_pref,
        options = {'HIDDEN'},
        update = update_aperture
    )
    aperture_preset : bpy.props.EnumProperty(
        name = "Lens Aperture Presets",     description = "Lens Aperture",
        items = [('0.95','f / 0.95',''),('1.2','f / 1.2',''),('1.4','f / 1.4',''),('1.8','f / 1.8',''),('2.0','f / 2.0',''),('2.4','f / 2.4',''),('2.8','f / 2.8',''),('3.5','f / 3.5',''),    ('4.0','f / 4.0',''),
        ('4.9','f / 4.9',''),('5.6','f / 5.6',''),('6.7','f / 6.7',''),('8.0','f / 8.0',''),('9.3','f / 9.3',''),('11','f / 11',''),('13','f / 13',''),('16','f / 16',''),('20','f / 20',''),('22','f / 22','')],
        default = '2.8',
        get = get_aperture_preset,
        set = set_aperture_preset,
    )

    # ISO properties
    iso : bpy.props.IntProperty(
        name = "ISO", description = "ISO setting",
        default = 100, soft_min = 50, soft_max = 12800,
        get = get_iso,
        set = set_iso,
    )
    iso_slider_enable : bpy.props.BoolProperty(
        name = "Iso Slider", description = "Enable ISO setting slider instead of preset list",
        # default = bpy.context.preferences.addons[__package__].preferences.iso_slider_pref,
        options = {'HIDDEN'},
        update = update_ev,
    )
    iso_preset : bpy.props.EnumProperty(
        name = "Iso Presets", description = "Camera Sensitivity",
        items = [('100','100',''),('125','125',''),('160','160',''),('200','200',''),('250','250',''),('320','320',''),('400','400',''),('500','500',''),('640','640',''),('800','800',''),('1000','1000',''),('1250','1250',''),
        ('1600','1600',''),('2000','2000',''),('2500','2500',''),('3200','3200',''),('4000','4000',''),('5000','5000',''),('6400','6400',''),('8000','8000',''),('10000','10000',''),('12800','12800',''),('16000','16000',''),
        ('20000','20000',''),('25600','25600',''),('32000','32000',''),('40000','40000',''),('51200','51200','')],
        default = '100',
        update = update_ev,
        get = get_iso_preset,
        set = set_iso_preset,
    )

    # White Balance properties
    wb_color : bpy.props.FloatVectorProperty(
        name='Color Picker', description="Use the Color Picker on the viewport and pick a grey material in your scene to do the white balance",
        subtype='COLOR', min=0.0, max=1.0, size=3, default=(0.5,0.5,0.5),
        options = {'HIDDEN'},
        update = update_wb_color,
    )
    color_temperature : bpy.props.IntProperty(
        name="Color Temperature", description=color_temp_desc,
        min=min_color_temperature, max=max_color_temperature, default=DEFAULT_COLOR_TEMPERATURE,
        get=get_color_temperature,
        set=set_color_temperature,
    )
    preview_color_temp : bpy.props.FloatVectorProperty(
        name='Preview Color', description="Color Temperature preview color",
        subtype='COLOR', min=0.0, max=1.0, size=3,
        options = {'HIDDEN'},
        get=get_preview_color_temp,
        set=set_preview_color_temp,
    )
    tint : bpy.props.IntProperty(
        name="Tint", description="Adjusts the amoung of Green or Magenta cast",
        min=min_color_tint, max=max_color_tint, default=DEFAULT_TINT,
        get=get_tint,
        set=set_tint,
    )
    preview_color_tint : bpy.props.FloatVectorProperty(
        name="Preview Color Tint", description="Tint preview color",
        subtype='COLOR', min=0.0, max=1.0, size=3,
        options = {'HIDDEN'},
        get=get_preview_color_tint,
        set=set_preview_color_tint,
    )
    

    # Resolution properties
    resolution_enabled : bpy.props.BoolProperty(
        name = "Enable Resolution override for this Camera",
        default = False,
        update = update_settings,
    )
    resolution_mode : bpy.props.EnumProperty(
        name = "Format", description = "Choose Custom Resolutions or Ratio presets",
        items = [('CUSTOM_RES','Custom Resolution',''),('CUSTOM_RATIO','Custom Ratio',''),
                ('11','1:1', ''),('32','3:2', ''),('43','4:3', ''),('67','6:7', ''),
                ('169','16:9', ''),('2351','2.35:1', ''),('2391','2.39:1', '')],
        options = {'HIDDEN'},
        update = update_resolution,
    )
    resolution_x : bpy.props.IntProperty(
        name = "X", description = "Horizontal Resolution",
        default = 1920, min = 0, subtype = 'PIXEL',
        options = {'HIDDEN'},
        update = update_resolution_value,
    )
    resolution_y : bpy.props.IntProperty(
        name = "Y", description = "Vertical Resolution",
        min = 0, default = 1080, subtype='PIXEL',
        options = {'HIDDEN'},
        update = update_resolution_value,
    )
    ratio_x : bpy.props.FloatProperty(
        name = "X", description = "Horizontal Ratio",
        min = 0.01, default = 16, precision = 2,
        options = {'HIDDEN'},
        update = update_ratio_value,
    )
    ratio_y : bpy.props.FloatProperty(
        name = "Y", description = "Vertical Ratio",
        min = 0.01, default = 9, precision = 2,
        options = {'HIDDEN'},
        update = update_ratio_value,
    )
    longedge : bpy.props.IntProperty(
        name = "Long Edge", description = "Long Edge Resolution",
        default = 1920, min = 0, subtype = 'PIXEL',
        options = {'HIDDEN'},
        update = update_resolution,
    )
    resolution_rotation : bpy.props.EnumProperty(
        name = "Orientation", description = "Rotation of the camera",
        items = [('LANDSCAPE','Landscape','','',0),('PORTRAIT','Portrait','','',1)],
        options = {'HIDDEN'},
        get = get_resolution_rotation,
        set = set_resolution_rotation,
    )
    fit_inside_sensor : bpy.props.BoolProperty(
        name = "Fit inside Sensor",
        description = "Automatically adjusts the Camera Sensor fit in order to make the Resolution fit inside the sensor. \n"
        "This is a smarter Auto Fit than the one provided by Blender.\n"
        "FOV calculation will be more accurate when trying to match a photo",
        default = False,
        options = {'HIDDEN'},
        update = update_fit_inside_sensor,
    )
    resize_shift_x : bpy.props.FloatProperty(default=0.0)
    resize_shift_y : bpy.props.FloatProperty(default=0.0)
    resize_stored_angle : bpy.props.FloatProperty(default=0.0)
    resize_orig_res_x : bpy.props.IntProperty(default=0)
    resize_orig_res_y : bpy.props.IntProperty(default=0)
    resize_orig_shift_x : bpy.props.FloatProperty(default=0)
    resize_orig_shift_y : bpy.props.FloatProperty(default=0)

    # View Layers properties
    view_layer_enabled : bpy.props.BoolProperty(
        name = "Enable View Layers override for this Camera",
        default = False,
        update = update_active_view_layer,
    )
    
    # AF-C property
    af_continuous_enabled : bpy.props.BoolProperty(
        name = "AF-C", description = "Autofocus Continuous: Realtime focus on the center of the frame.\n"
        "Requires to look through the Camera",
        default = False,
        options = {'HIDDEN'},
        update = update_af_continuous,
    )
    af_continuous_interval : bpy.props.FloatProperty(
        name="AF-C interval", description="Number of seconds between each autofocus update",
        default = 0.6, soft_min = 0.05,    min = 0.01,    soft_max = 3, precision = 2,
        subtype='TIME'
    )
    af_animate : bpy.props.BoolProperty(
        name = "Autofocus Auto-Key", description = "Automatically set keys on focus distance when using AF-S and AF-C",
        options = {'HIDDEN'},
        default = False,
    )
    # Drone Camera Settings
    match_speed : bpy.props.FloatProperty(
        name = "Transition Speed", description = "Speed at which it switches to the other camera. 4 is instant",
        default = 0.2, min = 0.01, soft_min = 0.02, soft_max= 1, max = 4,
    )
    is_matching : bpy.props.BoolProperty(
        name = "Is matchin camera",
        default = False,
    )
    target_camera : bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Target Camera", description="The camera that the Drone Camera will match"
    )
    # Light Threshold property
    light_threshold_warning:bpy.props.BoolProperty(
        name = "Light Threshold Warning",
        default = False,
    )
    # Use Dof replicate
    use_dof:bpy.props.BoolProperty(
        name = "Enable Depth of Field",
        default = False,
        options = {'HIDDEN'},
        get = get_use_dof,
        set = set_use_dof,
    )
    # Show Focus Plane
    show_focus_plane:bpy.props.BoolProperty(
        name = "Focus Plane",description="Show Focus Plane debug",
        default = False,
    )
    focus_plane_mat : bpy.props.PointerProperty(
        type=bpy.types.Material,
        name="Focus Plane Material", description="Material used for Focus plane"
    )
    focus_plane_color : bpy.props.FloatVectorProperty(
        name="Color", description="Set Color and Alpha opacity of the Focus Plane debug",
        subtype='COLOR', min=0.0, max=1.0, size=4,
        # default=bpy.context.preferences.addons[__package__].preferences.default_focus_plane_color,
        default=(1.0,0.0,0.0,0.2),
        options = {'HIDDEN'},
        get=get_focus_plane_color,
        set=set_focus_plane_color,
    )
    focus_plane_edge : bpy.props.FloatProperty(
        name = "Edge Detection", description = "Creates an outline where the focus plane meets the objects",
        default = 0.5, min = 0, soft_max= 1,
        get=get_focus_plane_edge,
        set=set_focus_plane_edge,
    )
    dof_limits: bpy.props.EnumProperty(
        name = "DoF Limits", description = "Display settings of Depth of Field limits",
        items = [('OFF','Off',''),('WIRE','Cylinder Wire',''), ('SHADED','Shaded', '')],
        default = 'WIRE',
        options = {'HIDDEN'},
        update = update_dof_limits,       
    )
    # Optical Vignetting
    opt_vignetting : bpy.props.BoolProperty(
        name = "Optical Vignetting",
        description=("Optical Vignetting can create Cat's Eye bokeh or Matte Box mechanical vignetting. \n"
                    "WARNING: Computational-heavy feature, expect longer render times. \n"
                    "Requires a very short clip start that will create Z-fighting issues in the viewport"),
        default = False,
        options = {'HIDDEN'},
        update = bokeh.update_opt_vignetting,
    )
    ov_scale : bpy.props.FloatProperty(
        name = "Optical Vignetting Scale",
        description="Controls the amount of optical vignetting",
        default = 0.5,
        min = 0.05,
        soft_max = 1,
    )
    ov_rotation: bpy.props.FloatProperty(
        name='Rotation',
        default=0, soft_min=-3.14159, soft_max=3.14159, unit='ROTATION',
    )
    opt_vignetting_tex: bpy.props.EnumProperty(
        name="Optical Vignetting Texture",
        items=bokeh.enum_previews_opt_vignetting,
        update=bokeh.update_opt_vignetting_tex,
    )
    # Bokeh
    bokeh : bpy.props.BoolProperty(
        name = "Bokeh Texture",
        description=("Bokeh Texture defines the looks of the Depth of Field, uniformly across the image. \n"
                    "WARNING: Computational-heavy feature, expect longer render times.\n"
                    "Requires a very short clip start that will create Z-fighting issues in the viewport"),
        default = False,
        options = {'HIDDEN'},
        update = bokeh.update_bokeh,
    )
    bokeh_rotation: bpy.props.FloatProperty(
        name='Rotation',
        default=0, soft_min=-3.14159, soft_max=3.14159, unit='ROTATION',
    )
    bokeh_brightness: bpy.props.FloatProperty(
    name='Brightness Multiplier',
    description="Adjusts brightness to compensate for energy loss due to a dark bokeh texture",
    default=1, soft_min=0, soft_max=5,
    )
    bokeh_saturation: bpy.props.FloatProperty(
    name='Saturation',
    description="Adjusts saturation of the texture",
    default=1, soft_min=0, soft_max=5,
    )
    # bokeh_contrast: bpy.props.FloatProperty(
    # name='Contrast',
    # description="Adjust contrast of the bokeh texture to accentuate details",
    # default=0, soft_min=-1, soft_max=1,
    # )
    bokeh_tex: bpy.props.EnumProperty(
        name="Optical Vignetting Texture",
        items=bokeh.enum_previews_bokeh,
        update=bokeh.update_bokeh_tex,
    )
    override_world : bpy.props.BoolProperty(
        name = "Set World per Camera",
        description = ("Requires to override World for each of your cameras, "
                    "or they will use the last World that was applied"),
        default = False,
        options = {'HIDDEN'},
        update = update_settings,
    )
    cam_world: bpy.props.PointerProperty(
        name="World Override",
        type=bpy.types.World,
        options = {'HIDDEN'},
        update = update_world,
    )
    lock_vertical_fov: bpy.props.BoolProperty(
        name = "Lock Vertical FOV",
        description = "Use Vertical Sensor Fit to get correct Field of View when recreating an Anamorphic lens",
        default = False,
        options = {'HIDDEN'},
        update = update_lock_vfov,
    )
    override_frames: bpy.props.BoolProperty(
        name = "Frames Override",
        description = "Requires to override frames for each of your cameras, "
                    "or they will use the last settings that were applied",
        default = False,
        options = {'HIDDEN'},
        update = update_settings,
    )
    cam_frame_start: bpy.props.IntProperty(
        name = "Frame Start",
        description = "Overrides Scene Frame Start for this camera",
        default = 1, min = 0,
        options = {'HIDDEN'},
        update = update_frame_start,
    )
    cam_frame_end: bpy.props.IntProperty(
        name = "Frame End",
        description = "Overrides Scene Frame End for this camera",
        default = 250, min = 0,
        options = {'HIDDEN'},
        update = update_frame_end,
    )
    cam_frame_current: bpy.props.IntProperty(
        name = "Still Current Frame",
        description = "Overrides Scene Current Frame for this camera. \n"
                    "Render Queue is is Still mode. Set Render Queue to Animation mode if you wish to override the frame range",
        default = 1, min = 0,
        options = {'HIDDEN'},
        update = update_frames,
    )
    override_samples: bpy.props.BoolProperty(
        name = "Samples Override",
        description = ("Requires to override Samples for each of your cameras, "
                    "or use the Main Camera to set the fallback value"),
        default = False,
        options = {'HIDDEN'},
        update = update_settings,
    )
    samples: bpy.props.IntProperty(
        name='Max Samples',
        default=4096, min=1,
        options = {'HIDDEN'},
        update = update_settings,
    )
    use_adaptive_threshold: bpy.props.BoolProperty(
        name = 'Noise Threshold',
        default = True,
        options = {'HIDDEN'},
        update = update_settings,
    )
    adaptive_threshold: bpy.props.FloatProperty(
        name='Noise Threshold',
        default=0.01, min=0,max=1,
        options = {'HIDDEN'},
        update = update_settings,
    )
    taa_render_samples: bpy.props.IntProperty(
        name='Samples',
        default=64, min=1,
        options = {'HIDDEN'},
        update = update_settings,
    )
    active_view_layer: bpy.props.EnumProperty(
        name="View Layer Override",
        items = view_layers_items,
        description = "List of View Layers available",
        options = {'HIDDEN'},
        update = update_active_view_layer,
    )
    active_bookmark_index : bpy.props.IntProperty(
        name = "Active Camera Bookmark Index",
        default = -1,
        )
