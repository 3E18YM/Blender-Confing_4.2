import bpy, math
from bpy.props import BoolProperty, StringProperty

def get_resolution_ratio(cam_pg):
    ratio_x = ratio_y = 1
    if cam_pg.resolution_mode == '11':
        ratio_x = 1
        ratio_y = 1
    elif cam_pg.resolution_mode == '32':
        ratio_x = 3
        ratio_y = 2
    elif cam_pg.resolution_mode == '43':
        ratio_x = 4
        ratio_y = 3
    elif cam_pg.resolution_mode == '67':
        ratio_x = 7
        ratio_y = 6
    elif cam_pg.resolution_mode == '169':
        ratio_x = 16
        ratio_y = 9
    elif cam_pg.resolution_mode == '2351':
        ratio_x = 2.35
        ratio_y = 1
    elif cam_pg.resolution_mode == '2391':
        ratio_x = 2.3864
        ratio_y = 1
    elif cam_pg.resolution_mode == 'CUSTOM_RATIO':
        ratio_x = cam_pg.ratio_x
        ratio_y = cam_pg.ratio_y
        if cam_pg.resolution_rotation == 'PORTRAIT':
            ratio_x,ratio_y = ratio_y,ratio_x
    return ratio_x, ratio_y

def resize_fov(context,camera):
    cam_pg = camera.photographer
    scene = context.scene
    scene_pg = scene.photographer
    new_fov = 0.5

    if cam_pg.resize_orig_res_x == 0:
        cam_pg.resize_orig_res_x =  cam_pg.resolution_x
    if cam_pg.resize_orig_res_y == 0:
        cam_pg.resize_orig_res_y =  cam_pg.resolution_y

    if cam_pg.resolution_mode == 'CUSTOM_RES':
        if scene_pg.resize_mode == 'PIXEL_OFFSET':
            resize_resolution_x = cam_pg.resolution_x + scene_pg.resize_offset_x
            resize_resolution_y = cam_pg.resolution_y + scene_pg.resize_offset_y
        elif scene_pg.resize_mode == 'PIXEL':
            resize_resolution_x = scene_pg.resize_resolution_x
            resize_resolution_y = scene_pg.resize_resolution_y
    
    else:
        ratio_x, ratio_y = get_resolution_ratio(cam_pg)
        if scene_pg.resize_mode == 'PIXEL_OFFSET':
            resize_resolution_x = cam_pg.resolution_x + scene_pg.resize_offset_longedge
            resize_resolution_y = cam_pg.resolution_y + int(scene_pg.resize_offset_longedge * ratio_y / ratio_x)

        elif scene_pg.resize_mode == 'PIXEL':
            resize_resolution_x = scene_pg.resize_longedge
            resize_resolution_y = int(scene_pg.resize_longedge * ratio_y / ratio_x)

        if cam_pg.resolution_rotation == 'PORTRAIT':
             resize_resolution_x,resize_resolution_y =  resize_resolution_y,resize_resolution_x

    if camera.sensor_fit == 'HORIZONTAL':
        old_hfov = camera.angle
        old_vfov =  2 * math.atan(math.tan(old_hfov / 2) / cam_pg.resolution_y / cam_pg.resolution_x)
        new_fov  = 2 * math.atan(math.tan(old_hfov / 2) * (resize_resolution_x / cam_pg.resolution_x))

        hfov_offset = (cam_pg.resize_orig_res_x - resize_resolution_x) / resize_resolution_x / 2 # + cam_pg.resize_orig_shift_x
        vfov_offset = (cam_pg.resize_orig_res_y - resize_resolution_y) / resize_resolution_x / 2 # + cam_pg.resize_orig_shift_y

    elif camera.sensor_fit == 'VERTICAL':
        old_vfov = camera.angle
        old_hfov =  2 * math.atan(math.tan(old_vfov / 2) / cam_pg.resolution_y / cam_pg.resolution_x)
        new_fov = 2 * math.atan(math.tan(old_vfov / 2) * (resize_resolution_y / cam_pg.resolution_y))

        hfov_offset = (cam_pg.resize_orig_res_x - resize_resolution_x) / resize_resolution_y / 2 # + cam_pg.resize_orig_shift_x
        vfov_offset = (cam_pg.resize_orig_res_y - resize_resolution_y) / resize_resolution_y / 2 # + cam_pg.resize_orig_shift_y

    
    return new_fov, resize_resolution_x, resize_resolution_y, hfov_offset, vfov_offset


class PHOTOGRAPHER_OT_FlipImage(bpy.types.Operator):
    bl_idname = "photographer.flip_image"
    bl_label = "Flip Image"
    bl_description = ("Flip image horizontally or vertically. \n "
                    "Can be useful to get a fresh look at the current composition")
    bl_options = {'UNDO'}

    use_scene_camera : BoolProperty(default=False)
    x : BoolProperty(default=False)
    y : BoolProperty(default=False)

    def execute(self,context):
        if self.use_scene_camera:
            obj = context.scene.camera
        else:
            obj = [o for o in bpy.data.objects if o.type == 'CAMERA' and o.data is context.camera][0]

        if self.x:
         obj.scale[0] *= -1.0
        
        if self.y:
         obj.scale[1] *= -1.0
        
        return {'FINISHED'}

class PHOTOGRAPHER_OT_ResizeCanvas(bpy.types.Operator):
    bl_idname = "photographer.resize_canvas"
    bl_label = "Resize Canvas"
    bl_description = ("Resize canvas using a specific direction")
    bl_options = {'UNDO'}

    camera : StringProperty()

    def execute(self,context):
        camera = bpy.data.cameras.get(self.camera,None)
        scene_pg = context.scene.photographer
        if camera:
            cam_pg = camera.photographer

            if cam_pg.resolution_mode == 'CUSTOM_RES':
                if scene_pg.resize_mode == 'PIXEL':
                    if scene_pg.resize_resolution_x == cam_pg.resolution_x and scene_pg.resize_resolution_y == cam_pg.resolution_y:
                        return {'CANCELLED'}
                elif scene_pg.resize_mode == 'PIXEL_OFFSET':
                    if scene_pg.resize_offset_x == 0 and scene_pg.resize_offset_y == 0:
                        return {'CANCELLED'}
            else:
                if scene_pg.resize_mode == 'PIXEL':
                    if scene_pg.resize_longedge == cam_pg.longedge:
                        return {'CANCELLED'}
                elif scene_pg.resize_mode == 'PIXEL_OFFSET':
                    if scene_pg.resize_offset_longedge == 0:
                        return {'CANCELLED'}
                
            # Storing for revert
            if cam_pg.resize_stored_angle == 0:
                cam_pg.resize_stored_angle = camera.angle
            if cam_pg.resize_shift_x == 0:
                cam_pg.resize_orig_res_x = cam_pg.resolution_x
            if cam_pg.resize_shift_y == 0:
                cam_pg.resize_orig_res_y = cam_pg.resolution_y
            
            scene_pg.resize_stored_anchor = scene_pg.resize_anchor


            new_fov, resize_resolution_x, resize_resolution_y, hfov_offset, vfov_offset = resize_fov(context,camera)
            cam_pg.resolution_x = resize_resolution_x
            cam_pg.resolution_y = resize_resolution_y
            camera.angle = new_fov

            if scene_pg.resize_anchor == 'TOP_LEFT':
                cam_pg.resize_shift_x = -hfov_offset 
                cam_pg.resize_shift_y = vfov_offset
            elif scene_pg.resize_anchor == 'LEFT':
                cam_pg.resize_shift_x = -hfov_offset
            elif scene_pg.resize_anchor == 'BOTTOM_LEFT':
                cam_pg.resize_shift_x = -hfov_offset
                cam_pg.resize_shift_y = -vfov_offset

            if scene_pg.resize_anchor == 'TOP':
                cam_pg.resize_shift_y = vfov_offset
            elif scene_pg.resize_anchor == 'BOTTOM':
                cam_pg.resize_shift_y = -vfov_offset

            if scene_pg.resize_anchor == 'TOP_RIGHT':
                cam_pg.resize_shift_x = hfov_offset
                cam_pg.resize_shift_y = vfov_offset
            elif scene_pg.resize_anchor == 'RIGHT':
                cam_pg.resize_shift_x = hfov_offset
            elif scene_pg.resize_anchor == 'BOTTOM_RIGHT':
                cam_pg.resize_shift_x = hfov_offset
                cam_pg.resize_shift_y = -vfov_offset

            camera.shift_x = cam_pg.resize_shift_x + cam_pg.lens_shift_x
            camera.shift_y = cam_pg.resize_shift_y + cam_pg.lens_shift
            
            cam_pg.resize_orig_shift_x = 0
            cam_pg.resize_orig_shift_y = 0

        return {'FINISHED'}
        
class PHOTOGRAPHER_OT_ResetResizeResolution(bpy.types.Operator):
    bl_idname = "photographer.reset_resize_resolution"
    bl_label = "Reset Resize Resolution"
    bl_description = ("")
    bl_options = {'UNDO'}

    camera : StringProperty()

    def execute(self,context):
        camera = bpy.data.cameras.get(self.camera,None)
        if camera:
            scene_pg = context.scene.photographer
            scene_pg.resize_resolution_x = camera.photographer.resolution_x
            scene_pg.resize_resolution_y = camera.photographer.resolution_y
            scene_pg.resize_offset_x = 0
            scene_pg.resize_offset_y = 0

        return {'FINISHED'}
        
class PHOTOGRAPHER_OT_SetResizeAnchor(bpy.types.Operator):
    bl_idname = "photographer.set_resize_anchor"
    bl_label = "Resize Anchor"
    bl_description = ("Set Anchor to defines in which direction the Canvas will be resized")
    bl_options = {'UNDO'}

    anchor : StringProperty()
    camera : StringProperty()

    def execute(self,context):
        camera = bpy.data.cameras.get(self.camera,None)
        scene_pg = context.scene.photographer
        if camera:
            cam_pg = camera.photographer
            if scene_pg.resize_anchor != self.anchor:
                context.scene.photographer.resize_anchor = self.anchor
                # cam_pg.resize_orig_res_x = 0
                # cam_pg.resize_orig_res_y = 0
                # if scene_pg.resize_anchor in {'TOP_LEFT','LEFT','BOTTOM_LEFT'}:
                #     cam_pg.resize_orig_shift_x = -camera.shift_x
                # elif scene_pg.resize_anchor in {'TOP','CENTER','BOTTOM'}:
                #     cam_pg.resize_orig_shift_x = - camera.shift_x / 2
                # else:
                #     cam_pg.resize_orig_shift_x = - camera.shift_x

                # if scene_pg.resize_anchor in {'BOTTOM_LEFT','BOTTOM','BOTTOM_RIGHT'}:
                #     cam_pg.resize_orig_shift_y = - camera.shift_y
                # elif scene_pg.resize_anchor in {'LEFT','CENTER','RIGHT'}:
                #     cam_pg.resize_orig_shift_y = camera.shift_y / 2
                # else:
                #     cam_pg.resize_orig_shift_y = camera.shift_y
        
        return {'FINISHED'}

class PHOTOGRAPHER_OT_RevertResizeCanvas(bpy.types.Operator):
    bl_idname = "photographer.revert_resize_canvas"
    bl_label = "Revert Resize Canvas"
    bl_description = ("Resizing Canvas using different Anchors cannot be stacked at the moment. \n"
                      "This will revert to your original framing so you can resize using a different anchor point")
    bl_options = {'UNDO'}

    camera : StringProperty()

    def execute(self,context):
        camera = bpy.data.cameras.get(self.camera,None)
        scene_pg = context.scene.photographer
        if camera:
            cam_pg = camera.photographer
            camera.shift_x = cam_pg.lens_shift_x
            camera.shift_y = cam_pg.lens_shift
            camera.angle = cam_pg.resize_stored_angle
            cam_pg.resolution_x = cam_pg.resize_orig_res_x
            cam_pg.resolution_y = cam_pg.resize_orig_res_y

            cam_pg.resize_shift_x = 0
            cam_pg.resize_shift_y = 0
            cam_pg.resize_stored_angle = 0                       
            scene_pg.resize_stored_anchor = ''                     
                
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)

class PHOTOGRAPHER_OT_SetFixedSensorFit(bpy.types.Operator):
    bl_idname = "photographer.set_fixed_sensor_fit"
    bl_label = "Set Fixed Sensor Fit"
    bl_description = ("Replaces Fit inside Sensor or Auto Sensor Fit to a fixed Sensor Fit")
    bl_options = {'UNDO'}

    use_scene_camera : BoolProperty(default=False)

    def execute(self,context):
        if self.use_scene_camera:
            camera = context.scene.camera.data
        else:
            camera = context.camera

        pg = camera.photographer

        if pg.fit_inside_sensor:
            stored_fit = camera.sensor_fit
            pg.fit_inside_sensor = False
            camera.sensor_fit = stored_fit

        elif camera.sensor_fit == 'AUTO':
            if context.scene.render.resolution_x > context.scene.render.resolution_y:
                camera.sensor_fit = 'HORIZONTAL'
            else:
                camera.sensor_height = camera.sensor_width
                camera.sensor_fit = 'VERTICAL'

        return {'FINISHED'}