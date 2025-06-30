import bpy
from bpy.types import GizmoGroup, Operator
from mathutils import Matrix, Vector, Quaternion
from math import pi, radians, copysign, degrees
from mathutils import Vector, Matrix, Quaternion
from bpy.props import EnumProperty, FloatVectorProperty
from bpy_extras.view3d_utils import location_3d_to_region_2d
import math



class PT_GGT_gizmo_cursor(GizmoGroup):
    bl_idname = 'PT_GGT_gizmo_cursor'
    bl_label = 'Gizmo for 3D Cursor'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT', 'SHOW_MODAL_ALL'}


    @classmethod
    def poll(cls, context):
        if context.space_data.show_gizmo:
            return context.scene.pivot_set.cursor_gizmo


    @classmethod
    def setup_keymap(cls, keyconfig):
        if not keyconfig.keymaps.find( name='Gizmo PRO Tweak', space_type='VIEW_3D' ):
            km = keyconfig.keymaps.new( name = 'Gizmo PRO Tweak', space_type = 'VIEW_3D' )
            kmi = km.keymap_items.new( 'gizmogroup.gizmo_tweak', type = 'LEFTMOUSE',  value = 'CLICK_DRAG', any = True )
            kmi.alt,  kmi.oskey = False, False

        else:
            km = keyconfig.keymaps.find( name = 'Gizmo PRO Tweak', space_type = 'VIEW_3D' ) #km.restore_to_default()
            if len(km.keymap_items) < 1:
                kmi = km.keymap_items.new( 'gizmogroup.gizmo_tweak', type = 'LEFTMOUSE',  value = 'CLICK_DRAG', any = True )
                kmi.alt,  kmi.oskey = False, False

        return km

    def setup(self, context):

        color_x = (1.0, 0.13, 0.24)
        color_y = (0.545, 0.8, 0.0)
        color_z = (0.0, 0.4, 1.0)
        color_highlight = (0.0, 0.0, 0.0)
        alpha = 0.5
        alpha_highlight = 0.9

        # --- ARROW
        self.arrow_x = self.gizmos.new('GIZMO_GT_arrow_3d')
        self.arrow_x.use_tooltip = False
        self.arrow_x.use_draw_offset_scale = True
        self.arrow_x.use_draw_modal = True
        self.arrow_x.color = color_x
        self.arrow_x.color_highlight = color_highlight
        self.arrow_x.alpha = alpha
        self.arrow_x.alpha_highlight = alpha_highlight
        self.ar_x = self.arrow_x.target_set_operator('transform.translate')
        self.ar_x.constraint_axis = (True, False, False)
        self.ar_x.release_confirm = True
        self.ar_x.cursor_transform = True

        self.arrow_y = self.gizmos.new('GIZMO_GT_arrow_3d')
        self.arrow_y.use_tooltip = False
        self.arrow_y.use_draw_offset_scale = True
        self.arrow_y.use_draw_modal = True
        self.arrow_y.color = color_y
        self.arrow_y.color_highlight = color_highlight
        self.arrow_y.alpha = alpha
        self.arrow_y.alpha_highlight = alpha_highlight
        self.ar_y = self.arrow_y.target_set_operator('transform.translate')
        self.ar_y.constraint_axis = (False, True, False)
        self.ar_y.release_confirm = True
        self.ar_y.cursor_transform = True

        self.arrow_z = self.gizmos.new('GIZMO_GT_arrow_3d')
        self.arrow_z.use_tooltip = False
        self.arrow_z.use_draw_offset_scale = True
        self.arrow_z.use_draw_modal = True
        self.arrow_z.color = color_z
        self.arrow_z.color_highlight = color_highlight
        self.arrow_z.alpha = alpha
        self.arrow_z.alpha_highlight = alpha_highlight
        self.ar_z = self.arrow_z.target_set_operator('transform.translate')
        self.ar_z.constraint_axis = (False, False, True)
        self.ar_z.release_confirm = True
        self.ar_z.cursor_transform = True

        # --- DIAL
        self.dial_x = self.gizmos.new('GIZMO_GT_dial_3d')
        self.dial_x.draw_options = {'CLIP'} # 'FILL_SELECT', 'ANGLE_VALUE'
        self.dial_x.color = color_x
        self.dial_x.color_highlight = color_highlight
        self.dial_x.alpha = alpha
        self.dial_x.alpha_highlight = alpha_highlight
        self.dial_x.use_tooltip = False
        self.dial_x.use_draw_value = True
        self.op_dx = self.dial_x.target_set_operator('pt.rotate_cursor')
        self.op_dx.axis = 'X'

        self.dial_y = self.gizmos.new('GIZMO_GT_dial_3d')
        self.dial_y.draw_options = {'CLIP'}
        self.dial_y.color = color_y
        self.dial_y.color_highlight = color_highlight
        self.dial_y.alpha = alpha
        self.dial_y.alpha_highlight = alpha_highlight
        self.dial_y.use_tooltip = False
        self.dial_y.use_draw_value = True
        self.op_dy = self.dial_y.target_set_operator('pt.rotate_cursor')
        self.op_dy.axis = 'Y'

        self.dial_z = self.gizmos.new('GIZMO_GT_dial_3d')
        self.dial_z.draw_options = {'CLIP'}
        self.dial_z.color = color_z
        self.dial_z.color_highlight = color_highlight
        self.dial_z.alpha = alpha
        self.dial_z.alpha_highlight = alpha_highlight
        self.dial_z.use_tooltip = False
        self.dial_z.use_draw_value = True
        self.op_dz = self.dial_z.target_set_operator('pt.rotate_cursor')
        self.op_dz.axis = 'Z'


        # --- DOT
        self.dot = self.gizmos.new('GIZMO_GT_move_3d')
        self.dot.use_tooltip = False
        self.dot.color = (1.0, 0.13, 0.24)
        self.dot.color_highlight = color_highlight
        self.dot.alpha = alpha
        self.dot.alpha_highlight = alpha_highlight
        self.dot.draw_options = {'FILL_SELECT', 'ALIGN_VIEW'}
        self.ar_dot = self.dot.target_set_operator('transform.translate')
        self.ar_dot.release_confirm = True
        self.ar_dot.cursor_transform = True


    def invoke_prepare(self, context, gizmo):
        settings = context.scene.pivot_set
        self.op_dx.coordinate_system = settings.cursor_orient
        self.op_dy.coordinate_system = settings.cursor_orient
        self.op_dz.coordinate_system = settings.cursor_orient

        self.ar_x.orient_type = settings.cursor_orient
        self.ar_y.orient_type = settings.cursor_orient
        self.ar_z.orient_type = settings.cursor_orient

    def draw_prepare(self, context):
        settings = context.scene.pivot_set
        cursor = context.scene.cursor

        orient = settings.cursor_orient #'GLOBAL' if context.window.scene.transform_orientation_slots[0].type == 'GLOBAL' else 'CURSOR'
        self.ar_x.orient_type = orient
        self.ar_x.orient_matrix_type = orient
        self.ar_y.orient_type = orient
        self.ar_y.orient_matrix_type = orient
        self.ar_z.orient_type = orient
        self.ar_z.orient_matrix_type = orient

        sizeGizmo = 1
        sizeCursor = 1
        lwDot = 3

        coef = 0.2 if sizeCursor > 0.6 else 0.5
        # --- DOT
        self.dot.scale_basis = sizeCursor * coef
        self.dot.line_width = sizeGizmo * lwDot
        self.dot.matrix_basis = cursor.matrix.normalized()

        l, r, s  = cursor.matrix.decompose()
        #orient_slots = context.window.scene.transform_orientation_slots[0].type
        if settings.cursor_orient == 'GLOBAL':
            xR = Quaternion( (0.0, 1.0, 0.0), radians(90) )
            yR = Quaternion( (1.0, 0.0, 0.0), radians(-90) )
            zR = Quaternion( (0.0, 0.0, 1.0), radians(0) )
            x_matrix_move = Matrix.LocRotScale(l, xR, s).normalized()
            y_matrix_move = Matrix.LocRotScale(l, yR, s).normalized()
            z_matrix_move = Matrix.LocRotScale(l, zR, s).normalized()

            x_matrix_rot = x_matrix_move
            y_matrix_rot = y_matrix_move
            z_matrix_rot = z_matrix_move

        else:
            xR = r @ Quaternion( (0.0, 1.0, 0.0), radians(90) )
            yR = r @ Quaternion( (1.0, 0.0, 0.0), radians(-90) )
            zR = r
            x_matrix_move = Matrix.LocRotScale(l, xR, s).normalized()
            y_matrix_move = Matrix.LocRotScale(l, yR, s).normalized()
            z_matrix_move = Matrix.LocRotScale(l, zR, s).normalized()


            x_matrix_rot = Matrix.LocRotScale(l, (r @ Quaternion( (0.0, 1.0, 0.0), radians(90) )), s).normalized()
            y_matrix_rot = Matrix.LocRotScale(l, (r @ Quaternion( (1.0, 0.0, 0.0), radians(-90) )), s).normalized()
            z_matrix_rot = Matrix.LocRotScale(l, r, s).normalized()



        mo_a = Matrix.Translation(Vector( (0.0, 0.0, 0.7)))







        # --- ARROW
        self.arrow_x.length = 0.3
        self.arrow_x.line_width = sizeCursor * 3
        self.arrow_x.scale_basis = sizeCursor
        self.arrow_x.matrix_basis = x_matrix_move
        self.arrow_x.matrix_offset = mo_a

        self.arrow_y.length = 0.3
        self.arrow_y.line_width = sizeCursor * 3
        self.arrow_y.scale_basis = sizeCursor
        self.arrow_y.matrix_basis = y_matrix_move
        self.arrow_y.matrix_offset = mo_a

        self.arrow_z.length = 0.3
        self.arrow_z.line_width = sizeCursor * 3
        self.arrow_z.scale_basis = sizeCursor
        self.arrow_z.matrix_basis = z_matrix_move
        self.arrow_z.matrix_offset = mo_a

        # --- DIAL
        self.dial_x.scale_basis = sizeCursor * 0.7
        self.dial_x.line_width = sizeCursor * 3
        self.dial_x.matrix_basis = x_matrix_rot

        self.dial_y.scale_basis = sizeCursor * 0.7
        self.dial_y.line_width = sizeCursor * 3
        self.dial_y.matrix_basis = y_matrix_rot

        self.dial_z.scale_basis = sizeCursor * 0.7
        self.dial_z.line_width = sizeCursor * 3
        self.dial_z.matrix_basis = z_matrix_rot



class PT_OT_rotate_cursor(Operator):
    bl_idname = 'pt.rotate_cursor'
    bl_label = 'Rotate 3D Cursor'

    axis: EnumProperty(
        name='Axis',
        items=[
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
        ],
        default='Z',  # Default axis
    )

    coordinate_system: EnumProperty(
        name='Coordinate System',
        items=[
            ('GLOBAL', 'Global', ''),
            ('CURSOR', 'Local', ''),
        ],
        default='GLOBAL',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_rotation = None
        self.init_mouse_pos = None
        self.prev_mouse_pos = None  # Keep track of previous mouse position
        self.cursor_location_2d = None
        self.rotation_axis = Vector((0.0, 0.0, 1.0))  # Default to Z axis
        self.total_angle = 0.0  # Total accumulated rotation angle

    def invoke(self, context, event):
        self.init_rotation = context.scene.cursor.rotation_euler.copy()
        self.init_mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))
        self.prev_mouse_pos = self.init_mouse_pos.copy()  # Initialize previous mouse position

        # Get the 2D screen position of the 3D cursor
        region = context.region
        rv3d = context.region_data
        cursor_location_3d = context.scene.cursor.location
        self.cursor_location_2d = location_3d_to_region_2d(region, rv3d, cursor_location_3d)

        # Set the rotation axis based on the selected axis
        if self.axis == 'X':
            self.rotation_axis = Vector((1, 0, 0))
        elif self.axis == 'Y':
            self.rotation_axis = Vector((0, 1, 0))
        elif self.axis == 'Z':
            self.rotation_axis = Vector((0, 0, 1))

        # Transform the rotation axis if in LOCAL mode
        if self.coordinate_system == 'CURSOR':
            cursor_rot = context.scene.cursor.rotation_euler.to_matrix()
            self.rotation_axis = cursor_rot @ self.rotation_axis

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.rotate_cursor(context, event)
        elif event.type == 'LEFTMOUSE':
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.scene.cursor.rotation_euler = self.init_rotation
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def rotate_cursor(self, context, event):
        region = context.region
        rv3d = context.region_data

        current_mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))

        if self.cursor_location_2d is None:
            return

        # Vectors from the cursor position to the previous and current mouse positions
        prev_vector = self.prev_mouse_pos - self.cursor_location_2d
        current_vector = current_mouse_pos - self.cursor_location_2d

        if prev_vector.length == 0 or current_vector.length == 0:
            self.prev_mouse_pos = current_mouse_pos.copy()
            return

        # Calculate the angle between the two vectors
        delta_angle = prev_vector.angle(current_vector)

        # Determine the sign of the rotation
        cross_z = prev_vector.x * current_vector.y - prev_vector.y * current_vector.x
        sign = 1 if cross_z > 0 else -1

        delta_angle *= sign

        # Adjust for camera position relative to the cursor
        # Get the view vector
        if rv3d.view_perspective == 'CAMERA':
            # When looking through a camera, use the camera's view matrix
            view_vector = rv3d.view_matrix.inverted().col[2].xyz.normalized()
        elif rv3d.is_perspective:
            # Perspective view
            view_vector = rv3d.view_matrix.inverted().col[2].xyz.normalized()
        else:
            # Orthographic view
            view_vector = rv3d.view_rotation @ Vector((0, 0, 1))

        # Compute the dot product between the view vector and the rotation axis
        dot = view_vector.dot(self.rotation_axis)
        if dot < 0:
            delta_angle = -delta_angle

        # Adjust sensitivity
        if event.shift:
            delta_angle *= 0.1

        # Update total angle
        self.total_angle += delta_angle

        # Snapping
        if event.ctrl:
            snap_increment = context.scene.tool_settings.snap_angle_increment_3d  # in radians
            snapped_angle = round(self.total_angle / snap_increment) * snap_increment
        else:
            snapped_angle = self.total_angle

        # Create the rotation matrix around the selected axis
        rot_mat = Matrix.Rotation(snapped_angle, 3, self.rotation_axis)

        # Apply rotation from the initial rotation
        new_rot_mat = rot_mat @ self.init_rotation.to_matrix()

        # Convert back to Euler angles
        new_rotation_euler = new_rot_mat.to_euler()

        # Apply the new rotation to the cursor without changing its location
        context.scene.cursor.rotation_euler = new_rotation_euler

        # Update previous mouse position
        self.prev_mouse_pos = current_mouse_pos.copy()

    def execute(self, context):
        return {'FINISHED'}







classes = [
    PT_GGT_gizmo_cursor,
    PT_OT_rotate_cursor,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)