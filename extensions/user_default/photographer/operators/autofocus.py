import bpy, math, blf
from .. import __package__ as base_package
from ..functions.functions import raycast, duplicate_object
from ..functions.lens_sim_compatibility import get_lens_sim_node
from ..functions.ui import draw_object_name_under_mouse
from mathutils import Vector
from mathutils.geometry import distance_point_to_plane

def set_focus_distance(cam_obj,hit_location):
    cam_dir = cam_obj.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
    dist = abs(distance_point_to_plane(cam_obj.matrix_world.to_translation(), hit_location, cam_dir))
    # print ('dist = ' + str(dist))
    cam_obj.data.dof.focus_distance = dist

def dof_calculation(fstop, fl, sw, sh, magnification=1):
    # https://en.wikipedia.org/wiki/Depth_of_focus#Calculation
    N = fstop
    f = fl / 1000 * magnification

    # Calculate Circle of confusion (diameter limit based on d/1500)
    # https://en.wikipedia.org/wiki/Circle_of_confusion#Circle_of_confusion_diameter_limit_based_on_d.2F1500
    c = math.sqrt(sw**2 + sh**2) / 1500    
    a = math.pow(f, 2) / (N * c * magnification / 1000)
    h = a + f
    return a, f, h 

def dof_hyperfocal(camera_data):
    fstop = camera_data.dof.aperture_fstop
    fl = camera_data.lens
    sw = camera_data.sensor_width
    sh = camera_data.sensor_height

    # Compared with online hyperfocal calculator
    # https://www.omnicalculator.com/other/hyperfocal-distance
    a,f,h = dof_calculation(fstop, fl, sw, sh, magnification=1)
    return round(h,2)

# AF Tracker functions
def create_af_target(context,location):
    cam_obj = context.scene.camera

    # Reuse AF_Target if one with camera name exists (workaround for Pointer crash)
    tgt = [o for o in bpy.data.objects if o.name == cam_obj.name + "_AF_Tracker"]
    if not tgt:
        af_target = bpy.data.objects.new(cam_obj.name + "_AF_Tracker", None)
        af_target.empty_display_type = "CUBE"
        af_target.show_name = True
        af_target.show_in_front = True
        af_target["is_af_target"] = True

        cam_coll_name = cam_obj.users_collection[0].name
        if bpy.data.collections.get(cam_coll_name,False):
            bpy.data.collections[cam_coll_name].objects.link(af_target)
        else:
            context.scene.collection.objects.link(af_target)
    else:
        af_target = tgt[0]

    cam_obj.data.dof.focus_object = af_target
    af_target.location = location

    return af_target

def set_af_key(context):
    cam = context.scene.camera.data

    current_frame = context.scene.frame_current
    cam.dof.keyframe_insert(data_path='focus_distance', frame=(current_frame))

def stop_playback(scene):
    settings = scene.camera.data.photographer

    if scene.frame_current == scene.frame_end:
        bpy.ops.screen.animation_cancel(restore_frame=False)
        settings.af_continuous_enabled = False
        bpy.app.handlers.frame_change_pre.remove(stop_playback)

def hide_focus_planes():
    # Clear list
    list = []
    # Disable Focus Plane of all cameras that could block the rays
    for o in bpy.data.objects:
        if o.get("is_focus_plane", False):
            if o.hide_viewport == False:
                list.append(o)
                o.hide_viewport = True
    return list

def hide_dof_objects():
    # Clear list
    list = []
    # Disable Focus Plane of all cameras that could block the rays
    for o in bpy.data.objects:
        if o.get("is_opt_vignetting", False) or o.get("is_bokeh_plane", False):
            if o.hide_viewport == False:
                list.append(o)
                o.hide_viewport = True
    return list

def update_dof_limits(self,context):
    cam_obj = [o for o in bpy.data.objects if o.type == 'CAMERA' and o.data is self.id_data][0]
    for c in cam_obj.children:
        if c.get("is_dof_limits", False):
            if self.dof_limits == 'OFF':
                c.hide_viewport = True
            elif self.dof_limits == 'WIRE':
                c.hide_viewport = False
                c.visible_camera = False
                c.display_type = 'BOUNDS'
                c.display_bounds_type = 'CONE'
            elif self.dof_limits == 'SHADED':
                c.visible_camera = True
                c.hide_viewport = False
                c.display_type = 'TEXTURED'

class PHOTOGRAPHER_OT_CreateFocusPlane(bpy.types.Operator):
    bl_idname = "photographer.create_focus_plane"
    bl_label = "Show Focus Plane"
    bl_description = "Adds Plane to visualize focus distance"
    bl_options = {'REGISTER', 'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        cam_obj = bpy.data.objects[self.camera]
        cam = cam_obj.data

        #Store the current object selection
        current_sel = context.selected_objects
        active_obj = context.view_layer.objects.active

        # Remove Camera scaling that would break the drivers
        if cam_obj.scale != [1,1,1]:
            cam_obj.scale = [1,1,1]

        # Deselect current selection
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode="OBJECT")
        
        for obj in bpy.context.selected_objects:
            obj.select_set(False)

        # Create Plane and name it
        bpy.ops.mesh.primitive_plane_add()
        focus_plane = context.view_layer.objects.active
        focus_plane.name = cam_obj.name + "_FocusPlane"

        focus_plane["is_focus_plane"] = True

        # Parent to Camera using No Inverse
        # (could not find command to parent with no_inverse, using operator instead)
        bpy.data.objects[cam_obj.name].select_set(True)
        bpy.data.objects[focus_plane.name].select_set(True)
        context.view_layer.objects.active = bpy.data.objects[cam_obj.name]
        bpy.ops.object.parent_no_inverse_set()

        #Restore the previous selection
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        for o in current_sel:
            bpy.data.objects[o.name].select_set(True)
        if active_obj:
            context.view_layer.objects.active = active_obj

        # Lock Focus Plane transform for user
        focus_plane.lock_location = focus_plane.lock_rotation = focus_plane.lock_scale = [True, True, True]

        # Disable selectable and hide from render
        focus_plane.hide_select = True
        focus_plane.hide_render = True
        focus_plane.visible_shadow = False

        # Enable Camera Limits to move the plane
        cam.show_limits = True

        # Plane location Z from Focus Distance
        d = focus_plane.driver_add('location',2).driver
        var = d.variables.new()
        var.name = 'fstop'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'dof.aperture_fstop'

        var = d.variables.new()
        var.name = 'fl'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'lens'

        var = d.variables.new()
        var.name = 'sw'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'sensor_width'

        var = d.variables.new()
        var.name = 'sh'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'sensor_height'

        if cam.dof.focus_object is not None:
            var = d.variables.new()
            var.name = 'cam_matrix'
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = cam_obj
            target.data_path = 'matrix_world'

            var = d.variables.new()
            var.name = 'tracker_matrix'
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = cam.dof.focus_object
            target.data_path = 'matrix_world'

            d.expression = "distance_to_plane(cam_matrix,tracker_matrix)"

        else:
            # Plane location Z from Focus Distance
            d = focus_plane.driver_add('location',2).driver
            var = d.variables.new()
            var.name = 'dist'
            target = var.targets[0]
            target.id_type = 'CAMERA'
            target.id = cam
            target.data_path = 'dof.focus_distance'

            d.expression = "-dist"

        # Plane location Y from Lens Shift and Focus distance
        d = focus_plane.driver_add('location',1).driver
        var = d.variables.new()
        var.name = 'lens_shift'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'shift_y'

        var = d.variables.new()
        var.name = 'fl'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'lens'

        var = d.variables.new()
        var.name = 'fstop'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'dof.aperture_fstop'

        var = d.variables.new()
        var.name = 'sw'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'sensor_width'

        var = d.variables.new()
        var.name = 'sh'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'sensor_height'

        var = d.variables.new()
        var.name = 'sf'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'sensor_fit'

        if cam.dof.focus_object is not None:
            var = d.variables.new()
            var.name = 'dist'
            var.type = 'LOC_DIFF'
            target = var.targets[0]
            target.id = cam_obj
            target = var.targets[1]
            target.id = cam.dof.focus_object
        else:
            var = d.variables.new()
            var.name = 'dist'
            target = var.targets[0]
            target.id_type = 'CAMERA'
            target.id = cam
            target.data_path = 'dof.focus_distance'

        d.expression = "tan(atan(lens_shift/(fl/sh)))*dist if (sf==2) else tan(atan(lens_shift/(fl/sw)))*dist"

        # Plane location X from Lens Shift and Focus distance
        d = focus_plane.driver_add('location',0).driver
        var = d.variables.new()
        var.name = 'lens_shift'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'shift_x'

        var = d.variables.new()
        var.name = 'fl'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'lens'

        var = d.variables.new()
        var.name = 'fstop'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'dof.aperture_fstop'

        var = d.variables.new()
        var.name = 'sw'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'sensor_width'

        var = d.variables.new()
        var.name = 'sh'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'sensor_height'

        var = d.variables.new()
        var.name = 'sf'
        target = var.targets[0]
        target.id_type = 'CAMERA'
        target.id = cam
        target.data_path = 'sensor_fit'

        if cam.dof.focus_object is not None:
            var = d.variables.new()
            var.name = 'dist'
            var.type = 'LOC_DIFF'
            target = var.targets[0]
            target.id = cam_obj
            target = var.targets[1]
            target.id = cam.dof.focus_object
        else:
            var = d.variables.new()
            var.name = 'dist'
            target = var.targets[0]
            target.id_type = 'CAMERA'
            target.id = cam
            target.data_path = 'dof.focus_distance'

        d.expression = "tan(atan(lens_shift/(fl/sh)))*dist if (sf==2) else tan(atan(lens_shift/(fl/sw)))*dist"

        # Scale driver
        fcurve_driver = focus_plane.driver_add('scale')
        drivers = [f.driver for f in fcurve_driver]
        for d in drivers:
            var = d.variables.new()
            var.name = 'rX'
            target = var.targets[0]
            target.id_type = 'SCENE'
            target.id = context.scene
            target.data_path = 'render.resolution_x'

            var = d.variables.new()
            var.name = 'rY'
            target = var.targets[0]
            target.id_type = 'SCENE'
            target.id = context.scene
            target.data_path = 'render.resolution_y'

            var = d.variables.new()
            var.name = 'fstop'
            target = var.targets[0]
            target.id_type = 'CAMERA'
            target.id = cam
            target.data_path = 'dof.aperture_fstop'

            var = d.variables.new()
            var.name = 'fl'
            target = var.targets[0]
            target.id_type = 'CAMERA'
            target.id = cam
            target.data_path = 'lens'

            var = d.variables.new()
            var.name = 'sw'
            target = var.targets[0]
            target.id_type = 'CAMERA'
            target.id = cam
            target.data_path = 'sensor_width'

            var = d.variables.new()
            var.name = 'sh'
            target = var.targets[0]
            target.id_type = 'CAMERA'
            target.id = cam
            target.data_path = 'sensor_height'

            var = d.variables.new()
            var.name = 'sf'
            target = var.targets[0]
            target.id_type = 'CAMERA'
            target.id = cam
            target.data_path = 'sensor_fit'

            # var = d.variables.new()
            # var.name = 'vfov'
            # target = var.targets[0]
            # target.id_type = 'CAMERA'
            # target.id = cam
            # target.data_path = 'photographer.lock_vertical_fov'

            if cam.dof.focus_object is not None:
                var = d.variables.new()
                var.name = 'dist'
                var.type = 'LOC_DIFF'
                target = var.targets[0]
                target.id = cam_obj
                target = var.targets[1]
                target.id = cam.dof.focus_object
            else:
                var = d.variables.new()
                var.name = 'dist'
                target = var.targets[0]
                target.id_type = 'CAMERA'
                target.id = cam
                target.data_path = 'dof.focus_distance'

            drivers[0].expression = '(dist * (sh/2) * rX) / (rY * fl) if (sf==2) else ((dist * (sw/2) / fl) if rX > rY else ((dist * (sw/2) * rX) / (rY * fl)))'
            drivers[1].expression = '(dist * (sh/2) / fl) if (sf==2) else ((dist * (sw/2) / fl) if rY > rX else ((dist * (sw/2) * rY) / (rX * fl)))'
            drivers[2].expression = '1'

        # Get material
        mat_name = focus_plane.name + "_Mat"
        mat = bpy.data.materials.get(mat_name)
        if mat is None:
            # create material
            mat = bpy.data.materials.new(name=mat_name)

        # Assign it to object
        if focus_plane.data.materials:
            # Assign to 1st material slot
            focus_plane.data.materials[0] = mat
        else:
            # Append if no slots
            focus_plane.data.materials.append(mat)

        # Viewport material settings
        mat.roughness = 1
        if bpy.app.version < (4,2,0):
            mat.blend_method = 'BLEND'
            mat.shadow_method = 'NONE'
        else:
            mat.surface_render_method = 'BLENDED'

        mat.diffuse_color = bpy.context.preferences.addons[base_package].preferences.default_focus_plane_color

        # Enable 'Use nodes':
        mat.use_nodes = True

        if mat.node_tree:
            mat.node_tree.links.clear()
            mat.node_tree.nodes.clear()

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Add lightpath shader
        lightpath = nodes.new('ShaderNodeLightPath')
        lightpath.location = (-400,0)

        # Add mix RGB
        mix_rgb = nodes.new('ShaderNodeMixRGB')
        mix_rgb.location = (-200,0)
        mix_rgb.name = "Focus Plane Color"
        mix_rgb.inputs[1].default_value = (0,0,0,1)
        mix_rgb.inputs[2].default_value = bpy.context.preferences.addons[base_package].preferences.default_focus_plane_color

        # Add emission shader
        emission = nodes.new('ShaderNodeEmission')
        emission.location = (0,0)

        # Add transparent shader
        transp = nodes.new('ShaderNodeBsdfTransparent')
        transp.location = (0,100)

         # Add Ambient Occlusion
        ao = nodes.new('ShaderNodeAmbientOcclusion')
        ao.location = (-200,600)
        ao.inputs[1].default_value = 1
        ao.inside=True

         # Add Contrast node
        contrast = nodes.new('ShaderNodeBrightContrast')
        contrast.location = (0,500)
        contrast.inputs[2].default_value = 0.1

        # Add Edge Detection Value
        edge = nodes.new('ShaderNodeValue')
        edge.location = (0,300)
        edge.name = edge.label = 'Edge Detection'
        edge.outputs[0].default_value = bpy.context.preferences.addons[base_package].preferences.default_focus_plane_edge

        # Add Alpha Value
        alpha = nodes.new('ShaderNodeValue')
        alpha.location = (0,200)
        alpha.name = alpha.label = 'Alpha'
        alpha.outputs[0].default_value = 0.4

        # Add Math Multiply
        mult = nodes.new('ShaderNodeMath')
        mult.location = (200,500)
        mult.operation = 'MULTIPLY'

        # Add Math Add
        add = nodes.new('ShaderNodeMath')
        add.location = (300,300)
        add.operation = 'ADD'
        add.use_clamp = True

        # Add mix shader
        mix = nodes.new('ShaderNodeMixShader')
        mix.location = (500,0)

        # Add output node
        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (700,0)

        # Connect all of them
        links.new(lightpath.outputs[0], mix_rgb.inputs[0])
        links.new(mix_rgb.outputs[0], emission.inputs[0])
        links.new(transp.outputs[0], mix.inputs[1])
        links.new(emission.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], output.inputs[0])

        links.new(ao.outputs[1], contrast.inputs[0])
        links.new(contrast.outputs[0], mult.inputs[0])
        links.new(edge.outputs[0], mult.inputs[1])
        links.new(mult.outputs[0], add.inputs[0])
        links.new(alpha.outputs[0], add.inputs[1])

        if bpy.app.version >= (4,2,0):
            links.new(add.outputs[0], mix.inputs[0])
        else:
            links.new(alpha.outputs[0], mix.inputs[0])

        # LuxCore support
        if context.scene.render.engine == 'LUXCORE':
            mat.luxcore.use_cycles_nodes = True
            # Force Viewport Refresh with a nasty trick
            shading = context.area.spaces.active.shading.type
            if shading == 'RENDERED':
                context.area.spaces.active.shading.type = 'WIREFRAME'
                context.area.spaces.active.shading.type = 'RENDERED'

        cam.photographer.show_focus_plane = True
        # Trick to set Focus Plane color if it has been changed
        cam.photographer.focus_plane_color = cam.photographer.focus_plane_color
        cam.photographer.focus_plane_edge = cam.photographer.focus_plane_edge

        depth_near = duplicate_object(focus_plane,True,True, bpy.context.collection)
        depth_near["is_dof_limits"] = True
        depth_near.name = cam_obj.name + "_DOF_Near"
        depth_near.visible_camera = False
        depth_near.visible_diffuse = False
        depth_near.visible_shadow = False
        for d in depth_near.animation_data.drivers:
            if "dist" in d.driver.expression:
                if "distance_to_plane" in d.driver.expression and cam.dof.focus_object is not None:
                    d.driver.expression = "dof_near_tracker(cam_matrix,tracker_matrix, fstop, fl, sw, sh)"
                else:
                    new_exp = d.driver.expression.replace("dist","dof_near(fstop, dist, fl, sw, sh)")
                    d.driver.expression = new_exp

        depth_far = duplicate_object(focus_plane,True,True, bpy.context.collection)
        depth_far["is_dof_limits"] = True
        depth_far.name = cam_obj.name + "_DOF_Far"
        depth_far.visible_camera = False
        depth_far.visible_diffuse = False
        depth_far.visible_shadow = False
        update_dof_limits(cam.photographer,context)
        for d in depth_far.animation_data.drivers:
            if "dist" in d.driver.expression:
                if "distance_to_plane" in d.driver.expression and cam.dof.focus_object is not None:
                    d.driver.expression = "dof_far_tracker(cam_matrix,tracker_matrix, fstop, fl, sw, sh)"
                else:
                    new_exp = d.driver.expression.replace("dist","dof_far(fstop, dist, fl, sw, sh)")
                    d.driver.expression = new_exp

        return {'FINISHED'}

class PHOTOGRAPHER_OT_DeleteFocusPlane(bpy.types.Operator):
    bl_idname = "photographer.delete_focus_plane"
    bl_label = "Hide Focus Plane"
    bl_description = "Removes Focus Plane object"
    bl_options = {'REGISTER', 'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        obj = bpy.data.objects
        cam_obj = obj[self.camera]
        cam = cam_obj.data

        # Disable Camera Limits
        cam.show_limits = False

        for c in cam_obj.children:
            # Checking to see if this object has the custom flag written to it- it will default to False in the event that the key does not exist
            if c.get("is_focus_plane", False):
                if isinstance(c.data, bpy.types.Mesh):
                    # remove the mesh data first, while the object still exists
                    bpy.data.meshes.remove(c.data)
                    try:
                        bpy.data.objects.remove(c)
                    except ReferenceError:
                        # ignore a ReferenceError exception when the StructRNA is removed
                        pass

        cam.photographer.show_focus_plane = False

        return {'FINISHED'}

class PHOTOGRAPHER_OT_FocusSingle(bpy.types.Operator):
    """Autofocus Single - Click on a mesh in the viewport to set the focus on its surface"""
    bl_idname = "photographer.focus_single"
    bl_label = "Autofocus Single"
    bl_options = {'REGISTER', 'UNDO'}

    def draw_callback_px(self, context):
        if self.object_name:
            draw_object_name_under_mouse(self)

    def modal(self, context, event):
        # Allow navigation for Blender and Maya shortcuts
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt and event.type == 'LEFTMOUSE' or event.alt and event.type == 'RIGHTMOUSE':
            return {'PASS_THROUGH'}

        cam_obj = context.scene.camera
        cam = cam_obj.data
        settings = cam.photographer

        # Disable AF-C if using AF-C
        if settings.af_continuous_enabled:
            settings.af_continuous_enabled = False

        if event.type == 'MOUSEMOVE':
            context.area.tag_redraw()
            self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            result, location, object, normal = raycast(context, event, cam_obj)
            if result:
                self.object_name = object.name
            else:
                self.object_name = ""

        # Enter focus picker
        if event.type == 'LEFTMOUSE':
            if event.value == 'RELEASE':
                if context.space_data.type == 'VIEW_3D':
                    # try:
                    #Enable DoF
                    if not settings.use_dof:
                        settings.use_dof = True

                    result, location, object, normal = raycast(context, event, cam_obj)

                    if not result:
                        self.report({'WARNING'}, "Raycast failed. Is the targeted object a mesh? Are you looking through the scene camera in this 3D view?")

                    elif context.scene.camera.data.dof.focus_object is not None:
                        self.report({'WARNING'}, "The camera already has a focus object, which will override the results of the Autofocus")
                        self.cancel(context)
                        return {'CANCELLED'}

                    else:
                        set_focus_distance(cam_obj,location)

                        #Set key if animate is on
                        if settings.af_animate:
                            bpy.ops.object.select_all(action='DESELECT')
                            bpy.data.objects[context.scene.camera.name].select_set(True)
                            context.view_layer.objects.active = context.scene.camera

                            set_af_key(context)

                        self.cancel(context)
                        return {'FINISHED'}
                else:
                    self.report({'WARNING'}, "Active space must be a View3d")
                    self.cancel(context)
                    return {'CANCELLED'}

        # Cancel Modal with RightClick and ESC
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
    
    def cancel(self,context):
        # Restore cursor
        if self.cursor_set:
            context.window.cursor_modal_restore()
        # Restore Focus Planes and DoF objects visibility
        for o in self.fp + self.dof_objects:
            o.hide_viewport = False 
        
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        context.area.tag_redraw()

    def invoke(self, context, event):
        self.cursor_set = True
        self.object_name = ""
        self.mouse_pos = (0,0)

        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, (context,), 'WINDOW', 'POST_PIXEL')
        context.window.cursor_modal_set('EYEDROPPER')
        context.window_manager.modal_handler_add(self)       

        # Hide all Focus Planes
        self.fp = hide_focus_planes()
        self.dof_objects = []
        unit_scale = context.scene.unit_settings.scale_length 
        if unit_scale != 1:
            self.dof_objects = hide_dof_objects()

        return {'RUNNING_MODAL'}

class PHOTOGRAPHER_OT_FocusTracking(bpy.types.Operator):
    """Autofocus Tracker: Click where you want to place the tracker"""
    bl_idname = "photographer.focus_tracking"
    bl_label = "Photographer Focus Tracking"
    bl_options = {'REGISTER', 'UNDO'}

    parent: bpy.props.BoolProperty()

    def draw_callback_px(self, context):
        if self.object_name:
            draw_object_name_under_mouse(self, True, self.parent)

    def modal(self, context, event):
        # Allow navigation for Blender and Maya shortcuts
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt and event.type == 'LEFTMOUSE' or event.alt and event.type == 'RIGHTMOUSE':
            return {'PASS_THROUGH'}

        cam_obj = context.scene.camera
        cam = context.scene.camera.data
        settings = cam.photographer

        context.area.tag_redraw()
        # Parent if Shift is pressed during modal
        self.parent = event.shift

        # Disable AF-C if using AF-C
        if settings.af_continuous_enabled:
            settings.af_continuous_enabled = False

        if event.type == 'MOUSEMOVE':
            self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            result, location, object, normal = raycast(context, event, cam_obj)
            if result:
                self.object_name = object.name
            else:
                self.object_name = ""

        # Enter focus picker
        if event.type == 'LEFTMOUSE':
            if event.value == 'RELEASE':
                if context.space_data.type == 'VIEW_3D':
                    # try:
                    #Raycast and store the hit location
                    result, location, object, normal = raycast(context, event, cam_obj)
                    if not result:
                        self.report({'WARNING'}, "Raycast failed. Is the targeted object a mesh? Are you looking through the scene camera in this 3D view?")

                    else:
                        cam['tracked_object'] = None
                        set_focus_distance(cam_obj,location)
                        #Enable DoF
                        if not settings.use_dof:
                            settings.use_dof = True

                        #Find what's under the mouse and set as parent
                        if object is not None:

                            if self.parent:
                                #Calculate the location relative to the parent object
                                location = object.matrix_world.inverted() @ location

                            #Create AF Tracking target object at the hit location
                            af_target = create_af_target(context,location)

                            af_target.empty_display_size = (1.0/object.scale.x)/10.0
                            #Parent the target object to the object under the mask
                            if self.parent:
                                af_target.parent = object
                                cam['tracked_object'] = object.name

                        else:
                            self.report({'WARNING'}, "Failed to find an object under the mouse, the Tracker could not be parented")

                        self.cancel(context)
                        return {'FINISHED'}
                else:
                    self.report({'WARNING'}, "Active space must be a View3d")
                    self.cancel(context)
                    return {'CANCELLED'}

        # Cancel Modal with RightClick and ESC
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
    
    def cancel(self,context):
        cam_obj = context.scene.camera
        # Restore cursor
        if self.cursor_set:
            context.window.cursor_modal_restore()
        # Restore Focus Planes and DoF objects visibility
        for o in self.fp + self.dof_objects:
            o.hide_viewport = False

        # Recreate Focus Plane
        if self.restore_focus_plane:
            bpy.ops.photographer.create_focus_plane(camera = cam_obj.name)
        
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        context.area.tag_redraw()

    def invoke(self, context, event):
        self.cursor_set = True
        self.object_name = ""
        self.mouse_pos = (0,0)

        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, (context,), 'WINDOW', 'POST_PIXEL')
        context.window.cursor_modal_set('EYEDROPPER')
        context.window_manager.modal_handler_add(self)

        # Focus Tracking needs to recreate the Focus Plane with correct drivers
        cam_obj = context.scene.camera
        settings = cam_obj.data.photographer

        self.restore_focus_plane = False
        if settings.show_focus_plane:
            bpy.ops.photographer.delete_focus_plane(camera = cam_obj.name)
            self.restore_focus_plane = True

        # Hide other cameras' focus planes
        self.fp = hide_focus_planes()
        self.dof_objects = hide_dof_objects()
        self.parent = event.shift
        return {'RUNNING_MODAL'}


class PHOTOGRAPHER_OT_FocusTracking_Cancel(bpy.types.Operator):
    """Autofocus Tracking Cancel"""
    bl_idname = "photographer.focus_tracking_cancel"
    bl_label = "Photographer Focus Tracking Cancel"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        cam_obj = context.scene.camera
        cam = cam_obj.data
        settings = cam.photographer

        restore_focus_plane = False
        # Delete Focus plane
        if settings.show_focus_plane:
            restore_focus_plane = True
            bpy.ops.photographer.delete_focus_plane(camera = cam_obj.name)

        focus_obj = cam.dof.focus_object
        if focus_obj is not None:
            if focus_obj.get("is_af_target", False):
                bpy.data.objects.remove(focus_obj)
            else:
                cam.dof.focus_object = None

            # settings.af_target = None

        # Restore Focus plane for correct distance driver
        if restore_focus_plane:
            bpy.ops.photographer.create_focus_plane(camera = cam_obj.name)

        return{'FINISHED'}


class PHOTOGRAPHER_OT_Bake_Autofocus(bpy.types.Operator):
    bl_idname = "photographer.bake_autofocus"
    bl_label = "Bake Animation"
    bl_description = ("Bake Auto Exposure or Autofocus to animation keys using the current range of the timeline")
    bl_options = {'UNDO'}

    def draw(self, context):
        layout = self.layout
        pg = context.scene.camera.data.photographer
        step = str(round(pg.af_continuous_interval * context.scene.render.fps))
        layout.label(text="Frame step based on AF-C interval and FPS: " + step)
        layout.label(text="Baking will delete already present keys.")
        layout.label(text="Do you want to continue?")

    def execute(self,context):
        scene = context.scene
        scene.frame_set(frame=scene.frame_start)
        
        cam = scene.camera.data
        pg = cam.photographer

        if cam.animation_data and cam.animation_data.action:
            for fcurve in cam.animation_data.action.fcurves:
                if fcurve.data_path == "dof.focus_distance":
                    cam.animation_data.action.fcurves.remove(fcurve)       

        step = round(pg.af_continuous_interval * scene.render.fps)
        if not pg.af_continuous_enabled:
            pg.af_continuous_enabled = True
        while scene.frame_current <= scene.frame_end:
            focus_continuous()
            cam.dof.keyframe_insert(data_path='focus_distance', frame=(scene.frame_current))
            scene.frame_set(frame = scene.frame_current + int(step))

        scene.frame_current = self.stored_current_frame
        pg.af_continuous_enabled = False

        return {'FINISHED'}
    
    def invoke(self,context,event):
        # Select Camera and make active or you won't notice you are adding a key in the timeline
        if context.scene.camera and context.scene.camera.type =='CAMERA':
            cam_obj = context.scene.camera
            for obj in bpy.context.selected_objects:
                obj.select_set(False)
            cam_obj.select_set(True)

            self.stored_current_frame = context.scene.frame_current
        
            return context.window_manager.invoke_props_dialog(self)

# Focus continuous timer function
def focus_continuous():
    context = bpy.context
    scene = context.scene
    cam_obj = scene.camera
    cam = cam_obj.data
    settings = cam.photographer
    timer = settings.af_continuous_interval

    # Do not AF-C if active camera is not a camera
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            if area.spaces[0].region_3d.view_perspective == 'CAMERA' :
                if cam_obj and cam_obj.type == 'CAMERA':
                    if settings.af_continuous_enabled :
                        #Enable DoF
                        if not settings.use_dof:
                            settings.use_dof = True

                        result, location, object, normal = raycast(context, None, cam_obj, continuous=True)
                        if result:
                            set_focus_distance(cam_obj,location)
                        #Little trick to update viewport as the header distance doesn't update automatically
                        # exposure = scene.view_settings.exposure
                        # scene.view_settings.exposure = exposure

                    #Set key if animate is on
                    if settings.af_animate:
                        #Select camera to see the keyframes
                        if bpy.ops.object.mode_set.poll():
                            bpy.ops.object.mode_set(mode="OBJECT")
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.data.objects[context.scene.camera.name].select_set(True)
                        context.view_layer.objects.active = cam_obj
                        set_af_key(context)

    return timer


def active_cam_check(context):
    # Hide AF buttons if looking through scene camera
    if bpy.context.preferences.addons[base_package].preferences.show_af_buttons_pref:
        # for area in bpy.context.screen.areas:
        if context.area.type == 'VIEW_3D':
            if context.area.spaces[0].region_3d.view_perspective == 'CAMERA' :
                if context.scene.camera:
                    if context.scene.camera.type == 'CAMERA':
                        return True

def focus_single_button(self, context):
    if active_cam_check(context):
        cam = context.scene.camera.data
        settings = cam.photographer
        if cam.dof.focus_object is None:
            icon_af = 'RESTRICT_RENDER_OFF'
            if settings.af_animate:
                icon_af = 'KEYTYPE_KEYFRAME_VEC'
            self.layout.operator("photographer.focus_single", text="AF-S", icon=icon_af)

def focus_continuous_button(self, context):
    if active_cam_check(context):
        cam = context.scene.camera.data
        settings = cam.photographer
        if cam.dof.focus_object is None:
            icon_af = 'HOLDOUT_ON'
            if settings.af_animate:
                icon_af = 'KEYTYPE_KEYFRAME_VEC'
            self.layout.prop(settings, "af_continuous_enabled", text="AF-C", icon=icon_af )

def focus_animate_button(self, context):
    if active_cam_check(context):
        settings = context.scene.camera.data.photographer
        self.layout.prop(settings, "af_animate", text="", icon="KEY_HLT" )

def focus_tracking_button(self, context):
    if active_cam_check(context):
        cam = context.scene.camera.data
        settings = cam.photographer
        if cam.dof.focus_object is None:
            self.layout.operator("photographer.focus_tracking", text="AF-Track", icon='OBJECT_DATA')
        if cam.dof.focus_object is not None:
            self.layout.operator("photographer.focus_tracking_cancel", text="Cancel AF Tracking", icon='OBJECT_DATA')

def focus_distance_header(self, context):
    if active_cam_check(context):
        cam = context.scene.camera.data
        if cam.dof.focus_object is None:
            dof_distance = str(round(context.scene.camera.data.dof.focus_distance*context.scene.unit_settings.scale_length,2))
            if not context.scene.unit_settings.system == 'NONE':
                dof_distance = dof_distance + "m"
            self.layout.label(text=dof_distance)

class PHOTOGRAPHER_OT_LensSim_SetFocusDistanceMode(bpy.types.Operator):
    bl_idname = "photographer.lens_sim_set_focus_distance_mode"
    bl_label = "Set Lens Sim Distance"
    bl_description = ("Only Distance Mode is supported for Lens Sim with Photographer at the moment")
    bl_options = {'UNDO'}

    cam_obj:bpy.props.StringProperty()

    def execute(self,context):
        cam_obj = bpy.data.objects.get(self.cam_obj,False)
        if cam_obj:
            if cam_obj.get('lens_sim_cam',False):
                lens_sim = get_lens_sim_node(cam_obj)
                if lens_sim.inputs["focus mode"].default_value != 1:
                    lens_sim.inputs["focus mode"].default_value = 1
        return {'FINISHED'}
