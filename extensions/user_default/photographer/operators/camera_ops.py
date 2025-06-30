import bpy
from .. import __package__ as base_package
from ..functions.functions import (
    interpolate_float,
    interpolate_int,
    calc_exposure_value,
    list_cameras,
    )
from ..functions.lens_sim_compatibility import is_lens_sim_cam
from .target import get_target,create_target
import mathutils

# DRONE CAMERA #
def interpolate_location(obj, target, speed):

    target_loc = target.matrix_world.to_translation()
    target_rot = target.matrix_world.to_quaternion()
    obj_rot = obj.matrix_world.to_quaternion()

    quat = mathutils.Quaternion(obj_rot).slerp(target_rot,speed)
    rotation_difference = abs(mathutils.Quaternion(target_rot).angle - mathutils.Quaternion(obj_rot).angle)
    obj.rotation_euler = quat.to_euler()

    obj.location = obj.location + (target_loc - obj.location)*speed
    distance = (target_loc - obj.location).length

    return distance,rotation_difference

def match_camera():
    context = bpy.context

    drone_cam_obj = bpy.data.objects.get('DroneCamera')
    if drone_cam_obj:
        drone_cam = drone_cam_obj.data
        mc_pg = drone_cam.photographer

        target_cam_obj = mc_pg.target_camera
        target_cam = target_cam_obj.data
        tc_pg = target_cam.photographer

        # Position speed matching
        position_speed = mc_pg.match_speed / 4 # Slow down transition to avoid very small values
        speed = mc_pg.match_speed  / 4

        # if speed < 1:
        #   speed == 1
        mc_pg.is_matching = True

        distance,rotation_difference = interpolate_location(drone_cam_obj,target_cam_obj, position_speed)

        lens_diff = lens_shift_diff = focus_dist_diff = color_temp_diff = tint_diff = 0
        ev_diff = exp_comp_diff = shutter_speed_diff = shutter_angle_diff = aperture_diff = 0

        # Focal Length
        if drone_cam.lens != target_cam.lens:
            drone_cam.lens, lens_diff = interpolate_float(drone_cam.lens, target_cam.lens, speed)

        # Lens Shit interpolation
        if mc_pg.lens_shift != tc_pg.lens_shift:
            mc_pg.lens_shift, lens_shift_diff = interpolate_float(mc_pg.lens_shift, tc_pg.lens_shift, speed)

        # Focus Distance interpolation
        if not mc_pg.af_continuous_enabled:
            if bpy.context.scene.render.engine == 'LUXCORE':
                drone_cam.luxcore.use_dof = target_cam.luxcore.use_dof
            else:
                drone_cam.dof.use_dof = target_cam.dof.use_dof
            drone_cam.dof.focus_distance, focus_dist_diff = interpolate_float(drone_cam.dof.focus_distance, target_cam.dof.focus_distance, speed)

        # White Balance interpolation
        if tc_pg.wb_enabled:
            mc_pg.wb_enabled = True

            mc_pg.color_temperature, color_temp_diff = interpolate_int(mc_pg.color_temperature, tc_pg.color_temperature, speed)
            mc_pg.tint, tint_diff = interpolate_int(mc_pg.tint, tc_pg.tint, speed)

        # Exposure interpolation
        if tc_pg.exposure_enabled:
            mc_pg.exposure_enabled = True

            mc_pg.exposure_mode = 'EV'
            target_ev = 0.0
            if tc_pg.exposure_mode == 'EV':
                target_ev = tc_pg.ev

            if tc_pg.exposure_mode == 'MANUAL':
                settings = tc_pg
                target_ev = calc_exposure_value(settings,context)

            mc_pg.ev, ev_diff = interpolate_float(mc_pg.ev,target_ev,speed)
            mc_pg.exposure_compensation, exp_comp_diff = interpolate_float(mc_pg.exposure_compensation, tc_pg.exposure_compensation, speed)

        # Motion Blur Shutter Speed or Shutter Angle Interpolation
        if tc_pg.shutter_mode == 'SPEED':
            if tc_pg.shutter_speed_slider_enable == False:
                tc_pg.shutter_speed = float(tc_pg.shutter_speed_preset)

            mc_pg.shutter_speed, shutter_speed_diff = interpolate_float(mc_pg.shutter_speed,tc_pg.shutter_speed,speed)

        if tc_pg.shutter_mode == 'ANGLE':
            if tc_pg.shutter_speed_slider_enable == False:
                tc_pg.shutter_angle = float(tc_pg.shutter_angle_preset)

            mc_pg.shutter_angle, shutter_angle_diff = interpolate_float(mc_pg.shutter_angle,tc_pg.shutter_angle,speed)

        # DOF Interpolation - Aperture
        if tc_pg.aperture_slider_enable == False:
            tc_pg.aperture = float(tc_pg.aperture_preset)

        mc_pg.aperture, aperture_diff = interpolate_float(mc_pg.aperture,tc_pg.aperture,speed)

        # Sensor Type
        mc_pg.sensor_type = tc_pg.sensor_type
        drone_cam.sensor_width = target_cam.sensor_width

        # Bools
        mc_pg.fisheye = tc_pg.fisheye
        drone_cam.dof.use_dof = target_cam.dof.use_dof
        mc_pg.motionblur_enabled = tc_pg.motionblur_enabled

        # Resolution - CRASH WITH ANIMATION RENDER
        # if tc_pg.resolution_enabled:
        #     mc_pg.resolution_enabled = True
        #     mc_pg.resolution_x = interpolate_float(mc_pg.resolution_x, tc_pg.resolution_x, speed)
        #     mc_pg.resolution_y = interpolate_float(mc_pg.resolution_y, tc_pg.resolution_y, speed)

        # Little trick to update viewport
        # bpy.ops.photographer.applyphotographersettings()

        # print (length)
        threshold = 0.001
        diffs = (
            distance,
            rotation_difference,
            lens_diff,
            lens_shift_diff,
            focus_dist_diff,
            color_temp_diff,
            tint_diff,
            ev_diff,
            exp_comp_diff,
            shutter_speed_diff,
            shutter_angle_diff,
            aperture_diff,
            )
        # for d in diffs:
        #     if d > threshold:
        #         print (diffs.index(d))
        #         stop = True
        #     else:
        #         stop = False
        #         break

        if all( d < threshold for d in diffs ):
            stop = True
            print ("Drone Camera: Matching done.")
        else:
            stop = False

        # if self.timer >= 15:
        #     stop = True
        #     print ("Drone Camera: Matching timed out. Consider increasing matching speed.")

        if stop:
            mc_pg.is_matching = False
            return None

        else:
            # self.timer += 0.01
            return 0.01

# SET CAMERA VIEW
class PHOTOGRAPHER_OT_LookThrough(bpy.types.Operator):
    bl_idname = 'photographer.look_through'
    bl_label = 'Look through'
    bl_description = ("Set as Scene Camera and look through it. \n"
                      "Ctrl-Click to set the Scene Camera without looking through it. \n"
                      "Shift-Click to set the Scene Camera and select it at the same time. \n"
                      "Alt-Click to make it the Main Camera")
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()
    look_through = True

    def execute(self,context):
 
        if bpy.app.timers.is_registered(match_camera):
            print ("Drone Camera: Canceling matching")
            bpy.app.timers.unregister(match_camera)
            drone_cam_obj = bpy.data.objects.get('DroneCamera')
            drone_cam_obj.data.photographer.is_matching = False

        obj = bpy.data.objects
        cam_obj = obj.get(self.camera)

        # Will remove after everyone will have upgraded Lens Sim to 1.0.1
        is_lens_sim_cam(cam_obj)

        if cam_obj.data.show_name != True:
            cam_obj.data.show_name = True

        # Turn on visibility for DoF objects
        for c in cam_obj.children:
            if c.get("is_opt_vignetting", False) or c.get("is_bokeh_plane", False):
                c.hide_viewport = False
                c.hide_render = False

        # List all Cameras except self
        cameras = [o for o in obj if o.type == 'CAMERA' and o!= cam_obj]
        for cams in cameras:
            for c in cams.children:
                if c.get("is_opt_vignetting", False) or c.get("is_bokeh_plane", False):
                    c.hide_viewport = True
                    c.hide_render = True

        context.scene.camera = cam_obj

        if self.look_through:
            area = context.area
            if area:
                if area.type == 'VIEW_3D':
                    view_3d_area = area.spaces.active
                    view_3d_area.region_3d.view_perspective = 'CAMERA'

        if hasattr(context.space_data,'local_view'):
            if context.space_data.local_view:
                context.space_data.camera = cam_obj

        # # Leaving the Depsgraph update do its job
        # settings = context.scene.camera.data.photographer
        # update_settings(settings,context)

        # Unfortunately, we need to update the View Layer here because handler update doesn't do it
        bpy.ops.photographer.set_view_layer(view_layer=context.scene.camera.data.photographer.active_view_layer, use_scene_camera=True)

        return {'FINISHED'}
    
    def invoke (self, context, event):
        if event.alt:
            if context.scene.photographer.main_camera == bpy.data.objects[self.camera].data:
                context.scene.photographer['main_camera'] = 0
            else:
                context.scene.photographer.main_camera = bpy.data.objects[self.camera].data
        if event.ctrl:
            self.look_through = False
        if event.shift:
            bpy.ops.photographer.select(obj_name=self.camera)

        return self.execute(context)

class PHOTOGRAPHER_OT_AddDroneCamera(bpy.types.Operator):
    bl_idname = 'photographer.add_dronecamera'
    bl_label = 'Add Drone Camera'
    bl_description = "Create a Drone Camera that can fly to other cameras"
    bl_options = {'UNDO'}

    def execute(self,context):
        if context.area.spaces[0].region_3d.view_perspective == 'CAMERA':
            context.area.spaces[0].region_3d.view_perspective ='PERSP'

        if bpy.data.objects.get('DroneCamera') and bpy.data.objects.get('DroneCamera').type != 'CAMERA':
                self.report({'ERROR'}, "There is already an object named Drone Camera which isn't a camera. Please delete or rename it")
        else:

            # Switch to object mode to create camera
            if bpy.context.scene.collection.all_objects:
                if bpy.context.object and bpy.context.object.mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.camera_add()
            # Name camera
            context.active_object.name = "DroneCamera"
            drone_cam_obj = bpy.data.objects[bpy.context.active_object.name]
            # Make it the Scene camera
            context.scene.camera = drone_cam_obj
            bpy.ops.view3d.camera_to_view()
            drone_cam_obj.data.show_name = True
            drone_cam = drone_cam_obj.data
            # Default non-adjustable settings
            drone_cam_obj.data.photographer.exposure_mode = 'EV'
            drone_cam.photographer.shutter_speed_slider_enable = True
            drone_cam.photographer.aperture_slider_enable = True
            drone_cam.photographer.renderable = False

            # New Camera default settings from Preferences
            prefs = bpy.context.preferences.addons[base_package].preferences
            drone_cam.show_passepartout = prefs.default_show_passepartout
            drone_cam.passepartout_alpha = prefs.default_passepartout_alpha
            drone_cam.photographer.sensor_type = prefs.default_sensor_type
            drone_cam.photographer.fit_inside_sensor = prefs.fit_inside_sensor
            drone_cam.clip_start = prefs.default_clip_start
            drone_cam.clip_end = prefs.default_clip_end

        return{'FINISHED'}

def add_camera(self,context,duplicate=False,match_viewport=False):
    prefs = bpy.context.preferences.addons[base_package].preferences
    old_target = None
    new_cam_focal = context.space_data.lens / 2    
    if context.scene.camera:
        if context.scene.camera.type == 'CAMERA':
            if context.area.spaces[0].region_3d.view_perspective == 'CAMERA':
                if context.space_data.use_local_camera:
                    new_cam_focal = context.space_data.camera.data.lens
                else:
                    new_cam_focal = context.scene.camera.data.lens

            if context.scene.camera.data.photographer.target_enabled:
                old_target = get_target(context.scene.camera.name)

    context.area.spaces.active.region_3d.view_perspective = 'PERSP'

    # Disable Local Camera because of bug that would move the camera to the cursor location
    stored_use_local_camera = context.space_data.use_local_camera
    if context.space_data.use_local_camera:
        context.space_data.use_local_camera = False

    # Disable Local View because of bug that would move the camera to the cursor location
    stored_local_view = context.space_data.local_view
    if context.space_data.local_view:
        bpy.ops.object.select_all(action='SELECT')
        selected_objects = [obj for obj in bpy.context.selected_objects]
        bpy.ops.view3d.localview(frame_selected=False)

    # Using bpy.ops.object.camera_add() to get the right context for bpy.ops.view3d.camera_to_view()
    if bpy.context.scene.collection.all_objects:
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

    if duplicate:
        if context.scene.camera and context.scene.camera.type == 'CAMERA':
            old_cam = context.scene.camera
            copy_cam = context.scene.camera.data.copy()
            new_cam = bpy.ops.object.camera_add()
            new_cam_obj = bpy.data.objects[bpy.context.active_object.name]
            new_cam = new_cam_obj.data
            new_cam_obj.data = copy_cam
            new_cam_obj.matrix_world = old_cam.matrix_world.copy()
            # Delete the other camera data that just got created
            if not new_cam.users:
                bpy.data.cameras.remove(new_cam,do_unlink=True)
            # Redeclare new_cam variable
            new_cam = new_cam_obj.data
            # Force Creating Bokeh meshes
            new_cam.photographer.renderable = True
            if new_cam.photographer.opt_vignetting:
                new_cam.photographer.opt_vignetting = True
            if new_cam.photographer.bokeh:
                new_cam.photographer.bokeh = True
            if new_cam.photographer.show_focus_plane:
                bpy.ops.photographer.create_focus_plane(camera=new_cam_obj.name)
            context.scene.camera = new_cam_obj

            # Set focal to match viewport field of view
            if match_viewport:
                bpy.ops.view3d.camera_to_view()
                new_cam.lens = new_cam_focal
                if prefs.frame_full_viewport:
                    bpy.ops.view3d.view_center_camera()

            bpy.ops.photographer.look_through(camera=new_cam_obj.name)
            if old_target:
                create_target(context,old_target.location,new_cam_obj)

            return {'FINISHED'}
        else:
            self.report({"ERROR"}, "No Active Scene camera to duplicate")
            return {'CANCELLED'}

    new_cam = bpy.ops.object.camera_add()

    new_cam_obj = bpy.data.objects[bpy.context.active_object.name]
    new_cam = new_cam_obj.data

    if context.scene.camera and context.scene.camera.type == 'CAMERA':
        # Work around crash
        old_cam = context.scene.camera
        sfp = old_cam.data.photographer.show_focus_plane
        if sfp:
            old_cam.data.photographer.show_focus_plane = False

        #Set New Camera as Scene Camera
        context.scene.camera = new_cam_obj
        old_cam.data.photographer.show_focus_plane = sfp

    if context.scene.render.engine == 'LUXCORE':
        new_cam.photographer.exposure_enabled = False

    bpy.ops.view3d.camera_to_view()

    # New Camera default settings from Preferences
    new_cam.show_passepartout = prefs.default_show_passepartout
    new_cam.passepartout_alpha = prefs.default_passepartout_alpha
    new_cam.photographer.sensor_type = prefs.default_sensor_type
    new_cam.photographer.fit_inside_sensor = prefs.fit_inside_sensor
    new_cam.clip_start = prefs.default_clip_start
    new_cam.clip_end = prefs.default_clip_end

    # Set focal to match viewport field of view
    new_cam.lens = new_cam_focal

    # Copy Position if current camera is a Mesh or a light
    if context.scene.camera.type != 'CAMERA':
        new_cam_obj.location = context.scene.camera.location            

    # If spotlight, use the spot angle as focal length
    if context.scene.camera.type == 'LIGHT':
        if context.scene.camera.data.photographer.light_type == 'SPOT':    
            new_cam.lens_unit = 'FOV'
            new_cam.angle = context.scene.camera.data.photographer.spot_size
            new_cam.lens_unit = 'MILLIMETERS'            

    if prefs.frame_full_viewport:
        bpy.ops.view3d.view_center_camera()

    new_cam.photographer.exposure_mode = prefs.exposure_mode_pref
    new_cam.photographer.shutter_speed_slider_enable = prefs.shutter_speed_slider_pref
    new_cam.photographer.aperture_slider_enable = prefs.aperture_slider_pref
    new_cam.photographer.iso_slider_enable = prefs.iso_slider_pref

    if prefs.color_temperature_mode == 'BLENDER' and bpy.app.version >= (4,3,0):
        new_cam.photographer.tint = 10

    new_cam.show_composition_thirds = prefs.show_composition_thirds
    new_cam.show_composition_center = prefs.show_composition_center
    new_cam.show_composition_center_diagonal = prefs.show_composition_center_diagonal
    new_cam.show_composition_golden = prefs.show_composition_golden
    new_cam.show_composition_golden_tria_a = prefs.show_composition_golden_tria_a
    new_cam.show_composition_golden_tria_b = prefs.show_composition_golden_tria_b
    new_cam.show_composition_harmony_tri_a = prefs.show_composition_harmony_tri_a
    new_cam.show_composition_harmony_tri_b = prefs.show_composition_harmony_tri_b
    new_cam.photographer.focus_plane_color = prefs.default_focus_plane_color
    new_cam.photographer.focus_plane_edge = prefs.default_focus_plane_edge
    new_cam.show_name = True

    bpy.ops.photographer.look_through(camera=new_cam_obj.name)

    # Set World and Frames override if another cam already has it
    new_cam.photographer.cam_frame_start = context.scene.frame_start
    new_cam.photographer.cam_frame_end = context.scene.frame_end

    c_override_w = [c for c in bpy.data.cameras if c.photographer.override_world]
    if c_override_w and context.scene.world:
        new_cam.photographer.cam_world = context.scene.world
        new_cam.photographer.override_world = True

    c_override_f = [c for c in bpy.data.cameras if c.photographer.override_frames]
    if c_override_f:
        new_cam.photographer.override_frames = True

    # If no Main Camera is present in the scene, and this is the first created camera the scene
    if context.scene.photographer.main_camera == 'NONE':
        cameras = [o for o in context.scene.objects if o.type=='CAMERA']
        if len(cameras)==1:
            # Make it the Main Camera
            context.scene.photographer.main_camera = new_cam_obj.name

    # Restore Local Camera setting and assign new camera if true
    context.space_data.use_local_camera = stored_use_local_camera
    if stored_use_local_camera == True:
        context.space_data.camera = new_cam_obj

    # Restore Local View with selected objects
    if stored_local_view:
        for obj in selected_objects:
            obj.select_set(True)
        bpy.ops.view3d.localview(frame_selected=False)
        # Deselect all objects
        for obj in selected_objects:
            obj.select_set(False)

    return {'FINISHED'}

class PHOTOGRAPHER_OT_AddCamera(bpy.types.Operator):
    bl_idname = 'photographer.add_cam'
    bl_label = 'Add Camera'
    bl_description = ("Create camera from current view. \n"
                    "Shift-Click to copy over settings from the current Scene Camera")
    bl_options = {'REGISTER','UNDO'}

    duplicate = False

    def execute(self,context):
        add_camera(self,context,duplicate=self.duplicate,match_viewport=True)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.duplicate = event.shift
        return self.execute(context)

class PHOTOGRAPHER_OT_DuplicateCamera(bpy.types.Operator):
    bl_idname = 'photographer.duplicate_cam'
    bl_label = 'Duplicate Camera'
    bl_description = ("Duplicates Scene camera in its current location and look through it")
    bl_options = {'REGISTER','UNDO'}

    def execute(self,context):
        add_camera(self,context,duplicate=True)
        return {'FINISHED'}

# Delete Camera
class PHOTOGRAPHER_OT_DeleteCamera(bpy.types.Operator):
    bl_idname = 'photographer.delete_cam'
    bl_label = 'Delete Camera'
    bl_options = {'REGISTER','UNDO'}

    camera: bpy.props.StringProperty()
    use_global: bpy.props.BoolProperty(
                default=False,
                name="Delete Global",
                description="Delete from all Scenes")

    @classmethod
    def description(self, context, event):
        return f'Shift-Click to delete "{event.camera}" globally'

    def execute(self,context):
        scene = context.scene
        cam_obj = scene.objects.get(self.camera)
        settings = cam_obj.data.photographer

        # Removing possible children object first
        if settings.bokeh:
            settings.bokeh = False
        
        if settings.opt_vignetting:
            settings.opt_vignetting = False

        if settings.show_focus_plane:
            bpy.ops.photographer.delete_focus_plane(camera = self.camera)

        focus_obj = cam_obj.data.dof.focus_object
        if focus_obj is not None:
            if focus_obj.get("is_af_target", False):
                bpy.data.objects.remove(focus_obj)

        bpy.ops.photographer.target_delete(obj_name=self.camera)

        # Deleting camera
        bpy.data.objects.remove(cam_obj)

        return{'FINISHED'}

    def invoke(self, context, event):
        self.use_global = event.shift
        wm = context.window_manager
        if self.use_global:
            return wm.invoke_confirm(self, event)
        else:
            return self.execute(context)

class PHOTOGRAPHER_OT_SwitchCamera(bpy.types.Operator):
    bl_idname = "view3d.switch_camera"
    bl_label = "Switch to this camera"
    bl_description = "Switch to this camera"
    bl_options = {'REGISTER', 'UNDO'}

    camera: bpy.props.StringProperty()
    # timer = 0
    # func = None

    def execute(self,context):
        cam = self.camera

        if bpy.app.timers.is_registered(match_camera):
            # print ("Cancel previous timer")
            bpy.app.timers.unregister(match_camera)

        if bpy.data.objects.get('DroneCamera') and bpy.data.objects.get('DroneCamera').type == 'CAMERA':
            if context.scene.camera != bpy.data.objects.get('DroneCamera'):
                context.scene.camera = bpy.data.objects.get('DroneCamera')

            drone_cam = bpy.data.objects.get('DroneCamera').data
            # context.scene.camera.data.photographer.target_camera = bpy.data.objects.get(cam)
            drone_cam.photographer.target_camera = bpy.data.objects.get(cam)

            if drone_cam.photographer.target_camera is None:
                self.report({'WARNING'}, "The camera" + drone_cam.photographer.target_camera + " doesn't exist anymore."
                            "Are you using a keyboard shortcut assigned to an old camera? Either create a camera named"
                            + drone_cam.photographer.target_camera + ", or remove the shortcut")
                return {'CANCELLED'}

            else:
                self.report({'INFO'}, "Drone Camera: Matching...")
                # self.func = functools.partial(match_camera,self)
                bpy.app.timers.register(match_camera)
                return {'FINISHED'}

        else:
            self.report({'WARNING'}, "There is no Drone Camera in the scene. Please create one first")
            return {'CANCELLED'}

class PHOTOGRAPHER_OT_CycleCamera(bpy.types.Operator):
    bl_idname = "view3d.cycle_camera"
    bl_label = "Look through the previous or next camera"
    bl_description = "Cyles through cameras in the scene"
    bl_options = {'UNDO'}

    previous: bpy.props.BoolProperty()

    def execute(self,context):
        cameras,cam_collections = list_cameras(context)
        if not cameras:
            return {'CANCELLED'}

        current_cam = None
        target_camera = None

        if context.scene.camera:
            current_cam = context.scene.camera.name
            if current_cam == 'DroneCamera':
                target_camera = bpy.data.objects.get('DroneCamera').data.photographer.target_camera
                if target_camera:
                    current_cam = target_camera.name
                else:
                    current_cam = cameras[0]

        if context.scene.photographer.cam_list_sorting == 'COLLECTION':
            cameras = []
            for coll in cam_collections:
                coll_cams = [obj.name for obj in coll.objects if obj.type=='CAMERA']
                coll_cams.sort()
                for cam in coll_cams:
                    if cam != "DroneCamera":
                        cameras.append(cam)

        if current_cam is not None:
            target = current_cam
            start_index = cameras.index(current_cam)
            length = len(cameras)
            for i in range(1,length):
                if self.previous:
                    index = (start_index - i) % length
                else:
                    index = (start_index + i) % length
                cam = cameras[index]
                if context.scene.photographer.cycle_renderable_only:
                    if bpy.data.objects[cam].data.photographer.renderable:
                        target = cam
                        break
                else:
                    target = cam
                    break        
                
            if context.scene.camera.name == 'DroneCamera':
                if not target_camera:
                    target = cameras[0]
                bpy.ops.view3d.switch_camera(camera=target)
            else:
                bpy.ops.photographer.look_through(camera=target)

        # # If no cameras in Scene, look through the first one
        # else:
        #     bpy.ops.photographer.look_through(camera=cameras[0])

        return {'FINISHED'}

class PHOTOGRAPHER_OT_SetDroneCameraKey(bpy.types.Operator):
    bl_idname = "photographer.set_key"
    bl_label = "Set Drone Camera keyframe"
    bl_description = "Set animation keyframe on Drone Camera position, focal length, exposure, focus distance and white balance"
    bl_options = {'UNDO'}

    def execute(self, context):
        drone_cam_obj = bpy.data.objects.get('DroneCamera')
        drone_cam = drone_cam_obj.data
        settings = drone_cam.photographer

        current_frame = context.scene.frame_current
        drone_cam_obj.keyframe_insert(data_path='location', frame=(current_frame))
        drone_cam_obj.keyframe_insert(data_path='rotation_euler', frame=(current_frame))
        drone_cam.keyframe_insert(data_path='lens', frame=(current_frame))
        drone_cam.keyframe_insert(data_path='sensor_width', frame=(current_frame))
        settings.keyframe_insert(data_path='ev', frame=(current_frame))
        settings.keyframe_insert(data_path='exposure_compensation', frame=(current_frame))
        settings.keyframe_insert(data_path='shutter_speed', frame=(current_frame))
        settings.keyframe_insert(data_path='shutter_angle', frame=(current_frame))
        settings.keyframe_insert(data_path='aperture', frame=(current_frame))
        settings.keyframe_insert(data_path='lens_shift', frame=(current_frame))
        settings.keyframe_insert(data_path='lens_shift_x', frame=(current_frame))
        settings.keyframe_insert(data_path='color_temperature', frame=(current_frame))
        settings.keyframe_insert(data_path='tint', frame=(current_frame))
        # settings.keyframe_insert(data_path='motionblur_enabled', frame=(current_frame))
        settings.keyframe_insert(data_path='sensor_type', frame=(current_frame))
        drone_cam.dof.keyframe_insert(data_path='use_dof', frame=(current_frame))
        drone_cam.dof.keyframe_insert(data_path='aperture_ratio', frame=(current_frame))
        drone_cam.dof.keyframe_insert(data_path='aperture_blades', frame=(current_frame))
        drone_cam.dof.keyframe_insert(data_path='aperture_rotation', frame=(current_frame))
        drone_cam.dof.keyframe_insert(data_path='focus_distance', frame=(current_frame))
        #Resolution - CRASH WITH ANIMATION RENDER
        # settings.keyframe_insert(data_path='resolution_x', frame=(current_frame))
        # settings.keyframe_insert(data_path='resolution_y', frame=(current_frame))

        if context.scene.render.engine == 'CYCLES':
            context.scene.cycles.keyframe_insert(data_path='light_sampling_threshold', frame=(current_frame))
        # Light Threshold for EEVEE is not animatable
        # elif context.scene.render.engine == 'BLENDER_EEVEE':
        #     context.scene.eevee.keyframe_insert(data_path='light_threshold', frame=(current_frame))

        return{'FINISHED'}

class PHOTOGRAPHER_OT_SetPassePartout_Full(bpy.types.Operator):
    bl_idname = 'photographer.set_passepartout_full'
    bl_label = 'Set Passepartout to 1'
    bl_description = ("Set Scene Camera Passepartout to 1 for accurate Viewport Compositing")
    bl_options = {'REGISTER','UNDO'}

    camera : bpy.props.StringProperty()

    def execute(self,context):
        cam = bpy.data.cameras.get(self.camera,None)
        if cam:
            if not cam.show_passepartout:
                cam.show_passepartout = True
            cam.passepartout_alpha = 1.0
        return {'FINISHED'}
    

class PHOTOGRAPHER_OT_SetMainCamera(bpy.types.Operator):
    bl_idname = 'photographer.set_main_camera'
    bl_label = 'Set Main Camera'
    bl_description = ("Set Current Scene Camera as Main Camera")
    bl_options = {'REGISTER','UNDO'}

    def execute(self,context):
        if context.scene.camera:
            if context.scene.photographer.main_camera == context.scene.camera.data:
                context.scene.photographer['main_camera'] = None
            else:
                context.scene.photographer.main_camera = context.scene.camera.data
            return {'FINISHED'}
        
class PHOTOGRAPHER_OT_SetViewportShading(bpy.types.Operator):
    bl_idname = 'photographer.set_viewport_shading'
    bl_label = 'Set Viewport Shading'
    bl_description = ("Some features require to change Viewport Shading to the correct mode")
    bl_options = {'REGISTER','UNDO'}

    type : bpy.props.StringProperty()

    def execute(self,context):
        shading = context.area.spaces.active.shading
        shading.type = self.type
        return {'FINISHED'}
    
class PHOTOGRAPHER_OT_ResetCameraScale(bpy.types.Operator):
    bl_idname = 'photographer.reset_camera_scale'
    bl_label = 'Reset Camera Scaling'
    bl_description = ("Resets camera scale to 1.0, as scaling cameras could introduce rendering issues.")
    bl_options = {'REGISTER','UNDO'}

    camera : bpy.props.StringProperty()

    def execute(self,context):
        cam = bpy.data.objects.get(self.camera,None)
        if cam:
            cam.scale = (1,1,1)
        return {'FINISHED'}
    

    