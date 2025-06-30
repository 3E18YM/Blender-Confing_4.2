import bpy, bgl, math, gpu
from ..functions.functions import  rgb_to_luminance, read_pixel_color
from ..functions.nodes import get_comp_group_node, get_comp_node_in_group
from ..properties.post_effects import postfx_grp_name
from .autofocus import hide_focus_planes
from ..constants import base_ev, photographer_presets_folder

class PHOTOGRAPHER_OT_AddExposureNode(bpy.types.Operator):
    bl_idname = "photographer.add_exposure_node"
    bl_label = "Add Exposure Node"
    bl_description = ("Apply Exposure during Compositing. \n Exposure won't be "
                    "visible in viewport if Viewport Compositing is disabled, but will be applied to EXR files")
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = context.scene
        if not scene.use_nodes:
            scene.use_nodes = True

        pfx_node = get_comp_group_node(context,postfx_grp_name)
        
        if not pfx_node:
            bpy.ops.photographer.post_effects_add()
            pfx_node = get_comp_group_node(context,postfx_grp_name)

        # Make sure PostFX node is also enabled
        if pfx_node.mute:
            pfx_node.mute = False

        # Get Exposure node in PFX group
        exposure_node = get_comp_node_in_group(pfx_node,'exposure')
        if exposure_node:
            exposure_node.mute = False

        # Turn on Compositing rendering
        scene.render.use_compositing = True
        exposure_node.inputs['Exposure'].default_value = scene.view_settings.exposure
        scene.view_settings.exposure = 0

        return {'FINISHED'}


class PHOTOGRAPHER_OT_DisableExposureNode(bpy.types.Operator):
    bl_idname = "photographer.disable_exposure_node"
    bl_label = "Disable Exposure Node"
    bl_description = "Remove Exposure from Compositing and use Color Management Exposure"
    bl_options = {'UNDO'}

    def execute(self, context):
        pfx_node = get_comp_group_node(bpy.context,postfx_grp_name)
        if pfx_node:
            exposure_node = get_comp_node_in_group(pfx_node,'exposure')
            if exposure_node:
                exposure_node.mute = True
                context.scene.view_settings.exposure = exposure_node.inputs['Exposure'].default_value

        return {'FINISHED'}


def exposure_picker(self,context):
    if self.use_scene_camera:
        settings = context.scene.camera.data.photographer
    else:
        settings = context.camera.photographer

    x,y = self.mouse_region_x, self.mouse_region_y
    # print (x,y)

    values = count = 0

    if bpy.app.version >= (3,2,2):
        # get currently bound framebuffer
        buffer = gpu.state.active_framebuffer_get()
    else:
        bgl.glDisable(bgl.GL_DEPTH_TEST)
        buffer = bgl.Buffer(bgl.GL_FLOAT, 3)

    for i in range(x-4, x+5):
        for j in range(y-4, y+5):
            value = read_pixel_color(i,j,buffer)
            lum = rgb_to_luminance(value)
            if lum != 0:
                    values += lum
                    count += 1

    if count != 0:            
        lum_avg = values/count
        # print("Luminance: " + str(lum_avg))

        # Exposure target
        mid_grey = 0.18
        diff_lum = lum_avg / mid_grey
        if diff_lum > 0:
            target = math.log2(diff_lum)
            settings.ev = base_ev + target

    del buffer

class PHOTOGRAPHER_OT_EVPicker(bpy.types.Operator):
    bl_idname = "exposure.picker"
    bl_label = "Pick Exposure"
    bl_description = "Pick a mid grey area in the 3D view to adjust the Exposure"
    bl_options = {'REGISTER', 'UNDO'}

    use_scene_camera: bpy.props.BoolProperty(default=False)
    mouse_region_x: bpy.props.IntProperty(default=0)
    mouse_region_y: bpy.props.IntProperty(default=0)
    comp_exposure: bpy.props.BoolProperty(default=False)

    def modal(self, context, event):
        if self.use_scene_camera:
            settings = context.scene.camera.data.photographer
        else:
            settings = context.camera.photographer

        context.area.tag_redraw()

        self.mouse_region_x = event.mouse_region_x
        self.mouse_region_y = event.mouse_region_y

        # Allow navigation for Blender and Maya shortcuts
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt and event.type == 'LEFTMOUSE' or event.alt and event.type == 'RIGHTMOUSE':
            return {'PASS_THROUGH'}

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if context.area.type=='VIEW_3D':
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            
            # Apply EV to Exposure Node or the next comp_exposure restoration will override the correct exposure
            pfx_node = get_comp_group_node(bpy.context,postfx_grp_name)
            if pfx_node:
                exposure_node = get_comp_node_in_group(pfx_node,'exposure')
                if exposure_node:
                    exposure_node.inputs['Exposure'].default_value = context.scene.view_settings.exposure

            # Restore Apply at Compositing
            context.scene.photographer.comp_exposure = self.comp_exposure

            # Restore Mouse Cursor from EYEDROPPER Icon
            if self.cursor_set:
                context.window.cursor_modal_restore()

            # Restore Focus Planes visibility
            for o in self.fp:
                o.hide_viewport = False

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            if context.area.type=='VIEW_3D':
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

            # Restore previous state
            context.scene.photographer.comp_exposure = self.comp_exposure
            settings.ev = self.stored_exposure
            settings.exposure_mode = self.stored_exposure_mode
            # Restore Focus Planes visibility
            for o in self.fp:
                o.hide_viewport = False

            # Restore Mouse Cursor from EYEDROPPER Icon
            if self.cursor_set:
                context.window.cursor_modal_restore()

            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):

        self.comp_exposure = False

        if context.area.type=='VIEW_3D':
            if self.use_scene_camera:
                settings = context.scene.camera.data.photographer
            else:
                settings = context.camera.photographer

            # Work around Apply at Compositing picker issue
            if context.scene.photographer.comp_exposure:
                self.comp_exposure = True
                context.scene.photographer.comp_exposure = False

            # Store state
            self.stored_exposure = settings.ev
            self.stored_exposure_mode = settings.exposure_mode

            self.fp = hide_focus_planes()

            if not settings.exposure_mode == 'EV':
                settings.exposure_mode = 'EV'

            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(exposure_picker, args, 'WINDOW', 'PRE_VIEW')

            # Set Cursor to EYEDROPPER icon
            self.cursor_set = True
            context.window.cursor_modal_set('EYEDROPPER')

            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}

        else:
            self.report({'WARNING'}, "No 3D view found")
            return {'CANCELLED'}

class PHOTOGRAPHER_OT_AddColorChart(bpy.types.Operator):
    bl_idname = "photographer.add_color_chart"
    bl_label = "Add Color Chart"
    bl_description = "Creates a plane at Cursor location with a Color Chart texture"
    bl_options = {'UNDO'}

    def execute(self, context):
        # Check if Color Chart object already exists
        colorcharts=[obj for obj in bpy.data.objects if obj.get("is_color_chart",False)]
        if colorcharts:
            for obj in colorcharts:
                obj.hide_viewport = False
                return {'FINISHED'}
        
        # Make sure we are in Object mode
        if context.object and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Create a plane at Cursor location
        bpy.ops.mesh.primitive_plane_add(size=1, location=context.scene.cursor.location)
        plane = context.selected_objects[0]
        plane.name = "Color Chart"
        plane.display_type = 'TEXTURED'
        plane.hide_render = True
        plane.visible_shadow = False
        # Add property to recognize Color Chart object
        plane['is_color_chart'] = True

        # Create a new material with Color Chart texture
        if not bpy.data.materials.get('Color Chart'):
            mat = bpy.data.materials.new(name='Color Chart')
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get('Principled BSDF')
            bsdf.inputs['Roughness'].default_value = 1
            tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
            tex.location = (-300,300)
            tex.image = bpy.data.images.load(photographer_presets_folder+"/exposure/ColorChart.png", check_existing=True)
            mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
        else:
            # Assign existing material to plane
            mat = bpy.data.materials.get('Color Chart')
        plane.data.materials.append(mat)
    
        return {'FINISHED'}
    