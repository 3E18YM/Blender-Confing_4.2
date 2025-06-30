import bpy, mathutils
from ..functions.functions import raycast
from ..functions.ui import draw_object_name_under_mouse

from .autofocus import hide_focus_planes, hide_dof_objects

def create_target(context,location,obj):
    # Reuse Target if one with camera name exists (workaround for Pointer crash)
    tgt = [o for o in bpy.data.objects if o.name == obj.name + "_Target"]
    if not tgt:
        target = bpy.data.objects.new(obj.name + "_Target", None)
        target.scale = (0.2,0.2,0.2)
        target.empty_display_type = "CUBE"
        target.show_name = True
        target.show_in_front = True
        target["is_target"] = True
        if obj.users_collection:
            obj_coll_name = obj.users_collection[0].name
            if obj_coll_name == 'Scene Collection':
                context.scene.collection.objects.link(target)
            else:
                bpy.data.collections[obj_coll_name].objects.link(target)
    else:
        target = tgt[0]

    # Clear previous Constraints
    constraints = [c for c in obj.constraints if c.name == "Aim Target"]
    if constraints:
        for c in constraints:
            obj.constraints.remove(c)

    # Create Constraints
    constraint = obj.constraints.new('TRACK_TO')
    constraint.name = "Aim Target"
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    target.location = location

    return target

def delete_target(obj_name):
    obj = bpy.data.objects[obj_name]
    settings = obj.data.photographer

    for c in obj.constraints:
        if c.target is not None:
            if c.target.get("is_target", False):
                bpy.data.objects.remove(c.target)
                obj.constraints.remove(c)

    settings.target_enabled = False

def get_target(obj_name):
    obj = bpy.data.objects[obj_name]
    for c in obj.constraints:
        if c.target is not None:
            if c.target.get("is_target", False):
                return c.target

class PHOTOGRAPHER_OT_TargetAdd(bpy.types.Operator):
    """Aim Target: Click where you want to place the target"""
    bl_idname = "photographer.target_add"
    bl_label = "Add Target"
    bl_description = ("Adds an Aim target on the object surface that you pick. \n"
                    "Ctrl-Click to create target at the center of the Camera frame. \n"
                    "Shift-Click to parent the target to the picked object")
    bl_options = {'UNDO'}

    obj_name: bpy.props.StringProperty()
    parent: bpy.props.BoolProperty()

    def draw_callback_px(self, context):
        if self.object_name:
            draw_object_name_under_mouse(self, True, self.parent)

    def modal(self, context, event):
        # Allow navigation for Blender and Maya shortcuts
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt and event.type == 'LEFTMOUSE' or event.alt and event.type == 'RIGHTMOUSE':
            return {'PASS_THROUGH'}

        obj = bpy.data.objects[self.obj_name]
        settings = obj.data.photographer

        context.area.tag_redraw()
        # Parent if Shift is pressed during modal
        self.parent = event.shift

        if event.type == 'MOUSEMOVE':
            self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            result, location, object, normal = raycast(context, event, obj)
            if result:
                self.object_name = object.name
            else:
                self.object_name = ""

        # Enter Target Picker
        if event.type == 'LEFTMOUSE':
            if event.value == 'RELEASE':
                if context.space_data.type == 'VIEW_3D':
                    # try:
                    #Raycast and store the hit location
                    result, location, object, normal = raycast(context, event, obj)
                    if not result:
                        self.report({'WARNING'}, "Raycast failed. Is the targeted object a mesh? Are you looking through the scene camera in this 3D view?")

                    else:
                        #Select what's under the mouse and store its name
                        if object is not None:
                            #Calculate the location relative to the parent object
                            if self.parent:
                                new_loc = object.matrix_world.inverted() @ location
                            else:
                                new_loc = location

                            #Create Target object at the hit location
                            target = create_target(context,new_loc,obj)

                            target.empty_display_size = (1.0/abs(obj.scale.x))/5.0
                            if self.parent:
                                #Parent the target object to the object under the mask
                                target.parent = object

                            #Set the Tracking to enable
                            settings.target_enabled = True
                        else:
                            self.report({'WARNING'}, "Failed to find an object under the mouse, the Tracker could not be placed")

                        #Restore the previous selection
                        # for obj in bpy.context.selected_objects:
                        #     obj.select_set(False)
                        # for o in current_sel:
                        #     bpy.data.objects[o.name].select_set(True)
                        # if active_obj:
                        #     context.view_layer.objects.active = active_obj

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
        self.object_name = ""
        self.mouse_pos = (0,0)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, (context,), 'WINDOW', 'POST_PIXEL')

        if event.ctrl:
            obj = bpy.data.objects[self.obj_name]
            settings = obj.data.photographer

            location_offset = mathutils.Vector((0, 0, -4))
            location = obj.matrix_world @ location_offset
            target = create_target(context,location,obj)
            target.empty_display_size = (1.0/abs(obj.scale.x))/5.0
            settings.target_enabled = True
            return {'FINISHED'}

        else:
            self.cursor_set = True
            context.window.cursor_modal_set('EYEDROPPER')
            context.window_manager.modal_handler_add(self)

            # Hide all Focus Planes and DoF objects
            self.fp = hide_focus_planes()
            self.dof_objects = []
            unit_scale = context.scene.unit_settings.scale_length 
            if unit_scale != 1:
                self.dof_objects = hide_dof_objects()

            self.parent = event.shift

            return {'RUNNING_MODAL'}


class PHOTOGRAPHER_OT_TargetDelete(bpy.types.Operator):
    bl_idname = "photographer.target_delete"
    bl_label = "Delete Target"
    bl_description = "Remove Aim Target"
    bl_options = {'REGISTER', 'UNDO'}

    obj_name: bpy.props.StringProperty()

    def execute(self, context):
        delete_target(self.obj_name)
        obj = bpy.data.objects[self.obj_name]
        if obj.type == 'LIGHT':
            obj.select_set(True)
            context.view_layer.objects.active = obj
        return{'FINISHED'}

class PHOTOGRAPHER_OT_TargetRefreshNames(bpy.types.Operator):
    bl_idname = "photographer.target_refresh_names"
    bl_label = "Refresh Target Names"
    bl_description = ("Rename all Targets using their parent Camera or Light name. \n"
        "Useful if Cameras or Lights got renamed after adding their targets")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.scene.objects:
            if obj.type in {'CAMERA','LIGHT'} and obj.constraints.get("Aim Target") is not None:
                target = obj.constraints["Aim Target"].target
                if target.name != obj.name+'_Target':
                    target.name = obj.name+'_Target'
        return{'FINISHED'}